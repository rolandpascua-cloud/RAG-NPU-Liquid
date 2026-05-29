# RAG-NPU-Liquid

A production-ready Retrieval-Augmented Generation (RAG) pipeline running entirely on the **AMD Ryzen AI Max+ 395 (Strix Halo) XDNA2 NPU** using FastFlowLM and the lfm2:1.2b model.

**Hardware Target:** ASUS ROG Flow Z13 (Fedora 43) — GPU held at 0%, inference on `/dev/accel/accel0` only.

## 🎯 Key Features

- **Local NPU Inference:** lfm2:1.2b on XDNA2 NPU via FastFlowLM (16.68s TTFT, 37.88 tok/s at 32k context)
- **Full 32k Context Window:** Hardcoded to use the complete 32,000-token context window
- **Privacy-First:** All processing local — no cloud APIs, no data leakage
- **Offline:** Works without internet connection
- **Efficient Chunking:** 900-char chunks with 12-document retrieval (optimized for embedding model's 256-token window)
- **Local Embeddings:** sentence-transformers/all-MiniLM-L6-v2 (CPU only)
- **Vector Store:** FAISS for fast similarity search
- **OpenAI-Compatible API:** FastFlowLM exposes standard `/v1` endpoints

## 📋 Prerequisites

- **Hardware:** AMD Ryzen AI Max+ 395 (Strix Halo) with XDNA2 NPU
- **OS:** Fedora 43 (or compatible Linux with XDNA driver)
- **Python:** 3.10+ (system Python fine)
- **FastFlowLM:** v0.9.40+ (already installed and working)
- **NPU Drivers:** AMD Unified Driver (amdxdna) — `/dev/accel/accel0` must exist and be accessible

## 📖 Documentation

- **[BENCHMARKS.md](./BENCHMARKS.md)** — Full performance data for lfm2:1.2b across all context lengths
- **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** — Deployment history, test results, and verified behavior
- **[config.py](./config.py)** — Central configuration (all parameters documented)

## 🚀 Quick Start

### 1. Setup (one-time)

```bash
cd RAG-NPU-Liquid  # Navigate to the project directory
bash setup.sh
```

This creates a Python venv and installs all dependencies.

### 2. Start FastFlowLM (in a separate terminal)

```bash
flm serve lfm2:1.2b
```

Verify it's running:
```bash
curl http://127.0.0.1:52625/v1/models
```

### 3. Add Your Documents

Place `.txt`, `.pdf`, or `.md` files in the `./docs/` directory:

```bash
# Example
cp ~/my_paper.pdf ./docs/
cp ~/notes.txt ./docs/
```

### 4. Ingest & Index

```bash
python ingest.py
```

This chunks documents, embeds them with sentence-transformers, and saves a FAISS index.
Expected output:
```
📂 Loading documents from ./docs/...
  ✓ Found 2 *.txt document(s)
✓ Total documents loaded: 2
✂️  Splitting documents (chunk_size=900, overlap=100)...
✓ Created 2 chunks
🧠 Creating embeddings (sentence-transformers/all-MiniLM-L6-v2)...
💾 Saving FAISS index to ./vectorstore/faiss_index...
✓ Index saved: ./vectorstore/faiss_index
✅ Ingestion complete!
```

### 5. Test the Pipeline

```bash
python test_rag.py
```

This runs 5 end-to-end tests:
1. Document ingestion ✅
2. FastFlowLM connection ✅
3. Answerable query ✅
4. Cross-document retrieval ✅
5. Out-of-scope fallback ✅

Expected output:
```
🧪 RAG Pipeline End-to-End Test Suite
...
📊 Test Results Summary
✅ Ingestion: PASS
✅ Query Engine: PASS
✅ Answerable Query: PASS
✅ Cross-Document Query: PASS
✅ Out-of-Scope Query: PASS
```

### 6. Start Interactive Querying

```bash
python rag_query.py
```

Then ask questions:
```
Enter your question (or 'quit' to exit): What does the Moon orbit?
🔍 Retrieving context and generating answer...
✅ Answer:
The Moon orbits the Earth every 27.3 days.

📄 Sources (12 chunks retrieved):
--- Source 1 ---
The Moon is Earth's only natural satellite. It orbits the Earth every 27.3 days...
```

## 📁 Project Structure

```
RAG-NPU-Liquid/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── setup.sh               # One-time setup script
├── config.py              # Configuration (single source of truth)
├── ingest.py              # Document ingestion + embedding
├── rag_query.py           # Interactive RAG query interface
├── test_rag.py            # End-to-end test suite
├── docs/                  # Your documents (create if missing)
│   ├── sample_moon.txt
│   ├── sample_mars.txt
│   └── (add your files here)
└── vectorstore/           # FAISS index (auto-created)
    └── faiss_index/
```

## ⚙️ Configuration

All settings are in `config.py`. Key parameters:

```python
# FastFlowLM endpoint
FLM_BASE_URL = "http://127.0.0.1:52625/v1"
FLM_MODEL = "lfm2:1.2b"
MAX_CONTEXT_TOKENS = 32000     # hardcoded — never change this

# Chunking (optimized for embedding model's 256-token window)
CHUNK_SIZE = 900               # chars (~225 tokens) — fits embedding model
CHUNK_OVERLAP = 100
RETRIEVAL_K = 12               # retrieve top-12 chunks (~4.5k context tokens)

# Generation
NUM_PREDICT = 2048             # output cap
TEMPERATURE = 0.1              # low temp for factual answers

# Paths
DOCS_DIR = "./docs"
VECTORSTORE_PATH = "./vectorstore/faiss_index"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

To change a setting, edit `config.py` then re-run `python ingest.py` if you changed chunk parameters.

**Note:** The 900-char chunk size is carefully tuned to avoid truncation by the embedding model's 256-token window. Larger chunks are silently truncated (~40% information loss). See [BENCHMARKS.md](./BENCHMARKS.md) for performance details.

## 🔍 How It Works

1. **Ingest** (`ingest.py`):
   - Load documents from `./docs/`
   - Split into 900-char chunks (900 chars ≈ 225 tokens, within embedding model's 256-token window)
   - Embed each chunk with sentence-transformers (1-pass, CPU-only)
   - Save FAISS index to `./vectorstore/faiss_index`

2. **Query** (`rag_query.py`):
   - Load FAISS index + embeddings
   - Embed user query with sentence-transformers
   - Retrieve top-12 most similar chunks
   - Build prompt with retrieved context
   - Send to FastFlowLM's `/v1/chat/completions` endpoint
   - Return answer + source documents

3. **Inference on NPU**:
   - FastFlowLM's serve command loads lfm2:1.2b onto `/dev/accel/accel0`
   - All inference happens on NPU (GPU at 0%)
   - Max context: 32,000 tokens (hardcoded)
   - Latency: ~16.7s time-to-first-token, then ~38 tok/s decode speed

## 📊 Performance Benchmarks

**Hardware:** ASUS ROG Flow Z13, Ryzen AI Max+ 395 (XDNA2), 30GB RAM

**Model:** lfm2:1.2b (1.2B params, ~0.9GB model size)

| Metric | Value |
|---|---|
| Model Size | ~0.9GB |
| Time-to-First-Token (32k context) | 16.68s |
| Decode Speed (32k context) | 37.88 tok/s |
| Decode Speed (1k context) | 60.37 tok/s |
| Memory (model + KV cache @ 32k) | <10GB |
| Max Context Window | 32,000 tokens |
| Device | /dev/accel/accel0 (XDNA2 NPU) |
| GPU Utilization | 0% |
| CPU (orchestration only) | ~0-18% |
| End-to-End Query Latency | 0.7-1.0s (including retrieval + embedding) |

**Full benchmark data:** See [BENCHMARKS.md](./BENCHMARKS.md) for complete latency/throughput across all context lengths and comparison with other models.

## 🛠️ Troubleshooting

### "Cannot connect to FastFlowLM at 127.0.0.1:52625"
**Fix:** Start FastFlowLM in a separate terminal:
```bash
flm serve lfm2:1.2b
```

### "FAISS index not found"
**Fix:** Run ingestion first:
```bash
python ingest.py
```

### "No documents found in ./docs/"
**Fix:** Add some `.txt`, `.pdf`, or `.md` files to the `./docs/` directory:
```bash
echo "My document content..." > ./docs/mydoc.txt
python ingest.py
```

### "ModuleNotFoundError: No module named 'langchain'"
**Fix:** Activate the venv and reinstall:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Embeddings are slow on first run"
Normal — sentence-transformers downloads the model on first use (~100MB download). Subsequent runs are fast (cached locally).

## 🔗 Coexisting Services on Z13

- **FastFlowLM** (NPU, port 52625) — this project
- **Lemonade Server** (GPU/ROCm, port 13305) — separate inference path

They don't interfere. For NPU-only inference, use FastFlowLM. For GPU inference (e.g., larger models), use Lemonade.

## 📝 Example Workflow

```bash
# 1. One-time setup
bash setup.sh

# 2. Add a document
echo "The Arctic is the northernmost region of Earth..." > ./docs/arctic.txt

# 3. Ingest
python ingest.py

# 4. Test
python test_rag.py

# 5. Query (make sure flm serve is running in another terminal)
python rag_query.py

# Sample interaction:
# Enter your question: What is the Arctic?
# ✅ Answer: The Arctic is the northernmost region of Earth...
```

## 🧪 Test Status

**Status:** ✅ **ALL TESTS PASSING**

```
✅ Ingestion: PASS
✅ Query Engine: PASS
✅ Answerable Query: PASS
✅ Cross-Document Query: PASS
✅ Out-of-Scope Query: PASS
```

Run tests with: `python test_rag.py`

Full test history and deployment log: [DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)

## 📚 References

- **FastFlowLM:** https://github.com/FastFlowLM/FastFlowLM
- **LangChain:** https://python.langchain.com/
- **Sentence Transformers:** https://www.sbert.net/
- **FAISS:** https://github.com/facebookresearch/faiss
- **AMD Ryzen AI:** https://www.amd.com/en/products/specifications/processors/ryzen/ryzen-ai/asus-rog-flow-z13-gz302ea

## 📄 License

This project is provided as-is for experimental and educational use. Follow FastFlowLM's license terms.

---

**Ready to build?** Start with `bash setup.sh`. Questions? Check:
- **[BENCHMARKS.md](./BENCHMARKS.md)** — Performance data
- **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** — Deployment history & test results
- **Troubleshooting section** (above)
- **[config.py](./config.py)** — Tunable parameters
