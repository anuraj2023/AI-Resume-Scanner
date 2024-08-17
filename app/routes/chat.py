# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import json
# from app.retriever import SelfQueryRetriever
# from app.llm_agent import ChatBot

# router = APIRouter()

# @router.websocket("/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             data = json.loads(data)
#             query = data['query']
#             history = data.get('history', [])

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
