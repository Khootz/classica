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

from pathway.stdlib.indexing.bm25 import TantivyBM25
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder
from pathway.stdlib.indexing.hybrid_index import HybridIndex

def get_index(task_id: str):
    store = get_store(task_id)
    if not store:
        print(f"⚠️ No DocumentStore found for task {task_id}")
        return None

    if task_id not in task_indexes:
        bm25 = TantivyBM25(store.docs.data, store.docs._metadata)
        embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
        task_indexes[task_id] = HybridIndex(retrievers=[bm25, embedder])

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
    idx = get_index(task_id)
    if not idx:
        return []

    # Build query table
    class QuerySchema(pw.Schema):
        data: str

    query_table = pw.debug.table_from_rows(rows=[(query,)], schema=QuerySchema)

    try:
        idx.k = k
    except Exception:
        pass

    # ✅ Pass the column reference
    results_table = idx.query(query_table.data, number_of_matches=k)

    # Convert Pathway table to dicts
    try:
        results = list(pw.debug.table_to_dicts(results_table))
        print(f"✅ Pathway returned {len(results)} results")
        return results
    except Exception as e:
        print(f"⚠️ Could not convert results: {e}")
        return []













