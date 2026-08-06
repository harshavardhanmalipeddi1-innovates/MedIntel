import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'backend')))

from fastapi import FastAPI
from backend.app.api.prediction import router as prediction_router

app = FastAPI(title="MedIntel API", version="1.0")

@app.get("/health")
def health_check():
    return {
      "status": "healthy",
      "service": "MedIntel API",
      "version": "1.0"
    }

app.include_router(prediction_router)
