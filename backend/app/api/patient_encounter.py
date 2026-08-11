from fastapi import APIRouter, HTTPException

from backend.app.schemas.patient_schema import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from backend.app.schemas.encounter_schema import (
    EncounterCreate,
    EncounterResponse,
)
from backend.services.firestore_service import FirestoreService
from backend.services.patient_service import PatientService
from backend.services.encounter_service import EncounterService

router = APIRouter()

firestore_service = FirestoreService()
patient_service = PatientService(firestore_service)
encounter_service = EncounterService(firestore_service)

@router.post("/patients", response_model=PatientResponse)
async def create_patient(request: PatientCreate):
    patient_id = patient_service.create_patient(request)
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=500, detail="Unable to create patient")
    return patient

@router.get("/patients", response_model=list[PatientResponse])
async def list_patients():
    return patient_service.list_patients()

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.patch("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: str, request: PatientUpdate):
    updated = patient_service.update_patient(patient_id, request)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=500, detail="Unable to retrieve updated patient")
    return patient

@router.post("/encounters", response_model=EncounterResponse)
async def create_encounter(request: EncounterCreate):
    encounter_id = encounter_service.create_encounter(request)
    encounter = encounter_service.get_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=500, detail="Unable to create encounter")
    return encounter

@router.get("/encounters/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(encounter_id: str):
    encounter = encounter_service.get_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter
