"""
Quick setup checker - verifies if backend can start.
"""

import sys
from pathlib import Path

def check_imports():
    """Check if all imports work."""
    print("Checking imports...")
    
    checks = {
        "FastAPI": "fastapi",
        "Uvicorn": "uvicorn",
        "SQLAlchemy": "sqlalchemy",
        "Pydantic": "pydantic",
        "LangChain": "langchain",
        "LangChain Community": "langchain_community",
        "FAISS": "faiss",
        "BM25": "rank_bm25",
        "Sentence Transformers": "sentence_transformers",
        "Transformers": "transformers",
        "SlowAPI": "slowapi",
        "CacheTools": "cachetools",
    }
    
    results = {}
    for name, module in checks.items():
        try:
            __import__(module)
            results[name] = True
            print(f"  [OK] {name}")
        except ImportError as e:
            results[name] = False
            print(f"  [X] {name} - {e}")
    
    return results

def check_config():
    """Check if config loads."""
    print("\nChecking configuration...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from app.config import settings
        print(f"  [OK] Config loaded")
        print(f"  [OK] Embedding model: {settings.embedding_model}")
        print(f"  [OK] LLM model: {settings.llm_model}")
        print(f"  [OK] Database URL: {settings.database_url}")
        return True
    except Exception as e:
        print(f"  [X] Config error: {e}")
        return False

def check_data_file():
    """Check if data file exists."""
    print("\nChecking data file...")
    data_path = Path(__file__).parent / "data" / "documentation.json"
    if data_path.exists():
        print(f"  [OK] Data file found: {data_path}")
        return True
    else:
        print(f"  [X] Data file not found: {data_path}")
        return False

def main():
    print("=" * 60)
    print("Backend Setup Checker")
    print("=" * 60)
    
    results = check_imports()
    config_ok = check_config()
    data_ok = check_data_file()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_ok = all(results.values()) and config_ok and data_ok
    
    if all_ok:
        print("[SUCCESS] All checks passed! Backend should be ready to run.")
        print("\nTo start the server:")
        print("  python run_server.py")
        print("  OR")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("[WARNING] Some checks failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

