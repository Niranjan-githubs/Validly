from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AnalysisRequest(BaseModel):
    startup_data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

class AnalysisStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None

class AnalysisResult(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SummaryRequest(BaseModel):
    session_id: str

class SummaryResponse(BaseModel):
    summary: Dict[str, Any]
    session_id: str

class CompleteAnalysisRequest(BaseModel):
    session_id: str
    startup_data: Dict[str, Any]

class CompleteAnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str 