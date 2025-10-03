from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

def gen_id():
    return str(uuid.uuid4())

class Task(SQLModel, table=True):
    id: str = Field(default_factory=gen_id, primary_key=True)
    name: str
    risk_level: str = "unknown"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    id: str = Field(default_factory=gen_id, primary_key=True)
    task_id: str = Field(foreign_key="task.id")
    filename: str
    path: str
    meta_json: Optional[str] = None   # instead of metadata
    ingested: bool = False
    red_flags: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(SQLModel, table=True):
    id: str = Field(default_factory=gen_id, primary_key=True)
    task_id: str = Field(foreign_key="task.id")
    role: str
    content: str
    status: str = "pending"
    reasoning_log: Optional[str] = None
    citations: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Memo(SQLModel, table=True):
    id: str = Field(default_factory=gen_id, primary_key=True)
    task_id: str = Field(foreign_key="task.id")
    summary: Optional[str] = None
    metrics: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
