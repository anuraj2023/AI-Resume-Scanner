from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, resume, job_description, candidate, workflow
from contextlib import asynccontextmanager
from app.prisma import prisma
# from app.milvus import milvus_connection
from config import get_env_vars

env_vars = get_env_vars()
MILVUS_URI = env_vars['MILVUS_URI']
MILVUS_API_KEY = env_vars['MILVUS_API_KEY']

@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    # milvus_connection.connect(
    #         alias="default", 
    #         uri=MILVUS_URI,
    #         token=MILVUS_API_KEY
    #     )
    yield
    await prisma.disconnect()
    #milvus_connection.disconnect("default")

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router)
app.include_router(job_description.router)
app.include_router(candidate.router)
app.include_router(workflow.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)