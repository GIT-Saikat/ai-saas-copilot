"""
Test script to check if backend can start without errors.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing Backend Startup")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from app.main import app
    print("   [OK] FastAPI app imported")
    
    from app.config import settings
    print("   [OK] Config loaded")
    
    from app.database import init_db
    print("   [OK] Database module imported")
    
    print("\n2. Testing database initialization...")
    init_db()
    print("   [OK] Database initialized")
    
    print("\n3. Testing RAG pipeline import...")
    from app.rag_pipeline import get_rag_pipeline
    print("   [OK] RAG pipeline module imported")
    
    print("\n4. Testing RAG pipeline initialization (this may take time)...")
    print("   [INFO] Loading embedding model and building indices...")
    rag = get_rag_pipeline()
    print(f"   [OK] RAG pipeline initialized")
    print(f"   [OK] Documents loaded: {len(rag.documents)}")
    print(f"   [OK] Vector store ready: {rag.vectorstore is not None}")
    print(f"   [OK] BM25 index ready: {rag.bm25_index is not None}")
    print(f"   [OK] Hybrid retriever ready: {rag.retriever is not None}")
    
    print("\n5. Testing a simple query...")
    result = rag.query("How do I create an account?")
    print(f"   [OK] Query executed successfully")
    print(f"   [OK] Answer length: {len(result['answer'])} chars")
    print(f"   [OK] Confidence: {result['confidence']:.3f}")
    print(f"   [OK] Response time: {result['response_time_ms']:.2f}ms")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Backend is ready to run!")
    print("=" * 60)
    print("\nTo start the server, run:")
    print("  python run_server.py")
    print("  OR")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nThen visit:")
    print("  http://localhost:8000/docs - API Documentation")
    print("  http://localhost:8000/api/health - Health Check")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Startup failed: {e}")
    print("\nFull error traceback:")
    traceback.print_exc()
    sys.exit(1)

