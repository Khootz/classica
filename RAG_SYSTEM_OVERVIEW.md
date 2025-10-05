# 🔍 Hybrid RAG System Overview

## How It Works

Your system now uses **Hybrid RAG** (Retrieval-Augmented Generation) that combines:
- **Structured financial data** (8 extracted fields from PDFs)
- **Full document text** (chunked and searchable)

---

## 📊 Simple Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DOCUMENT UPLOAD                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
                     Upload financial-report.pdf
                              ↓
                    ┌──────────────────────┐
                    │   LandingAI ADE      │
                    │  - Parse → Markdown  │
                    │  - Extract 8 fields  │
                    └──────────┬───────────┘
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
    ┌─────────────────┐              ┌──────────────────┐
    │ Pathway Metrics │              │  Pathway RAG     │
    │ (5 ratios)      │              │  (Hybrid Index)  │
    └─────────────────┘              └──────────────────┘
              ↓                               ↓
         Save to DB                pathway_index/{task_id}.json
                                    - Text chunks (1000 chars)
                                    - Structured data as text

┌─────────────────────────────────────────────────────────────┐
│                    2. CHAT QUERY                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
              "What are the key financial risks?"
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
    ┌─────────────────┐              ┌──────────────────┐
    │  Load Metrics   │              │   Search Index   │
    │  from Database  │              │  (Keyword-based) │
    └─────────┬───────┘              └────────┬─────────┘
              │                               │
              │  Debt ratio: 0.45             │  Top 5 chunks:
              │  Margin: 5%                   │  - "Revenue declined..."
              │  Insights: [...]              │  - "Debt restructuring..."
              │                               │
              └───────────────┬───────────────┘
                              ↓
                      ┌──────────────────┐
                      │   Gemini AI      │
                      │  (Enhanced with  │
                      │   RAG context)   │
                      └────────┬─────────┘
                              ↓
                  ┌────────────────────────┐
                  │  Response + Citations  │
                  └────────────────────────┘
                              ↓
                    Display in Frontend
