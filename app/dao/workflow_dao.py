from prisma.models import Workflow
from typing import List, Optional

class WorkflowDAO:

    def __init__(self, db):
        self.db = db

    async def create_workflow(self, data: dict) -> Workflow:
        return await self.db.workflow.create(data=data)

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return await self.db.workflow.find_unique(
            where={"id": workflow_id},
            include={"candidates": True}
        )

    async def update_workflow(self, workflow_id: str, data: dict) -> Workflow:
        return await self.db.workflow.update(where={"id": workflow_id}, data=data)

    async def delete_workflow(self, workflow_id: str) -> Workflow:
        return await self.db.workflow.delete(where={"id": workflow_id})

    async def get_all_workflows(self) -> List[Workflow]:
        return await self.db.workflow.find_many(include={"candidates": True})