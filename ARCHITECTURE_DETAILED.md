# 🏗️ Current System Architecture - Hybrid RAG Implementation

## System Overview

The system now combines **structured financial analysis** with **document retrieval (RAG)** to provide contextualized answers with citations.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                              │
│  - Upload PDFs                                                           │
│  - Chat Interface                                                        │
│  - Display Citations                                                     │
└─────────────────┬───────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                                  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    DOCUMENT UPLOAD PIPELINE                      │   │
│  │                                                                   │   │
│  │  1. Save PDF to disk                                             │   │
│  │  2. LandingAI ADE Parse → Markdown                               │   │
│  │  3. LandingAI ADE Extract → Structured JSON (8 fields)           │   │
│  │  4. Pathway: Normalize & Compute Ratios (5 metrics)              │   │
│  │  5. Finance Logic: Apply Rules → Generate Insights               │   │
│  │  6. Save to SQLite Database                                      │   │
│  │  7. 🆕 Pathway RAG: Index Document                               │   │
│  │     - Chunk markdown (1000 chars, 200 overlap)                   │   │
│  │     - Index structured data as text                              │   │
│  │     - Save to pathway_index/{task_id}_index.json                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CHAT QUERY PIPELINE                         │   │
│  │                                                                   │   │
│  │  1. Receive user query                                           │   │
│  │  2. Load structured data from DB (all docs in task)              │   │
│  │  3. Pathway: Compute financial metrics                           │   │
│  │  4. Finance Logic: Generate insights                             │   │
│  │  5. 🆕 Pathway RAG: Search Documents                             │   │
│  │     - Keyword search across chunks                               │   │
│  │     - Score by term frequency                                    │   │
│  │     - Return top 5 relevant chunks                               │   │
│  │  6. 🆕 Format Citations (doc name + chunk #)                     │   │
│  │  7. Gemini AI: Generate Answer                                   │   │
│  │     - Input: Structured metrics + Insights + Document excerpts   │   │
│  │     - Output: Natural language summary                           │   │
│  │  8. Save to DB with citations                                    │   │
│  │  9. Return response to frontend                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detailed Data Flow

### Phase 1: Document Upload & Indexing

```
User                          Backend Services                    Storage
 │                                                                    │
 │  Upload PDF                                                       │
 ├──────────────────────────►                                        │
 │                            LandingAI ADE                           │
 │                            ┌─────────────┐                        │
 │                            │ 1. Parse    │                        │
 │                            │    PDF      │                        │
 │                            └──────┬──────┘                        │
 │                                   │ Markdown                       │
 │                            ┌──────▼──────┐                        │
 │                            │ 2. Extract  │                        │
 │                            │    Fields   │                        │
 │                            └──────┬──────┘                        │
 │                                   │ JSON (8 fields)                │
 │                                   │                                │
 │                            ┌──────▼──────────────┐                │
 │                            │ 3. Pathway          │                │
 │                            │    - Normalize      │                │
 │                            │    - Compute Ratios │                │
 │                            └──────┬──────────────┘                │
 │                                   │ 5 Metrics                      │
 │                            ┌──────▼──────────────┐                │
 │                            │ 4. Finance Logic    │                │
 │                            │    - Apply Rules    │                │
 │                            │    - Gen Insights   │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Insights []                    │
 │                                   │                                │
 │                            ┌──────▼──────────────┐                │
 │                            │ 5. Save to SQLite   │───────────────►│
 │                            │    - Document       │        SQLite  │
 │                            │    - Extraction     │         DB     │
 │                            │    - Markdown       │                │
 │                            └─────────────────────┘                │
 │                                   │                                │
 │                            ┌──────▼──────────────┐                │
 │                         🆕 │ 6. Pathway RAG      │                │
 │                            │    - Chunk text     │                │
 │                            │    - Build index    │───────────────►│
 │                            │    - Save JSON      │     pathway_   │
 │                            └─────────────────────┘   index/*.json │
 │                                                                    │
 │  ◄─────── Upload Complete ────────────────────────────────────────┤
```

### Phase 2: Chat Query & Response Generation

```
User                          Backend Services                    Storage
 │                                                                    │
 │  Ask Question: "What are the key risks?"                          │
 ├──────────────────────────►                                        │
 │                            ┌─────────────────────┐                │
 │                            │ 1. Load Structured  │◄───────────────┤
 │                            │    Data from DB     │     SQLite     │
 │                            └──────┬──────────────┘                │
 │                                   │ Extraction JSON                │
 │                            ┌──────▼──────────────┐                │
 │                            │ 2. Pathway          │                │
 │                            │    - Compute        │                │
 │                            │      Metrics        │                │
 │                            └──────┬──────────────┘                │
 │                                   │ 5 Ratios                       │
 │                            ┌──────▼──────────────┐                │
 │                            │ 3. Finance Logic    │                │
 │                            │    - Gen Insights   │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Insights []                    │
 │                         🆕 ┌──────▼──────────────┐                │
 │                            │ 4. Pathway RAG      │                │
 │                            │    - Search index   │◄───────────────┤
 │                            │    - Score chunks   │   pathway_     │
 │                            │    - Top 5 results  │   index/*.json │
 │                            └──────┬──────────────┘                │
 │                                   │ Context + Sources              │
 │                         🆕 ┌──────▼──────────────┐                │
 │                            │ 5. Format Citations │                │
 │                            │    - Doc names      │                │
 │                            │    - Chunk numbers  │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Citations []                   │
 │                            ┌──────▼──────────────┐                │
 │                            │ 6. Build Prompt     │                │
 │                            │    - System: Role   │                │
 │                            │    - User: Query    │                │
 │                            │    - Metrics        │                │
 │                            │    - Insights       │                │
 │                         🆕 │    - Doc Excerpts   │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Prompt                         │
 │                            ┌──────▼──────────────┐                │
 │                            │ 7. Gemini AI        │                │
 │                            │    - Generate       │                │
 │                            │      Summary        │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Answer Text                    │
 │                            ┌──────▼──────────────┐                │
 │                            │ 8. Save to DB       │───────────────►│
 │                            │    - ChatMessage    │     SQLite     │
 │                            │    - Content        │                │
 │                            │    - Reasoning      │                │
 │                         🆕 │    - Citations      │                │
 │                            └──────┬──────────────┘                │
 │                                   │ Response                       │
 │  ◄─────── Answer + Citations ────┴────────────────────────────────┤
 │  
 │  Display:
 │  ┌─────────────────────────────────────────┐
 │  │ Answer: Based on the financial data...  │
 │  │                                          │
 │  │ Reasoning:                               │
 │  │ ✅ Healthy leverage: ratio 0.5           │
 │  │ ⚠️  Low profitability: margin 5%         │
 │  │                                          │
 │  │ Sources:                                 │
 │  │ 📄 10-Q.pdf (Page 3)                     │
 │  │ 📄 Financial-Report.pdf (Page 1)         │
 │  └─────────────────────────────────────────┘
```

---

## 🗄️ Storage Architecture

### SQLite Database
```
┌─────────────────────────────────────────────┐
│              SQLite Database                │
├─────────────────────────────────────────────┤
│                                             │
│  Task                                       │
│  ├── id: task_uuid                          │
│  ├── name: "Company XYZ Due Diligence"     │
│  └── risk_level: "healthy"                 │
│                                             │
│  Document                                   │
│  ├── id: doc_uuid                           │
│  ├── task_id: task_uuid                     │
│  ├── filename: "10-Q.pdf"                   │
│  ├── path: "./uploads/task_id/10-Q.pdf"    │
│  ├── markdown: "# Financial Report..."     │
│  ├── extraction_json: "{Revenue: 1M...}"   │
│  └── red_flags: "[⚠️ Low margin...]"        │
│                                             │
│  ChatMessage                                │
│  ├── id: chat_uuid                          │
│  ├── task_id: task_uuid                     │
│  ├── role: "agent"                          │
│  ├── content: "Based on analysis..."       │
│  ├── reasoning_log: "[✅ Healthy...]"       │
│  ├── citations: "[{doc: '10-Q.pdf'...}]"   │
│  └── status: "done"                         │
│                                             │
│  Memo                                       │
│  ├── task_id: task_uuid                     │
│  ├── summary: "Executive summary..."       │
│  └── metrics: "{debt_to_equity: 0.5...}"   │
└─────────────────────────────────────────────┘
```

### 🆕 Pathway RAG Index (JSON Files)
```
pathway_index/
  └── {task_id}_index.json
      [
        {
          "task_id": "abc-123",
          "doc_id": "doc-456",
          "chunk_id": "doc-456_chunk_0",
          "text": "The company reported revenue...",
          "type": "text_chunk",
          "metadata": {
            "filename": "10-Q.pdf",
            "chunk_index": 0,
            "total_chunks": 15
          }
        },
        {
          "task_id": "abc-123",
          "doc_id": "doc-456",
          "chunk_id": "doc-456_structured",
          "text": "Company: Acme\nRevenue: 1000000...",
          "type": "structured_data",
          "metadata": {
            "extraction": {
              "Company": "Acme Inc",
              "Revenue": "1000000",
              ...
            }
          }
        }
      ]
```

---

## 🧩 Component Interaction Matrix

| Component | Reads From | Writes To | Purpose |
|-----------|------------|-----------|---------|
| **LandingAI ADE** | Uploaded PDFs | Markdown + JSON | Parse & extract fields |
| **Pathway (Metrics)** | ADE JSON | Computed ratios | Normalize & calculate |
| **Finance Logic** | Pathway output | Insight strings | Rule-based analysis |
| **🆕 Pathway RAG** | Markdown + JSON | Index files | Chunk & index documents |
| **Gemini AI** | Metrics + Insights + 🆕 RAG context | Summary text | Generate answers |
| **SQLite** | All components | Document, Chat, Memo | Persistent storage |

---

## 🔍 RAG Search Process (Detailed)

```
Query: "What are the revenue trends?"
   │
   ▼
┌─────────────────────────────────────────┐
│ 1. Load Index for Task                  │
│    pathway_index/{task_id}_index.json   │
└───────────────┬─────────────────────────┘
                │ All chunks + metadata
                ▼
┌─────────────────────────────────────────┐
│ 2. Tokenize Query                       │
│    ["revenue", "trends"]                │
└───────────────┬─────────────────────────┘
                │ Keywords
                ▼
┌─────────────────────────────────────────┐
│ 3. Score Each Chunk                     │
│    For each chunk:                      │
│      score = count("revenue") +         │
│              count("trends")            │
└───────────────┬─────────────────────────┘
                │ Scored chunks
                ▼
┌─────────────────────────────────────────┐
│ 4. Sort by Score (descending)           │
│    [chunk_5: score=8,                   │
│     chunk_2: score=5,                   │
│     chunk_12: score=3, ...]             │
└───────────────┬─────────────────────────┘
                │ Ranked list
                ▼
┌─────────────────────────────────────────┐
│ 5. Return Top 5                         │
│    - Text content                       │
│    - Source metadata                    │
│    - Chunk index                        │
└─────────────────────────────────────────┘
```

---

## 🎯 Key Differences: Before vs After RAG

### Before (Structured Only)
```
Query → Fetch DB Metrics → Compute Ratios → Generate Insights
                                                    ↓
                                    Gemini (metrics only)
                                                    ↓
                                    Answer (no citations)
```

### After (Hybrid RAG)
```
Query → Fetch DB Metrics → Compute Ratios → Generate Insights
              ↓                                      ↓
        🆕 Search RAG Index                  Combine Context
              ↓                                      ↓
        Retrieve Chunks ────────────► Gemini (metrics + excerpts)
              ↓                                      ↓
        Format Citations ──────────► Answer + Citations
```

---

## 📊 Performance Characteristics

| Aspect | Details |
|--------|---------|
| **Indexing Time** | ~1-2 seconds per document |
| **Chunk Size** | 1000 characters |
| **Overlap** | 200 characters |
| **Search Method** | Keyword frequency (TF-like) |
| **Top-K Results** | 5 chunks |
| **Storage** | JSON files (one per task) |
| **Scalability** | Good for <100 docs per task |

---

## 🔮 Future Enhancement Opportunities

1. **Semantic Search**
   - Replace keyword matching with vector embeddings
   - Use sentence-transformers or OpenAI embeddings
   - Store in vector DB (Pinecone, Weaviate, ChromaDB)

2. **Advanced Ranking**
   - Implement BM25 algorithm
   - Add TF-IDF scoring
   - Use reranking models (cross-encoders)

3. **Streaming Mode**
   - Use Pathway's native streaming capabilities
   - Real-time index updates
   - Live document ingestion

4. **Multi-modal**
   - Index tables separately
   - Image/chart extraction
   - Structured data querying

5. **Cross-Document**
   - Aggregate insights across multiple docs
   - Timeline construction
   - Contradiction detection

---

## 🛡️ Error Handling & Resilience

```
RAG Pipeline with Graceful Degradation:

try:
    rag_context = pathway_rag.get_rag_context(task_id, query)
    context_text = rag_context.get("context", "")
    citations = format_citations(rag_context.get("sources", []))
except Exception as e:
    print(f"⚠️ RAG failed (non-critical): {e}")
    context_text = ""  # Fall back to empty context
    citations = []     # No citations

# System continues with structured metrics regardless
gemini_prompt = build_prompt(metrics, insights, context_text)
answer = gemini.generate(prompt)
save_to_db(answer, citations)  # Works even if citations=[]
```

**Result:** Even if RAG completely fails, the system still provides structured metric analysis.

---

## 📈 Data Flow Summary

```
INPUT (PDF)
    ↓
┌───────────────┐
│ ADE Extract   │ → 8 structured fields
└───────┬───────┘
        ├──────────┐
        │          │
        ▼          ▼
┌───────────┐  ┌──────────────┐
│ Pathway   │  │ Pathway RAG  │
│ Metrics   │  │ Index        │
│ (5 ratios)│  │ (chunks)     │
└─────┬─────┘  └──────┬───────┘
      │               │
      ▼               ▼
┌──────────────────────────┐
│    QUERY PROCESSING      │
│  - Metrics               │
│  - Insights              │
│  - RAG Context  🆕        │
│  - Citations    🆕        │
└──────────┬───────────────┘
           │
           ▼
    ┌────────────┐
    │  Gemini AI │
    └─────┬──────┘
          │
          ▼
OUTPUT (Answer + Citations)
```

This hybrid approach gives you the best of both worlds: **precise financial metrics** + **contextual document understanding**! 🎉
