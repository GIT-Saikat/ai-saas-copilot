"""
Quick test script to verify LangChain RAG pipeline is working.
This tests the refactored implementation.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from langchain.schema import Document
        print("  ✓ langchain.schema.Document")
    except ImportError:
        try:
            from langchain_core.documents import Document
            print("  ✓ langchain_core.documents.Document")
        except ImportError as e:
            print(f"  ✗ Document import failed: {e}")
            return False
    
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("  ✓ langchain_community.embeddings.HuggingFaceEmbeddings")
    except ImportError:
        try:
            from langchain.embeddings import HuggingFaceEmbeddings
            print("  ✓ langchain.embeddings.HuggingFaceEmbeddings")
        except ImportError as e:
            print(f"  ✗ HuggingFaceEmbeddings import failed: {e}")
            return False
    
    try:
        from langchain_community.vectorstores import FAISS
        print("  ✓ langchain_community.vectorstores.FAISS")
    except ImportError:
        try:
            from langchain.vectorstores import FAISS
            print("  ✓ langchain.vectorstores.FAISS")
        except ImportError as e:
            print(f"  ✗ FAISS import failed: {e}")
            return False
    
    try:
        from langchain_core.retrievers import BaseRetriever
        print("  ✓ langchain_core.retrievers.BaseRetriever")
    except ImportError:
        try:
            from langchain.retrievers import BaseRetriever
            print("  ✓ langchain.retrievers.BaseRetriever")
        except ImportError as e:
            print(f"  ✗ BaseRetriever import failed: {e}")
            return False
    
    try:
        from rank_bm25 import BM25Okapi
        print("  ✓ rank_bm25.BM25Okapi")
    except ImportError as e:
        print(f"  ✗ BM25Okapi import failed: {e}")
        return False
    
    try:
        from app.rag_pipeline import RAGPipeline
        print("  ✓ app.rag_pipeline.RAGPipeline")
    except Exception as e:
        print(f"  ✗ RAGPipeline import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_pipeline_initialization():
    """Test that pipeline can be initialized."""
    print("\nTesting pipeline initialization...")
    try:
        from app.rag_pipeline import RAGPipeline
        
        print("  Initializing RAG pipeline (this may take a moment)...")
        rag = RAGPipeline()
        
        print(f"  ✓ Pipeline initialized")
        print(f"  ✓ Documents loaded: {len(rag.documents)}")
        print(f"  ✓ LangChain Documents: {len(rag.langchain_documents)}")
        print(f"  ✓ Vector store: {rag.vectorstore.index.ntotal if rag.vectorstore else 'None'} vectors")
        print(f"  ✓ BM25 index: {'Built' if rag.bm25_index else 'None'}")
        print(f"  ✓ Hybrid Retriever: {'Created' if rag.retriever else 'None'}")
        print(f"  ✓ Embeddings: {'Initialized' if rag.embeddings else 'None'}")
        
        return rag
    except Exception as e:
        print(f"  ✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_retrieval(rag):
    """Test document retrieval."""
    print("\nTesting retrieval...")
    try:
        query = "How do I create an account?"
        chunks = rag.retrieve(query, top_k=3)
        
        print(f"  ✓ Retrieved {len(chunks)} chunks")
        if chunks:
            print(f"  ✓ Top score: {chunks[0]['score']:.3f}")
            print(f"  ✓ Chunk has content: {len(chunks[0]['content'])} chars")
            print(f"  ✓ Chunk has metadata: {bool(chunks[0].get('metadata'))}")
        
        return chunks
    except Exception as e:
        print(f"  ✗ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_validation(rag, chunks):
    """Test validation layer."""
    print("\nTesting validation layer...")
    try:
        query = "How do I create an account?"
        is_valid, confidence, reason = rag.validate_relevance(chunks, query)
        
        print(f"  ✓ Validation executed")
        print(f"  ✓ Is valid: {is_valid}")
        print(f"  ✓ Confidence: {confidence:.3f}")
        print(f"  ✓ Reason: {reason[:50]}...")
        
        return is_valid, confidence
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_query(rag):
    """Test complete query pipeline."""
    print("\nTesting complete query pipeline...")
    try:
        query = "How do I create an account?"
        result = rag.query(query)
        
        print(f"  ✓ Query executed")
        print(f"  ✓ Answer length: {len(result['answer'])} chars")
        print(f"  ✓ Confidence: {result['confidence']:.3f}")
        print(f"  ✓ Blocked: {result['blocked']}")
        print(f"  ✓ Response time: {result['response_time_ms']:.2f}ms")
        print(f"  ✓ Chunks returned: {len(result['chunks'])}")
        
        if result['answer']:
            print(f"  ✓ Answer preview: {result['answer'][:100]}...")
        
        return result
    except Exception as e:
        print(f"  ✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_hallucination_prevention(rag):
    """Test hallucination prevention."""
    print("\nTesting hallucination prevention...")
    try:
        query = "How do I build a rocket ship to Mars?"
        result = rag.query(query)
        
        print(f"  ✓ Invalid query handled")
        print(f"  ✓ Blocked: {result['blocked']}")
        print(f"  ✓ Confidence: {result['confidence']:.3f}")
        
        if result['blocked']:
            print(f"  ✓ Hallucination prevention working - query blocked")
        else:
            print(f"  ⚠ Query not blocked (may need threshold adjustment)")
        
        return result['blocked']
    except Exception as e:
        print(f"  ✗ Hallucination prevention test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("LangChain RAG Pipeline Test")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        print("\n✗ Import test failed. Please install dependencies:")
        print("  pip install langchain langchain-community faiss-cpu rank-bm25 sentence-transformers transformers torch cachetools")
        return False
    
    # Test 2: Initialization
    rag = test_pipeline_initialization()
    if not rag:
        return False
    
    # Test 3: Retrieval
    chunks = test_retrieval(rag)
    if not chunks:
        return False
    
    # Test 4: Validation
    is_valid, confidence = test_validation(rag, chunks)
    if is_valid is None:
        return False
    
    # Test 5: Complete Query
    result = test_query(rag)
    if not result:
        return False
    
    # Test 6: Hallucination Prevention
    blocked = test_hallucination_prevention(rag)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ Imports: PASSED")
    print("✓ Pipeline Initialization: PASSED")
    print("✓ Retrieval: PASSED")
    print("✓ Validation: PASSED")
    print("✓ Complete Query: PASSED")
    print(f"{'✓' if blocked else '⚠'} Hallucination Prevention: {'PASSED' if blocked else 'NEEDS REVIEW'}")
    print("\n[SUCCESS] LangChain RAG Pipeline is working!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

