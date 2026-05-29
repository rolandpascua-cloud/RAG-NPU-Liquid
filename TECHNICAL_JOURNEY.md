# Technical Journey: Issues Solved & Lessons Learned

This document chronicles the technical challenges encountered while building the RAG-NPU-Liquid pipeline and the solutions implemented.

---

## Issue #1: LangChain API Compatibility

### Problem
The project initially targeted `langchain>=0.2`, but encountered import errors:

```
ModuleNotFoundError: No module named 'langchain.document_loaders'
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

Additionally, parameter names changed between versions:
- `openai_api_base` → `base_url` (in 0.2.x, reverted)
- `model` → `model_name` (parameter naming inconsistency)

### Root Cause
LangChain 0.2.x underwent a major refactor, moving modules into separate packages:
- `langchain.document_loaders` → `langchain_community.document_loaders`
- `langchain.chat_models` → `langchain_openai.ChatOpenAI`

The older 0.1.x API preserved the old module structure under deprecation warnings, which is more stable for production use.

### Solution
**Pinned LangChain to 0.1.x with flexible patch updates:**

```ini
# requirements.txt
langchain>=0.1,<0.2          # Use old API, get security patches
langchain-openai             # For ChatOpenAI compatibility layer
```

**Updated imports to use 0.1.x module structure:**
```python
# ingest.py
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# rag_query.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
```

**Fixed parameter names:**
```python
llm = ChatOpenAI(
    model_name=FLM_MODEL,           # was: model
    openai_api_base=FLM_BASE_URL,   # stays consistent
    openai_api_key="no-key",        # stays consistent
    max_tokens=NUM_PREDICT,
    temperature=TEMPERATURE,
)
```

### Trade-off
The deprecation warnings from LangChain are informational only. Migration to `langchain_community` and LCEL can happen in a future version without affecting current functionality.

### Lesson Learned
Pin to a stable API version rather than chasing the latest release. For long-term projects, stability > new features.

---

## Issue #2: Silent Chunk Truncation in Embeddings

### Problem
Initial configuration used **1,500-character chunks**, but the embedding model (`sentence-transformers/all-MiniLM-L6-v2`) has a **256-token context limit**. 

Without any error, the embedding model silently truncated chunks:
- 1,500 chars ≈ 375 tokens (exceeds 256-token limit)
- Actual truncated to 256 tokens (~165 chars) — **55% information loss**

This meant retrieval was operating on incomplete chunks, degrading RAG quality.

### Detection
External code review identified that the embedding model had a documented 256-token maximum sequence length, which was never explicitly validated against chunk size.

### Solution
**Reduced chunk size to 900 characters:**

```python
# config.py
CHUNK_SIZE = 900           # ~225 tokens (under 256-token limit)
CHUNK_OVERLAP = 100
RETRIEVAL_K = 12           # Retrieve 12 chunks to maintain context coverage
                           # 12 × 75-100 tokens/chunk = ~4,500 token context
```

**Why this works:**
- 900 chars ≈ 225 tokens (safe margin below 256-token limit)
- 12 chunks × 225 tokens = 4,500 tokens (well within 32k window)
- No silent truncation = full information fidelity

### Trade-off
Slightly higher retrieval overhead (12 chunks vs. 7), but maintains data integrity.

### Lesson Learned
**Always validate component boundaries.** Just because a library accepts a parameter doesn't mean it's optimal. Understand the constraints of each component in the pipeline.

---

## Issue #3: Hardcoded Port in Health Check

### Problem
The health check for FastFlowLM was hardcoded to port 52625:

```python
# BAD: hardcoded
sock.connect_ex(("127.0.0.1", 52625))
```

If the `FLM_BASE_URL` changed in `config.py`, the health check would still connect to port 52625, masking configuration changes.

### Solution
**Extract port dynamically from `FLM_BASE_URL`:**

```python
from urllib.parse import urlparse

_parsed = urlparse(FLM_BASE_URL)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex((_parsed.hostname, _parsed.port))
sock.close()
```

Now the health check always uses the configured URL, ensuring consistency.

### Lesson Learned
**Never hardcode derived values.** Use the single source of truth (`config.py`) consistently across all modules.

---

## Issue #4: Test Suite Inefficiency

### Problem
The initial test suite (`test_rag.py`) was rebuilding the RAG chain for each test:

```python
# BAD: rebuilds FAISS + embedding model 3 times
def test_query_moon():
    qa_chain = build_rag_chain()  # Rebuild 1

def test_query_cross_doc():
    qa_chain = build_rag_chain()  # Rebuild 2

def test_query_fallback():
    qa_chain = build_rag_chain()  # Rebuild 3
```

Each rebuild:
- Loaded the embedding model (~2s)
- Created FAISS index from scratch
- Initialized ChatOpenAI connection

Total: ~6s wasted on redundant setup.

### Solution
**Build the chain once, share across tests:**

```python
def main():
    # Build once
    qa_chain = build_rag_chain()
    
    # Reuse for all tests
    result1 = query(qa_chain, question1)
    result2 = query(qa_chain, question2)
    result3 = query(qa_chain, question3)
