"""
backend/main.py
---------------
FastAPI application — REST API for the Eco Lifestyle Agent.
All routes are prefixed with /api/v1.

Run with:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config.settings import settings
from rag.pipeline import get_pipeline
from utils.helpers import (
    get_daily_eco_tip,
    get_random_tip,
    calculate_carbon_footprint,
    get_eco_score_label,
)
from utils.logger import logger


# ── App Initialisation ────────────────────────────────────────

app = FastAPI(
    title="Eco Lifestyle Agent API",
    description="AI-powered eco-friendly lifestyle assistant using IBM Granite + RAG",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Dependency: lazy pipeline loading ────────────────────────

def get_rag_pipeline():
    return get_pipeline(settings)


# ── Request / Response Models ─────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[dict] = Field(default_factory=list)
    user_preferences: dict = Field(default_factory=dict)
    filter_category: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    retrieved_chunks: int
    retrieval_scores: list[float]
    processing_time_ms: int


class CarbonRequest(BaseModel):
    electricity_kwh_per_month: float = 0
    lpg_cylinders_per_year: float = 0
    car_km_per_day: float = 0
    car_fuel_type: str = "petrol"
    bike_km_per_day: float = 0
    bus_km_per_day: float = 0
    metro_km_per_day: float = 0
    flights_per_year: int = 0
    avg_flight_km: float = 1500
    diet_type: str = "medium_meat"
    food_waste_kg_per_week: float = 1.0


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""


# ── Routes ────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Eco Lifestyle Agent API", "version": "1.0.0"}


@app.get("/api/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    pipeline=Depends(get_rag_pipeline),
):
    """
    Main chat endpoint — processes a user question through the RAG pipeline
    and returns an AI-generated response with source citations.
    """
    start = time.perf_counter()
    logger.info(f"Chat request: {request.question[:80]!r}")

    try:
        result = pipeline.query(
            question=request.question,
            conversation_history=request.conversation_history,
            user_preferences=request.user_preferences,
            filter_category=request.filter_category,
        )
    except Exception as exc:
        logger.error(f"Pipeline error: {exc}")
        raise HTTPException(status_code=500, detail=f"AI pipeline error: {str(exc)}")

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieved_chunks=result["retrieved_chunks"],
        retrieval_scores=result["retrieval_scores"],
        processing_time_ms=elapsed_ms,
    )


@app.post("/api/v1/chat/stream", tags=["Chat"])
async def chat_stream(
    request: ChatRequest,
    pipeline=Depends(get_rag_pipeline),
):
    """Streaming chat endpoint — returns Server-Sent Events."""

    def event_generator():
        for token in pipeline.stream_query(
            question=request.question,
            conversation_history=request.conversation_history,
            user_preferences=request.user_preferences,
        ):
            if isinstance(token, dict) and token.get("__meta__"):
                import json
                yield f"data: [DONE] {json.dumps(token)}\n\n"
            else:
                yield f"data: {token}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/tip/daily", tags=["Tips"])
async def daily_tip():
    """Return the deterministic daily eco tip."""
    return {"tip": get_daily_eco_tip()}


@app.get("/api/v1/tip/random", tags=["Tips"])
async def random_tip():
    """Return a random eco tip (for refresh button)."""
    return {"tip": get_random_tip()}


@app.post("/api/v1/carbon/calculate", tags=["Carbon Calculator"])
async def calculate_carbon(request: CarbonRequest):
    """
    Calculate annual carbon footprint from household inputs.
    Returns per-category and total CO₂e in tonnes.
    """
    result = calculate_carbon_footprint(
        electricity_kwh_per_month=request.electricity_kwh_per_month,
        lpg_cylinders_per_year=request.lpg_cylinders_per_year,
        car_km_per_day=request.car_km_per_day,
        car_fuel_type=request.car_fuel_type,
        bike_km_per_day=request.bike_km_per_day,
        bus_km_per_day=request.bus_km_per_day,
        metro_km_per_day=request.metro_km_per_day,
        flights_per_year=request.flights_per_year,
        avg_flight_km=request.avg_flight_km,
        diet_type=request.diet_type,
        food_waste_kg_per_week=request.food_waste_kg_per_week,
    )
    grade, description = get_eco_score_label(result["total_tco2e"])
    return {
        **result,
        "eco_grade": grade,
        "eco_description": description,
        "india_average_tco2e": 1.9,
        "paris_target_tco2e": 2.5,
    }


@app.post("/api/v1/documents/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or text file to be ingested into the vector store.
    """
    allowed_types = {"application/pdf", "text/plain"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Only PDF and TXT allowed."
        )

    upload_dir = PROJECT_ROOT / "datasets" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    content = await file.read()
    file_path.write_bytes(content)
    logger.info(f"Uploaded file saved: {file_path}")

    # Ingest asynchronously (simplified — run synchronously here)
    try:
        from scripts.ingest_documents import ingest_pdf, ingest_text_file
        from rag.vector_store import get_vector_store
        vs = get_vector_store(settings)
        if file.filename.endswith(".pdf"):
            chunks = ingest_pdf(file_path, vs, settings.chunk_size, settings.chunk_overlap)
        else:
            chunks = ingest_text_file(file_path, vs, settings.chunk_size, settings.chunk_overlap)
        return {"status": "success", "filename": file.filename, "chunks_added": chunks}
    except Exception as exc:
        logger.error(f"Ingestion error: {exc}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exc)}")


@app.post("/api/v1/feedback", tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):
    """Record user feedback for a chat response."""
    logger.info(f"Feedback received — id={request.message_id} rating={request.rating}")
    # In production: store in a database
    return {"status": "received", "message": "Thank you for your feedback!"}


@app.get("/api/v1/categories", tags=["Knowledge Base"])
async def list_categories():
    """List available knowledge base categories."""
    return {
        "categories": [
            "waste_management", "water_conservation", "energy", "transport",
            "food", "government_schemes", "recycling", "sustainable_products",
            "carbon_footprint", "biodiversity", "air_quality", "sustainable_living",
            "climate_change",
        ]
    }
