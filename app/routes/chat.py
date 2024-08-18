from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from pymilvus import Milvus
from app.prisma import prisma
from app.dao.workflow_dao import WorkflowDAO
from app.models import ChatMessage
from app.retriever import SelfQueryRetriever
from app.llm_agent import ChatBot
from config import get_env_vars

router = APIRouter()

env_vars = get_env_vars()
EMBEDDING_MODEL = env_vars['EMBEDDING_MODEL']
MILVUS_URI = env_vars['MILVUS_URI']
MILVUS_API_KEY = env_vars['MILVUS_API_KEY']
OPEN_AI_KEY = env_vars['OPEN_AI_KEY'] 

workflow_dao = WorkflowDAO(prisma)

# @router.websocket("/websocket/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             data = json.loads(data)
#             query = data['query']
#             history = data.get('history', [])
#             vectorstore_db = Milvus.from_existing_index(
#                                 embedding=embedding_model,
#                                 collection_name="resume_collection",
#                                 connection_args={
#                                     "uri": MILVUS_URI,
#                                     "token": MILVUS_API_KEY
#                                 }
#                             )

#             if not vectordb or not rag_pipeline or not llm:
#                 await websocket.send_text(json.dumps({"error": "Please upload resumes first."}))
#                 continue
            
#             if not job_description:
#                 await websocket.send_text(json.dumps({"error": "Please upload a job description first."}))
#                 continue
            
#             try:
#                 # Below 2 lines are important
#                 rag_pipeline = SelfQueryRetriever(vectordb, df)
#                 llm = ChatBot(api_key=OPEN_AI_KEY, model="gpt-4o-mini")
#                 document_list = rag_pipeline.retrieve_docs(query, llm, "Generic RAG")
#                 query_type = rag_pipeline.meta_data["query_type"]
                
#                 # Include job description in the context
#                 document_list.append(f"Job Description: {job_description}")
                
#                 stream_message = llm.generate_message_stream(query, document_list, history, query_type)
                
#                 async for chunk in stream_message:
#                     await websocket.send_text(json.dumps({"chunk": chunk}))
                
#                 await websocket.send_text(json.dumps({"complete": True}))
#             except Exception as e:
#                 await websocket.send_text(json.dumps({"error": f"Error processing query: {str(e)}"}))
#     except WebSocketDisconnect:
#         print("WebSocket disconnected")

@router.post("/chat")
async def chat_with_documents(msg: ChatMessage, workflow_id: str):
    try:
        while True:
            query = msg.content
            #history = data.get('history', [])
            history = []
            vector_db = Milvus(
                            embedding_function=EMBEDDING_MODEL,
                            collection_name="resume_collection",
                            connection_args={
                                "uri": MILVUS_URI,
                                "token": MILVUS_API_KEY
                            }
                        )

            if not vector_db:
                print("vector db not found")
                return {"error": "vector db error"}
            
            try:
                # Below 2 lines are important
                rag_pipeline = SelfQueryRetriever(vector_db)
                llm = ChatBot(api_key=OPEN_AI_KEY, model="gpt-4o-mini")
                document_list = rag_pipeline.retrieve_docs(query, llm, "Generic RAG")
                query_type = rag_pipeline.meta_data["query_type"]
                print("query type is : ", query_type)

                workflow = await workflow_dao.get_workflow_with_candidates(workflow_id)
                print("workflow is : ", workflow)
                
                # Include job description in the context
                document_list.append(f"Job Description: {workflow.jobDescription}")
                
                stream_message = llm.generate_message_stream(query, document_list, history, query_type)
                return stream_message
                
            except Exception as e:
                print("Exception occured : ", str(e))
    except Exception as e:
        print("Exception occured : ", str(e))