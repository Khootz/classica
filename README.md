# Diligent 🔍

**AI-Powered Financial Document Analysis Assistant**

Diligent extracts structured financial data from PDFs, computes key metrics, and generates AI-powered summaries. Built for financial analysts and deal teams who need quick insights from financial documents.

> **Important:** This tool assists analysts—it does not replace human judgment or comprehensive due diligence. Always verify outputs with source documents.

---

## What This Actually Does

**Document Processing:**
- Uploads PDF files to the system
- Uses LandingAI ADE to parse PDFs and extract 8 structured fields: Company Name, Revenue, Total Debt, Equity, Cash Flow, Net Income, EBITDA, Operating Income
- Stores extracted data and markdown conversion in SQLite database

**Financial Analysis:**
- Pathway normalizes extracted data and computes 5 financial ratios:
  - Debt-to-Equity ratio
  - Debt-to-Revenue ratio
  - Net Margin (%)
  - Return on Equity (ROE %)
  - Cash Flow to Debt coverage
- Generates rule-based insights (leverage warnings, profitability flags, liquidity alerts)

**AI Chat Interface:**
- Ask questions about uploaded documents
- Gemini AI generates natural language summaries from structured metrics
- Returns reasoning steps showing which rules triggered
- **Note:** No citation tracking to specific pages/tables—responses are based on aggregated structured data

**Memo Export:**
- Creates a PDF memo with executive summary and key metrics
- Exports to local file system (no cloud storage)

---

## What This Does NOT Do

- **No RAG or vector search** – Does not retrieve specific clauses, facts, or text snippets from documents
- **No multi-document summarization** – Cannot synthesize insights across multiple PDFs
- **No contract analysis** – Cannot extract clauses, change-of-control provisions, or legal terms
- **No patent/CIM/pitch deck parsing** – Only extracts the 8 predefined financial fields listed above
- **No citations** – Cannot point to specific pages, tables, or text spans in source documents
- **No VDR integration** – Does not connect to enterprise document management systems
- **No watched folders** – Must manually upload files through the web UI

---

## Actual Use Cases (Limited Scope)

1. **Quick financial extraction from 10-Ks/10-Qs** – If the document contains the 8 fields in extractable format
2. **Leverage and liquidity screening** – Rule-based flags for debt ratios and cash flow coverage
3. **Batch processing** – Upload multiple financial PDFs to one dataroom, get aggregated metrics
4. **Export summary memos** – Generate PDF reports with extracted metrics

**Not suitable for:** Contract review, patent analysis, comprehensive due diligence, or any task requiring retrieval of specific text from documents.

---

## Tech Stack

**Frontend:**
- Next.js 15 + React 19 + TypeScript
- Tailwind CSS + Radix UI

**Backend:**
- FastAPI + SQLModel (SQLite)
- LandingAI ADE for PDF parsing and field extraction
- Pathway for data normalization and ratio computation
- Google Gemini AI (`gemini-2.5-flash`) for natural language summaries
- ReportLab for PDF export

**No embeddings, no vector database, no retrieval system.**

---

## Architecture & Data Flow

1. **Upload:** User uploads PDF via frontend
2. **Parse:** Backend sends PDF to LandingAI ADE → Returns markdown + JSON with 8 fields
3. **Normalize:** Pathway ingests ADE JSON, handles missing values, computes 5 ratios
4. **Analyze:** Finance logic applies threshold rules → Generates insight strings (⚠️/✅)
5. **Chat:** User asks question → Gemini receives structured metrics + insights → Returns summary
6. **Store:** All data saved to SQLite (`Document`, `ChatMessage`, `Memo` tables)
7. **Export:** ReportLab generates PDF from memo text and metrics JSON

**Key limitation:** No indexing of document text. Cannot answer "Where does it say X?" or "Show me the clause about Y."

---

## Models & APIs Used

| Service | Purpose | Cost |
|---------|---------|------|
| **LandingAI ADE** | PDF → Markdown + structured field extraction | Pay-per-document |
| **Google Gemini AI** | Natural language summary generation | Free tier: 15 req/min |
| **Pathway** | Data normalization and metric computation | Free (local library) |

**Disclaimer:** AI-generated summaries may be inaccurate. Always verify with source documents. No citations are provided to trace answers back to specific content.

