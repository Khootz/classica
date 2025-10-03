from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
import json, uuid, time

from database import get_session
from models import ChatMessage, Memo
from services import gemini_client, pathway_client, finance_logic

router = APIRouter()

# --- In-memory status tracker (for polling) ---
chat_status = {}  # {chat_id: {"status": str, "progress": int, "message": str}}

def update_status(chat_id, status, progress, message):
    chat_status[chat_id] = {"status": status, "progress": progress, "message": message}


@router.post("/")
def create_chat(
    task_id: str,
    payload: dict,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    user_message = payload.get("message")

    # 1. Store user message
    chat_id = str(uuid.uuid4())
    chat_msg = ChatMessage(
        id=chat_id,
        task_id=task_id,
        role="user",
        content=user_message,
        status="pending"
    )
    session.add(chat_msg)
    session.commit()

    # 2. Launch background agent process
    background_tasks.add_task(run_agent_pipeline, chat_id, task_id, user_message, session)

    # 3. Return chat_id immediately
    return {"chat_id": chat_id, "status": "pending"}


@router.get("/{chat_id}/status")
def get_chat_status(chat_id: str):
    return chat_status.get(chat_id, {"status": "unknown", "progress": 0})


@router.get("/{chat_id}")
def get_chat_result(chat_id: str, session: Session = Depends(get_session)):
    chat = session.get(ChatMessage, chat_id)
    if not chat:
        return {"error": "Chat not found"}
    return {
        "chat_id": chat.id,
        "role": chat.role,
        "response": chat.content,
        "reasoning_log": json.loads(chat.reasoning_log or "[]"),
        "citations": json.loads(chat.citations or "[]"),
        "status": chat.status
    }


# --- Background pipeline ---
def run_agent_pipeline(chat_id: str, task_id: str, user_message: str, session: Session):
    update_status(chat_id, "parsing_documents", 20, "Parsing documents with ADE / Pathway")

    # 1. CFO agent: generate sub-questions using Gemini
    subq_prompt = [
        {"role": "system", "content": "You are a CFO assistant. Break the user's question into financial checks like revenue, debt, cash flow, ownership, contracts."},
        {"role": "user", "content": user_message}
    ]
    subquestions = gemini_client.ask_gemini(subq_prompt)
    update_status(chat_id, "searching_index", 50, "Searching relevant documents")

    # 2. Query Pathway index for each sub-question
    hits = []
    for q in subquestions.split("\n"):
        res = pathway_client.search_index(task_id, q)
        hits.extend(res)

    # 3. Apply Finance Logic (if structured JSON is available)
    structured_data = {}  # TODO: gather ADE JSON for task docs
    finance_results = finance_logic.analyze_financials(structured_data)

    update_status(chat_id, "computing_metrics", 80, "Computing ratios and risks")

    # 4. Summarize with Gemini
    final_prompt = [
        {"role": "system", "content": "You are a CFO. Write a short, executive summary of the company's financial health."},
        {"role": "user", "content": f"Question: {user_message}\nFindings: {finance_results}\nEvidence: {hits}"}
    ]
    summary = gemini_client.ask_gemini(final_prompt)

    # 5. Save in DB
    chat_msg = session.get(ChatMessage, chat_id)
    chat_msg.role = "agent"
    chat_msg.content = summary
    chat_msg.reasoning_log = json.dumps(finance_results["reasoning_log"])
    chat_msg.citations = json.dumps([h for h in hits[:3]])  # top 3 sources
    chat_msg.status = "done"
    session.add(chat_msg)
    existing_memo = session.exec(select(Memo).where(Memo.task_id == task_id)).first()

    memo_text = summary
    metrics = {
        "revenue_growth": next((s["value"] for s in finance_results["reasoning_log"] if "growth" in s["step"]), None),
        "debt_equity_ratio": next((s["value"] for s in finance_results["reasoning_log"] if "Debt/Equity" in s["step"]),
                                  None),
    }

    if existing_memo:
        existing_memo.summary = memo_text
        existing_memo.metrics = json.dumps(metrics)
        session.add(existing_memo)
    else:
        new_memo = Memo(task_id=task_id, summary=memo_text, metrics=json.dumps(metrics))
        session.add(new_memo)

    session.commit()

    update_status(chat_id, "done", 100, "Analysis complete")
