from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class CandidateBase(BaseModel):
    name: str
    phoneNumber: str
    linkedinUrl: Optional[str] = None
    emailId: str
    uploadResumeUrl: str
    totalWorkExperience: str
    qualifiedForInterview: bool
    interviewMailSent: bool
    matchingSkillsAsPerJd: List[str]
    fitmentMatchScore: int
    parsedResume: Dict[str, Any]

class CandidateCreate(CandidateBase):
    workflowId: str

class CandidateResponse(CandidateBase):
    id: str
    workflowId: str

class WorkflowCreate(BaseModel):
    name: str
    jobDescription: str
    jobDescriptionUrl: str
    additionalParameters: Optional[List[str]] = []

class WorkflowResponse(BaseModel):
    id: str
    name: str
    jobDescription: str
    jobDescriptionUrl: str
    additionalParameters: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]