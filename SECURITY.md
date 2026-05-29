# Security Policy

## Reporting Security Issues

**Do not open public GitHub issues for security vulnerabilities.**

If you discover a security issue, please email the maintainers privately with:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if you have one)

Please allow 30 days for a response and fix before public disclosure.

---

## Security Considerations

### 1. API Key Management

**RAG-NPU-Liquid does NOT require API keys** for local inference, maintaining privacy:

- ✅ All LLM inference runs on your local NPU
- ✅ All embeddings computed locally on CPU
- ✅ No cloud APIs called
- ✅ No network communication with external services

**Important:** Do not hardcode real API keys if you modify the code for external services.

### 2. Document Privacy

**Your documents stay on your machine:**

- Documents are not uploaded anywhere
- FAISS index is stored locally
- Only embeddings and vectors are created from your documents
- Original document paths and contents are not logged

**Best practices:**
- Sanitize sensitive documents before ingestion
- Use file permissions to restrict access to `./vectorstore/`
- Store documents in a private directory

### 3. Network Security

**Default configuration is localhost-only:**

```python
FLM_BASE_URL = "http://127.0.0.1:52625/v1"  # Localhost only
```

If you expose FastFlowLM to a network (example with placeholder):

```python
FLM_BASE_URL = "http://<your-machine-ip>:52625/v1"  # Network access - replace <your-machine-ip>
# Example: FLM_BASE_URL = "http://192.168.1.100:52625/v1"
```

**Add authentication:**
- Use firewall rules to restrict access
- Never expose port 52625 to the internet
- Consider VPN/SSH tunneling for remote access

### 4. Dependency Vulnerabilities

**Monitor for known vulnerabilities:**

```bash
# Check dependencies for known issues
pip-audit

# Update to latest patches
pip install --upgrade -r requirements.txt
```

**Dependencies:**
- `langchain` — Core RAG orchestration
- `faiss-cpu` — Vector database
- `sentence-transformers` — Embeddings
- `pypdf` — PDF parsing
- `openai` — API compatibility layer (unused in local mode)

All pinned to stable versions with security patches available.

### 5. File Permissions

```bash
# Ensure documents are readable only by you
chmod 700 docs/
chmod 700 vectorstore/
chmod 700 venv/

# Check current permissions
ls -la docs/ vectorstore/
```

---

## Security Best Practices

### For Development

1. **Never commit credentials:**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   secrets.txt
   ```

2. **Use environment variables for configuration:**
   ```python
   import os
   FLM_BASE_URL = os.getenv("FLM_BASE_URL", "http://127.0.0.1:52625/v1")
   ```

3. **Validate user input:**
   ```python
   # rag_query.py already does this
   question = input("Enter your question: ").strip()
   if not question:
       continue
   ```

### For Deployment

1. **Isolate FastFlowLM:**
   - Run in a dedicated user account
   - Restrict port 52625 with firewall
   - Use network segmentation

2. **Backup your data:**
   ```bash
   # Back up FAISS index periodically
   tar -czf vectorstore_backup_$(date +%Y%m%d).tar.gz vectorstore/
   ```

3. **Monitor resource usage:**
   - GPU should stay at 0% (NPU-only inference)
   - Memory should stay under 10GB
   - CPU orchestration < 20%

4. **Regular updates:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Known Limitations

### 1. No Input Sanitization on Document Content

While RAG-NPU-Liquid doesn't execute code from documents, malformed PDFs or large files could cause:
- High memory usage
- Slow ingestion
- Embedding model timeout

> [!TIP]
> **Mitigation:**
- Validate document format before ingestion
- Set file size limits
- Monitor ingestion process

### 2. No Rate Limiting

If exposed to a network, there's no built-in rate limiting. Add at the application level:

```python
# Example: Rate limit queries to 10 per minute
from functools import wraps
import time

def rate_limit(calls_per_minute=10):
    min_interval = 60 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

### 3. No Authentication

The default setup has no user authentication. For multi-user systems:

- Add authentication to any REST API wrapper
- Use OS-level file permissions
- Implement user-specific vectorstores

---

## Security Checklist

Before deploying to production:

- [ ] Documents are sanitized (no sensitive PII)
- [ ] `.gitignore` excludes `venv/`, `vectorstore/`, `docs/`
- [ ] File permissions are restricted (`chmod 700`)
- [ ] FastFlowLM is localhost-only or firewalled
- [ ] Firewall blocks external access to port 52625
- [ ] Regular backups of FAISS index
- [ ] Dependencies are up-to-date (`pip-audit` passes)
- [ ] No credentials in code or config files
- [ ] Resource limits monitored (memory, CPU, GPU)
- [ ] Error messages don't leak sensitive info

---

## Incident Response

If you discover or suspect a security issue:

1. **Stop the service** if necessary
2. **Don't share details publicly** — email maintainers privately
3. **Document** what happened and how to reproduce
4. **Wait for patch** before public disclosure

---

## Third-Party Security

This project depends on:

- **FastFlowLM** — AMD's official inference engine
- **LangChain** — Widely-used RAG framework
- **FAISS** — Meta's vector database
- **sentence-transformers** — Hugging Face community project

All are actively maintained and have security processes in place.

---

For security questions or concerns, please reach out to the maintainers privately.
