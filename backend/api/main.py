from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uuid
from typing import Dict, Any

# Import routes
from .routes import chat

# Import services
from .services.redis import RedisService
from .services.firebase import FirebaseService
from .deps.firebase_auth import get_current_user
from utils.session_utils import get_user_session


# Import models
from .models.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisStatus, 
    AnalysisResult, SummaryRequest, SummaryResponse,
    CompleteAnalysisRequest, CompleteAnalysisResponse
)

# Import core pipeline
from core.pipeline import ParallelFoundrScanPipeline

# Import agents
from agents.idea_agent import StartupIdeaAnalyzer

# Add HTTPBearer security scheme
bearer_scheme = HTTPBearer()


# Initialize FastAPI app
app = FastAPI(
    title="FoundrScan API",
    description="AI-powered startup analysis and validation platform",
    version="1.0.0",
    swagger_ui_init_oauth={
        # You can add OAuth client config here if needed
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
redis_service = RedisService()
firebase_service = FirebaseService()
pipeline = ParallelFoundrScanPipeline(firebase_service)

# Include routers
app.include_router(chat.router)

# In-memory job store (use Redis/DB in production)
jobs = {}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "redis_connected": redis_service.ping(),
        "firebase_connected": True  # TODO: Add Firebase health check
    }

@app.post("/api/chat/summary", response_model=SummaryResponse, dependencies=[Depends(bearer_scheme)])
def get_chat_summary(req: SummaryRequest, user=Depends(get_current_user)):
    try:
        uid = user["uid"]
        # Get session from Firestore under the user's UID
        session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(req.session_id)
        session_doc = session_ref.get()
        
        if not session_doc.exists:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session_data = session_doc.to_dict()
        print("Session data:", session_data)
        
        analyzer = StartupIdeaAnalyzer()
        conversation = session_data["conversation"]
        user_idea = session_data.get("initial_idea", "")
        if not user_idea:
            for msg in conversation:
                if msg.get("role") == "user":
                    user_idea = msg.get("content", "")
                    break
        
        summary = analyzer.generate_summary(user_idea, conversation)
        summary_dict = summary.to_dict()
        
        # Store summary in the user's session document
        session_ref.update({"summary": summary_dict})
        
        return SummaryResponse(summary=summary_dict, session_id=req.session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.post("/api/analysis/start", response_model=AnalysisResponse)
def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start analysis with provided startup data"""
    try:
        job_id = str(uuid.uuid4())
        
        # Save job status
        job_status = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "message": "Analysis started"
        }
        redis_service.save_job_status(job_id, job_status)
        
        # Add background task
        background_tasks.add_task(run_analysis_job, job_id, req.startup_data)
        
        return AnalysisResponse(
            job_id=job_id,
            status="started",
            message="Analysis job started"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )

@app.post("/api/analysis/start_from_session", response_model=AnalysisResponse, dependencies=[Depends(bearer_scheme)])
def start_analysis_from_session(req: SummaryRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """Start analysis from existing session"""
    try:
        uid = user["uid"]
        session_data = get_user_session(uid, req.session_id, firebase_service)
        # Extract startup data from session
        startup_data = {
            "title": session_data.get("initial_idea", "Unknown Startup"),
            "description": "Extracted from chat session",
            "conversation": session_data.get("conversation", [])
        }
        job_id = str(uuid.uuid4())
        job_status = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "message": "Analysis started from session"
        }
        redis_service.save_job_status(job_id, job_status)
        background_tasks.add_task(run_analysis_job, job_id, startup_data)
        return AnalysisResponse(
            job_id=job_id,
            status="started",
            message="Analysis job started from session"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis from session: {str(e)}"
        )

@app.get("/api/analysis/{job_id}/status", response_model=AnalysisStatus)
def get_status(job_id: str):
    """Get analysis job status"""
    job_status = redis_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return AnalysisStatus(**job_status)

@app.get("/api/analysis/{job_id}/result", response_model=AnalysisResult)
def get_result(job_id: str):
    """Get analysis results"""
    job_status = redis_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Get results from Firebase
    result = firebase_service.get_analysis_result(job_id)
    
    return AnalysisResult(
        job_id=job_id,
        status=job_status["status"],
        result=result
    )

@app.get("/api/sessions/{session_id}", dependencies=[Depends(bearer_scheme)])
def get_session_info(session_id: str, user=Depends(get_current_user)):
    uid = user["uid"]
    session_data = get_user_session(uid, session_id, firebase_service)
    return {
        "session_id": session_id,
        "turn_count": session_data.get("turn_count", 0),
        "is_ready": session_data.get("is_ready", False),
        "initial_idea": session_data.get("initial_idea", "")
    }

@app.delete("/api/sessions/{session_id}", dependencies=[Depends(bearer_scheme)])
def clear_session(session_id: str, user=Depends(get_current_user)):
    uid = user["uid"]
    session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
    session_ref.delete()
    redis_service.delete_session(session_id)
    return {"message": "Session cleared"}

def run_analysis_job(job_id: str, startup_data: Dict[str, Any], user=Depends(get_current_user)):
    """Run analysis job in background"""
    try:
        # Update status to running
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "running",
            "progress": 0.1,
            "message": "Starting analysis pipeline"
        })
        uid = user["uid"]
        session_id = startup_data.get("session_id") or job_id  # fallback to job_id if not present

        
        # Run pipeline
        result = pipeline.run_pipeline(startup_data, uid, session_id)
        
        # Save results to Firebase
        firebase_service.save_analysis_result(job_id, result)
        
        # Update status to completed
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "completed",
            "progress": 1.0,
            "message": "Analysis completed successfully"
        })
        
    except Exception as e:
        # Update status to failed
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "failed",
            "progress": 0.0,
            "message": f"Analysis failed: {str(e)}"
        })

@app.post("/api/analysis/save_complete_analysis", response_model=CompleteAnalysisResponse)
def save_complete_analysis(req: CompleteAnalysisRequest, background_tasks: BackgroundTasks):
    """Save complete analysis to Firebase"""
    try:
        job_id = str(uuid.uuid4())
        
        job_status = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "message": "Saving complete analysis"
        }
        redis_service.save_job_status(job_id, job_status)
        
        background_tasks.add_task(
            run_analysis_and_save_to_firebase, 
            job_id, 
            req.startup_data, 
            req.session_id
        )
        
        return CompleteAnalysisResponse(
            job_id=job_id,
            status="started",
            message="Complete analysis started"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start complete analysis: {str(e)}"
        )

def run_analysis_and_save_to_firebase(job_id: str, startup_summary: Dict[str, Any], session_id: str, user = Depends(get_current_user)):
    """Run analysis and save to Firebase"""
    try:
        # Update status
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "running",
            "progress": 0.2,
            "message": "Running analysis pipeline"
        })
        uid = user["uid"]
        
        # Run pipeline
        result = pipeline.run_pipeline(startup_summary, uid, session_id)
        
        # Update status
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "running",
            "progress": 0.8,
            "message": "Saving to Firebase"
        })
        
        # Serialize for Firebase
        def serialize_for_firebase(obj):
            if isinstance(obj, (set, frozenset)):
                return list(obj)
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
        
        # Save to Firebase
        firebase_service.save_output(session_id, result)
        
        # Update status to completed
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "completed",
            "progress": 1.0,
            "message": "Analysis saved to Firebase"
        })
        
    except Exception as e:
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "failed",
            "progress": 0.0,
            "message": f"Analysis failed: {str(e)}"
        })

@app.get("/api/analysis/results/{session_id}", dependencies=[Depends(bearer_scheme)])
def get_analysis_results(session_id: str, user=Depends(get_current_user)):
    uid = user["uid"]
    session_data = get_user_session(uid, session_id, firebase_service)
    result = session_data.get("summary")
    if not result:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    return result
