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
        "Company": {"type": "string"},
        "Revenue": {"type": "string"},
        "TotalDebt": {"type": "string"},
        "Equity": {"type": "string"},
        "CashFlow": {"type": "string"},
        "NetIncome": {"type": "string"},
        "EBITDA": {"type": "string"},
        "OperatingIncome": {"type": "string"}
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
    # 1️⃣ Save file locally
    task_dir = os.path.join(UPLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ ADE parse → markdown
    parsed = landing_ai.parse_pdf(file_path)
    markdown = parsed.get("markdown", "")

    # 3️⃣ ADE extract → structured JSON
    extraction = landing_ai.extract_from_markdown(markdown, DEFAULT_SCHEMA)
    extraction_json = extraction.get("extraction", {})
    import json
    print("\n🚀 Raw ADE Response:", json.dumps(extraction, indent=2))
    print("🧩 ADE Extraction JSON:", json.dumps(extraction_json, indent=2))

    # ---------------------------------------------------
    # 🧩 4️⃣ Pathway pipeline: compute financial metrics
    # ---------------------------------------------------
    metrics = pathway_client.process_ade_data(extraction_json)

    # ---------------------------------------------------
    # 🧠 5️⃣ CFO logic (based on Pathway pipeline results)
    # ---------------------------------------------------
    analysis = finance_logic.analyze_financials(extraction_json)

    # ---------------------------------------------------
    # 💾 6️⃣ Save all metadata to DB
    # ---------------------------------------------------
    doc = Document(
        task_id=task_id,
        filename=file.filename,
        path=file_path,
        markdown=markdown,
        extraction_json=json.dumps(extraction_json),
        meta_json=json.dumps({"parsed": True}),
        ingested=True,
        red_flags=json.dumps(analysis["insights"])  # update key name
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    # ---------------------------------------------------
    # ✅ 7️⃣ Return a rich response
    # ---------------------------------------------------
    return {
        "id": doc.id,
        "task_id": task_id,
        "filename": doc.filename,
        "ingested": True,
        "metrics": metrics,
        "analysis": analysis,
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
