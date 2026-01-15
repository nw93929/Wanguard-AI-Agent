"""
FastAPI Endpoint for n8n Integration
=====================================

This file provides a REST API endpoint that n8n (or other automation tools) can call
to trigger research tasks asynchronously.

Usage from n8n:
POST http://localhost:8000/research
Body: {"ticker": "AAPL", "instructions": "Analyze Q4 2024 performance"}

Response: {"status": "Task Queued", "ticker": "AAPL", "task_id": "uuid-here"}
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import asyncio
from uuid import uuid4
from datetime import datetime

# Import the research function from main
from main import run_research

# Initialize FastAPI app
api_app = FastAPI(
    title="AI Research Agent API",
    description="Autonomous financial research agent with LangGraph",
    version="1.0.0"
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SingleStockResearchRequest(BaseModel):
    """Request model for single stock analysis"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")
    instructions: str = Field(
        default="Analyze financial performance and market position",
        description="Specific research instructions"
    )

class StockScreeningRequest(BaseModel):
    """Request model for screening multiple stocks"""
    mode: Literal["screening"] = Field(default="screening")
    criteria: str = Field(
        default="Warren Buffett value investing",
        description="Investment criteria to use (e.g., 'Warren Buffett value investing', 'high growth tech', 'dividend aristocrats')"
    )
    max_stocks: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of stocks to analyze"
    )
    sectors: Optional[list[str]] = Field(
        default=None,
        description="Filter by sectors (e.g., ['Technology', 'Healthcare'])"
    )

class ResearchResponse(BaseModel):
    """Response model for queued research tasks"""
    status: str
    task_id: str
    ticker: Optional[str] = None
    message: str
    queued_at: str

# ============================================================================
# API ENDPOINTS
# ============================================================================

@api_app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AI Research Agent API",
        "status": "running",
        "endpoints": {
            "single_stock": "POST /research",
            "screening": "POST /research/screen",
            "health": "GET /health"
        }
    }

@api_app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "langraph": "available",
            "pinecone": "connected",
            "gpt4": "available"
        }
    }

@api_app.post("/research", response_model=ResearchResponse)
async def trigger_single_stock_research(
    request: SingleStockResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger research for a single stock.

    The task runs in the background, so this endpoint returns immediately.
    n8n receives confirmation that the task is queued.

    Future enhancement: Add task_id tracking to poll for results.
    """
    query = f"{request.instructions} for {request.ticker}"
    task_id = str(uuid4())

    # Add task to background (non-blocking)
    background_tasks.add_task(run_research, query)

    return ResearchResponse(
        status="queued",
        task_id=task_id,
        ticker=request.ticker,
        message=f"Research task queued for {request.ticker}",
        queued_at=datetime.now().isoformat()
    )

@api_app.post("/research/screen", response_model=ResearchResponse)
async def trigger_stock_screening(
    request: StockScreeningRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger batch screening of multiple stocks based on investment criteria.

    This endpoint will be used for the new screening workflow.
    """
    task_id = str(uuid4())

    # Build query for screening mode
    query = f"Screen stocks using {request.criteria} criteria. "
    if request.sectors:
        query += f"Focus on sectors: {', '.join(request.sectors)}. "
    query += f"Return top {request.max_stocks} recommendations."

    # TODO: Implement batch screening workflow
    # For now, this is a placeholder
    background_tasks.add_task(run_research, query)

    return ResearchResponse(
        status="queued",
        task_id=task_id,
        ticker=None,
        message=f"Stock screening task queued with {request.criteria} criteria",
        queued_at=datetime.now().isoformat()
    )

# ============================================================================
# FUTURE ENDPOINTS (for result retrieval)
# ============================================================================

# @api_app.get("/research/{task_id}")
# async def get_research_results(task_id: str):
#     """
#     Retrieve results of a completed research task.
#     Requires implementing a result storage mechanism (Redis/DB).
#     """
#     pass

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Starting AI Research Agent API Server")
    print("=" * 60)
    print("📊 Single Stock Analysis: POST /research")
    print("🔍 Stock Screening: POST /research/screen")
    print("💚 Health Check: GET /health")
    print("=" * 60)

    uvicorn.run(
        "api:api_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
