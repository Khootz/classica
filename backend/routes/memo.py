from fastapi import APIRouter, Depends
from sqlmodel import Session, select
import json, os
from database import get_session
from models import Memo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()

@router.get("/")
def get_memo(task_id: str, session: Session = Depends(get_session)):
    memo = session.exec(select(Memo).where(Memo.task_id == task_id)).first()
    if memo:
        return {
            "task_id": task_id,
            "summary": memo.summary,
            "metrics": json.loads(memo.metrics or "{}")
        }

    return {
        "task_id": task_id,
        "summary": "No memo available yet",
        "metrics": {}
    }


@router.post("/export")
def export_memo(task_id: str, session: Session = Depends(get_session)):
    memo = session.exec(select(Memo).where(Memo.task_id == task_id)).first()
    if not memo:
        return {"error": "No memo available"}

    export_dir = "./exports"
    os.makedirs(export_dir, exist_ok=True)
    file_path = os.path.join(export_dir, f"{task_id}_memo.pdf")

    # Build PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Due Diligence Memo", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Task ID:</b> {task_id}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Executive Summary:</b>", styles["Heading2"]))
    story.append(Paragraph(memo.summary or "No summary available", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Key Metrics:</b>", styles["Heading2"]))
    metrics = json.loads(memo.metrics or "{}")
    for k, v in metrics.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story.append(Spacer(1, 20))

    doc.build(story)

    return {
        "task_id": task_id,
        "file_url": file_path
    }
