from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import io
import pandas as pd
from app.s3_ingestor import upload_to_s3
from app.vector_data_ingestor import ingest
from app.resume_data_extractor import extract_resume_data
from app.text_extractor import extract_text_from_file
from config import get_env_vars
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

router = APIRouter()

env_vars = get_env_vars()
OPEN_AI_KEY = env_vars['OPEN_AI_KEY']
S3_BUCKET_NAME = env_vars['S3_BUCKET_NAME']

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})

@router.post("/upload_resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    global vectordb, rag_pipeline, llm
    
    df_list = []
    for file in files:
        try:
            content = await file.read()
            text = extract_text_from_file(content)
            
            df_list.append({"ID": file.filename, "Content": text})
            
            # Upload to S3
            s3_file_name = f"resumes/{file.filename}"
            status, url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
            if not status:
                raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
    
    try:
        # Upload to VectorDB
        df = pd.DataFrame(df_list)
        vectordb = ingest(df, "Content", embedding_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting data to vector database: {str(e)}")

    try:
        # Extract data in JSON form resume using LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=OPEN_AI_KEY)
        json_resume_list = extract_resume_data(df_list, llm)
        # Save the extracted JSON resume data to mongoDB candidate table
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting resume data: {str(e)}")

    return {"message": f"Successfully processed {len(df_list)} resume files."}