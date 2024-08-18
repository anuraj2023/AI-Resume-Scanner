from fastapi import APIRouter, HTTPException
from typing import List
from app.dao.workflow_dao import WorkflowDAO
from app.models import WorkflowCreate, WorkflowResponse, CandidateCreate, CandidateResponse
from app.prisma import prisma

router = APIRouter()
workflow_dao = WorkflowDAO(prisma)

@router.post("/workflows/", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate):
    return await workflow_dao.create_workflow(workflow.model_dump())

@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def read_workflow(workflow_id: str):
    workflow = await workflow_dao.get_workflow_with_candidates(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow: WorkflowCreate):
    updated_workflow = await workflow_dao.update_workflow(workflow_id, workflow.model_dump())
    if updated_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return await workflow_dao.get_workflow_with_candidates(workflow_id)

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    deleted_workflow = await workflow_dao.delete_workflow(workflow_id)
    if deleted_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@router.get("/workflows/", response_model=List[WorkflowResponse])
async def read_all_workflows():
    return await workflow_dao.get_all_workflows_with_candidates()

@router.post("/workflows/{workflow_id}/candidates", response_model=CandidateResponse)
async def add_candidate_to_workflow(workflow_id: str, candidate: CandidateCreate):
    return await workflow_dao.add_candidate_to_workflow(workflow_id, candidate.model_dump())

@router.delete("/workflows/{workflow_id}/candidates/{candidate_id}", response_model=CandidateResponse)
async def remove_candidate_from_workflow(workflow_id: str, candidate_id: str):
    return await workflow_dao.remove_candidate_from_workflow(candidate_id)