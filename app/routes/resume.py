from fastapi import APIRouter, File, Query, UploadFile, HTTPException
from typing import List
import io
import pandas as pd
from app.models import CandidateCreate
from app.prisma import prisma
from app.dao.candidate_dao import  CandidateDAO
from app.s3_ingestor import upload_to_s3
from app.vector_data_ingestor import ingest
from app.resume_data_extractor import extract_resume_data
from app.text_extractor import extract_text_from_file
from config import get_env_vars
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from app.logging_config import logger

router = APIRouter()

env_vars = get_env_vars()
OPEN_AI_KEY = env_vars['OPEN_AI_KEY']
S3_BUCKET_NAME = env_vars['S3_BUCKET_NAME']
EMBEDDING_MODEL = env_vars['EMBEDDING_MODEL']

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})

candidate_dao = CandidateDAO(prisma)

@router.post("/upload_resumes/")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    workflow_id: str = Query(..., description="The ID of the workflow to associate the resumes with")):
    #global vectordb, rag_pipeline, llm
    df_list = []
    for file in files:
        try:
            content = await file.read()
            text = extract_text_from_file(content)
            
            df_list.append({"ID": file.filename, "Content": text})
            
            # Upload to S3
            s3_file_name = f"resumes/{file.filename}"
            status, resume_url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
            if not status:
                raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
    
    try:
        # Upload to VectorDB
        df = pd.DataFrame(df_list)
        ingest(df, "Content", embedding_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting data to vector database: {str(e)}")

    try:
        # Extract data in JSON form resume using LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=OPEN_AI_KEY)
        json_resume_list = extract_resume_data(df_list, llm)
        
        # Save the extracted JSON resume data to mongoDB candidate table
        for resume_data in json_resume_list:
            candidate_info = resume_data['candidate_info']
            skills = resume_data.get('skills', [])
            
            candidate_data = CandidateCreate(
                name=candidate_info['name'],
                phoneNumber=candidate_info.get('phone', ''),
                linkedinUrl=next((profile['url'] for profile in candidate_info.get('profiles', []) if profile.get('network', '').lower() == 'linkedin'), None),
                emailId=candidate_info.get('email', ''),
                uploadResumeUrl=resume_url,
                totalWorkExperience=candidate_info.get('total_work_experience', ''),
                qualifiedForInterview=False,
                interviewMailSent=False,
                matchingSkillsAsPerJd=[skill['name'] for skill in skills if isinstance(skill, dict)],
                fitmentMatchScore=0,
                workflowId=workflow_id,
                parsedResume=resume_data 
            )
            
            try:
                await candidate_dao.create_candidate(candidate_data.model_dump())
                logger.info(f"Candidate saved in database")
            except Exception as e:
                logger.error(f"Error saving candidate {candidate_info['name']}: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting resume data: {str(e)}")

    return {"message": f"Successfully processed {len(df_list)} resume files."}