---

## Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- API keys: [Google Gemini](https://makersuite.google.com/app/apikey) and [LandingAI](https://landing.ai/)

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
LANDINGAI_API_KEY=your_landingai_api_key
```

Run backend:
```bash
uvicorn main:app --reload --port 8000
```

Backend: `http://localhost:8000` | API docs: `http://localhost:8000/docs`

---

### Frontend Setup

```bash
cd frontend
pnpm install  # or npm install
pnpm dev      # or npm run dev
```

Frontend: `http://localhost:3000`

---

## How to Use

1. **Create Dataroom** – Click "New Dataroom" in sidebar
2. **Upload PDF** – Must contain at least Revenue, Debt, and Equity fields
3. **View Insights** – Red flags popup shows leverage/liquidity warnings
4. **Ask Questions** – Type in chat (e.g., "What's the debt-to-equity ratio?")
5. **Export Memo** – Click "View Summary" → "Export to PDF"

**Limitations:**
- If ADE cannot extract the required fields, metrics will be zero
- Chat answers are based on aggregated metrics only, not document content
- No way to verify which part of the document the data came from

---

## Project Structure

```
backend/
  ├── main.py              # FastAPI app
  ├── database.py          # SQLite setup
  ├── models.py            # Task, Document, ChatMessage, Memo schemas
  ├── routes/
  │   ├── tasks.py         # Dataroom CRUD
  │   ├── documents.py     # Upload → ADE → Pathway pipeline
  │   ├── chat.py          # Gemini chat with structured metrics
  │   └── memo.py          # PDF export
  └── services/
      ├── landing_ai.py    # ADE API client
      ├── pathway_client.py # Data normalization + ratio computation
      ├── finance_logic.py  # Rule-based insight generation
      └── gemini_client.py  # Gemini API wrapper

frontend/
  ├── app/                 # Next.js pages
  ├── components/          # React components
  │   ├── chat-interface.tsx
  │   ├── dataroom-sidebar.tsx
  │   └── upload-modal.tsx
  └── lib/api.ts           # API client
```

---

## Known Issues & Limitations

1. **No retrieval system** – Cannot answer questions about specific clauses, facts, or details from documents
2. **No citations** – Impossible to verify where extracted data came from in the PDF
3. **Limited field extraction** – Only 8 hardcoded fields; cannot extract custom fields
4. **No multi-doc synthesis** – Each document processed independently; no cross-document analysis
5. **No audit trail** – Cannot track which user made which changes or reviewed which flags
6. **No human-in-the-loop** – No review queue for accepting/dismissing red flags
7. **Local-only exports** – PDFs saved to local file system, not cloud storage

---

## License

MIT License



---

## Troubleshooting

**`ModuleNotFoundError`** → Activate venv: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux), then `pip install -r requirements.txt`

**`Invalid API key`** → Check `backend/.env` has valid `GEMINI_API_KEY` and `LANDINGAI_API_KEY`

**Database errors** → Delete `backend/db/app.db` and restart backend

**Frontend errors** → Run `pnpm install` again, ensure backend is running on port 8000

**Zero metrics returned** → ADE could not extract the required fields from your PDF. Try a different document format or check ADE compatibility.

---

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env` in `backend/`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
LANDINGAI_API_KEY=your_landingai_api_key_here
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

---

### Frontend Setup

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend runs at `http://localhost:3000`.

---

## How to Demo

1. Create a new dataroom
2. Upload 5 sample files (10-Q, CIM, contract, pitch deck, patent)
3. Ask: *"What are the key financial risks?"*
4. Drop in a new file mid-demo
5. Ask a follow-up that depends on the new file: *"Does the new contract have change-of-control provisions?"*
6. Export the IC memo to PDF

---

## Troubleshooting

**`ModuleNotFoundError`** → Activate venv: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux), then `pip install -r requirements.txt`

**`Invalid API key`** → Check `backend/.env` has valid `GEMINI_API_KEY` and `LANDINGAI_API_KEY`

**Database errors** → Delete `backend/db/app.db` and restart backend

**Frontend errors** → Run `pnpm install` again, ensure backend is running on port 8000

**Zero metrics returned** → ADE could not extract the required fields from your PDF. Try a different document format or check ADE compatibility.

---

## License

MIT License