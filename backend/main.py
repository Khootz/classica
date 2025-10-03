from fastapi import FastAPI
from database import init_db, get_session
from routes import tasks, documents, chat, memo
from services import pathway_client

app = FastAPI(title="CFO Copilot Backend")

@app.on_event("startup")
def on_startup():
    # 1. Init DB
    init_db()

    # 2. Reload indexes
    from sqlmodel import Session
    with Session(next(get_session)) as session:
        pathway_client.rebuild_indexes_from_db(session)

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(documents.router, prefix="/tasks/{task_id}/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/tasks/{task_id}/chat", tags=["Chat"])
app.include_router(memo.router, prefix="/tasks/{task_id}/memo", tags=["Memo"])
