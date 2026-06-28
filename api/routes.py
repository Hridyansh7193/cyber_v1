from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from typing import Dict, Any
from api.models import ScanRequest, ScanResponse, StatusResponse, CancelResponse
from api.dependencies import get_scan_service, get_report_service, get_default_config
from services.scan_service import ScanService
from services.report_service import ReportService
from config.schemas import BugHunterConfig
import json

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/version")
def version():
    return {"version": "0.1.0"}

@router.post("/scan", response_model=ScanResponse)
def start_scan(
    request: ScanRequest, 
    scan_service: ScanService = Depends(get_scan_service),
    default_config: BugHunterConfig = Depends(get_default_config)
):
    try:
        cfg = default_config
        if request.config:
            cfg = BugHunterConfig.model_validate(request.config)
            
        job_id = scan_service.submit_scan(request.domain, cfg)
        return ScanResponse(job_id=job_id, message="Scan submitted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Top-level exception catch to prevent traceback leakage via FastAPI HTTP response.
        # Original error is logged.
        import logging
        logging.getLogger(__name__).error("Internal API error during scan submission", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal pipeline error occurred")

@router.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str, scan_service: ScanService = Depends(get_scan_service)):
    status = scan_service.get_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(**status)

@router.get("/report/{job_id}")
def get_report(
    job_id: str, 
    format: str = "json",
    scan_service: ScanService = Depends(get_scan_service)
):
    rep = scan_service.get_report(job_id, format)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found or not generated")
        
    if format.lower() == "markdown":
        return PlainTextResponse(content=rep.content)
    
    # Render JSON correctly from the generated string content
    return Response(content=rep.content, media_type="application/json")

@router.post("/cancel/{job_id}", response_model=CancelResponse)
def cancel_scan(job_id: str, scan_service: ScanService = Depends(get_scan_service)):
    success = scan_service.cancel_scan(job_id)
    if success:
        return CancelResponse(job_id=job_id, cancelled=True, message="Job cancelled successfully")
    return CancelResponse(job_id=job_id, cancelled=False, message="Job could not be cancelled")
