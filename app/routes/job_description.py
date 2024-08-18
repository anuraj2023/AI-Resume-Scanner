from fastapi import APIRouter, File, UploadFile, HTTPException
import io

from langchain_openai import ChatOpenAI
from app.prisma import prisma
from app.dao.workflow_dao import WorkflowDAO
from app.jd_data_extractor import extract_jd_data
from app.models import WorkflowCreate
from app.s3_ingestor import upload_to_s3
from app.text_extractor import extract_text_from_file
from config import get_env_vars

router = APIRouter()
workflow_dao = WorkflowDAO(prisma)

env_vars = get_env_vars()
S3_BUCKET_NAME = env_vars['S3_BUCKET_NAME']
OPEN_AI_KEY = env_vars['OPEN_AI_KEY']

@router.post("/upload_job_description/")
async def upload_job_description(file: UploadFile = File(...)):
    #global job_description
    try:
        content = await file.read()
        text = extract_text_from_file(content)
        
        # Upload to S3
        s3_file_name = f"job-descriptions/{file.filename}"
        status, jd_url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
        if not status:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
        
        # Extract relevant information from JD using LLM
        try:
            llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=OPEN_AI_KEY)
            llm_extracted_jd = extract_jd_data(text, llm)
            if llm_extracted_jd != "Error":
                # Save extracted relevant information to Mongo DB workflow table
                wf = WorkflowCreate(
                    name="abcd",
                    jobDescription= llm_extracted_jd,
                    jobDescriptionUrl= jd_url
                )
                created_wf = await workflow_dao.create_workflow(wf.model_dump())
                return created_wf
            else:
                raise HTTPException("Error occured while extracting relevant information from JD")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving job description to DB: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading job description: {str(e)}")