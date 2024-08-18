from prisma.models import Candidate
from typing import List, Optional

class CandidateDAO:
    def __init__(self, db):
        self.db = db

    async def create_candidate(self, data: dict) -> Candidate:
        return await self.db.candidate.create(data=data)

    async def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return await self.db.candidate.find_unique(where={"id": candidate_id})

    async def update_candidate(self, candidate_id: str, data: dict) -> Optional[Candidate]:
        return await self.db.candidate.update(where={"id": candidate_id}, data=data)

    async def delete_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return await self.db.candidate.delete(where={"id": candidate_id})

    async def get_all_candidates(self) -> List[Candidate]:
        return await self.db.candidate.find_many()

    async def get_candidates_by_workflow_id(self, workflow_id: str) -> List[Candidate]:
        return await self.db.candidate.find_many(where={"workflowId": workflow_id})