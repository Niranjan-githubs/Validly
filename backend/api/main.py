#main.py

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uuid
from typing import Dict, Any
import os
import logging

# Import routes
from .routes import chat
from fastapi import Response

from fpdf import FPDF
# Import services
from .services.redis import RedisService
from .services.firebase import FirebaseService
from .deps.firebase_auth import get_current_user
from utils.session_utils import get_user_session
from utils.dashboard_transformer import transform_dashboard_data
from utils.report_generator import generate_natural_language_report,  generate_pdf_from_sections

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from slowapi.middleware import SlowAPIMiddleware

logging.basicConfig(
    level=logging.INFO,  # or logging.ERROR for less verbosity
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

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

app = FastAPI(
    title="FoundrScan API",
    description="AI-powered startup analysis and validation platform",
    version="1.0.0",
    swagger_ui_init_oauth={},
)

# Configure CORS
origins = [
    "http://localhost:5174",  # Vite dev server
    "http://localhost:5173",  # Alternative Vite port
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Changed to False since we're using Bearer token
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]
)

# Initialize services
redis_service = RedisService()
firebase_service = FirebaseService()
pipeline = ParallelFoundrScanPipeline(firebase_service)

# Initialize SlowAPI Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

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
@limiter.limit("3/minute")
def get_chat_summary(request: Request, req: SummaryRequest, user=Depends(get_current_user)):
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

@app.get("/api/chat/summary", response_model=SummaryResponse, dependencies=[Depends(bearer_scheme)])
@limiter.limit("5/minute")
def get_or_generate_chat_summary(
        request: Request,
        session_id: str = Query(..., description="The ID of the session to retrieve summary for"),
        user=Depends(get_current_user)
):
        try:
            uid = user["uid"]
            session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
            session_doc = session_ref.get()

            if not session_doc.exists:
                raise HTTPException(status_code=404, detail="Session not found")

            session_data = session_doc.to_dict()

            summary = session_data.get("summary")
            if summary:
                return SummaryResponse(summary=summary, session_id=session_id)

            # Reuse logic from POST endpoint: regenerate summary
            analyzer = StartupIdeaAnalyzer()
            conversation = session_data["conversation"]
            user_idea = session_data.get("initial_idea", "")
            if not user_idea:
                for msg in conversation:
                    if msg.get("role") == "user":
                        user_idea = msg.get("content", "")
                        break

            summary_obj = analyzer.generate_summary(user_idea, conversation)
            summary_dict = summary_obj.to_dict()

            # Save the new summary to Firestore
            session_ref.update({"summary": summary_dict})

            return SummaryResponse(summary=summary_dict, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate or retrieve summary: {str(e)}")

@app.post("/api/analysis/start", response_model=AnalysisResponse)
def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """Start analysis with provided startup data"""
    uid = user["uid"]
    try:
        job_id = str(uuid.uuid4())
        
        # Save job status with session_id link
        job_status = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "message": "Analysis started",
            "session_id": req.startup_data.get("session_id", job_id)  # Link to session
        }
        redis_service.save_job_status(job_id, job_status)
        
        # Add background task
        background_tasks.add_task(run_analysis_job, job_id, req.startup_data, uid)
        
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
@limiter.limit("2/minute")
def start_analysis_from_session(request: Request, req: SummaryRequest, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """Start analysis from existing session"""
    try:
        uid = user["uid"]
        session_data = get_user_session(uid, req.session_id, firebase_service)
        # Extract startup data from session
        startup_data = {
            "title": session_data.get("initial_idea", "Unknown Startup"),
            "description": "Extracted from chat session",
            "conversation": session_data.get("conversation", []),
            "session_id": req.session_id  # Include session_id
        }
        job_id = str(uuid.uuid4())
        job_status = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "message": "Analysis started from session",
            "session_id": req.session_id  # Link to session
        }
        redis_service.save_job_status(job_id, job_status)
        background_tasks.add_task(run_analysis_job, job_id, startup_data, uid)
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
def get_result(job_id: str, user=Depends(get_current_user)):
    """Get analysis results from user session"""
    uid = user["uid"]
    
    # Get job status to find session_id
    job_status = redis_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Get session_id from job status
    session_id = job_status.get("session_id", job_id)
    
    # Get results from user session instead of separate storage
    try:
        session_data = get_user_session(uid, session_id, firebase_service)
        result = session_data.get("complete_analysis")
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        return AnalysisResult(
            job_id=job_id,
            status=job_status["status"],
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@app.get("/api/sessions/{session_id}", dependencies=[Depends(bearer_scheme)])
def get_session_info(session_id: str, user=Depends(get_current_user)):
    uid = user["uid"]
    session_data = get_user_session(uid, session_id, firebase_service)
    return {
        "session_id": session_id,
        "turn_count": session_data.get("turn_count", 0),
        "is_ready": session_data.get("is_ready", False),
        "initial_idea": session_data.get("initial_idea", ""),
        "analysis_status": session_data.get("analysis_status", "not_started")  # New field
    }

@app.delete("/api/sessions/{session_id}", dependencies=[Depends(bearer_scheme)])
def clear_session(session_id: str, user=Depends(get_current_user)):
    uid = user["uid"]
    session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
    session_ref.delete()
    redis_service.delete_session(session_id)
    return {"message": "Session cleared"}

def run_analysis_job(job_id: str, startup_data: Dict[str, Any], uid: str):
    """Run analysis job in background - saves only to user session"""
    try:
        # Get session_id from startup_data or fallback to job_id
        session_id = startup_data.get("session_id", job_id)
        
        # Update session with analysis status
        session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
        session_ref.update({"analysis_status": "running"})
        
        # Update job status
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "running",
            "progress": 0.1,
            "message": "Starting analysis pipeline",
            "session_id": session_id
        })
        
        # Run pipeline - this now saves directly to user session
        result = pipeline.run_pipeline(startup_data, uid, session_id)
        
        # Update session with completion status
        session_ref.update({"analysis_status": "completed"})
        
        # Update job status to completed (no duplicate result storage)
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "completed",
            "progress": 1.0,
            "message": "Analysis completed successfully",
            "session_id": session_id
        })
        
    except Exception as e:
        # Update session with error status
        session_id = startup_data.get("session_id", job_id)
        session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
        session_ref.update({"analysis_status": "failed", "error": str(e)})
        
        # Update job status to failed
        redis_service.save_job_status(job_id, {
            "job_id": job_id,
            "status": "failed",
            "progress": 0.0,
            "message": f"Analysis failed: {str(e)}",
            "session_id": session_id
        })