```

---

## 🔄 Step-by-Step Process

### Phase 1: Indexing (When You Upload)

1. **Upload PDF** → Saved to `uploads/{task_id}/filename.pdf`

2. **LandingAI ADE Parse** → Extracts markdown text from entire document

3. **LandingAI ADE Extract** → Pulls 8 structured fields:
   - Company, Revenue, TotalDebt, Equity
   - CashFlow, NetIncome, EBITDA, OperatingIncome

4. **Pathway RAG Indexing** → Creates searchable index:
   ```python
   # Text is chunked into 1000-char pieces with 200-char overlap
   chunks = [
     "The company reported revenue of $1M in Q1...",
     "Debt restructuring was completed in March...",
     ...
   ]
   
   # Saved to: pathway_index/{task_id}_index.json
   {
     "task_id": "abc-123",
     "doc_id": "doc-456",
     "chunk_id": "doc-456_chunk_0",
     "text": "The company reported revenue...",
     "metadata": {
       "filename": "financial-report.pdf",
       "chunk_index": 0
     }
   }
   ```

5. **Save to Database** → Document record with markdown + extraction_json

---

### Phase 2: Retrieval (When You Ask Questions)

1. **You ask**: *"What are the key financial risks?"*

2. **Load structured data** from database:
   ```json
   {
     "revenue": "1000000",
     "totaldebt": "450000",
     "equity": "1000000"
   }
   ```

3. **Compute metrics** via Pathway + Finance Logic:
   ```json
   {
     "debt_to_equity": 0.45,
     "profit_margin": 0.05,
     "insights": ["✅ Healthy leverage", "⚠️ Low margin"]
   }
   ```

4. **🔍 RAG Search** (NEW!):
   ```python
   # Search index for keywords: "financial", "risks"
   # Score each chunk by term frequency
   # Return top 5 most relevant chunks
   
   results = [
     {
       "text": "Revenue declined 15% due to market conditions...",
       "filename": "10-Q.pdf",
       "chunk_index": 2,
       "score": 8
     },
     {
       "text": "Debt restructuring plan announced...",
       "filename": "10-Q.pdf",
       "chunk_index": 5,
       "score": 5
     }
   ]
   ```

5. **Build Enhanced Prompt** for Gemini:
   ```
   System: You are a CFO assistant. Given structured data and document excerpts...
   
   User:
   Question: What are the key financial risks?
   
   Structured data: {revenue: 1M, debt: 450K...}
   Metrics: {debt_to_equity: 0.45...}
   Insights: ["✅ Healthy leverage", "⚠️ Low margin"]
   
   📄 Relevant document excerpts:
   Revenue declined 15% due to market conditions...
   Debt restructuring plan announced...
   ```

6. **Gemini Generates Answer** with full context

7. **Format Citations**:
   ```json
   [
     {"document": "10-Q.pdf", "page": "Chunk 2"},
     {"document": "10-Q.pdf", "page": "Chunk 5"}
   ]
   ```

8. **Save to Database** → ChatMessage with content + citations

9. **Display in Frontend** → Answer + Sources section

---

## ✅ Will You See Citations?

**YES!** Here's what you'll see:

### Backend Response:
```json
{
  "chat_id": "abc-123",
  "response": "Based on the financial data, the company shows healthy leverage with a debt-to-equity ratio of 0.45. However, as mentioned in the 10-Q report, revenue declined 15% due to market conditions...",
  "reasoning_log": [
    "✅ Healthy debt-to-equity ratio: 0.45",
    "⚠️ Low profit margin: 5%"
  ],
  "citations": [
    {"document": "10-Q.pdf", "page": "Chunk 2"},
    {"document": "10-Q.pdf", "page": "Chunk 5"}
  ],
  "status": "done"
}
```

### Frontend Display:
```
┌────────────────────────────────────────────┐
│ 🤖 Agent                                   │
│                                            │
│ Based on the financial data, the company   │
│ shows healthy leverage with a debt-to-     │
│ equity ratio of 0.45. However, as mentioned│
│ in the 10-Q report, revenue declined 15%...│
│                                            │
│ Reasoning:                                 │
│ ✅ Healthy debt-to-equity ratio: 0.45      │
│ ⚠️ Low profit margin: 5%                   │
│                                            │
│ Sources:                                   │
│ 🔗 10-Q.pdf (Chunk 2)                      │
│ 🔗 10-Q.pdf (Chunk 5)                      │
└────────────────────────────────────────────┘
```

---

## 🧪 How to Test

### Step 1: Upload a Document
```
1. Select a dataroom (or create new)
2. Upload a financial PDF (10-Q, earnings report, etc.)
3. Wait for processing to complete
```

**Check Backend Logs:**
```
✅ Indexed document doc-456 with 15 chunks + structured data
```

**Verify Index File Created:**
```powershell
ls D:\mna-agent\backend\pathway_index\
# Should show: {task_id}_index.json
```

### Step 2: Ask a Question
```
Type in chat: "What are the revenue trends?"
Send message
```

**Check Backend Logs:**
```
🧾 Structured data sent to CFO agent: {...}
✅ RAG found 3 relevant chunks
```

### Step 3: Verify Citations Appear
```
Look for "Sources:" section below the answer
Should show: 🔗 filename.pdf (Chunk X)
```

---

## 🎯 When Citations Appear

| Scenario | Citations? | Why? |
|----------|-----------|------|
| Document uploaded, question asked | ✅ YES | RAG finds relevant chunks |
| No document uploaded | ❌ NO | Nothing to search, citations=[] |
| Document uploaded but question unrelated | ⚠️ MAYBE | Depends if keywords match |
| RAG search fails | ❌ NO | Graceful fallback, citations=[] |

---

## 🔧 Technical Details

### Index Storage
- **Location**: `backend/pathway_index/{task_id}_index.json`
- **Format**: JSON array of chunk objects
- **Size**: ~100-500 KB per document (depending on length)

### Search Algorithm
- **Type**: Keyword-based (term frequency)
- **Process**: 
  1. Tokenize query into words
  2. Count occurrences in each chunk
  3. Score by total matches
  4. Return top 5
- **Future**: Can upgrade to semantic search with embeddings

### Chunking Strategy
- **Size**: 1000 characters per chunk
- **Overlap**: 200 characters between chunks
- **Boundary**: Tries to break at sentence endings (periods, newlines)
- **Result**: Typically 10-20 chunks per financial document

---

## 🎉 Summary

**Your RAG system is fully functional!** When you:
1. Upload a PDF → It gets indexed automatically
2. Ask a question → System searches indexed chunks
3. Get answer → Includes citations pointing to source chunks

The citations will show as **"filename.pdf (Chunk X)"** in the Sources section below each agent response.

**Fixed:** Frontend now correctly displays `citation.document` and `citation.page` (was using wrong field names `doc` and `Page {page}` before).
