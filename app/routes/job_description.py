from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from app.s3_ingestor import upload_to_s3
from app.text_extractor import extract_text_from_file
from config import get_env_vars

router = APIRouter()

env_vars = get_env_vars()
S3_BUCKET_NAME = env_vars['S3_BUCKET_NAME']

@router.post("/upload_job_description/")
async def upload_job_description(file: UploadFile = File(...)):
    global job_description
    try:
        content = await file.read()
        text = extract_text_from_file(content)
        
        # Upload to S3
        s3_file_name = f"job-descriptions/{file.filename}"
        status, url = upload_to_s3(io.BytesIO(content), S3_BUCKET_NAME, s3_file_name)
        if not status:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to S3")
        
        job_description = text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing job description: {str(e)}")

    # Save the extracted JSON JD data to postgreSQL workflow table

    return {"message": f"Successfully uploaded job description: {file.filename}"}