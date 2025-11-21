"""
RAG Pipeline Implementation using LangChain - FREE TOOLS ONLY
Uses LangChain for RAG orchestration with sentence-transformers embeddings and Hugging Face models.

Phase 3 Implementation with LangChain:
- Document Processing (Step 3.1) - LangChain Document Loaders
- Embedding Generation (Step 3.2) - LangChain HuggingFaceEmbeddings
- Vector Store Setup with Persistence (Step 3.3) - LangChain FAISS
- BM25 Setup for Hybrid Search (Step 3.4) - Custom Hybrid Retriever
- Retrieval Function (Step 3.5) - LangChain Retrieval Chain
- Validation Layer with Hallucination Prevention (Step 3.6)
- Answer Generation (Step 3.7) - LangChain LLM Chain
"""

import json
import time
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path

try:
    # Try newer LangChain versions (1.0+)
    from langchain_core.documents import Document
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
except ImportError:
    # Fallback for older LangChain versions (0.1.x)
    try:
        from langchain.schema import Document
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
    except ImportError:
        try:
            from langchain.schema import Document
            from langchain.embeddings import HuggingFaceEmbeddings
            from langchain.vectorstores import FAISS
            from langchain.retrievers import BaseRetriever
            from langchain.callbacks.manager import CallbackManagerForRetrieverRun
        except ImportError as e:
            print(f"Warning: {e}. Some features may not work until dependencies are installed.")

try:
    from rank_bm25 import BM25Okapi
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    import faiss
except ImportError as e:
    print(f"Warning: {e}. Some features may not work until dependencies are installed.")

from app.config import settings
from app.cache import get_cached_embedding, cache_embedding


