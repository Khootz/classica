# Classica - AI-Powered M&A Due Diligence Assistant

**Intelligent document analysis and financial extraction for deal teams**

Classica helps analysts extract structured financial data from M&A documents, perform semantic search across datarooms, and generate AI-powered insights with full citations.

🔗 **Live Demo**: [Coming Soon]

---

## ✨ Features

- 📊 **39-Field Financial Extraction** - Revenue, EBITDA, debt, margins, ratios
- 🔍 **Hybrid RAG Search** - Semantic + keyword search across documents
- 💬 **AI Chat Interface** - Ask questions, get cited answers
- 📄 **PDF Analysis** - Upload 10-Qs, CIMs, financial statements
- 📈 **Auto-computed Metrics** - D/E ratio, net margin, ROE, coverage ratios
- 📋 **Investment Memo Export** - Generate summary reports

---

## 🚀 Quick Start

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for deployment instructions.

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLModel, SQLite
- **AI**: OpenRouter API, LandingAI Document Extraction
- **Deployment**: Vercel (Frontend), Render (Backend)

---

## 📄 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss changes.

---

## ⚠️ Disclaimer

This tool assists analysts but does not replace human judgment or comprehensive due diligence. Always verify AI-generated insights against source documents.
