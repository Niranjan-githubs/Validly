from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_voice: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    session_id: str
    done: bool = False
    audio_url: Optional[str] = None

class ChatSession(BaseModel):
    session_id: str
    conversation: List[Dict[str, str]]
    ready: bool = False
    turn_count: int = 0
    latest_response: str = ""
    is_ready: bool = False
    initial_idea: Optional[str] = None

class VoiceRequest(BaseModel):
    session_id: Optional[str] = None
    audio_data: bytes

class VoiceResponse(BaseModel):
    message: str
    session_id: str
    audio_url: Optional[str] = None 