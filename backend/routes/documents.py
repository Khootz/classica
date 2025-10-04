from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session, select
import os, json, shutil

from database import get_session
from models import Document
from services import landing_ai, pathway_client, finance_logic

router = APIRouter()
UPLOAD_DIR = "./uploads"

# Default schema for ADE extract
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "Revenue": {"type": "string"},
        "TotalDebt": {"type": "string"},
        "Equity": {"type": "string"},
        "CashFlow": {"type": "string"}
    },
    "required": ["Revenue", "TotalDebt", "Equity"]
}

# -----------------------
# Upload a document (POST)
# -----------------------
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

    # 2. ADE parse → markdown
    parsed = landing_ai.parse_pdf(file_path)
    markdown = parsed.get("markdown", "")

    # 3. ADE extract → structured JSON
    extraction = landing_ai.extract_from_markdown(markdown, DEFAULT_SCHEMA)
    extraction_json = extraction.get("extraction", {})

    # 4. Build docs for Pathway
    docs_to_add = [
        {"text": markdown, "metadata": {"doc": file.filename}},
        {"text": json.dumps(extraction_json), "metadata": {"doc": file.filename}}
    ]
    pathway_client.add_to_index(task_id, docs_to_add)

    # 5. Run finance logic
    analysis = finance_logic.analyze_financials(extraction_json)

    # 6. Save to DB
    doc = Document(
        task_id=task_id,
        filename=file.filename,
        path=file_path,
        markdown=markdown,
        extraction_json=json.dumps(extraction_json),
        meta_json=json.dumps({"parsed": True}),
        ingested=True,
        red_flags=json.dumps(analysis["red_flags"])
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    return {
        "id": doc.id,
        "task_id": task_id,
        "filename": doc.filename,
        "ingested": True,
        "red_flags": analysis["red_flags"],
        "extraction": extraction_json
    }

# ---------------------
# List documents (GET)
# ---------------------
@router.get("/")
async def list_documents(task_id: str, session: Session = Depends(get_session)):
    docs = session.exec(select(Document).where(Document.task_id == task_id)).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "ingested": d.ingested,
            "red_flags": json.loads(d.red_flags or "[]"),
            "created_at": str(d.created_at)
        }
        for d in docs
    ]
