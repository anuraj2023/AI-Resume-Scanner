from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.dao.candidate_dao import CandidateDAO
from app.models import CandidateCreate, CandidateResponse
from app.prisma import prisma

router = APIRouter()
candidate_dao = CandidateDAO(prisma)

@router.post("/candidates/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate):
    return await candidate_dao.create_candidate(candidate.dict())

@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def read_candidate(candidate_id: str):
    candidate = await candidate_dao.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(candidate_id: str, candidate: CandidateCreate):
    updated_candidate = await candidate_dao.update_candidate(candidate_id, candidate.dict())
    if updated_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return updated_candidate

@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    deleted_candidate = await candidate_dao.delete_candidate(candidate_id)
    if deleted_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted successfully"}

@router.get("/candidates/", response_model=List[CandidateResponse])
async def read_all_candidates():
    return await candidate_dao.get_all_candidates()