# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-05-28

### Initial Release - Production Ready

#### Added
- Core RAG pipeline with FastFlowLM integration
- FAISS vector store for similarity search
- Local CPU embeddings (sentence-transformers/all-MiniLM-L6-v2)
- LangChain orchestration (RetrievalQA chain)
- Comprehensive test suite (5 end-to-end tests)
- Full 32k token context window support
- Dynamic configuration via `config.py`
- Document ingestion pipeline (supports .txt, .pdf, .md)
- Interactive CLI for querying (`rag_query.py`)
- NPU-exclusive inference (GPU at 0%)

#### Documentation
- README.md — Project overview
- INSTALL.md — Step-by-step installation guide
- BENCHMARKS.md — Performance data for lfm2:1.2b
- DEPLOYMENT_LOG.md — Deployment history & test results
- TECHNICAL_JOURNEY.md — Issues overcome & lessons learned
- CONTRIBUTING.md — Contribution guidelines
- SECURITY.md — Security best practices
- LICENSE — MIT License
- CHANGELOG.md — This file

#### Performance
- 60.4 tok/s decode speed at 1k context
- 37.9 tok/s decode speed at 32k context
- 16.68s TTFT at 32k context
- 0.7-1.0s end-to-end query latency (including retrieval)
- ~0.9GB model footprint
- <10GB total memory usage at 32k context

#### Testing
- Document ingestion validation
- FastFlowLM connectivity check
- Answerable query test
- Cross-document retrieval test
- Out-of-scope query fallback test
- All 5 tests passing on Fedora 43 Z13

#### Infrastructure
- Virtual environment setup (setup.sh)
- Dependency pinning (requirements.txt)
- .gitignore for Python projects
- GitHub-ready packaging
- Sanitized configuration (no hardcoded paths/IPs)

### Technical Decisions

#### LangChain API Version
- **Decision:** Pin to langchain>=0.1,<0.2
- **Reason:** 0.1.x API is stable; 0.2.x is in transition with breaking changes
- **Trade-off:** Deprecation warnings (informational only, no functional impact)

#### Chunk Size Optimization
- **Decision:** 900 chars per chunk (~225 tokens)
- **Reason:** Prevents silent truncation by embedding model's 256-token limit
- **Trade-off:** Slightly higher retrieval overhead (12 chunks vs 7)

#### Port Discovery
- **Decision:** Dynamic extraction from FLM_BASE_URL via urllib.parse
- **Reason:** Ensures health check uses configured URL, not hardcoded port
- **Trade-off:** Minimal overhead for parsing

#### Dependency Versioning
- **Decision:** Range constraints (e.g., langchain>=0.1,<0.2)
- **Reason:** Allow security patches while preventing breaking changes
- **Trade-off:** Less reproducibility (use pip freeze for exact pins)

#### Configuration Centralization
- **Decision:** All settings in config.py
- **Reason:** Single source of truth for all parameters
- **Trade-off:** Must edit and restart to change values (no hot-reload)

### Known Limitations

1. **LangChain 0.1.x Deprecation Warnings**
   - Informational only, no functional impact
   - Migration to 0.2.x can happen in future version

2. **No Real-Time Streaming**
   - Responses are generated fully before returning
   - Streaming can be added in future version

3. **No Authentication**
   - Default setup is single-user only
   - Add authentication when integrating with other systems

4. **No Rate Limiting**
   - Built-in rate limiting not present
   - Add at application level if exposed to multiple users

---

## Future Releases

### Planned for v1.1.0
- [ ] Migrate to LCEL (LangChain Expression Language)
- [ ] Add structured logging
- [ ] Implement timeout protection
- [ ] REST API wrapper

### Planned for v1.2.0
- [ ] Multi-model support (easy switching)
- [ ] Web UI dashboard
- [ ] Batch document ingestion
- [ ] Performance profiling tools

### Under Consideration
- Chat history persistence
- Model quantization
- Distributed embedding computation
- Redis vector cache

---

## Support & Feedback

- **Issues:** GitHub Issues for bugs and feature requests
- **Discussions:** GitHub Discussions for questions
- **Contributing:** See CONTRIBUTING.md

---

## How to Upgrade

### From v1.0.0 to v1.1.0 (when released)

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python test_rag.py  # Verify everything still works
```

---

## Version History

- **v1.0.0** (2026-05-28) — Production Ready Release
  - Initial public release
  - All tests passing
  - Comprehensive documentation

---

**For detailed information about each version, see the [GitHub Releases](https://github.com/yourusername/RAG-NPU-Liquid/releases) page.**
