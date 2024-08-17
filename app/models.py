from pydantic import BaseModel, Field
from typing import List, Optional

class CandidateCreate(BaseModel):
    name: str
    phoneNumber: str
    linkedinUrl: Optional[str]
    emailId: str
    uploadResumeUrl: str
    totalWorkExperience: str
    qualifiedForInterview: bool
    interviewMailSent: bool
    matchingSkillsAsPerJd: List[str]
    fitmentMatchScore: int
    workflowId: str

class WorkflowCreate(BaseModel):
    name: str
    jobDescription: str
    jobDescriptionUrl: str
    additionalParameters: List[str]
    candidates: List[str]


class CandidateResponse(CandidateCreate):
    id: str

class WorkflowResponse(WorkflowCreate):
    id: str
    candidates: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]