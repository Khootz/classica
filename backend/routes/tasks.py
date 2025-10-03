from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Task
from database import get_session

router = APIRouter()

@router.post("/")
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/")
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
