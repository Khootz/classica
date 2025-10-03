try:
    from pathway.xpacks.llm.vectorstore.hybrid_index import HybridIndex
except ImportError:
    # fallback for other versions
    from pathway.xpacks.llm.vectorstore import HybridIndex

from sqlmodel import Session, select
from models import Document
import json

task_indexes = {}

def get_index(task_id: str):
    if task_id not in task_indexes:
        task_indexes[task_id] = HybridIndex()
    return task_indexes[task_id]

def add_to_index(task_id: str, doc_text: str, metadata: dict):
    idx = get_index(task_id)
    idx.add(doc_text, metadata=metadata)

def search_index(task_id: str, query: str):
    idx = get_index(task_id)
    return idx.search(query)

def rebuild_indexes_from_db(session: Session):
    """
    Rebuild all Pathway indexes from DB on startup.
    """
    docs = session.exec(select(Document)).all()
    for doc in docs:
        idx = get_index(doc.task_id)

        # load extracted JSON if present
        if doc.meta_json:
            try:
                extracted = json.loads(doc.meta_json)
                idx.add(json.dumps(extracted), metadata={"doc": doc.filename})
            except Exception:
                pass
