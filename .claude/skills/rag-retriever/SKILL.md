# RAG Retriever Skill

## Metadata
```yaml
name: rag-retriever
description: Retrieves relevant documents from vector databases for RAG. Implements semantic search, hybrid search, reranking, MMR, and metadata filtering using Chroma, Pinecone, or FAISS.
version: 1.0.0
category: ai-ml
tags: [rag, retrieval, search, vector-search, semantic-search, hybrid-search]
dependencies: [langchain, chromadb, sentence-transformers, rank-bm25]
```

## When to Use This Skill

Use this skill when:
- User says "Search documents" or "Find relevant context"
- Need semantic search (search by meaning, not keywords)
- Phase III: AI assistant needs to retrieve context
- Implementing question-answering system
- Building document search feature
- Need to find similar code snippets
- Retrieving context for LLM prompts

## What This Skill Provides

### 1. Search Types
- **Semantic Search**: Vector similarity (find by meaning)
- **Keyword Search**: BM25 full-text search
- **Hybrid Search**: Combine semantic + keyword (best results)
- **MMR (Maximum Marginal Relevance)**: Diverse results
- **Similarity with Score**: Get relevance scores

### 2. Retrieval Strategies
- **Top-K Retrieval**: Get N most relevant documents
- **Threshold Filtering**: Only return results above score threshold
- **Metadata Filtering**: Filter by file type, date, tags, etc.
- **Multi-Query Retrieval**: Reformulate query for better coverage
- **Parent Document Retrieval**: Return full document from chunk match

### 3. Reranking
- **Cross-Encoder Reranking**: Reorder results with better model
- **Cohere Rerank API**: Production-grade reranking
- **Custom scoring**: Weight different factors

### 4. Result Processing
- **Deduplication**: Remove similar results
- **Context Window Fitting**: Ensure results fit LLM context
- **Source Citation**: Track provenance
- **Relevance Scoring**: Quantify quality of matches

### 5. Query Enhancement
- **Query Expansion**: Add synonyms/related terms
- **Query Decomposition**: Break complex queries into parts
- **Hypothetical Document Embeddings (HyDE)**: Generate answer first, then search

---

## Installation

### Core Dependencies
```bash
# Using uv (recommended)
uv add langchain langchain-community langchain-openai
uv add chromadb sentence-transformers
uv add rank-bm25  # For keyword search

# Using pip
pip install langchain langchain-community langchain-openai
pip install chromadb sentence-transformers rank-bm25
```

### Optional Reranking
```bash
# Cross-encoder models
uv add sentence-transformers

# Cohere reranking (production)
uv add cohere
```

---

## Implementation Examples

### Example 1: Basic Semantic Search

```python
"""
Basic semantic search with Chroma.
"""

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

class RAGRetriever:
    """Retrieve relevant documents for RAG."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "documents",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize retriever.

        Args:
            persist_directory: Chroma database location
            collection_name: Collection to query
            embedding_model: OpenAI embedding model
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize vector store
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )

    def search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents.

        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum relevance score (0-1)

        Returns:
            List of documents with metadata and scores
        """
        # Search with scores
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query=query,
            k=k
        )

        # Format results
        formatted_results = []
        for doc, score in results:
            # Apply threshold if specified
            if score_threshold and score < score_threshold:
                continue

            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
                "source": doc.metadata.get("source", "Unknown")
            })

        return formatted_results

    def search_by_vector(
        self,
        embedding: List[float],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search using pre-computed embedding vector.

        Args:
            embedding: Query embedding vector
            k: Number of results

        Returns:
            List of matching documents
        """
        collection = self.client.get_collection(self.collection_name)

        results = collection.query(
            query_embeddings=[embedding],
            n_results=k
        )

        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "id": results['ids'][0][i]
            })

        return formatted_results

    def filter_by_metadata(
        self,
        query: str,
        k: int = 5,
        metadata_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with metadata filtering.

        Args:
            query: Search query
            k: Number of results
            metadata_filter: Metadata conditions (e.g., {"file_type": "python"})

        Returns:
            Filtered results
        """
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
                "filter": metadata_filter
            }
        )

        docs = retriever.get_relevant_documents(query)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "Unknown")
            }
            for doc in docs
        ]


# Usage Example
if __name__ == "__main__":
    # Initialize retriever
    retriever = RAGRetriever(
        persist_directory="./chroma_db",
        collection_name="todo_app_docs"
    )

    # Search
    query = "How do I create a new task?"
    results = retriever.search(query, k=3)

    print(f"Query: {query}\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['source']} (score: {result['score']:.3f})")
        print(f"   {result['content'][:150]}...")
        print()
```

---

### Example 2: MMR (Maximum Marginal Relevance)

