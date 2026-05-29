#!/bin/bash
set -e

echo "=========================================="
echo "🚀 RAG-NPU-Liquid Setup"
echo "=========================================="

# Create virtual environment
echo ""
echo "1️⃣  Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "2️⃣  Installing Python dependencies..."
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="

echo ""
echo "📋 Pre-flight Checklist:"
echo ""
echo "1. Start FastFlowLM (in a separate terminal):"
echo "   flm serve lfm2:1.2b"
echo "   (FastFlowLM will serve on http://127.0.0.1:52625/v1)"
echo ""
echo "2. Verify FastFlowLM is running:"
echo "   curl http://127.0.0.1:52625/v1/models"
echo ""
echo "3. Ingest documents:"
echo "   source venv/bin/activate"
echo "   python ingest.py"
echo ""
echo "4. Run tests:"
echo "   python test_rag.py"
echo ""
echo "5. Start interactive RAG query:"
echo "   python rag_query.py"
echo ""
echo "📖 For detailed instructions, see INSTALL.md"
echo "=========================================="
