from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import resume, job_description, candidate, workflow, chat
from config import get_env_vars
from contextlib import asynccontextmanager
from app.prisma import prisma

@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    yield
    await prisma.disconnect()

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
# app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)