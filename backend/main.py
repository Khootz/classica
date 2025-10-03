from fastapi import FastAPI
from database import init_db, get_session
from routes import tasks, documents, chat, memo
from services import pathway_client
from database import engine
from sqlmodel import Session

app = FastAPI(title="CFO Copilot Backend")

@app.on_event("startup")
def on_startup():
    init_db()
    # Open a plain session directly, not via get_session()
    with Session(engine) as session:
        pathway_client.rebuild_indexes_from_db(session)

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(documents.router, prefix="/tasks/{task_id}/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/tasks/{task_id}/chat", tags=["Chat"])
app.include_router(memo.router, prefix="/tasks/{task_id}/memo", tags=["Memo"])
