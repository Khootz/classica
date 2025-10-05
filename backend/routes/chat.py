from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
import json, uuid

from database import get_session
from models import ChatMessage, Memo, Document
from services import gemini_client, finance_logic, pathway_rag

router = APIRouter()

# --- In-memory status tracker (for polling) ---
chat_status = {}  # {chat_id: {"status": str, "progress": int, "message": str}}


def update_status(chat_id, status, progress, message):
    chat_status[chat_id] = {"status": status, "progress": progress, "message": message}


# ----------------------
# Get All Chats for Task
# ----------------------
@router.get("/")
def get_all_chats(task_id: str, session: Session = Depends(get_session)):
    chats = session.exec(
        select(ChatMessage)
        .where(ChatMessage.task_id == task_id)
        .order_by(ChatMessage.created_at)
    ).all()
    
    return [
        {
            "chat_id": chat.id,
            "role": chat.role,
            "response": chat.content,
            "reasoning_log": json.loads(chat.reasoning_log or "[]"),
            "citations": json.loads(chat.citations or "[]"),
            "status": chat.status,
            "created_at": chat.created_at.isoformat(),
        }
        for chat in chats
    ]


# ----------------------
# Create Chat Request
# ----------------------
@router.post("/")
def create_chat(
    task_id: str,
    payload: dict,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user_message = payload.get("message", "")
    chat_id = str(uuid.uuid4())

    # Store initial chat record
    chat_msg = ChatMessage(
        id=chat_id,
        task_id=task_id,
        role="user",
        content=user_message,
        status="pending",
    )
    session.add(chat_msg)
    session.commit()

    # Background processing
    background_tasks.add_task(run_agent_pipeline, chat_id, task_id, user_message, session)

    return {"chat_id": chat_id, "status": "pending"}


# ----------------------
# Poll Chat Status
# ----------------------
@router.get("/{chat_id}/status")
def get_chat_status(chat_id: str):
    return chat_status.get(chat_id, {"status": "unknown", "progress": 0})


# ----------------------
# Get Chat Result
# ----------------------
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
        "status": chat.status,
    }


# ----------------------
# Background CFO Agent
# ----------------------
def run_agent_pipeline(chat_id: str, task_id: str, user_message: str, session: Session):
    try:
        update_status(chat_id, "loading_data", 10, "Fetching financial data from ADE")

        # 1️⃣ Fetch all ADE JSONs from DB for this task
        docs = session.exec(select(Document).where(Document.task_id == task_id)).all()
        if not docs:
            update_status(chat_id, "failed", 100, "No document found for this task.")
            return

        structured_data = {}
        for d in docs:
            try:
                extracted = json.loads(d.extraction_json or "{}")
                # Normalize key casing to avoid mismatches
                extracted = {k.lower(): v for k, v in extracted.items()}
                structured_data.update(extracted)
            except Exception as e:
                print(f"⚠️ Could not parse ADE JSON for {d.filename}: {e}")

        print(f"🧾 Structured data sent to CFO agent: {structured_data}")

        update_status(chat_id, "computing_metrics", 40, "Processing data through Pathway pipeline")

        # 2️⃣ Compute Pathway-based metrics
        analysis = finance_logic.analyze_financials(structured_data)
        metrics = analysis.get("summary", {})
        insights = analysis.get("insights", [])

        update_status(chat_id, "searching_documents", 60, "Searching indexed documents")

        # 🔍 3️⃣ RAG: Search indexed documents for relevant context
        try:
            rag_context = pathway_rag.get_rag_context(task_id, user_message)
            context_text = rag_context.get("context", "")
            rag_sources = rag_context.get("sources", [])
            citations = [
                {
                    "document": source["filename"],
                    "page": f"Chunk {source['chunk_index']}"
                }
                for source in rag_sources
            ]
            print(f"✅ RAG found {len(rag_sources)} relevant chunks")
        except Exception as e:
            print(f"⚠️ RAG search failed (non-critical): {e}")
            context_text = ""
            citations = []
        
        # If no RAG citations but we have docs, add document-level citations
        if not citations and docs:
            citations = [
                {
                    "document": d.filename,
                    "page": "Financial Data"
                }
                for d in docs[:3]  # Show up to 3 documents as sources
            ]

        update_status(chat_id, "summarizing", 70, "Generating CFO summary via Gemini")

        # 4️⃣ Create LLM summary using Gemini with RAG context
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a CFO assistant. Given structured financial data, computed ratios, "
                    "and relevant document excerpts, write a concise but insightful summary of "
                    "the company's financial health. Highlight key risks, leverage, liquidity, "
                    "and performance insights clearly. IMPORTANT: Always reference the source documents "
                    "in your response. Use natural citations like 'According to the 10-Q report...' or "
                    "'The financial statements show...'. Every major claim should cite its source. "
                    "CRITICAL: Output PLAIN TEXT ONLY. Do not use markdown formatting, asterisks, "
                    "hashtags, or any special formatting. Write in normal sentences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User question: {user_message}\n\n"
                    f"Structured data: {json.dumps(structured_data, indent=2)}\n\n"
                    f"Computed metrics: {json.dumps(metrics, indent=2)}\n\n"
                    f"Insights: {json.dumps(insights, indent=2)}\n\n"
                    f"📄 Relevant document excerpts:\n{context_text if context_text else 'No relevant excerpts found.'}"
                ),
            },
        ]
        summary = gemini_client.ask_gemini(prompt)

        update_status(chat_id, "saving_results", 90, "Saving CFO agent results")

        # 5️⃣ Save to DB with citations
        chat_msg = session.get(ChatMessage, chat_id)
        chat_msg.role = "agent"
        chat_msg.content = summary
        chat_msg.reasoning_log = json.dumps(insights)
        chat_msg.citations = json.dumps(citations)  # 🆕 Save RAG citations
        chat_msg.status = "done"
        session.add(chat_msg)

        # 6️⃣ Create / update memo summary
        existing_memo = session.exec(select(Memo).where(Memo.task_id == task_id)).first()
        memo_text = summary
        core_metrics = {
            "debt_to_equity": metrics.get("debt_to_equity"),
            "debt_to_revenue": metrics.get("debt_to_revenue"),
            "cash_flow": metrics.get("cash_flow"),
        }

        if existing_memo:
            existing_memo.summary = memo_text
            existing_memo.metrics = json.dumps(core_metrics)
            session.add(existing_memo)
        else:
            new_memo = Memo(task_id=task_id, summary=memo_text, metrics=json.dumps(core_metrics))
            session.add(new_memo)

        session.commit()
        update_status(chat_id, "done", 100, "Analysis complete ✅")

    except Exception as e:
        update_status(chat_id, "failed", 100, f"Agent pipeline failed: {e}")
        print(f"❌ Agent pipeline failed: {e}")
