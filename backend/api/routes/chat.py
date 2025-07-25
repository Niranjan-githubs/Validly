from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer

import uuid
import tempfile
import os
from typing import Optional, List
from gtts import gTTS
import requests

from ..models.chat import ChatRequest, ChatResponse, VoiceRequest, VoiceResponse
from ..services.redis import RedisService
from ..services.firebase import FirebaseService
from agents.idea_agent import StartupIdeaAnalyzer
from ..deps.firebase_auth import get_current_user
from utils import info_tracker

router = APIRouter(prefix="/api/chat", tags=["chat"])
bearer_scheme = HTTPBearer()

# Initialize services
redis_service = RedisService()
firebase_service = FirebaseService()

def process_chat_and_webhook(req, session_id, uid):
    try:
        # Reuse the synchronous chat logic to get the response
        analyzer = StartupIdeaAnalyzer()
        # Load or create session_data as in the main endpoint
        # (You may want to refactor this logic into a helper for DRY)
        session_data = redis_service.get_session(session_id)
        if not session_data:
            session_doc = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id).get()
            if session_doc.exists:
                session_data = session_doc.to_dict()
            else:
                session_data = None
        if not session_data:
            user_idea = req.message
            system_prompt = """You are a startup idea validator. Your goal is to gather specific information about the startup idea to create a structured summary. Ask ONE clear question at a time about:
- Target users/market
- Problem being solved
- Solution details
- Business model
- Monetization strategy
- Competition
- Key differentiators
- Technical requirements
- Potential risks
- Vision

Be concise and direct. When you have enough information to create a complete summary, say \"✅ I'm ready to summarize\"."""
            response = analyzer.query_model(
                "Ask ONE specific question about who the target users are and what problem they're facing. Be brief.",
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_idea}]
            )
            conversation = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_idea},
                {"role": "assistant", "content": response}
            ]
            messages = [msg['content'] for msg in conversation if msg['role'] in ('user', 'assistant')]
            _, is_ready = info_tracker.extract_startup_info(messages)
            session_data = {
                "conversation": conversation,
                "ready": is_ready,
                "turn_count": 1,
                "latest_response": response,
                "is_ready": is_ready,
                "initial_idea": user_idea
            }
        else:
            conversation = session_data["conversation"]
            conversation.append({"role": "user", "content": req.message})
            response = analyzer.query_model(
                """Ask ONE specific question about the next most important aspect of the startup that we haven't covered yet. Focus on:
- Problem being solved
- Solution details
- Business model
- Monetization strategy
- Competition
- Key differentiators
- Technical requirements
- Potential risks
- Vision

Be brief and direct. If we have enough information for a complete summary, say \"✅ I'm ready to summarize\".""",
                conversation
            )
            conversation.append({"role": "assistant", "content": response})
            messages = [msg['content'] for msg in conversation if msg['role'] in ('user', 'assistant')]
            _, is_ready = info_tracker.extract_startup_info(messages)
            session_data.update({
                "conversation": conversation,
                "ready": is_ready,
                "turn_count": session_data.get("turn_count", 0) + 1,
                "latest_response": response,
                "is_ready": is_ready
            })
        if session_data["is_ready"]:
            firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id).set(session_data)
            redis_service.delete_session(session_id)
        else:
            redis_service.save_session(session_id, session_data)
        chat_response = {
            "response": response,
            "session_id": session_id,
            "done": session_data["is_ready"]
        }
        requests.post(req.webhook_url, json=chat_response, timeout=10)
    except Exception as e:
        print(f"Failed to process chat and send webhook: {e}")

