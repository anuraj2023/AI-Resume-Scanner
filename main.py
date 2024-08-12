from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
from typing import List
import uvicorn
import json
from app.s3_ingestor import upload_to_s3
from app.data_ingestor import ingest
from app.retriever import SelfQueryRetriever
from app.llm_agent import ChatBot
from langchain_huggingface import HuggingFaceEmbeddings
from config import get_env_vars
import io
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load environment variables
env_vars = get_env_vars()
OPEN_AI_KEY = env_vars['OPEN_AI_KEY']
S3_BUCKET_NAME = env_vars['S3_BUCKET_NAME']

# Initialize global variables
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
vectordb = None
rag_pipeline = None
llm = None
job_description = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]

@app.post("/upload_resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    global vectordb, rag_pipeline, llm
    
    df_list = []
    for file in files:
        content = await file.read()
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(io.BytesIO(content))
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        df_list.append({"ID": file.filename, "Content": text})
        
        # Upload to S3
        s3_file_name = f"resumes/{file.filename}"
        status, url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
        if not status:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
    
    df = pd.DataFrame(df_list)
    vectordb = ingest(df, "Content", embedding_model)
    rag_pipeline = SelfQueryRetriever(vectordb, df)
    llm = ChatBot(api_key=OPEN_AI_KEY, model="gpt-3.5-turbo")
    
    return {"message": f"Successfully processed {len(df_list)} resume files."}

@app.post("/upload_job_description/")
async def upload_job_description(file: UploadFile = File(...)):
    global job_description
    content = await file.read()
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(io.BytesIO(content))
    elif file.filename.endswith('.docx'):
        text = extract_text_from_docx(io.BytesIO(content))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
    
    # Upload to S3
    s3_file_name = f"job-descriptions/{file.filename}"
    status, url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
    if not status:
        raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
    
    job_description = text
    
    return {"message": f"Successfully uploaded job description: {file.filename}"}

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            query = data['query']
            history = data.get('history', [])
            
            if not vectordb or not rag_pipeline or not llm:
                await websocket.send_text(json.dumps({"error": "Please upload resumes first."}))
                continue
            
            if not job_description:
                await websocket.send_text(json.dumps({"error": "Please upload a job description first."}))
                continue
            
            document_list = rag_pipeline.retrieve_docs(query, llm, "Generic RAG")
            query_type = rag_pipeline.meta_data["query_type"]
            
            # Include job description in the context
            document_list.append(f"Job Description: {job_description}")
            
            stream_message = llm.generate_message_stream(query, document_list, history, query_type)
            
            async for chunk in stream_message:
                await websocket.send_text(json.dumps({"chunk": chunk}))
            
            await websocket.send_text(json.dumps({"complete": True}))
    except WebSocketDisconnect:
        print("WebSocket disconnected")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = DocxDocument(docx_file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)