# COMMENTED OUT: Redundant analysis endpoints that used separate storage
# @app.post("/api/analysis/save_complete_analysis", response_model=CompleteAnalysisResponse)
# def save_complete_analysis(req: CompleteAnalysisRequest, background_tasks: BackgroundTasks):
#     """Save complete analysis to Firebase"""
#     # This is now handled by the main analysis pipeline
#     pass

# def run_analysis_and_save_to_firebase(job_id: str, startup_summary: Dict[str, Any], session_id: str, uid: str):
#     """Run analysis and save to Firebase"""
#     # This functionality is now integrated into run_analysis_job
#     pass

@app.get("/api/analysis/results/{session_id}", dependencies=[Depends(bearer_scheme)])
def get_analysis_results(session_id: str, user=Depends(get_current_user)):
    """Get analysis results directly from user session"""
    uid = user["uid"]
    session_data = get_user_session(uid, session_id, firebase_service)
    
    # Check if analysis exists
    complete_analysis = session_data.get("complete_analysis")
    if not complete_analysis:
        # Check if analysis is in progress
        analysis_status = session_data.get("analysis_status", "not_started")
        if analysis_status == "running":
            raise HTTPException(status_code=202, detail="Analysis in progress")
        else:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
    
    dashboard_data = transform_dashboard_data(complete_analysis)
    return dashboard_data
    # return complete_analysis

# Fixed endpoint in main.py

@app.get("/generate-pdf/{session_id}", dependencies=[Depends(bearer_scheme)])
async def generate_pdf(session_id: str, user: dict = Depends(get_current_user)):
    """Generate a PDF report using dashboard data transformation."""
    uid = user["uid"]
    try:
        logging.info(f"Starting PDF generation for session: {session_id}")
        # Get session data
        session_data = get_user_session(uid, session_id, firebase_service)
        logging.info(f"Got session data keys: {list(session_data.keys()) if session_data else 'None'}")
        # Extract the complete_analysis from session_data
        complete_analysis = session_data.get('complete_analysis')
        logging.info(f"Complete analysis exists: {complete_analysis is not None}")
        if not complete_analysis:
            logging.info("Using sample data as fallback")
            complete_analysis = create_sample_analysis_data()
        # Transform to dashboard data
        dashboard_data = transform_dashboard_data(complete_analysis)
        logging.info(f"Dashboard data keys: {list(dashboard_data.keys())}")
        # Generate the report sections
        sections = generate_natural_language_report(dashboard_data)
        # Generate PDF bytes with error handling
        logging.info("Generating PDF...")
        pdf_bytes = generate_pdf_from_sections(sections)
        logging.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        # Return Response with proper headers
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=analysis_{session_id}.pdf"
            }
        )
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        import traceback
        traceback.logging.info_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Helper function to create sample data based on your document structure

    