class HybridRetriever(BaseRetriever):
    """
    Custom LangChain retriever that combines vector search (FAISS) and BM25.
    Implements hybrid retrieval for better search results.
    """
    
    def __init__(
        self,
        vectorstore: FAISS,
        bm25_index: BM25Okapi,
        document_texts: List[str],
        metadata: List[Dict],
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        k: int = 5
    ):
        # Don't call super().__init__() to avoid Pydantic validation issues
        # Store attributes directly
        object.__setattr__(self, '_vectorstore', vectorstore)
        object.__setattr__(self, '_bm25_index', bm25_index)
        object.__setattr__(self, '_document_texts', document_texts)
        object.__setattr__(self, '_metadata', metadata)
        object.__setattr__(self, '_vector_weight', vector_weight)
        object.__setattr__(self, '_bm25_weight', bm25_weight)
        object.__setattr__(self, '_k', k)
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """Retrieve documents using hybrid search (vector + BM25)."""
        # Vector search using LangChain FAISS
        vector_docs = self._vectorstore.similarity_search_with_score(query, k=self._k * 2)
        
        # Extract vector scores and normalize
        vector_scores_dict = {}
        for doc, score in vector_docs:
            # FAISS returns L2 distance, convert to similarity (lower distance = higher similarity)
            # Normalize to 0-1 range
            similarity = 1 / (1 + score)  # Simple conversion
            doc_idx = self._get_doc_index(doc)
            if doc_idx is not None:
                vector_scores_dict[doc_idx] = similarity
        
        # BM25 search
        tokenized_query = query.lower().split()
        if not tokenized_query:
            return []
        
        bm25_scores = self._bm25_index.get_scores(tokenized_query)
        
        # Normalize BM25 scores to 0-1
        bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1
        bm25_scores_normalized = bm25_scores / bm25_max if bm25_max > 0 else bm25_scores
        
        # Combine scores
        combined_scores = {}
        for idx in range(len(self._document_texts)):
            vector_score = vector_scores_dict.get(idx, 0.0)
            bm25_score = bm25_scores_normalized[idx]
            combined_score = (
                self._vector_weight * vector_score +
                self._bm25_weight * bm25_score
            )
            combined_scores[idx] = combined_score
        
        # Sort by combined score and get top_k
        sorted_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in sorted_indices[:self._k]]
        
        # Build LangChain Documents with scores
        results = []
        for idx in top_indices:
            doc = Document(
                page_content=self._document_texts[idx],
                metadata={
                    **self._metadata[idx],
                    'score': combined_scores[idx],
                    'vector_score': vector_scores_dict.get(idx, 0.0),
                    'bm25_score': float(bm25_scores_normalized[idx])
                }
            )
            results.append(doc)
        
        return results
    
    def _get_doc_index(self, doc: Document) -> Optional[int]:
        """Get document index from metadata."""
        doc_id = doc.metadata.get('id')
        if doc_id:
            for idx, meta in enumerate(self._metadata):
                if meta.get('id') == doc_id:
                    return idx
        return None
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Public method to retrieve documents (required by BaseRetriever interface)."""
        # Create a dummy run_manager if needed
        from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
        return self._get_relevant_documents(query, run_manager=None)


class RAGPipeline:
    """Main RAG pipeline using LangChain with FREE tools only."""
    
    def __init__(self):
        """Initialize the RAG pipeline with LangChain components."""
        self.documents: List[Dict] = []
        self.langchain_documents: List[Document] = []
        self.document_texts: List[str] = []
        self.metadata: List[Dict] = []
        self.vectorstore: Optional[FAISS] = None
        self.bm25_index: Optional[BM25Okapi] = None
        self.retriever: Optional[HybridRetriever] = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.llm_tokenizer = None
        self.llm_model = None
        self.use_inference_api = False
        
        # Initialize LangChain embeddings (FREE - sentence-transformers via HuggingFaceEmbeddings)
        print(f"Loading LangChain embedding model: {settings.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        
        # Initialize LLM (FREE - Hugging Face)
        self._init_llm()
        
        # Load and process documents
        self._load_documents()
        self._build_indices()
    
    def _init_llm(self):
        """Initialize free Hugging Face LLM."""
        print(f"Loading LLM model: {settings.llm_model}")
        try:
            if settings.use_hf_inference and settings.huggingface_api_key:
                # Use Hugging Face Inference API (free tier)
                from huggingface_hub import InferenceClient
                self.hf_client = InferenceClient(
                    model=settings.llm_model,
                    token=settings.huggingface_api_key
                )
                self.use_inference_api = True
            else:
                # Use local model (completely free)
                model_name = settings.llm_model
                print(f"Loading local model: {model_name}")
                self.llm_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.llm_model = AutoModelForCausalLM.from_pretrained(model_name)
                self.llm_tokenizer.pad_token = self.llm_tokenizer.eos_token
                self.use_inference_api = False
                print(f"Using local Hugging Face model: {model_name} (completely free)")
        except Exception as e:
            print(f"Warning: Could not load LLM model: {e}")
            print("Will use simple template-based answers")
            self.llm_model = None
    
    def _load_documents(self):
        """Load documents from JSON file and create LangChain Documents."""
        data_path = Path(settings.data_path)
        if not data_path.is_absolute():
            data_path = Path(__file__).parent.parent / data_path
        
        if not data_path.exists():
            raise FileNotFoundError(f"Documentation file not found: {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
        
        for doc in docs:
            # Validate required fields
            required_fields = ['id', 'category', 'question', 'answer', 'tags']
            if not all(field in doc for field in required_fields):
                continue
            
            # Create rich content string for better embeddings
            tags_str = ', '.join(doc.get('tags', []))
            content = (
                f"Category: {doc['category']}\n"
                f"Question: {doc['question']}\n"
                f"Answer: {doc['answer']}\n"
                f"Tags: {tags_str}"
            )
            
            # Create metadata
            metadata = {
                'id': doc['id'],
                'category': doc['category'],
                'source': 'documentation.json',
                'question': doc['question'],
                'answer': doc['answer'],
                'tags': doc.get('tags', [])
            }
            
            # Create LangChain Document
            langchain_doc = Document(
                page_content=content,
                metadata=metadata
            )
            
            self.document_texts.append(content)
            self.documents.append(doc)
            self.metadata.append(metadata)
            self.langchain_documents.append(langchain_doc)
        
        print(f"Loaded {len(self.documents)} documents as LangChain Documents")
    
    def _build_indices(self):
        """Build both vector (FAISS via LangChain) and BM25 indices with persistence."""
        if not self.langchain_documents:
            raise ValueError("No documents loaded")
        
        # Check if we can load from disk
        vector_index_path = self._get_index_path(settings.vector_index_path)
        
        # Try to load existing FAISS index
        if vector_index_path.exists() and (vector_index_path.parent / "index.faiss").exists():
            try:
                print("Loading existing LangChain FAISS index from disk...")
                self.vectorstore = FAISS.load_local(
                    str(vector_index_path.parent),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded FAISS index with {self.vectorstore.index.ntotal} vectors")
                
                # Verify index matches current documents
                if self.vectorstore.index.ntotal == len(self.langchain_documents):
                    print("Index matches current document count, using cached index")
                else:
                    print("Index count mismatch, rebuilding...")
                    self._rebuild_indices(vector_index_path)
            except Exception as e:
                print(f"Error loading index from disk: {e}. Rebuilding...")
                self._rebuild_indices(vector_index_path)
        else:
            # Build new indices
            self._rebuild_indices(vector_index_path)
        
        # Build BM25 index (always rebuild as it's fast)
        tokenized_docs = [doc.lower().split() for doc in self.document_texts]
        self.bm25_index = BM25Okapi(tokenized_docs)
        print("Built BM25 index")
        
        # Create hybrid retriever
        self.retriever = HybridRetriever(
            vectorstore=self.vectorstore,
            bm25_index=self.bm25_index,
            document_texts=self.document_texts,
            metadata=self.metadata,
            vector_weight=settings.vector_weight,
            bm25_weight=settings.bm25_weight,
            k=settings.max_context_chunks
        )
        print("Created LangChain Hybrid Retriever")
    
    def _rebuild_indices(self, vector_index_path: Path):
        """Rebuild and save FAISS index using LangChain."""
        print("Building LangChain FAISS index...")
        
        # Create FAISS vector store from documents using LangChain
        self.vectorstore = FAISS.from_documents(
            self.langchain_documents,
            self.embeddings
        )
        print(f"Built FAISS index with {self.vectorstore.index.ntotal} vectors")
        
        # Save to disk using LangChain
        try:
            vector_index_path.parent.mkdir(parents=True, exist_ok=True)
            self.vectorstore.save_local(
                str(vector_index_path.parent),
                index_name="index"
            )
            print(f"Saved LangChain FAISS index to disk: {vector_index_path.parent}")
        except Exception as e:
            print(f"Warning: Could not save index to disk: {e}")
    
    def _get_index_path(self, path_str: str) -> Path:
        """Get absolute path for index file."""
        path = Path(path_str)
        if not path.is_absolute():
            path = Path(__file__).parent.parent / path
        return path
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Hybrid retrieval using LangChain retriever.
        
        Args:
            query: User query string
            top_k: Number of results to return (defaults to MAX_CONTEXT_CHUNKS)
        
        Returns:
            List of retrieved chunks with scores and metadata
        """
        if not query or not query.strip():
            return []
        
        if top_k is None:
            top_k = settings.max_context_chunks
        
        if not self.retriever:
            raise ValueError("RAG pipeline not properly initialized. Retriever missing.")
        
        try:
            # Use LangChain hybrid retriever
            docs = self.retriever.get_relevant_documents(query)
            
            # Format results
            results = []
            for doc in docs[:top_k]:
                results.append({
                    'content': doc.page_content,
                    'score': doc.metadata.get('score', 0.0),
                    'metadata': {
                        'id': doc.metadata.get('id'),
                        'category': doc.metadata.get('category'),
                        'question': doc.metadata.get('question'),
                        'answer': doc.metadata.get('answer'),
                        'tags': doc.metadata.get('tags', [])
                    }
                })
            
            return results
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
    
    def validate_relevance(self, chunks: List[Dict], query: str) -> Tuple[bool, float, str]:
        """
        Validate relevance of retrieved chunks with multi-layer validation.
        
        Implements three validation mechanisms from Phase 3 Step 3.6:
        1. Similarity Threshold - Block answers below threshold
        2. Context Consistency Check - Ensure top results are similar
        3. Content Coverage - Check if retrieved chunks contain answer keywords
        
        Returns:
            Tuple of (is_valid, confidence_score, reason)
        """
        if not chunks:
            return False, 0.0, "No chunks retrieved"
        
        top_score = chunks[0]['score']
        
        # Validation 1: Similarity Threshold
        if top_score < settings.similarity_threshold:
            return False, top_score, f"Similarity score {top_score:.2f} below threshold {settings.similarity_threshold}"
        
        # Validation 2: Context Consistency Check
        if len(chunks) >= 3:
            scores = [chunk['score'] for chunk in chunks[:3]]
            variance = np.var(scores)
            if variance > settings.variance_threshold:
                return False, top_score, f"High score variance {variance:.3f} indicates ambiguous query"
        
        # Validation 3: Content Coverage
        query_words = set(word.lower() for word in query.split() if len(word) > 2)
        if query_words:
            top_chunk_words = set(word.lower() for word in chunks[0]['content'].split() if len(word) > 2)
            overlap = len(query_words & top_chunk_words) / len(query_words)
            
            if overlap < settings.keyword_overlap_threshold:
                return False, top_score, f"Low keyword overlap {overlap:.2f} - retrieved content may not be relevant"
        
        return True, top_score, "All validation checks passed"
    
    def generate_answer(self, query: str, chunks: List[Dict]) -> str:
        """
        Generate answer using FREE Hugging Face LLM with retrieved context.
        
        Args:
            query: User query
            chunks: Retrieved document chunks
        
        Returns:
            Generated answer string
        """
        if not chunks:
            return "I don't have enough information to answer this question. Please try rephrasing or contact support."
        
        # Build context with scores
        context_parts = []
        for chunk in chunks:
            score = chunk['score']
            # Use answer from metadata if available, otherwise use full content
            content = chunk.get('metadata', {}).get('answer', chunk['content'])
            context_parts.append(f"[Score: {score:.2f}]\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = f"""You are a helpful support assistant. Answer based ONLY on the provided documentation.

Context:
{context}

Question: {query}

Answer based on the context above:"""
        
        # Generate answer using FREE Hugging Face model
        try:
            if self.use_inference_api:
                answer = self.hf_client.text_generation(
                    prompt,
                    max_new_tokens=settings.max_tokens,
                    temperature=settings.temperature,
                    return_full_text=False
                )
            elif self.llm_model is not None:
                max_prompt_length = 1024
                if len(prompt) > max_prompt_length:
                    prompt = prompt[:max_prompt_length//2] + "\n...\n" + prompt[-max_prompt_length//2:]
                
                inputs = self.llm_tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
                
                with torch.no_grad():
                    outputs = self.llm_model.generate(
                        inputs,
                        max_new_tokens=settings.max_tokens,
                        temperature=settings.temperature,
                        do_sample=settings.temperature > 0,
                        pad_token_id=self.llm_tokenizer.eos_token_id,
                        eos_token_id=self.llm_tokenizer.eos_token_id,
                        repetition_penalty=1.1
                    )
                
                answer = self.llm_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            else:
                # Fallback: Use best matching chunk's answer
                best_chunk = chunks[0]
                answer = best_chunk['metadata'].get('answer', 'I found relevant information but cannot generate a detailed answer.')
            
            answer = answer.strip()
            
            # Post-processing: Check for refusal patterns
            refusal_patterns = [
                "i don't know", "i cannot", "i'm unable", "i don't have",
                "insufficient information", "i don't have enough",
                "cannot answer", "unable to answer"
            ]
            if any(pattern in answer.lower() for pattern in refusal_patterns):
                best_chunk = chunks[0]
                answer = best_chunk['metadata'].get('answer', 'I found relevant information but cannot generate a detailed answer.')
            
            if not answer or len(answer) < 10:
                best_chunk = chunks[0]
                answer = best_chunk['metadata'].get('answer', 'I found relevant information but cannot generate a detailed answer.')
            
            return answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            best_chunk = chunks[0]
            return best_chunk['metadata'].get('answer', 'I encountered an error while generating an answer. Please try again or contact support.')
    
    def query(self, user_query: str) -> Dict:
        """
        Complete RAG pipeline using LangChain: retrieve, validate, and generate answer.
        
        Args:
            user_query: User's question
        
        Returns:
            Dictionary with answer, chunks, confidence, and blocked status
        """
        start_time = time.time()
        
        if not user_query or not user_query.strip():
            return {
                'answer': "Please provide a valid question.",
                'chunks': [],
                'confidence': 0.0,
                'blocked': True,
                'response_time_ms': (time.time() - start_time) * 1000
            }
        
        try:
            # Retrieve relevant chunks using LangChain retriever
            chunks = self.retrieve(user_query)
            
            # Validate relevance
            is_valid, confidence, validation_reason = self.validate_relevance(chunks, user_query)
            
            # Generate answer or block
            if is_valid:
                answer = self.generate_answer(user_query, chunks)
                blocked = False
            else:
                if settings.debug:
                    answer = f"I don't have enough information to answer this question. ({validation_reason}) Please try rephrasing or contact support."
                else:
                    answer = "I don't have enough information to answer this question. Please try rephrasing or contact support."
                blocked = True
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Format chunks for response
            formatted_chunks = []
            for chunk in chunks:
                formatted_chunks.append({
                    'content': chunk['content'],
                    'score': chunk['score'],
                    'metadata': {
                        'id': chunk['metadata']['id'],
                        'category': chunk['metadata']['category']
                    }
                })
            
            return {
                'answer': answer,
                'chunks': formatted_chunks,
                'confidence': confidence,
                'blocked': blocked,
                'response_time_ms': response_time_ms
            }
        except Exception as e:
            print(f"Error in RAG pipeline query: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            return {
                'answer': "I encountered an error while processing your question. Please try again or contact support.",
                'chunks': [],
                'confidence': 0.0,
                'blocked': True,
                'response_time_ms': response_time_ms
            }


# Global RAG pipeline instance (initialized on startup)
rag_pipeline: Optional[RAGPipeline] = None

def get_rag_pipeline() -> RAGPipeline:
    """Get or initialize the global RAG pipeline instance."""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()
    return rag_pipeline
