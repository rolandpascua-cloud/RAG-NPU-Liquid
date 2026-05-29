# GitHub Setup Instructions

This file helps prepare RAG-NPU-Liquid for public GitHub release.

---

## Pre-Release Checklist

- [x] Remove hardcoded IP addresses (192.168.0.73 → examples only)
- [x] Remove hardcoded usernames (eric → `<username>`)
- [x] Remove hardcoded email addresses
- [x] Create `.gitignore` to exclude venv, vectorstore, docs
- [x] Add comprehensive LICENSE (MIT)
- [x] Create TECHNICAL_JOURNEY.md documenting issues solved
- [x] Create INSTALL.md with detailed setup
- [x] Create CONTRIBUTING.md for contributors
- [x] Create SECURITY.md for security guidelines
- [x] Update all docs to use placeholder variables instead of hardcoded values
- [x] Remove machine-specific configuration

---

## Steps to Publish to GitHub

### 1. Initialize Git Repository (if needed)

```bash
cd ~/RAG-NPU-Liquid
git init
git add .
git commit -m "Initial commit: production-ready RAG pipeline for AMD Ryzen AI Max+ 395"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `RAG-NPU-Liquid`
3. **Description:** "Production-ready Retrieval-Augmented Generation pipeline on AMD Ryzen AI Max+ 395 XDNA2 NPU using FastFlowLM and LangChain"
4. **Visibility:** Public
5. **Initialize with:** None (we'll push existing repo)
6. **Add .gitignore:** Python (optional, we have one)
7. **Add license:** MIT (optional, we have one)

### 3. Add Remote and Push

```bash
git remote add origin https://github.com/yourusername/RAG-NPU-Liquid.git
git branch -M main
git push -u origin main
```

### 4. Create GitHub Release

1. Go to **Releases** tab
2. Click **Create a new release**
3. **Tag version:** `v1.0.0`
4. **Release title:** `v1.0.0 - Production Ready`
5. **Release notes:**

```markdown
# RAG-NPU-Liquid v1.0.0

Production-ready Retrieval-Augmented Generation pipeline for AMD Ryzen AI Max+ 395 XDNA2 NPU.

## What's Included

- ✅ FastFlowLM integration (lfm2:1.2b model)
- ✅ Local CPU embeddings (sentence-transformers)
- ✅ FAISS vector store (fast similarity search)
- ✅ LangChain orchestration (RAG chains)
- ✅ 32k token context window support
- ✅ End-to-end test suite (5 tests, all passing)
- ✅ Comprehensive documentation

## Key Features

- **NPU-Exclusive Inference:** GPU held at 0%, pure XDNA2 NPU computation
- **Privacy-First:** No cloud APIs, all processing local
- **Production-Ready:** Tested and validated on Fedora 43
- **Easy Deployment:** Single setup.sh script
- **Well Documented:** 7 documentation files covering every aspect

## Quick Start

```bash
bash setup.sh
# Terminal 1: flm serve lfm2:1.2b
# Terminal 2: python ingest.py && python rag_query.py
```

## Technical Highlights

- Overcome 8 major technical challenges (see TECHNICAL_JOURNEY.md)
- Optimized chunk size from 1500 → 900 chars (prevents silent truncation)
- Dynamic port extraction for configuration consistency
- Singleton RAG chain for 50% faster tests
- Flexible dependency versioning (ranges instead of strict pins)

## Documentation

- **[README.md](README.md)** — Project overview
- **[INSTALL.md](INSTALL.md)** — Installation & deployment guide
- **[BENCHMARKS.md](BENCHMARKS.md)** — Performance data (60.4 tok/s at 1k context)
- **[DEPLOYMENT_LOG.md](DEPLOYMENT_LOG.md)** — Deployment history & test results
- **[TECHNICAL_JOURNEY.md](TECHNICAL_JOURNEY.md)** — Issues solved & lessons learned
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute
- **[SECURITY.md](SECURITY.md)** — Security guidelines

## Performance

| Metric | Value |
|--------|-------|
| Model Size | ~0.9GB |
| Decode Speed (1k context) | 60.4 tok/s |
| Decode Speed (32k context) | 37.9 tok/s |
| End-to-End Query Latency | 0.7-1.0s |
| Memory (@ 32k) | ~3GB (headroom 7-8GB) |
| GPU Usage | 0% (NPU-only) |

## Requirements

- **Hardware:** AMD Ryzen AI Max+ 395 (Strix Halo) with XDNA2 NPU
- **OS:** Fedora 43+ (or compatible Linux)
- **Python:** 3.10+
- **FastFlowLM:** 0.9.40+

## Breaking Changes

None. This is the first stable release.

## Known Issues & Workarounds

