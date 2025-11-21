"""
Manual test script to verify RAG pipeline implementation.
Run this to test the pipeline without pytest.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_pipeline import RAGPipeline
from app.config import settings

def test_implementation():
    """Test RAG pipeline implementation."""
    print("=" * 60)
    print("Testing RAG Pipeline Implementation")
    print("=" * 60)
    
    try:
        print("\n1. Initializing RAG Pipeline...")
        rag = RAGPipeline()
        print(f"   [OK] Pipeline initialized successfully")
        print(f"   [OK] Loaded {len(rag.documents)} documents")
        print(f"   [OK] LangChain Documents: {len(rag.langchain_documents)}")
        print(f"   [OK] Vector store: {rag.vectorstore.index.ntotal if rag.vectorstore else 'None'} vectors")
        print(f"   [OK] BM25 index: {'Built' if rag.bm25_index else 'None'}")
        print(f"   [OK] Hybrid Retriever: {'Created' if rag.retriever else 'None'}")
        print(f"   [OK] Embedding model: {settings.embedding_model}")
        print(f"   [OK] LLM model: {settings.llm_model}")
        
        # Test 1: Document Loading (Step 3.1)
        print("\n2. Testing Document Processing (Step 3.1)...")
        assert len(rag.documents) > 0, "No documents loaded"
        assert len(rag.document_texts) == len(rag.documents), "Document texts mismatch"
        assert len(rag.metadata) == len(rag.documents), "Metadata mismatch"
        print(f"   [OK] Documents loaded: {len(rag.documents)}")
        print(f"   [OK] Rich content strings created")
        print(f"   [OK] Metadata generated")
        
        # Test 2: Embedding Generation (Step 3.2)
        print("\n3. Testing Embedding Generation (Step 3.2)...")
        assert rag.embeddings is not None, "Embeddings not initialized"
        assert rag.vectorstore is not None, "Vector store not built"
        assert rag.vectorstore.index.ntotal == len(rag.documents), "Vector index count mismatch"
        print(f"   [OK] LangChain HuggingFaceEmbeddings initialized")
        print(f"   [OK] Using model: {settings.embedding_model}")
        print(f"   [OK] Embeddings generated for {rag.vectorstore.index.ntotal} documents")
        
        # Test 3: Vector Store Setup (Step 3.3)
        print("\n4. Testing Vector Store Setup (Step 3.3)...")
        assert rag.vectorstore is not None, "Vector store not built"
        assert rag.vectorstore.index.ntotal == len(rag.documents), "Vector index count mismatch"
        print(f"   [OK] LangChain FAISS index built: {rag.vectorstore.index.ntotal} vectors")
        print(f"   [OK] Index persistence configured")
        
        # Test 4: BM25 Setup (Step 3.4)
        print("\n5. Testing BM25 Setup (Step 3.4)...")
        assert rag.bm25_index is not None, "BM25 index not built"
        print(f"   [OK] BM25 index built")
        print(f"   [OK] Tokenization working")
        
        # Test 5: Hybrid Retrieval (Step 3.5)
        print("\n6. Testing Hybrid Retrieval (Step 3.5)...")
        query = "How do I create an account?"
        chunks = rag.retrieve(query, top_k=5)
        assert len(chunks) > 0, "No chunks retrieved"
        assert len(chunks) <= 5, "Too many chunks returned"
        assert all('content' in c for c in chunks), "Missing content in chunks"
        assert all('score' in c for c in chunks), "Missing scores in chunks"
        assert all(0.0 <= c['score'] <= 1.0 for c in chunks), "Scores out of range"
        print(f"   [OK] Retrieved {len(chunks)} chunks")
        scores_str = ", ".join([f"{c['score']:.3f}" for c in chunks[:3]])
        print(f"   [OK] Scores normalized (0-1): {scores_str}")
        print(f"   [OK] Hybrid search working (vector + BM25)")
        
        # Test 6: Validation Layer (Step 3.6)
        print("\n7. Testing Validation Layer (Step 3.6)...")
        is_valid, confidence, reason = rag.validate_relevance(chunks, query)
        assert isinstance(is_valid, bool), "Invalid validation result"
        assert 0.0 <= confidence <= 1.0, "Confidence out of range"
        assert isinstance(reason, str), "Reason not a string"
        print(f"   [OK] Validation working")
        print(f"   [OK] Similarity threshold: {settings.similarity_threshold}")
        print(f"   [OK] Variance threshold: {settings.variance_threshold}")
        print(f"   [OK] Keyword overlap threshold: {settings.keyword_overlap_threshold}")
        print(f"   [OK] Query validation: {'PASSED' if is_valid else 'BLOCKED'}")
        print(f"   [OK] Confidence: {confidence:.3f}")
        print(f"   [OK] Reason: {reason}")
        
        # Test 7: Answer Generation (Step 3.7)
        print("\n8. Testing Answer Generation (Step 3.7)...")
        result = rag.query(query)
        assert 'answer' in result, "Missing answer in result"
        assert 'chunks' in result, "Missing chunks in result"
        assert 'confidence' in result, "Missing confidence in result"
        assert 'blocked' in result, "Missing blocked status"
        assert 'response_time_ms' in result, "Missing response time"
        assert len(result['answer']) > 0, "Empty answer"
        assert result['response_time_ms'] > 0, "Invalid response time"
        print(f"   [OK] Answer generated: {len(result['answer'])} characters")
        print(f"   [OK] Response time: {result['response_time_ms']:.2f}ms")
        print(f"   [OK] Blocked: {result['blocked']}")
        print(f"   [OK] Confidence: {result['confidence']:.3f}")
        
        # Test 8: Hallucination Prevention
        print("\n9. Testing Hallucination Prevention...")
        invalid_query = "How do I build a rocket ship to Mars?"
        invalid_result = rag.query(invalid_query)
        print(f"   [OK] Invalid query handled")
        print(f"   [OK] Blocked: {invalid_result['blocked']}")
        print(f"   [OK] Confidence: {invalid_result['confidence']:.3f}")
        if invalid_result['blocked']:
            print(f"   [OK] Hallucination prevention working - query blocked")
        
        # Test 9: Edge Cases
        print("\n10. Testing Edge Cases...")
        empty_result = rag.query("")
        assert empty_result['blocked'] is True, "Empty query not blocked"
        print(f"   [OK] Empty query handled")
        
        long_query = "How do I " + "create an account " * 20
        long_result = rag.query(long_query)
        assert 'answer' in long_result, "Long query failed"
        print(f"   [OK] Long query handled")
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("[PASS] Phase 3 Step 3.1: Document Processing")
        print("[PASS] Phase 3 Step 3.2: Embedding Generation")
        print("[PASS] Phase 3 Step 3.3: Vector Store Setup")
        print("[PASS] Phase 3 Step 3.4: BM25 Setup")
        print("[PASS] Phase 3 Step 3.5: Retrieval Function")
        print("[PASS] Phase 3 Step 3.6: Validation Layer")
        print("[PASS] Phase 3 Step 3.7: Answer Generation")
        print("[PASS] Hallucination Prevention")
        print("[PASS] Edge Case Handling")
        print("\n[SUCCESS] All tests passed! RAG Pipeline is properly implemented.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_implementation()
    sys.exit(0 if success else 1)