```python
"""
MMR retrieval for diverse, non-redundant results.
"""

class MMRRetriever(RAGRetriever):
    """Retriever with MMR for result diversity."""

    def search_mmr(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search using MMR for diverse results.

        Args:
            query: Search query
            k: Number of results to return
            fetch_k: Number of initial candidates
            lambda_mult: Diversity factor (0=max diversity, 1=max relevance)

        Returns:
            Diverse set of relevant documents
        """
        docs = self.vectorstore.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "Unknown")
            }
            for doc in docs
        ]

    def compare_search_types(self, query: str, k: int = 3):
        """Compare standard search vs MMR."""
        print(f"Query: {query}\n")

        # Standard semantic search
        print("=== Standard Semantic Search ===")
        standard = self.search(query, k=k)
        for i, result in enumerate(standard, 1):
            print(f"{i}. {result['source']}")
            print(f"   {result['content'][:100]}...\n")

        # MMR search
        print("\n=== MMR Search (Diverse Results) ===")
        mmr = self.search_mmr(query, k=k, lambda_mult=0.5)
        for i, result in enumerate(mmr, 1):
            print(f"{i}. {result['source']}")
            print(f"   {result['content'][:100]}...\n")


# Usage
mmr_retriever = MMRRetriever(collection_name="todo_app_docs")

mmr_retriever.compare_search_types("How do I authenticate users?", k=3)
```

---

### Example 3: Hybrid Search (Semantic + Keyword)

```python
"""
Hybrid search combining vector similarity and keyword matching.
"""

from rank_bm25 import BM25Okapi
import numpy as np
from typing import Tuple

class HybridRetriever(RAGRetriever):
    """Hybrid retriever combining semantic and keyword search."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bm25 = None
        self._documents = None

    def _build_bm25_index(self):
        """Build BM25 index from all documents."""
        if self._bm25 is not None:
            return

        # Get all documents
        collection = self.client.get_collection(self.collection_name)
        all_docs = collection.get()

        self._documents = [
            {
                "content": content,
                "metadata": metadata,
                "id": doc_id
            }
            for content, metadata, doc_id in zip(
                all_docs['documents'],
                all_docs['metadatas'],
                all_docs['ids']
            )
        ]

        # Tokenize and build BM25 index
        tokenized_docs = [doc['content'].split() for doc in self._documents]
        self._bm25 = BM25Okapi(tokenized_docs)

        print(f"✓ Built BM25 index for {len(self._documents)} documents")

    def keyword_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        BM25 keyword search.

        Args:
            query: Search query
            k: Number of results

        Returns:
            Documents with BM25 scores
        """
        self._build_bm25_index()

        # Tokenize query
        tokenized_query = query.split()

        # Get BM25 scores
        scores = self._bm25.get_scores(tokenized_query)

        # Get top-k
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_indices:
            results.append((
                self._documents[idx],
                float(scores[idx])
            ))

        return results

    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic and keyword.

        Args:
            query: Search query
            k: Number of results
            semantic_weight: Weight for semantic scores (0-1)
            keyword_weight: Weight for keyword scores (0-1)

        Returns:
            Ranked results from hybrid scoring
        """
        # Semantic search
        semantic_results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=k * 2  # Get more candidates
        )

        # Keyword search
        keyword_results = self.keyword_search(query, k=k * 2)

        # Build score dictionaries
        semantic_scores = {
            doc.metadata.get('source', doc.page_content[:50]): score
            for doc, score in semantic_results
        }

        keyword_scores = {}
        for doc_dict, score in keyword_results:
            key = doc_dict['metadata'].get('source', doc_dict['content'][:50])
            # Normalize BM25 scores to 0-1 range
            keyword_scores[key] = score / (max(s for _, s in keyword_results) + 1e-6)

        # Combine scores
        all_docs = {}
        for doc, sem_score in semantic_results:
            key = doc.metadata.get('source', doc.page_content[:50])
            kw_score = keyword_scores.get(key, 0)

            hybrid_score = (
                semantic_weight * sem_score +
                keyword_weight * kw_score
            )

            all_docs[key] = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": hybrid_score,
                "semantic_score": sem_score,
                "keyword_score": kw_score,
                "source": key
            }

        # Sort by hybrid score
        sorted_docs = sorted(
            all_docs.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        return sorted_docs[:k]


# Usage
hybrid_retriever = HybridRetriever(collection_name="todo_app_docs")

results = hybrid_retriever.hybrid_search(
    "create new task with priority",
    k=5,
    semantic_weight=0.7,
    keyword_weight=0.3
)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['source']}")
    print(f"   Hybrid: {result['score']:.3f} (Sem: {result['semantic_score']:.3f}, KW: {result['keyword_score']:.3f})")
    print(f"   {result['content'][:100]}...\n")
```

---

