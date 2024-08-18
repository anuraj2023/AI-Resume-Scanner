from prisma.models import Workflow, Candidate
from typing import List, Optional, Dict, Any

class WorkflowDAO:
    def __init__(self, db):
        self.db = db

    async def create_workflow(self, data: dict) -> Workflow:
        print("data is : ", data)
        return await self.db.workflow.create(data=data)

    async def get_workflow_with_candidates(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        workflow = await self.db.workflow.find_unique(
            where={"id": workflow_id}
        )
        if not workflow:
            return None
        
        candidates = await self.db.candidate.find_many(
            where={"workflowId": workflow_id}
        )
        
        return {**workflow.dict(), "candidates": candidates}

    async def update_workflow(self, workflow_id: str, data: dict) -> Workflow:
        return await self.db.workflow.update(where={"id": workflow_id}, data=data)

    async def delete_workflow(self, workflow_id: str) -> Workflow:
        # First, delete all associated candidates
        await self.db.candidate.delete_many(where={"workflowId": workflow_id})
        # Then delete the workflow
        return await self.db.workflow.delete(where={"id": workflow_id})

    async def get_all_workflows_with_candidates(self) -> List[Dict[str, Any]]:
        workflows = await self.db.workflow.find_many()
        result = []
        for workflow in workflows:
            candidates = await self.db.candidate.find_many(
                where={"workflowId": workflow.id}
            )
            result.append({**workflow.dict(), "candidates": candidates})
        return result

    async def add_candidate_to_workflow(self, workflow_id: str, candidate_data: dict) -> Candidate:
        candidate_data["workflowId"] = workflow_id
        return await self.db.candidate.create(data=candidate_data)

    async def remove_candidate_from_workflow(self, candidate_id: str) -> Candidate:
        return await self.db.candidate.delete(where={"id": candidate_id})