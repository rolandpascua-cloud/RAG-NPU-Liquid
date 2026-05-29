# Documents Directory

This directory is where you place your source documents for the RAG pipeline.

## Supported Formats

- **`.txt`** — Plain text files
- **`.pdf`** — PDF documents
- **`.md`** — Markdown files

## Adding Documents

```bash
# Copy documents here
cp ~/my_document.txt docs/
cp ~/paper.pdf docs/
cp ~/notes.md docs/

# Then ingest
python ../ingest.py
```

## Example Usage

```bash
# Create a sample document
cat > docs/example.txt << 'EOF'
The Moon is Earth's only natural satellite. It orbits Earth every 27.3 days
and is the fifth-largest moon in the solar system. The Moon has a diameter
of about 3,474 km, which is roughly one-quarter of Earth's diameter.
EOF

# Ingest and index
python ../ingest.py

# Query the RAG pipeline
python ../rag_query.py
# Enter: "How far is the Moon from Earth?"
```

## Size Recommendations

- **Total documents:** Up to 500MB (fits in ~10GB memory budget)
- **Individual file:** No strict limit, but consider splitting very large documents (>50MB)
- **Document count:** No limit, but ingestion time scales linearly

## Notes

- The ingestion process creates chunks of ~900 characters (~225 tokens)
- Chunks are automatically embedded and indexed in FAISS
- Original documents are not stored; only chunks are indexed
- To update documents, place new ones here and re-run `python ingest.py`

## Clearing the Index

```bash
# Remove old index to start fresh
rm -rf ../vectorstore/faiss_index

# Remove documents
rm docs/*

# Ingest new documents
python ../ingest.py
```