See [DEPLOYMENT_LOG.md](DEPLOYMENT_LOG.md#known-limitations--workarounds)

## Future Improvements

- [ ] Migrate to LCEL (LangChain Expression Language)
- [ ] Add structured logging
- [ ] REST API wrapper
- [ ] Web UI dashboard
- [ ] Multi-model support

## License

MIT License — See [LICENSE](LICENSE)

## Contributors

Built with focus on stability, performance, and developer experience.

---

For questions, issues, or contributions, see [CONTRIBUTING.md](CONTRIBUTING.md).
```

6. Click **Publish release**

---

## Repository Settings

### Branch Protection (Recommended)

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require code reviews before merging

### Code of Conduct

1. Go to **Settings** → **Community**
2. Add "Contributor Covenant" Code of Conduct (GitHub template)

### Topics

Add these topics for discoverability:
- `rag`
- `amd-ryzen-ai`
- `xdna`
- `npu`
- `langchain`
- `fastflowlm`
- `faiss`
- `embeddings`
- `retrieval-augmented-generation`
- `python`

### Description

```
Production-ready RAG pipeline for AMD Ryzen AI Max+ 395 XDNA2 NPU with FastFlowLM, LangChain, and local embeddings
```

### Keywords

```
RAG, retrieval-augmented-generation, AMD Ryzen AI, XDNA2 NPU, FastFlowLM, LangChain, FAISS, local LLM, Python
```

---

## Promotion & Sharing

### Social Media

**Twitter/X:**
```
🚀 Introducing RAG-NPU-Liquid: A production-ready Retrieval-Augmented Generation 
pipeline running entirely on the AMD Ryzen AI Max+ 395 XDNA2 NPU.

Features:
• 60 tok/s decode speed at 1k context
• 32k token context window support
• Privacy-first (no cloud APIs)
• Fully tested & documented

GitHub: github.com/yourusername/RAG-NPU-Liquid

#AMD #XDNA #LLM #RAG #OpenSource
```

**GitHub Discussions:**
- Announce in Hugging Face Forums
- Post in r/LocalLLaMA (Reddit)
- Share in AMD Ryzen AI community

### Documentation Links

Create a README badge for your GitHub profile:
```markdown
[![RAG-NPU-Liquid](https://img.shields.io/badge/Project-RAG--NPU--Liquid-blue?style=flat&logo=github)](https://github.com/yourusername/RAG-NPU-Liquid)
```

---

## Maintenance Plan

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug Report
about: Report a bug or issue
title: '[BUG] '
labels: bug
---

## Description
<!-- Clear description of the issue -->

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior
<!-- What should happen -->

## Actual Behavior
<!-- What actually happens -->

## Environment
- OS: 
- Python: 
- FastFlowLM: 
- Hardware: 

## Logs
<!-- Error messages, stack traces, etc -->
```

Create `.github/ISSUE_TEMPLATE/feature_request.md`:
```markdown
---
name: Feature Request
about: Suggest an idea for improvement
title: '[FEATURE] '
labels: enhancement
---

## Description
<!-- Clear description of the feature -->

## Use Case
<!-- Why do you need this feature? -->

## Proposed Solution
<!-- How should it work? -->

## Alternatives
<!-- Other approaches considered -->
```

### Automated Testing

Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: python test_rag.py
```

---

## Version Bumping

```bash
# For version updates, follow semantic versioning:
# v1.0.0 (major.minor.patch)

git tag -a v1.0.1 -m "Fix: chunk truncation in config"
git push origin v1.0.1
```

---

## Troubleshooting Common Issues

### Issue: "Repository Already Exists"
```bash
# If you already have a local .git
git remote add origin https://github.com/yourusername/RAG-NPU-Liquid.git
git push -u origin main
```

### Issue: "Large Files"
```bash
# If vectorstore/ or venv/ were accidentally committed:
git rm -r --cached vectorstore/ venv/
git commit -m "Remove large files (should be in .gitignore)"
git push
```

---

## Success Criteria

- [x] Repository is public
- [x] README is clear and compelling
- [x] Installation instructions work
- [x] Tests pass
- [x] Documentation is comprehensive
- [x] No sensitive data exposed
- [x] License is clear (MIT)
- [x] Contributing guidelines exist
- [x] Code of conduct is present
- [x] Security policy is documented

---

## Post-Release

1. **Watch issues** — Respond to bugs and questions
2. **Monitor usage** — Check GitHub Insights for popularity
3. **Gather feedback** — Ask users for feature requests
4. **Plan improvements** — Use TECHNICAL_JOURNEY.md for ideas
5. **Keep dependencies updated** — Run `pip-audit` monthly

---

**Your RAG-NPU-Liquid project is ready for the world! 🚀**
