# Installation & Setup Guide

Comprehensive guide for setting up RAG-NPU-Liquid on your AMD Ryzen AI Max+ 395 system.

---

## Prerequisites

### Hardware
- **Processor:** AMD Ryzen AI Max+ 395 (Strix Halo) with XDNA2 NPU (50 TOPS)
- **RAM:** 16GB minimum, 30GB+ recommended
- **Storage:** 5GB for models, dependencies, and vectorstore

### Software
- **OS:** Fedora 43+ or compatible Linux with XDNA driver support
- **Python:** 3.10 or later
- **FastFlowLM:** 0.9.40+ (pre-installed on your system)
- **NPU Drivers:** AMD Unified Driver (amdxdna) with `/dev/accel/accel0` accessible

### Verify Prerequisites

```bash
# Check Python version
python3 --version
# Expected: Python 3.10.x or later

# Check FastFlowLM
flm --version
# Expected: FastFlowLM version 0.9.40 or later

# Check NPU access
ls -la /dev/accel/accel0
# Expected: character device, readable by your user
```

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/RAG-NPU-Liquid.git
cd RAG-NPU-Liquid
```

### 2. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows/WSL2:
```bash
python3 -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# or
venv\Scripts\activate.bat      # Windows CMD
```

### 3. Install Dependencies

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt
```

**Expected installation time:** 2-5 minutes (first-time downloads ~500MB)

**Dependencies installed:**
- `langchain>=0.1,<0.2` — RAG orchestration (0.1.x for stability)
- `langchain-openai` — OpenAI-compatible API client
- `faiss-cpu` — Vector similarity search
- `sentence-transformers` — CPU-based embeddings (~100MB download)
- `pypdf` — PDF document loading
- `openai`, `huggingface-hub`, `tiktoken` — Supporting libraries

### 4. Verify Installation

```bash
# Check imports
python3 -c "from langchain.chains import RetrievalQA; print('✅ LangChain OK')"
python3 -c "from langchain.embeddings import HuggingFaceEmbeddings; print('✅ Embeddings OK')"
python3 -c "import faiss; print('✅ FAISS OK')"

# Check FastFlowLM connectivity
curl http://127.0.0.1:52625/v1/models 2>/dev/null | grep -q "lfm2" && echo "✅ FastFlowLM detected" || echo "⚠️ FastFlowLM not running"
```

---

## Configuration

All settings are in **`config.py`**. Review and customize as needed:

```python
# FastFlowLM endpoint (default: localhost port 52625)
FLM_BASE_URL = "http://127.0.0.1:52625/v1"
FLM_MODEL = "lfm2:1.2b"

# Context window (do not change unless you modify FastFlowLM serve command)
MAX_CONTEXT_TOKENS = 32000

# Chunking (optimized for embedding model's 256-token window)
CHUNK_SIZE = 900           # characters (~225 tokens)
CHUNK_OVERLAP = 100
RETRIEVAL_K = 12           # retrieve top-12 chunks

# Generation
NUM_PREDICT = 2048         # max output tokens
TEMPERATURE = 0.1          # low temp for factual answers

# Paths
DOCS_DIR = "./docs"        # where to place your documents
VECTORSTORE_PATH = "./vectorstore/faiss_index"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

**For remote deployment,** update `FLM_BASE_URL`:
```python
FLM_BASE_URL = "http://192.168.1.100:52625/v1"  # Replace with your Z13 IP
```

---

## Running the Pipeline

### Step 1: Start FastFlowLM (Terminal 1)

```bash
# In any directory, activate venv if needed
source venv/bin/activate
flm serve lfm2:1.2b
```

**Expected output:**
```
🚀 Initializing FastFlowLM 0.9.40...
📍 Loading lfm2:1.2b onto /dev/accel/accel0...
✅ Model loaded successfully
🔗 Listening on http://127.0.0.1:52625
```

**Verify in another terminal:**
```bash
curl http://127.0.0.1:52625/v1/models
# Expected: {"object":"list","data":[{"id":"lfm2:1.2b",...}]}
```

### Step 2: Add Your Documents (Terminal 2)

```bash
cd RAG-NPU-Liquid
source venv/bin/activate

# Create docs directory if it doesn't exist
mkdir -p docs

# Add documents (supports .txt, .pdf, .md)
cp ~/my_document.pdf docs/
cp ~/notes.txt docs/
# ... add more documents
```

### Step 3: Ingest Documents

```bash
python ingest.py
```

**Expected output:**
```
📂 Loading documents from ./docs/...
  ✓ Found 2 *.txt document(s)
  ✓ Found 1 *.pdf document(s)
✓ Total documents loaded: 3
✂️  Splitting documents (chunk_size=900, overlap=100)...
✓ Created 12 chunks
🧠 Creating embeddings (sentence-transformers/all-MiniLM-L6-v2)...
Loading weights: 100%|██████████| 103/103 [00:02<00:00, 45.2it/s]
💾 Saving FAISS index to ./vectorstore/faiss_index...
✓ Index saved: ./vectorstore/faiss_index

✅ Ingestion complete!
  Documents: 3
  Chunks: 12
  Embedding model: sentence-transformers/all-MiniLM-L6-v2
```

### Step 4: Run Tests

```bash
python test_rag.py
```

**Expected output:**
```
🧪 RAG Pipeline End-to-End Test Suite
================================================================================

[SETUP] Creating sample documents...
✓ Created moon.txt
✓ Created mars.txt
✓ Sample documents ready

