"""RAG Pipeline Configuration - Single Source of Truth for all constants."""

# FastFlowLM Configuration
FLM_BASE_URL = "http://127.0.0.1:52625/v1"
FLM_MODEL = "lfm2:1.2b"
MAX_CONTEXT_TOKENS = 32000
NUM_PREDICT = 2048
TEMPERATURE = 0.1

# Chunking Strategy
# all-MiniLM-L6-v2 truncates at 256 tokens (~800-900 chars). Keeping chunks at
# 900 chars ensures the full chunk is embedded. With 32k LLM context and k=12,
# that's ~10,800 chars of retrieved context — well within the lfm2:1.2b window.
CHUNK_SIZE = 900
CHUNK_OVERLAP = 100
RETRIEVAL_K = 12

# Storage Paths
VECTORSTORE_PATH = "./vectorstore/faiss_index"
DOCS_DIR = "./docs"

# Embeddings Model
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# FastFlowLM Serve Command (run in separate terminal before querying)
FLM_SERVE_CMD = "flm serve lfm2:1.2b"

# Prompt Template for RAG
RAG_PROMPT_TEMPLATE = """You are a helpful assistant. Answer ONLY using the context provided below.
If the answer is not in the context, say "I don't have enough information to answer that."
Do not make up facts.

Context:
{context}

Question: {question}

Answer:"""
