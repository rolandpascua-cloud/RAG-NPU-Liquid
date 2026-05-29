# Contributing to RAG-NPU-Liquid

Thank you for your interest in contributing! This document outlines how to contribute to RAG-NPU-Liquid.

---

## Code of Conduct

Be respectful and inclusive. We welcome contributors of all backgrounds and experience levels.

---

## How to Contribute

### 1. Report Issues

Found a bug? Have a feature request? [Create an issue](https://github.com/yourusername/RAG-NPU-Liquid/issues) with:
- **Title:** Clear, descriptive summary
- **Description:** Detailed explanation of the issue
- **Steps to Reproduce:** How to replicate the bug
- **Expected vs. Actual Behavior:** What should happen vs. what actually happens
- **Environment:** OS, Python version, FastFlowLM version, Hardware

**Example:**
```
Title: Chunk truncation affects retrieval quality

Description:
When using CHUNK_SIZE > 900 chars, the embedding model silently truncates chunks, degrading retrieval.

Steps to Reproduce:
1. Set CHUNK_SIZE = 1500 in config.py
2. Run python ingest.py
3. Run python test_rag.py
4. Cross-document query returns incomplete context

Expected: Full chunks are embedded and retrieved
Actual: Chunks are silently truncated at 256 tokens

Environment:
- OS: Fedora 43
- Python: 3.11.2
- FastFlowLM: 0.9.40
- Hardware: Ryzen AI Max+ 395 (Strix Halo)
```

---

### 2. Submit Pull Requests

#### Fork & Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/RAG-NPU-Liquid.git
cd RAG-NPU-Liquid
git remote add upstream https://github.com/original/RAG-NPU-Liquid.git
```

#### Create a Feature Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/issue-123
```

#### Make Changes

1. **Follow code style:**
   - Use clear, descriptive names
   - Add docstrings for public functions
   - Keep functions focused and small
   - Comment only non-obvious logic

2. **Update tests:**
   ```bash
   python test_rag.py  # Run existing tests
   ```

3. **Update documentation:**
   - If you change configuration, update `config.py` comments
   - If you change dependencies, update `requirements.txt`
   - If you fix an issue, update `TECHNICAL_JOURNEY.md`

#### Commit & Push

```bash
git add .
git commit -m "feat: add streaming response support"
# or
git commit -m "fix: prevent chunk truncation with embedding limit check"

git push origin feature/my-feature
```

**Commit message guidelines:**
- Use imperative mood ("add feature" not "added feature")
- Start with type: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Reference issues: `closes #123`

**Example:**
```
fix: validate chunk size against embedding model context limit

Prevents silent truncation of chunks by the embedding model.
Reduces CHUNK_SIZE from 1500 to 900 chars (~225 tokens),
which fits within the 256-token context window.

Closes #42
```

#### Create Pull Request

1. Go to GitHub and create a PR
2. **Title:** Clear summary (e.g., "Add streaming responses")
3. **Description:**
   - What changed and why
   - How to test the change
   - Any breaking changes or limitations
   - Related issues

**Example PR description:**
```markdown
## Summary
Adds streaming response support to allow real-time token generation without waiting for full context.

## Changes
- Added `stream=True` parameter to `ChatOpenAI` initialization
- Updated `query()` function to yield tokens instead of returning full response
- Added `test_streaming_query` to test suite

## How to Test
```bash
python rag_query.py
# Type: "What is the Moon?" and observe tokens streaming in real-time
```

## Breaking Changes
None. Streaming is opt-in; existing code continues to work.

## Related Issues
Closes #88
```

---

## Development Workflow

### Testing

```bash
# Run full test suite
python test_rag.py

# Run specific test
python -c "from test_rag import test_ingestion; test_ingestion()"

# Create sample docs for manual testing
mkdir -p docs
echo "The Moon orbits Earth..." > docs/test_moon.txt
python ingest.py
python rag_query.py  # Test manually
```

### Documentation

Update relevant docs when making changes:

| Change | Update |
|--------|--------|
| New configuration parameter | `config.py` + `INSTALL.md` |
| Bug fix | `TECHNICAL_JOURNEY.md` (under Issue section) |
| Performance improvement | `BENCHMARKS.md` (if significant) |
| New feature | `README.md` + inline docstrings |
| Dependency change | `requirements.txt` + `INSTALL.md` |

---

## Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt

# For linting (optional but recommended)
pip install black flake8 mypy

# Format code
black *.py

# Check for style issues
flake8 *.py

# Type checking
mypy ingest.py rag_query.py
```

---

## Areas for Contribution

### High Priority
- [ ] Migrate to LCEL (LangChain Expression Language)
- [ ] Add structured logging for debugging
- [ ] Implement timeout protection for FastFlowLM downtime

### Medium Priority
- [ ] REST API wrapper around `rag_query.py`
- [ ] Multi-model support (test with other benchmarked models)
- [ ] Web UI dashboard

### Low Priority
- [ ] Chat history persistence
- [ ] Performance profiling tools
- [ ] Model quantization experimentation

---

## Commit History Best Practices

Keep the main branch clean:

```bash
# Before submitting PR, clean up commit history
git log --oneline
# Keep logical commits, squash WIP commits

# Example: squash multiple commits into one
git rebase -i HEAD~3  # Interactive rebase last 3 commits
```

---

## Review Process

1. **Automated checks:**
   - Tests must pass (`python test_rag.py`)
   - No breaking changes to public APIs

2. **Code review:**
   - At least one approval required
   - Address review comments

3. **Merge:**
   - Squash commits to main branch
   - Delete feature branch

---

## Documentation Style

Follow these conventions:

### Python Docstrings
```python
def build_rag_chain():
    """Build RAG chain with FastFlowLM backend.
    
    Returns:
        RetrievalQA: Configured RAG chain ready for queries.
        
    Raises:
        FileNotFoundError: If FAISS index not found.
    """
```

### Markdown Headers
```markdown
# Main Title (one per file)
## Section Heading
### Subsection
#### Detail
```

### Code Examples
```markdown
Use backticks for inline code: `config.py`

Multi-line code blocks:
\`\`\`python
python ingest.py
\`\`\`

Terminal output:
\`\`\`
Expected: FAISS index saved
\`\`\`
```

---

## Performance Benchmarking

When optimizing, measure before and after:

```bash
# Time a function
time python ingest.py

# Profile memory usage
python -m memory_profiler ingest.py

# Profile CPU usage
python -m cProfile -s cumulative test_rag.py
```

---

## Questions?

- Check **[TECHNICAL_JOURNEY.md](./TECHNICAL_JOURNEY.md)** for past issues
- Read **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** for deployment insights
- Review **[INSTALL.md](./INSTALL.md)** for setup details

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve RAG-NPU-Liquid! 🚀
