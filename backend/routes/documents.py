from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session, select
import os, json, shutil

from database import get_session
from models import Document
from services import landing_ai, pathway_client, finance_logic

router = APIRouter()

UPLOAD_DIR = "./uploads"

@router.post("/")
async def upload_document(
    task_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # 1. Save file
    task_dir = os.path.join(UPLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Call LandingAI ADE
    extracted_data = landing_ai.extract_with_ade(file_path)

    # 3. Add to Pathway index
    pathway_client.add_to_index(task_id, json.dumps(extracted_data), metadata={"doc": file.filename})

    # 4. Run Finance Logic
    analysis = finance_logic.analyze_financials(extracted_data)

    # 5. Save in DB
    doc = Document(
        task_id=task_id,
        filename=file.filename,
        path=file_path,
        metadata=json.dumps({"extracted": True}),
        ingested=True,
        red_flags=json.dumps(analysis["red_flags"])
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    # 6. Return response
    return {
        "id": doc.id,
        "task_id": task_id,
        "filename": doc.filename,
        "ingested": True,
        "red_flags": analysis["red_flags"]
    }