### Example 4: Reranking with Cross-Encoder

```python
"""
Rerank search results using cross-encoder for better relevance.
"""

from sentence_transformers import CrossEncoder

class RerankingRetriever(HybridRetriever):
    """Retriever with cross-encoder reranking."""

    def __init__(self, *args, rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", **kwargs):
        super().__init__(*args, **kwargs)
        self.rerank_model = CrossEncoder(rerank_model)

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder.

        Args:
            query: Original query
            documents: Initial retrieved documents
            top_k: Number of top results to return (None = all)

        Returns:
            Reranked documents with new scores
        """
        if not documents:
            return []

        # Create query-document pairs
        pairs = [[query, doc['content']] for doc in documents]

        # Get reranking scores
        scores = self.rerank_model.predict(pairs)

        # Add reranking scores
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = float(score)
            doc['original_score'] = doc.get('score', 0)

        # Sort by rerank score
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)

        if top_k:
            reranked = reranked[:top_k]

        return reranked

    def search_with_reranking(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search with reranking pipeline.

        Args:
            query: Search query
            k: Final number of results
            fetch_k: Initial candidates to fetch

        Returns:
            Reranked top-k results
        """
        # Initial retrieval (get more candidates)
        initial_results = self.hybrid_search(
            query,
            k=fetch_k,
            semantic_weight=0.7,
            keyword_weight=0.3
        )

        # Rerank
        reranked_results = self.rerank(query, initial_results, top_k=k)

        return reranked_results


# Usage
reranking_retriever = RerankingRetriever(collection_name="todo_app_docs")

query = "How do I update a task's priority?"
results = reranking_retriever.search_with_reranking(query, k=3, fetch_k=10)

print(f"Query: {query}\n")
for i, result in enumerate(results, 1):
    print(f"{i}. {result['source']}")
    print(f"   Rerank Score: {result['rerank_score']:.3f}")
    print(f"   Original Score: {result['original_score']:.3f}")
    print(f"   {result['content'][:150]}...")
    print()
```

---

### Example 5: Multi-Query Retrieval

```python
"""
Generate multiple query variations for better coverage.
"""

from langchain.retrievers import MultiQueryRetriever
from langchain_openai import ChatOpenAI

class MultiQueryRAGRetriever(RAGRetriever):
    """Retriever that generates multiple query variations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = ChatOpenAI(temperature=0)

    def multi_query_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate query variations and retrieve from all.

        Args:
            query: Original query
            k: Number of results per query variation

        Returns:
            Deduplicated results from all queries
        """
        # Create multi-query retriever
        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": k}),
            llm=self.llm
        )

        # Retrieve
        docs = retriever.get_relevant_documents(query)

        # Deduplicate by content hash
        seen = set()
        unique_docs = []

        for doc in docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "Unknown")
                })

        return unique_docs


# Usage
multi_retriever = MultiQueryRAGRetriever(collection_name="todo_app_docs")

results = multi_retriever.multi_query_search("task completion", k=3)

print(f"Found {len(results)} unique results across query variations")
for result in results:
    print(f"- {result['source']}")
```

---

## Retrieval Patterns

### Pattern 1: Context Window Fitting
```python
def retrieve_with_context_limit(
    retriever: RAGRetriever,
    query: str,
    max_tokens: int = 3000
) -> List[Dict[str, Any]]:
    """Retrieve results that fit in context window."""
    import tiktoken

    enc = tiktoken.encoding_for_model("gpt-4")
    results = []
    token_count = 0

    for result in retriever.search(query, k=20):
        content_tokens = len(enc.encode(result['content']))

        if token_count + content_tokens <= max_tokens:
            results.append(result)
            token_count += content_tokens
        else:
            break

    return results
```

### Pattern 2: Metadata Filtering
```python
# Search only Python files
results = retriever.filter_by_metadata(
    query="authentication logic",
    metadata_filter={"file_type": ".py"}
)

# Search recent documents
from datetime import datetime, timedelta

recent_date = (datetime.now() - timedelta(days=7)).isoformat()
results = retriever.filter_by_metadata(
    query="new features",
    metadata_filter={"indexed_at": {"$gte": recent_date}}
)
```

### Pattern 3: Multi-Stage Retrieval
```python
def multi_stage_retrieval(query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Fast initial retrieval (get 50 candidates)
    Stage 2: Rerank top candidates (get 10)
    Stage 3: Filter by score threshold (get 5)
    """
    # Stage 1: Initial retrieval
    initial = hybrid_retriever.hybrid_search(query, k=50)

    # Stage 2: Reranking
    reranked = reranking_retriever.rerank(query, initial, top_k=10)

    # Stage 3: Threshold filtering
    final = [r for r in reranked if r['rerank_score'] > 0.5]

    return final[:5]
```

---

