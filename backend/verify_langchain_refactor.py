"""
Verification script for LangChain RAG refactoring.
Checks code structure and provides status report.
"""

import sys
import ast
from pathlib import Path

def check_langchain_usage():
    """Check if LangChain is used in the RAG pipeline."""
    rag_file = Path(__file__).parent / "app" / "rag_pipeline.py"
    
    if not rag_file.exists():
        print("ERROR: rag_pipeline.py not found")
        return False
    
    with open(rag_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "LangChain Document": "from langchain" in content or "langchain.schema" in content or "langchain_core" in content,
        "HuggingFaceEmbeddings": "HuggingFaceEmbeddings" in content,
        "FAISS Vector Store": "FAISS" in content and "vectorstore" in content.lower(),
        "BaseRetriever": "BaseRetriever" in content,
        "HybridRetriever": "HybridRetriever" in content and "class HybridRetriever" in content,
        "BM25 Integration": "BM25Okapi" in content,
        "Validation Layer": "validate_relevance" in content,
        "Answer Generation": "generate_answer" in content,
    }
    
    print("=" * 60)
    print("LangChain RAG Pipeline Code Verification")
    print("=" * 60)
    print("\nChecking code structure...\n")
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[X]"
        print(f"{symbol} {check_name}: {status}")
        if not passed:
            all_passed = False
    
    # Check for old implementation
    old_indicators = [
        ("Direct FAISS", "faiss.IndexFlatL2" in content and "self.vector_index" in content),
        ("Direct SentenceTransformer", "SentenceTransformer(" in content and "self.embedding_model" in content),
    ]
    
    print("\nChecking for old implementation patterns...\n")
    has_old = False
    for indicator_name, found in old_indicators:
        if found:
            print(f"[!] {indicator_name}: Still present (may be mixed with LangChain)")
            has_old = True
    
    if not has_old:
        print("[OK] No old implementation patterns found")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("STATUS: Code structure looks correct for LangChain refactoring")
        print("\nTo test functionality, install dependencies:")
        print("  pip install langchain langchain-community faiss-cpu rank-bm25")
        print("  pip install sentence-transformers transformers torch cachetools")
        print("\nThen run: python test_langchain_rag.py")
    else:
        print("STATUS: Some LangChain components may be missing")
    print("=" * 60)
    
    return all_passed


def check_imports_structure():
    """Check import structure."""
    rag_file = Path(__file__).parent / "app" / "rag_pipeline.py"
    
    with open(rag_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\nChecking import statements...\n")
    
    langchain_imports = []
    for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
        if "from langchain" in line or "import langchain" in line:
            langchain_imports.append((i, line.strip()))
    
    if langchain_imports:
        print("Found LangChain imports:")
        for line_num, import_line in langchain_imports:
            print(f"  Line {line_num}: {import_line}")
    else:
        print("[!] No LangChain imports found in first 50 lines")
    
    return len(langchain_imports) > 0


if __name__ == "__main__":
    print("\n")
    structure_ok = check_langchain_usage()
    imports_ok = check_imports_structure()
    
    print("\n" + "=" * 60)
    if structure_ok and imports_ok:
        print("VERIFICATION: PASSED")
        print("\nThe code has been refactored to use LangChain.")
        print("Install dependencies to test functionality.")
    else:
        print("VERIFICATION: NEEDS REVIEW")
        print("\nSome LangChain components may need to be added.")
    print("=" * 60)
    
    sys.exit(0 if (structure_ok and imports_ok) else 1)

