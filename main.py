from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import asyncio

from celery_worker import celery_app, run_financial_analysis
from celery.result import AsyncResult
from crewai import Crew, Process,LLM
from agents import financial_analyst,verifier,investment_advisor,risk_assessor
from task import analyze_financial_document,verification,investment_analysis,risk_assessment

app = FastAPI(title="Financial Document Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to frontend url in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

# FIX: Endpoint name fixed to not be the same as the tool
@app.post("/analyze")
async def analyze_financial_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/{file.filename}_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Process the financial document with all analysts
        task = run_financial_analysis.delay(query, file_path)
    
        return {
            "status": "Task Enqueued",
            "task_id": task.id,
            "check_status_url": f"/status/{task.id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "state": res.state,
        "result": res.result if res.ready() else "Processing..."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)