## CLI Tool

```python
"""
CLI for RAG retrieval operations.
"""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="rag-search", help="RAG Search Tool")
console = Console()

@app.command("search")
def search(
    query: str = typer.Argument(..., help="Search query"),
    k: int = typer.Option(5, help="Number of results"),
    collection: str = typer.Option("documents", help="Collection name"),
    method: str = typer.Option("semantic", help="Search method: semantic, hybrid, mmr")
):
    """Search for relevant documents."""
    if method == "semantic":
        retriever = RAGRetriever(collection_name=collection)
        results = retriever.search(query, k=k)
    elif method == "hybrid":
        retriever = HybridRetriever(collection_name=collection)
        results = retriever.hybrid_search(query, k=k)
    elif method == "mmr":
        retriever = MMRRetriever(collection_name=collection)
        results = retriever.search_mmr(query, k=k)
    else:
        console.print(f"[red]Unknown method: {method}[/red]")
        return

    # Display results
    table = Table(title=f"Search Results: {query}")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Source", style="yellow")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Preview", style="white")

    for i, result in enumerate(results, 1):
        score = result.get('score', result.get('rerank_score', 0))
        preview = result['content'][:80] + "..."

        table.add_row(
            str(i),
            result['source'],
            f"{score:.3f}",
            preview
        )

    console.print(table)

@app.command("compare")
def compare_methods(
    query: str = typer.Argument(..., help="Search query"),
    k: int = typer.Option(3, help="Number of results"),
    collection: str = typer.Option("documents", help="Collection name")
):
    """Compare different retrieval methods."""
    console.print(f"[cyan]Query: {query}[/cyan]\n")

    # Semantic
    console.print("[yellow]SEMANTIC SEARCH[/yellow]")
    semantic = RAGRetriever(collection_name=collection)
    results = semantic.search(query, k=k)
    for i, r in enumerate(results, 1):
        console.print(f"  {i}. {r['source']} ({r['score']:.3f})")

    # Hybrid
    console.print("\n[yellow]HYBRID SEARCH[/yellow]")
    hybrid = HybridRetriever(collection_name=collection)
    results = hybrid.hybrid_search(query, k=k)
    for i, r in enumerate(results, 1):
        console.print(f"  {i}. {r['source']} ({r['score']:.3f})")

if __name__ == "__main__":
    app()
```

Usage:
```bash
# Semantic search
python rag_search.py search "How to create tasks" --k 5

# Hybrid search
python rag_search.py search "authentication" --method hybrid

# Compare methods
python rag_search.py compare "task management"
```

---

## Best Practices

1. **Retrieval Strategy**:
   - Start with semantic search for MVP
   - Add hybrid search for keyword-heavy queries
   - Use MMR for diverse results
   - Always rerank top candidates

2. **Performance**:
   - Fetch more candidates (20-50), rerank to top-k (3-5)
   - Cache embeddings and search results
   - Use metadata filtering to reduce search space
   - Monitor retrieval latency

3. **Quality**:
   - Set relevance score thresholds (e.g., > 0.7)
   - Deduplicate similar results
   - Include source citations
   - Test with real user queries

4. **Context Management**:
   - Fit results in LLM context window
   - Prioritize most relevant chunks
   - Include metadata for citation
   - Keep chunk provenance

5. **Search Methods**:
   - Semantic: General questions, concept search
   - Keyword: Specific terms, code search
   - Hybrid: Best of both worlds
   - MMR: When diversity matters

---

## Quality Checklist

Before considering RAG retrieval complete:
- [ ] Semantic search working with embeddings
- [ ] Relevance scores returned and validated
- [ ] Metadata filtering implemented
- [ ] MMR available for diversity
- [ ] Hybrid search combining semantic + keyword
- [ ] Reranking with cross-encoder
- [ ] Deduplication working
- [ ] Context window fitting implemented
- [ ] Source citations included
- [ ] CLI or API for queries
- [ ] Performance benchmarked (latency, quality)

---

## Integration with Todo App

### Phase III: AI Task Assistant Retrieval

```python
# Initialize retriever with reranking
retriever = RerankingRetriever(
    collection_name="task_knowledge",
    persist_directory="./chroma_db"
)

# User asks question
user_query = "How do I filter tasks by status?"

# Retrieve relevant context
context_docs = retriever.search_with_reranking(
    query=user_query,
    k=3,  # Top 3 results
    fetch_k=10  # Rerank from 10 candidates
)

# Format context for LLM
context_text = "\n\n".join([
    f"Source: {doc['source']}\n{doc['content']}"
    for doc in context_docs
])

# Now pass to rag-answerer to generate response
print(f"Retrieved {len(context_docs)} relevant documents")
```

This retrieves the most relevant documentation chunks to answer the user's question about the Todo App.
