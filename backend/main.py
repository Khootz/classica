
from dotenv import load_dotenv

# Load env before services
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, engine
from sqlmodel import Session
from routes import tasks, documents, chat, memo
# from services import pathway_client  # Not needed at startup

app = FastAPI(title="CFO Copilot Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    # with Session(engine) as session:
    #     pathway_client.rebuild_indexes_from_db(session)

# Routes
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(documents.router, prefix="/tasks/{task_id}/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/tasks/{task_id}/chat", tags=["Chat"])
app.include_router(memo.router, prefix="/tasks/{task_id}/memo", tags=["Memo"])
