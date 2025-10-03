# Pathway RAG with Gemini AI

A real-time RAG (Retrieval-Augmented Generation) pipeline using Pathway and Google's Gemini AI for processing JSON documents.

## Features

- 📄 **JSON Document Processing**: Automatically processes JSON files from a specified directory
- 🔄 **Real-Time Updates**: Automatically detects and indexes new/modified documents
- 🤖 **Gemini AI Integration**: Uses Google's Gemini for embeddings and chat responses
- ⚙️ **Configurable**: Easy configuration via `config.py` and `.env`
- 🚀 **REST API**: Query via HTTP endpoints

## Setup

### 1. Install Dependencies

```bash
cd rag
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Prepare Data Directory

Create a `data` folder and add your JSON files:

```bash
mkdir data
# Add your JSON files to the data folder
```

### 4. Configure Data Source (Optional)

Edit `config.py` to customize:

```python
# Change data source path
DATA_SOURCE_PATH = "./data/"  # Your JSON files directory

# Adjust retrieval settings
DEFAULT_RETRIEVAL_K = 3  # Number of documents to retrieve

# Change model settings
LLM_MODEL = "gemini-1.5-flash"  # Or "gemini-1.5-pro"
TEMPERATURE = 0.7
```

## Usage

### Start the RAG Server

```bash
python main.py
```

You should see:
```
✅ RAG Pipeline is running!
📡 Send queries to: http://0.0.0.0:8011
📁 Watching for changes in: ./data/
🤖 Using model: gemini-1.5-flash
```

### Send Queries

Using curl:
```bash
curl --data '{"messages": "What information is in the documents?"}' http://localhost:8011
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8011",
    json={"messages": "What are the key financial metrics?"}
)
print(response.json())
```

Using JavaScript/Fetch:
```javascript
fetch('http://localhost:8011', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({messages: 'Summarize the documents'})
})
.then(r => r.json())
.then(data => console.log(data));
```

## Configuration Options

### `config.py`

| Constant | Description | Default |
|----------|-------------|---------|
| `DATA_SOURCE_PATH` | Path to JSON files | `"./data/"` |
| `SERVER_HOST` | Server host | `"0.0.0.0"` |
| `SERVER_PORT` | Server port | `8011` |
| `DEFAULT_RETRIEVAL_K` | Documents to retrieve | `3` |
| `LLM_MODEL` | Gemini model | `"gemini-1.5-flash"` |
| `TEMPERATURE` | LLM temperature | `0.7` |
| `MAX_OUTPUT_TOKENS` | Max response tokens | `2048` |

### `.env`

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional: Switch to OpenAI (requires code modification)
# OPENAI_API_KEY=sk-...
```

## JSON Document Format

The pipeline supports various JSON structures:

### JSON Object
```json
{
  "company": "TechCorp",
  "revenue": "10M",
  "employees": 50
}
```

### JSON Array
```json
[
  {"deal": "Microsoft", "value": "5M"},
  {"deal": "Google", "value": "3M"}
]
```

### Nested JSON
```json
{
  "financials": {
    "2023": {"revenue": "10M", "profit": "2M"},
    "2024": {"revenue": "15M", "profit": "3M"}
  }
}
```

## Real-Time Updates

The pipeline automatically watches the data directory:
- **Add new files**: Automatically indexed
- **Modify files**: Index is updated
- **Delete files**: Removed from index

No restart needed! 🔥

## Switching to OpenAI

To use OpenAI instead of Gemini, modify `main.py`:

1. Replace `GeminiEmbedder` with:
```python
from pathway.xpacks.llm.embedders import OpenAIEmbedder
embedder = OpenAIEmbedder(api_key=os.environ["OPENAI_API_KEY"])
```

2. Replace `GeminiChat` with:
```python
model = llms.OpenAIChat(
    model="gpt-4o-mini",
    api_key=os.environ["OPENAI_API_KEY"],
)
```

3. Update `.env`:
```bash
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in the `rag` folder
- Check that the API key is correctly set in `.env`

### "No documents found"
- Verify JSON files exist in the `DATA_SOURCE_PATH` directory
- Check file permissions

### Port already in use
- Change `SERVER_PORT` in `config.py`
- Or kill the process using port 8011

## Architecture

```
JSON Files (data/) 
    ↓
Document Store (Pathway)
    ├─ JSON Parser
    ├─ Token Splitter
    └─ Gemini Embeddings
    ↓
Vector Index (BruteForce KNN)
    ↓
Query → Retrieval → Context
    ↓
Gemini Chat (Answer Generation)
    ↓
REST API Response
```

## Performance Tips

1. **Adjust chunk size**: Modify `MIN_TOKENS` and `MAX_TOKENS` in `config.py`
2. **Change retrieval count**: Adjust `DEFAULT_RETRIEVAL_K` (higher = more context, slower)
3. **Use faster model**: Switch to `gemini-1.5-flash` for speed
4. **Use better model**: Switch to `gemini-1.5-pro` for quality

## License

MIT