[TEST 1] Document Ingestion ... ✅ PASS
[TEST 2] Query Engine & FastFlowLM Connection ... ✅ PASS
[TEST 3] Answerable Query (Moon) ... ✅ PASS
[TEST 4] Cross-Document Query (Moon vs Mars) ... ✅ PASS
[TEST 5] Out-of-Scope Query (Venus) ... ✅ PASS

================================================================================
📊 Test Results Summary
================================================================================
Total: 5 PASS, 0 FAIL, 0 SKIP

✅ All tests passed!
```

### Step 5: Start Querying (Terminal 3)

```bash
cd RAG-NPU-Liquid
source venv/bin/activate
python rag_query.py
```

**Interactive CLI:**
```
================================================================================
🚀 RAG Pipeline - FastFlowLM + FAISS
================================================================================
LLM: lfm2:1.2b @ http://127.0.0.1:52625/v1
Max context: 32000 tokens
Retrieval: top-12 chunks
Vectorstore: ./vectorstore/faiss_index
================================================================================
✅ FastFlowLM is running
✅ RAG pipeline ready

Enter your question (or 'quit' to exit): What is the largest volcano on Mars?
🔍 Retrieving context and generating answer...

✅ Answer:
The largest volcano on Mars is Olympus Mons, which stands about 21 kilometers high...

📄 Sources (12 chunks retrieved):
--- Source 1 ---
Olympus Mons is a shield volcano on Mars. It is the largest volcano in the solar...
```

Type `quit`, `exit`, or `q` to exit.

---

## Troubleshooting

### Issue: "Cannot connect to FastFlowLM at 127.0.0.1:52625"

**Solution:** Ensure FastFlowLM is running in a separate terminal:
```bash
flm serve lfm2:1.2b
```

Also check:
```bash
curl http://127.0.0.1:52625/v1/models
# If this fails, FastFlowLM is not running
```

---

### Issue: "FAISS index not found at ./vectorstore/faiss_index"

**Solution:** Run ingestion first:
```bash
python ingest.py
```

Ensure you have documents in `./docs/`:
```bash
ls docs/
# Should list your .txt, .pdf, or .md files
```

---

### Issue: "No documents found in ./docs/"

**Solution:** Add documents to the `docs/` directory:
```bash
mkdir -p docs
echo "This is my document content..." > docs/sample.txt
python ingest.py
```

---

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution:** Activate virtual environment and reinstall:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue: "Embeddings are slow on first run"

**Normal behavior.** The first run downloads the embedding model (~100MB):
```
Loading weights:   0%|          | 0/103 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 103/103 [00:02<00:00, 45.2it/s]
```

Subsequent runs use the cached model and are much faster (< 1 second).

---

### Issue: "GPU is not at 0% during inference"

**Verify FastFlowLM is using NPU, not GPU:**
```bash
# Check during inference
watch -n 0.1 "rocm-smi --showuse"  # Should show GPU at 0%

# Check FastFlowLM logs
# FastFlowLM should print: "Loaded on /dev/accel/accel0"
```

If GPU is high, FastFlowLM may have fallen back to GPU. Check:
1. NPU drivers are installed (`ls -la /dev/accel/accel0`)
2. Your user has permission to `/dev/accel/accel0`
3. FastFlowLM version is 0.9.40+ with NPU support

---

## Performance Optimization

### Faster Startup (Skip Embedding Model Cache)
```bash
# Embedding model is cached in ~/.cache/huggingface/
# To force re-download on next run:
rm -rf ~/.cache/huggingface/sentence-transformers/
python ingest.py  # Will re-download
```

### Reduce Memory Footprint
```python
# In config.py, reduce retrieval_k:
RETRIEVAL_K = 6  # Instead of 12, fewer chunks = less context
```

### Faster Ingestion for Large Datasets
Chunk size optimization doesn't apply here, but you can:
```bash
# Process documents in batches
# Ingest subset1, then subset2, then merge indices
```

---

## Deployment to Remote Machine

### From WSL2/Local Machine

```bash
# Deploy to remote Z13 machine (replace <remote-ip> with your machine's IP)
scp -r ~/RAG-NPU-Liquid user@<remote-ip>:~/
ssh user@<remote-ip> 'cd ~/RAG-NPU-Liquid && bash setup.sh'

# Then on remote machine
ssh user@<remote-ip>
cd ~/RAG-NPU-Liquid
source venv/bin/activate
flm serve lfm2:1.2b  # Terminal 1
python ingest.py      # Terminal 2
python rag_query.py   # Terminal 3
```

**Example:**
```bash
scp -r ~/RAG-NPU-Liquid user@192.168.1.100:~/
ssh user@192.168.1.100 'cd ~/RAG-NPU-Liquid && bash setup.sh'
```

### Update config.py for Remote

```python
# config.py on remote machine
FLM_BASE_URL = "http://127.0.0.1:52625/v1"  # Local to remote machine (127.0.0.1 = localhost on that machine)
```

---

## Next Steps

- **[README.md](./README.md)** — Project overview and quick start
- **[BENCHMARKS.md](./BENCHMARKS.md)** — Performance data
- **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** — Deployment history
- **[TECHNICAL_JOURNEY.md](./TECHNICAL_JOURNEY.md)** — Issues overcome
- **[config.py](./config.py)** — All configurable parameters

---

## Support

For issues not covered above, check:
1. **[TECHNICAL_JOURNEY.md](./TECHNICAL_JOURNEY.md)** — Common challenges and solutions
2. **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** — Known limitations and workarounds
3. **GitHub Issues** — Search for your problem

---

*Last updated: 2026-05-28*
