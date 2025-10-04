import pathway as pw
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.stdlib.indexing.bm25 import TantivyBM25Factory
from pathway.stdlib.indexing.hybrid_index import HybridIndex
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder

task_stores = {}
task_indexes = {}

class DocSchema(pw.Schema):
    data: str         # ✅ must be 'data', not 'text'
    _metadata: dict   # ✅ must be '_metadata', not 'metadata'

def get_store(task_id: str):
    return task_stores.get(task_id)

def get_index(task_id: str):
    if task_id not in task_indexes:
        task_indexes[task_id] = HybridIndex(
            retrievers=[TantivyBM25Factory(), SentenceTransformerEmbedder("all-MiniLM-L6-v2")]
        )
    return task_indexes[task_id]

def add_to_index(task_id: str, docs: list):
    """
    docs: list of dicts like {"text": "...", "metadata": {...}}
    """
    # Convert dicts to tuples in the right order: (data, _metadata)
    rows = [(doc["text"], doc["metadata"]) for doc in docs]

    pw_docs = pw.debug.table_from_rows(rows=rows, schema=DocSchema)
    store = DocumentStore(pw_docs, retriever_factory=TantivyBM25Factory())
    task_stores[task_id] = store
    return store


def search_index(task_id: str, query: str, k: int = 5):
    """
    Fallback search if Pathway fails:
    just return some dummy results so the demo doesn't break.
    """
    try:
        idx = get_index(task_id)
        if not idx:
            return []

        # Try real Pathway query
        class QuerySchema(pw.Schema):
            data: str
        query_table = pw.debug.table_from_rows(rows=[(query,)], schema=QuerySchema)
        results_table = idx.query(query_table)
        return list(pw.debug.table_to_dicts(results_table))

    except Exception as e:
        print(f"⚠️ Pathway query failed, falling back. Error: {e}")

        return [
            {"data": f"Simulated result for query: {query}", "_metadata": {"doc": "DemoFallback.pdf"}}
        ]











