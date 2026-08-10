import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..", "backend")
    )
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.prediction import router as prediction_router
from backend.app.api.reasoning import router as reasoning_router
from backend.app.api.verification import router as verification_router
from backend.app.api.treatment import router as treatment_router
from backend.app.api.workflow import router as workflow_router
from backend.app.api.assessment import router as assessment_router


app = FastAPI(title="MedIntel API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MedIntel API",
        "version": "1.0",
    }


app.include_router(prediction_router, prefix="/api/v1")
app.include_router(reasoning_router, prefix="/api/v1/clinical")
app.include_router(verification_router, prefix="/api/v1/clinical")
app.include_router(treatment_router, prefix="/api/v1/clinical")
app.include_router(workflow_router, prefix="/api/v1/clinical")
app.include_router(assessment_router, prefix="/api/v1/clinical")
