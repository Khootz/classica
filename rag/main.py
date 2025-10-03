"""
Pathway RAG Pipeline with Gemini AI
Processes JSON documents and provides real-time question answering.
"""

import pathway as pw
from pathway.stdlib.indexing.nearest_neighbors import BruteForceKnnFactory
from pathway.xpacks.llm import llms
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.parsers import ParseUnstructured
from pathway.xpacks.llm.splitters import TokenCountSplitter
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Import configuration
from config import (
    DATA_SOURCE_PATH,
    DATA_FORMAT,
    SERVER_HOST,
    SERVER_PORT,
    DEFAULT_RETRIEVAL_K,
    MIN_TOKENS,
    MAX_TOKENS,
    ENCODING_NAME,
    LLM_MODEL,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    AUTOCOMMIT_DURATION_MS,
    DELETE_COMPLETED_QUERIES,
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# Custom Gemini Embedder
class GeminiEmbedder(pw.UDF):
    """Custom embedder using Google's Gemini embedding model"""

    def __init__(self):
        super().__init__()
        self.model_name = "models/embedding-001"

    def __wrapped__(self, txt: str) -> list[float]:
        result = genai.embed_content(
            model=self.model_name,
            content=txt,
            task_type="retrieval_document",
        )
        return result["embedding"]


# Custom Gemini Chat Model
class GeminiChat(pw.UDF):
    """Custom chat model using Google's Gemini"""

    def __init__(self, model_name: str = LLM_MODEL, temperature: float = TEMPERATURE):
        super().__init__()
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

    def __wrapped__(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
        )
        return response.text


# JSON Parser for Pathway
class JSONParser(pw.UDF):
    """Parse JSON files and extract text content"""

    def __wrapped__(self, contents: bytes) -> list[tuple[str, dict]]:
        import json

        try:
            data = json.loads(contents.decode("utf-8"))
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # Convert dict to readable text
                text = json.dumps(data, indent=2)
                metadata = {"type": "json_object"}
                return [(text, metadata)]
            elif isinstance(data, list):
                # Process each item in the list
                results = []
                for idx, item in enumerate(data):
                    text = json.dumps(item, indent=2)
                    metadata = {"type": "json_array_item", "index": idx}
                    results.append((text, metadata))
                return results
            else:
                # Fallback for primitive types
                text = str(data)
                metadata = {"type": "json_primitive"}
                return [(text, metadata)]
        except json.JSONDecodeError as e:
            # Return error info if JSON is invalid
            error_text = f"Invalid JSON: {str(e)}"
            metadata = {"type": "error", "error": str(e)}
            return [(error_text, metadata)]


# Document Indexing
print(f"Loading documents from: {DATA_SOURCE_PATH}")

documents = pw.io.fs.read(
    DATA_SOURCE_PATH,
    format="binary",
    with_metadata=True,
)

# Set up text splitter
text_splitter = TokenCountSplitter(
    min_tokens=MIN_TOKENS,
    max_tokens=MAX_TOKENS,
    encoding_name=ENCODING_NAME,
)

# Set up embedder
embedder = GeminiEmbedder()

# Set up retriever
retriever_factory = BruteForceKnnFactory(
    embedder=embedder,
)

# Set up JSON parser
parser = JSONParser()

# Create document store
print("Creating document store...")
document_store = DocumentStore(
    docs=documents,
    retriever_factory=retriever_factory,
    parser=parser,
    splitter=text_splitter,
)

# User Queries Setup
print(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")

webserver = pw.io.http.PathwayWebserver(host=SERVER_HOST, port=SERVER_PORT)


class QuerySchema(pw.Schema):
    messages: str


queries, writer = pw.io.http.rest_connector(
    webserver=webserver,
    schema=QuerySchema,
    autocommit_duration_ms=AUTOCOMMIT_DURATION_MS,
    delete_completed_queries=DELETE_COMPLETED_QUERIES,
)

# Format queries for document retrieval
queries = queries.select(
    query=pw.this.messages,
    k=DEFAULT_RETRIEVAL_K,
    metadata_filter=None,
    filepath_globpattern=None,
)

# Document Retrieval
retrieved_documents = document_store.retrieve_query(queries)
retrieved_documents = retrieved_documents.select(docs=pw.this.result)

# Combine queries with retrieved documents
queries_context = queries + retrieved_documents


# Build Context and Prompt
def get_context(documents):
    """Extract text content from retrieved documents"""
    content_list = []
    for doc in documents:
        content_list.append(str(doc["text"]))
    return "\n\n".join(content_list)


@pw.udf
def build_prompts_udf(documents, query) -> str:
    """Build prompt with context and query"""
    context = get_context(documents)
    prompt = f"""You are a helpful AI assistant analyzing financial and business documents.

Context (Retrieved Documents):
{context}

Question: {query}

Please provide a detailed and accurate answer based on the context provided. If the context doesn't contain enough information to answer the question, please state that clearly."""
    return prompt


prompts = queries_context + queries_context.select(
    prompts=build_prompts_udf(pw.this.docs, pw.this.query)
)

# Define Gemini Model
model = GeminiChat(model_name=LLM_MODEL, temperature=TEMPERATURE)

# Generate Answers
responses = prompts.select(
    *pw.this.without(pw.this.query, pw.this.prompts, pw.this.docs),
    result=model(pw.this.prompts),
)

# Return Answers
writer(responses)

# Run the Pipeline
print("✅ RAG Pipeline is running!")
print(f"📡 Send queries to: http://{SERVER_HOST}:{SERVER_PORT}")
print(f"📁 Watching for changes in: {DATA_SOURCE_PATH}")
print(f"🤖 Using model: {LLM_MODEL}")
print("\nExample query:")
print(f'curl --data \'{{"messages": "What information is in the documents?"}}\' http://localhost:{SERVER_PORT}')
print("\nPress Ctrl+C to stop...")

pw.run()
