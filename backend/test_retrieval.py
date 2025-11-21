"""Test retrieval directly."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.rag_pipeline import get_rag_pipeline

print("Loading RAG pipeline...")
rag = get_rag_pipeline()

print("\nTesting retrieval...")
query = "How do I create an account?"
chunks = rag.retrieve(query, top_k=3)

print(f"\nRetrieved {len(chunks)} chunks")
if chunks:
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\nChunk {i}:")
        print(f"  Score: {chunk['score']:.3f}")
        print(f"  Content preview: {chunk['content'][:150]}...")
        print(f"  Metadata: {chunk['metadata']}")
else:
    print("\nNo chunks retrieved. Checking retriever...")
    if rag.retriever:
        print("Retriever exists, testing directly...")
        try:
            docs = rag.retriever.get_relevant_documents(query)
            print(f"Retriever returned {len(docs)} documents")
            if docs:
                print(f"First doc: {docs[0].page_content[:100]}...")
        except Exception as e:
            print(f"Error in retriever: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Retriever is None!")

