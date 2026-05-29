#!/usr/bin/env python3
"""
End-to-end test of the RAG pipeline.
Usage: python test_rag.py
"""

import sys
import time
from pathlib import Path

from config import DOCS_DIR


def setup_sample_docs():
    """Create sample documents for testing."""
    docs_path = Path(DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    # Document 1: Information about the Moon
    moon_doc = docs_path / "moon.txt"
    moon_content = """The Moon is Earth's only natural satellite. It orbits the Earth every 27.3 days.
The Moon is about 384,400 km from Earth on average. Its diameter is approximately 3,474 km.
The Moon has no atmosphere. Its surface is covered with craters and mountains.
The tallest mountain on the Moon is Korolev crater's central peak at approximately 10.786 km above the reference level.
The Moon was formed about 4.5 billion years ago. Scientists believe it formed from a giant impact between Earth and a Mars-sized body.
The Moon is the fifth-largest moon in the solar system."""
    moon_doc.write_text(moon_content)
    print(f"✓ Created {moon_doc.name}")

    # Document 2: Information about Mars
    mars_doc = docs_path / "mars.txt"
    mars_content = """Mars is the fourth planet from the Sun in our solar system.
It is often called the "Red Planet" because it appears red in color due to iron oxide on its surface.
Mars has a diameter of about 6,779 km, roughly half that of Earth.
The atmosphere of Mars is primarily carbon dioxide with traces of nitrogen and argon.
Mars has two small moons named Phobos and Deimos.
The largest volcano in the solar system, Olympus Mons, is located on Mars.
Olympus Mons is about 21 km tall and has a diameter of about 600 km.
Mars is believed to have had liquid water on its surface in the past.
Scientists continue to search for evidence of ancient microbial life on Mars."""
    mars_doc.write_text(mars_content)
    print(f"✓ Created {mars_doc.name}")

    return [moon_doc, mars_doc]


def test_ingestion():
    """Test document ingestion."""
    print("\n[TEST 1] Document Ingestion")
    print("-" * 60)

    try:
        from ingest import ingest
        ingest()
        return True
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return False


def test_query_engine():
    """Test the RAG query engine."""
    print("\n[TEST 2] Query Engine & FastFlowLM Connection")
    print("-" * 60)

    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 52625))
    sock.close()

    if result != 0:
        print(f"⚠️  FastFlowLM not running on port 52625")
        print(f"   Start it with: flm serve lfm2:1.2b")
        return None  # Skip query tests, but don't fail

    print("✓ FastFlowLM is running")
    return True


def _flm_is_running():
    """Check if FastFlowLM is reachable."""
    import socket
    from urllib.parse import urlparse
    from config import FLM_BASE_URL
    parsed = urlparse(FLM_BASE_URL)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((parsed.hostname, parsed.port))
    sock.close()
    return result == 0


def test_answerable_query(qa_chain):
    """Test a query that should be answerable from the documents."""
    print("\n[TEST 3] Answerable Query (Moon)")
    print("-" * 60)

    try:
        from rag_query import query

        question = "How far is the Moon from Earth?"
        start_time = time.time()
        result = query(qa_chain, question)
        elapsed = time.time() - start_time

        answer = result["answer"].lower()
        expected_keywords = ["384400", "384,400", "km", "distance", "moon", "earth"]
        found_keywords = [kw for kw in expected_keywords if kw in answer]

        if found_keywords:
            print(f"✓ Answer contains expected keywords: {found_keywords}")
            print(f"  Response time: {elapsed:.2f}s")
            return True
        else:
            print(f"⚠️  Answer doesn't contain expected keywords")
            print(f"  Answer: {answer[:200]}")
            return False

    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cross_document_query(qa_chain):
    """Test a query requiring information from multiple documents."""
    print("\n[TEST 4] Cross-Document Query (Moon vs Mars)")
    print("-" * 60)

    try:
        from rag_query import query

        question = "What are the largest volcanoes mentioned in the documents?"
        start_time = time.time()
        result = query(qa_chain, question)
        elapsed = time.time() - start_time

        answer = result["answer"].lower()
        expected_keywords = ["olympus mons", "mars", "volcano"]
        found_keywords = [kw for kw in expected_keywords if kw in answer]

        if found_keywords:
            print(f"✓ Answer contains expected keywords: {found_keywords}")
            print(f"  Response time: {elapsed:.2f}s")
            return True
        else:
            print(f"⚠️  Answer doesn't contain expected keywords")
            print(f"  Answer: {answer[:200]}")
            return False

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


def test_out_of_scope_query(qa_chain):
    """Test a query that should fall back to 'I don't have enough information'."""
    print("\n[TEST 5] Out-of-Scope Query (Venus)")
    print("-" * 60)

    try:
        from rag_query import query

        question = "What is the surface temperature of Venus?"
        start_time = time.time()
        result = query(qa_chain, question)
        elapsed = time.time() - start_time

        answer = result["answer"].lower()
        fallback_phrases = [
            "i don't have enough information",
            "don't have enough information",
            "i don't know",
            "not in the context",
            "no information",
        ]

        has_fallback = any(phrase in answer for phrase in fallback_phrases)

        if has_fallback:
            print(f"✓ Correctly returned fallback response")
            print(f"  Response: {answer[:150]}")
            print(f"  Response time: {elapsed:.2f}s")
            return True
        else:
            print(f"⚠️  Did not return fallback response")
            print(f"  Answer: {answer[:200]}")
            return False

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("🧪 RAG Pipeline End-to-End Test Suite")
    print("=" * 80)

    # Create sample documents
    print("\n[SETUP] Creating sample documents...")
    setup_sample_docs()
    print("✓ Sample documents ready")

    # Run tests
    test_results = {}

    test_results["Ingestion"] = test_ingestion()
    test_results["Query Engine"] = test_query_engine()

    if test_results.get("Query Engine") is not False:
        if _flm_is_running():
            from rag_query import build_rag_chain
            print("\n⚙️  Building shared RAG chain (one-time model load)...")
            shared_chain = build_rag_chain()
            test_results["Answerable Query"] = test_answerable_query(shared_chain)
            test_results["Cross-Document Query"] = test_cross_document_query(shared_chain)
            test_results["Out-of-Scope Query"] = test_out_of_scope_query(shared_chain)
        else:
            for name in ("Answerable Query", "Cross-Document Query", "Out-of-Scope Query"):
                test_results[name] = None

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in test_results.items():
        if result is True:
            print(f"✅ {test_name}: PASS")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAIL")
            failed += 1
        else:
            print(f"⏭️  {test_name}: SKIP")
            skipped += 1

    print("-" * 80)
    print(f"Total: {passed} PASS, {failed} FAIL, {skipped} SKIP")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
