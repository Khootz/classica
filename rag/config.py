"""
Configuration constants for the RAG pipeline.
Modify these values to customize the RAG behavior.
"""

# Data Source Configuration
DATA_SOURCE_PATH = "./data/"  # Change this to your JSON files directory
DATA_FORMAT = "json"  # Format of source files

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8011

# Retrieval Configuration
DEFAULT_RETRIEVAL_K = 3  # Number of documents to retrieve per query

# Chunking Configuration
MIN_TOKENS = 100
MAX_TOKENS = 500
ENCODING_NAME = "cl100k_base"

# Embedding Model Configuration
EMBEDDING_MODEL = "models/embedding-001"  # Gemini embedding model

# LLM Configuration
LLM_MODEL = "gemini-1.5-flash"  # Gemini model for chat
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 2048

# Autocommit Configuration
AUTOCOMMIT_DURATION_MS = 50
DELETE_COMPLETED_QUERIES = False