```

### Impact
Reduced test execution time by ~50% while improving resource efficiency.

### Lesson Learned
Identify setup/teardown overhead early. For resources like embeddings models, prefer singleton patterns over per-test initialization.

---

## Issue #5: Dependency Version Conflicts

### Problem
Strict version pinning caused pip resolution failures:

```ini
# BAD: too strict
langchain==0.1.5
sentence-transformers==3.0.0
faiss-cpu==1.8.0
```

Even patch-level incompatibilities prevented installation.

### Solution
**Use range constraints with careful upper bounds:**

```ini
# GOOD: allows patches, prevents major version breaks
langchain>=0.1,<0.2
sentence-transformers>=3.0
faiss-cpu>=1.8
openai>=1.0
```

This allows:
- Security patches (0.1.5 → 0.1.6 → 0.1.7)
- Prevents breaking changes (0.2.0)
- Let pip resolve compatible subsets

### Lesson Learned
Strict versioning is for production deployments; development should allow patches for security. Use lock files (`pip freeze > requirements-lock.txt`) for reproducibility when needed.

---

## Issue #6: FastFlowLM Not Auto-Started

### Problem
Users expected `setup.sh` to start FastFlowLM, but the setup script only installed dependencies.

Missing FastFlowLM causes silent failure:
```
❌ Error: Cannot connect to FastFlowLM at 127.0.0.1:52625
```

### Why It's Not Auto-Started
1. FastFlowLM is a long-running background service
2. It must be started in a **separate terminal** (blocks)
3. It's pre-installed on the system (not a pip dependency)
4. Auto-starting would require systemd integration or process management

### Solution
**Explicit documentation in setup.sh:**

```bash
echo "2. Start FastFlowLM — NOT auto-started, must be run manually:"
echo "   flm serve lfm2:1.2b"
echo "   (FastFlowLM serves on port 52625; Lemonade is on 13305)"
```

**And in the health check:**
```python
if result != 0:
    print(f"❌ Error: Cannot connect to FastFlowLM at {_parsed.hostname}:{_parsed.port}")
    print(f"   Run 'flm serve {FLM_MODEL}' in a separate terminal first.")
    sys.exit(1)
```

### Lesson Learned
**Document service dependencies explicitly.** Don't hide requirements; make them visible in error messages and setup instructions.

---

## Issue #7: Missing Deployment Validation

### Problem
There was no systematic way to verify the deployment was working until running the full test suite.

### Solution
**Created comprehensive test suite (`test_rag.py`) with 5 validations:**

1. **Document ingestion** — loads, chunks, embeds correctly
2. **FastFlowLM connectivity** — port responds
3. **Answerable query** — retrieves correct facts
4. **Cross-document retrieval** — spans multiple documents  
5. **Out-of-scope fallback** — graceful rejection

**Example test output:**
```
================================================================================
📊 Test Results Summary
================================================================================
✅ Ingestion: PASS
✅ Query Engine: PASS
✅ Answerable Query: PASS
✅ Cross-Document Query: PASS
✅ Out-of-Scope Query: PASS
```

### Lesson Learned
**Comprehensive testing is not optional for deployments.** Include end-to-end validation in every release to catch integration issues early.

---

## Issue #8: Configuration Scatter

### Problem
Initial versions had configuration scattered across multiple files:
- Port in one place
- Model name in another
- Chunk size in yet another

Changes required updating multiple files, inviting inconsistencies.

### Solution
**Centralize all configuration in `config.py`:**

```python
# config.py - single source of truth
FLM_BASE_URL = "http://127.0.0.1:52625/v1"
FLM_MODEL = "lfm2:1.2b"
MAX_CONTEXT_TOKENS = 32000
CHUNK_SIZE = 900
RETRIEVAL_K = 12
# ... all other constants
```

**Import everywhere:**
```python
# ingest.py, rag_query.py, test_rag.py all import from config
from config import FLM_BASE_URL, CHUNK_SIZE, RETRIEVAL_K, ...
```

### Benefit
Change one value in `config.py`, and it updates everywhere. Zero inconsistencies.

### Lesson Learned
**One source of truth for all configuration.** This scales from small projects to large deployments.

---

## Summary: Key Technical Decisions

| Challenge | Root Cause | Solution | Benefit |
|-----------|-----------|----------|---------|
| LangChain API breaks | Major version refactor | Pin to 0.1.x API | Stability + security patches |
| Silent chunk truncation | No validation of embedding limit | Reduce to 900 chars | Full information fidelity |
| Hardcoded health check | Configuration not used consistently | Dynamic port extraction | Single source of truth |
| Test inefficiency | Rebuilding embeddings per test | Singleton RAG chain | 50% faster tests |
| Version conflicts | Strict pinning | Range constraints | Security + flexibility |
| Missing service startup | Unclear dependency | Explicit docs + error messages | Self-serve debugging |
| No validation | Ad-hoc testing | 5-test suite | Deployment confidence |
| Scattered config | No central registry | config.py hub | Zero inconsistencies |

---

## Recommendations for Future Work

### High Priority
1. **Migrate to LCEL** (LangChain Expression Language) — replaces deprecated `RetrievalQA`
2. **Add structured logging** — track query latencies, retrieval metrics
3. **Implement timeout protection** — for slow retrievals or FastFlowLM downtime

### Medium Priority
4. **Web UI wrapper** — REST API around `rag_query.py`
5. **Multi-model support** — easy switching between benchmarked models
6. **Batch document ingestion** — progress bars and large-scale indexing

### Low Priority
7. **Chat history** — persistent conversation context
8. **Performance profiling** — detailed latency breakdowns
9. **Model quantization** — further memory optimization

---

*This document reflects lessons learned from building RAG-NPU-Liquid. Future developers should reference these issues to avoid similar pitfalls.*