@router.post("/", response_model=ChatResponse, dependencies=[Depends(bearer_scheme)])
async def chat_endpoint(req: ChatRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """Handle chat messages and manage conversation sessions"""

    uid = user["uid"]
    try:
        session_id = req.session_id or str(uuid.uuid4())
        if req.webhook_url and req.webhook_url.startswith("http"):
            background_tasks.add_task(process_chat_and_webhook, req, session_id, uid)
            return {"response": "Processing", "session_id": session_id, "done": False}

        session_data = redis_service.get_session(session_id)
        
        if not session_data:
            session_doc = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id).get()
            if session_doc.exists:
                session_data = session_doc.to_dict()
            else:
                session_data = None

        if not session_data:
            # New session logic
            analyzer = StartupIdeaAnalyzer()
            user_idea = req.message
            
            # Use a more focused system prompt
            system_prompt = """You are a startup idea validator. Your goal is to gather specific information about the startup idea to create a structured summary. Ask ONE clear question at a time about:
- Target users/market
- Problem being solved
- Solution details
- Business model
- Monetization strategy
- Competition
- Key differentiators
- Technical requirements
- Potential risks
- Vision

Be concise and direct. When you have enough information to create a complete summary, say \"✅ I'm ready to summarize\"."""
            
            # First response - ask about target users/market
            response = analyzer.query_model(
                "Ask ONE specific question about who the target users are and what problem they're facing. Be brief.",
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_idea}]
            )
            
            conversation = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_idea},
                {"role": "assistant", "content": response}
            ]
            # Use info_tracker to determine readiness
            messages = [msg['content'] for msg in conversation if msg['role'] in ('user', 'assistant')]
            _, is_ready = info_tracker.extract_startup_info(messages)
            session_data = {
                "conversation": conversation,
                "ready": is_ready,
                "turn_count": 1,
                "latest_response": response,
                "is_ready": is_ready,
                "initial_idea": user_idea
            }
        else:
            # Existing session logic
            analyzer = StartupIdeaAnalyzer()
            conversation = session_data["conversation"]
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": req.message})

            # Get AI response - focus on next piece of information needed
            response = analyzer.query_model(
                """Ask ONE specific question about the next most important aspect of the startup that we haven't covered yet. Focus on:
- Problem being solved
- Solution details
- Business model
- Monetization strategy
- Competition
- Key differentiators
- Technical requirements
- Potential risks
- Vision

Be brief and direct. If we have enough information for a complete summary, say \"✅ I'm ready to summarize\".""",
                conversation
            )
            conversation.append({"role": "assistant", "content": response})
            # Use info_tracker to determine readiness
            messages = [msg['content'] for msg in conversation if msg['role'] in ('user', 'assistant')]
            _, is_ready = info_tracker.extract_startup_info(messages)
            session_data.update({
                "conversation": conversation,
                "ready": is_ready,
                "turn_count": session_data.get("turn_count", 0) + 1,
                "latest_response": response,
                "is_ready": is_ready
            })
        
        # Archive to Firestore if ready, else save to Redis
        if session_data["is_ready"]:
            # Save under outputs/{uid}/sessions/{session_id}
            firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id).set(session_data)
            redis_service.delete_session(session_id)
        else:
            redis_service.save_session(session_id, session_data)

        return ChatResponse(
            response=response,
            session_id=session_id,
            done=session_data["is_ready"]
        )
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

@router.get("/sessions", response_model=List[str], dependencies=[Depends(bearer_scheme)])
async def list_user_sessions(user=Depends(get_current_user)):
    """List all session IDs for the authenticated user"""
    uid = user["uid"]
    try:
        sessions_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions')
        sessions = sessions_ref.stream()
        session_ids = [session.id for session in sessions]
        return session_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.post("/voice")
async def chat_voice_endpoint(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = None
):
    """Handle voice input for chat"""
    try:
        # Save the uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # TODO: Implement speech-to-text conversion
            # For now, return a placeholder response
            message = "Voice input received (speech-to-text not implemented yet)"
            
            # Process the message through chat endpoint
            chat_request = ChatRequest(message=message, session_id=session_id)
            return await chat_endpoint(chat_request)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process voice input: {str(e)}"
        )

@router.get("/audio/{session_id}/latest")
async def get_latest_audio(session_id: str):
    """Get the latest audio response for a session"""
    try:
        session_data = redis_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        latest_response = session_data.get("latest_response", "")
        
        # Generate audio from text
        tts = gTTS(text=latest_response, lang='en')
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            
            def audio_generator():
                with open(temp_file.name, 'rb') as f:
                    yield f.read()
                os.unlink(temp_file.name)
        
        return StreamingResponse(
            audio_generator(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=response_{session_id}.mp3"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audio: {str(e)}"
        ) 