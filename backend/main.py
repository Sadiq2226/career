from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from .agent.service import get_service

app = FastAPI(title="Agentic AI Insights Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    degree: Optional[str] = None
    year: Optional[int] = None


class CompareRequest(BaseModel):
    institution_a: str
    institution_b: str
    year: Optional[int] = None


class ROIRequest(BaseModel):
    institution: str
    degree: str
    tuition_total: float
    years: int = 4


@app.get("/")
def root():
    return {
        "status": "ok", 
        "service": "Agentic AI Insights Generator",
        "version": "2.0",
        "features": ["Real-time data", "Enhanced analytics", "Parent insights", "ROI calculations"]
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    svc = get_service()
    return svc.analyze_employment(req.degree, req.year)


@app.get("/insights")
def insights(q: str = Query(..., description="Question to summarize against reports")):
    svc = get_service()
    return svc.summarize_outcomes(q)


@app.post("/compare")
def compare(req: CompareRequest):
    svc = get_service()
    return svc.compare_institutions(req.institution_a, req.institution_b, req.year)


@app.get("/support-services")
def support_services():
    svc = get_service()
    return {"institutions": svc.support_services_index()}


@app.post("/roi")
def roi(req: ROIRequest):
    svc = get_service()
    return svc.roi_estimate(req.institution, req.degree, req.tuition_total, req.years)
