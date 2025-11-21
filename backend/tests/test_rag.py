"""
Tests for RAG pipeline functionality.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_pipeline import RAGPipeline
from app.config import settings


@pytest.fixture
def rag_pipeline():
    """Create a RAG pipeline instance for testing."""
    # Note: This will require actual API keys and data file
    # In a real test environment, you'd use mocks or test fixtures
    try:
        return RAGPipeline()
    except Exception as e:
        pytest.skip(f"RAG pipeline initialization failed: {e}")


def test_rag_pipeline_initialization(rag_pipeline):
    """Test that RAG pipeline initializes correctly."""
    assert rag_pipeline is not None
    assert len(rag_pipeline.documents) > 0
    assert rag_pipeline.vectorstore is not None
    assert rag_pipeline.bm25_index is not None
    assert rag_pipeline.retriever is not None


def test_document_loading(rag_pipeline):
    """Test that documents are loaded correctly."""
    assert len(rag_pipeline.documents) > 0
    assert len(rag_pipeline.document_texts) == len(rag_pipeline.documents)
    assert len(rag_pipeline.metadata) == len(rag_pipeline.documents)


def test_retrieval(rag_pipeline):
    """Test document retrieval."""
    query = "How do I create an account?"
    results = rag_pipeline.retrieve(query, top_k=5)
    
    assert len(results) > 0
    assert len(results) <= 5
    assert all('content' in r for r in results)
    assert all('score' in r for r in results)
    assert all('metadata' in r for r in results)
    assert all(0.0 <= r['score'] <= 1.0 for r in results)


def test_validation(rag_pipeline):
    """Test relevance validation."""
    query = "How do I create an account?"
    chunks = rag_pipeline.retrieve(query, top_k=5)
    
    is_valid, confidence, reason = rag_pipeline.validate_relevance(chunks, query)
    
    assert isinstance(is_valid, bool)
    assert 0.0 <= confidence <= 1.0
    assert isinstance(reason, str)


def test_query_pipeline(rag_pipeline):
    """Test complete query pipeline."""
    query = "How do I reset my password?"
    result = rag_pipeline.query(query)
    
    assert 'answer' in result
    assert 'chunks' in result
    assert 'confidence' in result
    assert 'blocked' in result
    assert 'response_time_ms' in result
    assert isinstance(result['blocked'], bool)
    assert 0.0 <= result['confidence'] <= 1.0
    assert result['response_time_ms'] > 0


def test_empty_query(rag_pipeline):
    """Test handling of empty queries."""
    result = rag_pipeline.query("")
    assert result['blocked'] is True
    assert len(result['chunks']) == 0
    assert result['confidence'] == 0.0


def test_hybrid_search(rag_pipeline):
    """Test hybrid search (vector + BM25) returns results."""
    query = "How do I reset my password?"
    results = rag_pipeline.retrieve(query, top_k=5)
    
    assert len(results) > 0
    assert len(results) <= 5
    # Verify scores are normalized (0-1 range)
    assert all(0.0 <= r['score'] <= 1.0 for r in results)
    # Verify results are sorted by score (descending)
    scores = [r['score'] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_validation_threshold_blocking(rag_pipeline):
    """Test that validation blocks queries below threshold."""
    # Query that definitely won't be in docs
    query = "What is the meaning of life and the universe?"
    chunks = rag_pipeline.retrieve(query, top_k=5)
    
    is_valid, confidence, reason = rag_pipeline.validate_relevance(chunks, query)
    
    # Should be blocked if confidence is below threshold
    if confidence < settings.similarity_threshold:
        assert is_valid is False
        assert "threshold" in reason.lower() or "similarity" in reason.lower()


def test_answer_generation(rag_pipeline):
    """Test answer generation with valid query."""
    query = "How do I create an account?"
    result = rag_pipeline.query(query)
    
    assert 'answer' in result
    assert len(result['answer']) > 0
    assert isinstance(result['answer'], str)
    # Answer should not be empty or just error message
    assert len(result['answer']) > 20


def test_hallucination_prevention(rag_pipeline):
    """Test that questions not in docs are blocked (hallucination prevention)."""
    # Query that's definitely not in documentation
    query = "How do I build a rocket ship to Mars?"
    result = rag_pipeline.query(query)
    
    # Should be blocked
    assert result['blocked'] is True
    assert "don't have enough information" in result['answer'].lower() or \
           "try rephrasing" in result['answer'].lower()


def test_edge_case_long_query(rag_pipeline):
    """Test handling of very long queries."""
    long_query = "How do I " + "create an account " * 50  # Very long query
    result = rag_pipeline.query(long_query)
    
    # Should still return a result (may be blocked or answered)
    assert 'answer' in result
    assert 'chunks' in result
    assert isinstance(result['blocked'], bool)


def test_edge_case_special_characters(rag_pipeline):
    """Test handling of queries with special characters."""
    query = "How do I reset my password? (I forgot it!)"
    result = rag_pipeline.query(query)
    
    assert 'answer' in result
    assert 'chunks' in result


def test_retrieval_ranking(rag_pipeline):
    """Test that retrieval returns results in correct order."""
    query = "account creation signup"
    results = rag_pipeline.retrieve(query, top_k=3)
    
    if len(results) > 1:
        # Scores should be in descending order
        scores = [r['score'] for r in results]
        assert scores == sorted(scores, reverse=True)


def test_validation_empty_chunks(rag_pipeline):
    """Test validation with empty chunks."""
    is_valid, confidence, reason = rag_pipeline.validate_relevance([], "test query")
    
    assert is_valid is False
    assert confidence == 0.0
    assert "no chunks" in reason.lower() or "no chunks retrieved" in reason.lower()


def test_performance_response_time(rag_pipeline):
    """Test that response time is reasonable."""
    query = "How do I create an account?"
    result = rag_pipeline.query(query)
    
    # Response time should be reasonable (less than 10 seconds for local model)
    assert result['response_time_ms'] < 10000  # 10 seconds
    assert result['response_time_ms'] > 0


def test_chunks_metadata(rag_pipeline):
    """Test that retrieved chunks have proper metadata."""
    query = "How do I create an account?"
    chunks = rag_pipeline.retrieve(query, top_k=3)
    
    for chunk in chunks:
        assert 'content' in chunk
        assert 'score' in chunk
        assert 'metadata' in chunk
        assert 'id' in chunk['metadata']
        assert 'category' in chunk['metadata']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

