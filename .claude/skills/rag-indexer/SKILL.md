# RAG Indexer Skill

## Metadata
```yaml
name: rag-indexer
description: Indexes documents, code, and data for retrieval-augmented generation (RAG). Handles chunking, embedding generation, and vector database storage using Chroma, Pinecone, Weaviate, or FAISS.
version: 1.0.0
category: ai-ml
tags: [rag, embeddings, vector-db, indexing, search, ai]
dependencies: [langchain, chromadb, openai, sentence-transformers]
```

## When to Use This Skill

Use this skill when:
- User says "Index documents for RAG" or "Create embeddings"
- Building knowledge base for AI assistants
- Implementing semantic search
- Phase III: AI-powered task assistant needs context
- Need to make documents/code searchable by meaning
- Setting up vector database for retrieval
- Creating document embeddings for similarity search

## What This Skill Provides

### 1. Document Chunking Strategies
- **Fixed-size chunking**: Split by character count
- **Recursive chunking**: Split by paragraph → sentence → word
- **Semantic chunking**: Split by topic/meaning boundaries
- **Code-aware chunking**: Respect function/class boundaries
- **Markdown-aware chunking**: Preserve headers and structure
- **Overlap strategy**: Maintain context between chunks

### 2. Embedding Generation
- **OpenAI embeddings**: text-embedding-3-small, text-embedding-3-large
- **Open-source models**: sentence-transformers (all-MiniLM-L6-v2, all-mpnet-base-v2)
- **Batch processing**: Efficient bulk embedding generation
- **Caching**: Avoid re-embedding unchanged content
- **Cost optimization**: Choose model based on quality/cost tradeoff

### 3. Vector Database Integration
- **Chroma**: Local-first, simple, Python-native (recommended for MVP)
- **Pinecone**: Managed, scalable, production-ready
- **Weaviate**: Open-source, GraphQL, multimodal
- **FAISS**: Facebook's library, fastest for local
- **pgvector**: PostgreSQL extension for existing DB

### 4. Document Loaders
- Markdown files (.md)
- Code files (.py, .js, .ts, .java, etc.)
- PDF documents
- Text files (.txt)
- JSON/YAML configuration files
- API documentation
- Git repositories

### 5. Metadata Management
- File paths and names
- Creation/modification timestamps
- Document type and format
- Author information
- Tags and categories
- Custom metadata fields

---

## Installation

### Core Dependencies
```bash
# Using uv (recommended)
uv add langchain langchain-community langchain-openai
uv add chromadb sentence-transformers
uv add tiktoken  # Token counting for OpenAI

# Using pip
pip install langchain langchain-community langchain-openai
pip install chromadb sentence-transformers tiktoken
```

### Optional Vector Databases
```bash
# Pinecone (managed cloud)
uv add pinecone-client

# Weaviate (self-hosted or cloud)
uv add weaviate-client

# FAISS (Facebook's library)
uv add faiss-cpu  # or faiss-gpu for GPU support
```

### Document Loaders
```bash
# PDF support
uv add pypdf

# Microsoft Office support
uv add python-docx python-pptx

# Web scraping
uv add beautifulsoup4 requests
```

---

## Implementation Examples

### Example 1: Basic RAG Indexer (Chroma + OpenAI)

```python
"""
Basic RAG indexer using Chroma and OpenAI embeddings.
Perfect for MVP and local development.
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.schema import Document
import os

class RAGIndexer:
    """Index documents for retrieval-augmented generation."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "text-embedding-3-small",
        collection_name: str = "documents"
    ):
        """
        Initialize RAG indexer.

        Args:
            persist_directory: Where to store Chroma database
            embedding_model: OpenAI embedding model to use
            collection_name: Name of the collection in Chroma
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

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

    def chunk_documents(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: Documents to chunk
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks

        Returns:
            List of chunked documents
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)

        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)

        return chunks

    def load_directory(
        self,
        directory: str,
        glob_pattern: str = "**/*.md",
        exclude_patterns: List[str] = None
    ) -> List[Document]:
        """
        Load documents from directory.

        Args:
            directory: Directory path to load from
            glob_pattern: Pattern to match files
            exclude_patterns: Patterns to exclude

        Returns:
            List of loaded documents
        """
        if exclude_patterns is None:
            exclude_patterns = ["**/node_modules/**", "**/.venv/**", "**/__pycache__/**"]

        loader = DirectoryLoader(
            directory,
            glob=glob_pattern,
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True,
            exclude=exclude_patterns
        )

        documents = loader.load()

        print(f"✓ Loaded {len(documents)} documents from {directory}")
        return documents

    def index_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Index documents into vector database.

        Args:
            documents: Documents to index
            batch_size: Number of documents per batch

        Returns:
            Indexing statistics
        """
        total_docs = len(documents)
        indexed_count = 0

        print(f"Indexing {total_docs} documents...")

        # Process in batches
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]

            # Add to vector store
            self.vectorstore.add_documents(batch)

            indexed_count += len(batch)
            print(f"✓ Indexed {indexed_count}/{total_docs} documents")

        return {
            "total_documents": total_docs,
            "indexed_count": indexed_count,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }

    def index_directory(
        self,
        directory: str,
        glob_pattern: str = "**/*.md",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Complete indexing pipeline for a directory.

        Args:
            directory: Directory to index
            glob_pattern: File pattern to match
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks

        Returns:
            Indexing statistics
        """
        # Load documents
        documents = self.load_directory(directory, glob_pattern)

        # Chunk documents
        chunks = self.chunk_documents(documents, chunk_size, chunk_overlap)
        print(f"✓ Created {len(chunks)} chunks from {len(documents)} documents")

        # Index chunks
        stats = self.index_documents(chunks)
        stats["original_documents"] = len(documents)
        stats["chunks_created"] = len(chunks)

        return stats

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed collection."""
        collection = self.client.get_collection(self.collection_name)

        return {
            "collection_name": self.collection_name,
            "document_count": collection.count(),
            "persist_directory": self.persist_directory
        }


# Usage Example
if __name__ == "__main__":
    # Initialize indexer
    indexer = RAGIndexer(
        persist_directory="./chroma_db",
        embedding_model="text-embedding-3-small",
        collection_name="todo_app_docs"
    )

    # Index documentation
    stats = indexer.index_directory(
        directory="./specs",
        glob_pattern="**/*.md",
        chunk_size=1000,
        chunk_overlap=200
    )

    print("\n📊 Indexing Complete:")
    print(f"  - Original documents: {stats['original_documents']}")
    print(f"  - Chunks created: {stats['chunks_created']}")
    print(f"  - Indexed: {stats['indexed_count']}")

    # Get collection stats
    collection_stats = indexer.get_collection_stats()
    print(f"\n📁 Collection: {collection_stats['collection_name']}")
    print(f"  - Total documents: {collection_stats['document_count']}")
```

---

### Example 2: Code-Aware Indexer

```python
"""
Code-aware indexer that respects code structure.
Splits code at function/class boundaries.
"""

from langchain.text_splitter import (
    Language,
    RecursiveCharacterTextSplitter,
)
from typing import List
from pathlib import Path

class CodeIndexer(RAGIndexer):
    """Specialized indexer for code files."""

    # Language configurations
    LANGUAGE_MAP = {
        ".py": Language.PYTHON,
        ".js": Language.JS,
        ".ts": Language.TS,
        ".java": Language.JAVA,
        ".cpp": Language.CPP,
        ".go": Language.GO,
        ".rs": Language.RUST,
        ".rb": Language.RUBY,
    }

    def chunk_code_file(
        self,
        file_path: str,
        chunk_size: int = 2000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """
        Chunk code file while respecting structure.

        Args:
            file_path: Path to code file
            chunk_size: Max characters per chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of code chunks
        """
        path = Path(file_path)
        suffix = path.suffix

        # Get language
        language = self.LANGUAGE_MAP.get(suffix)
        if not language:
            # Fall back to generic text splitter
            return self.chunk_documents(
                [Document(page_content=path.read_text(), metadata={"source": file_path})],
                chunk_size,
                chunk_overlap
            )

        # Create language-specific splitter
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Load and split
        code_content = path.read_text()
        chunks = splitter.create_documents(
            texts=[code_content],
            metadatas=[{
                "source": file_path,
                "language": language.value,
                "file_type": suffix
            }]
        )

        return chunks

    def index_codebase(
        self,
        codebase_path: str,
        file_extensions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Index entire codebase.

        Args:
            codebase_path: Root path of codebase
            file_extensions: Extensions to index (default: all supported)

        Returns:
            Indexing statistics
        """
        if file_extensions is None:
            file_extensions = list(self.LANGUAGE_MAP.keys())

        all_chunks = []
        file_count = 0

        # Process each file extension
        for ext in file_extensions:
            files = Path(codebase_path).rglob(f"*{ext}")

            for file_path in files:
                # Skip excluded paths
                if any(x in str(file_path) for x in ["node_modules", ".venv", "__pycache__"]):
                    continue

                try:
                    chunks = self.chunk_code_file(str(file_path))
                    all_chunks.extend(chunks)
                    file_count += 1
                    print(f"✓ Indexed {file_path.name} ({len(chunks)} chunks)")
                except Exception as e:
                    print(f"✗ Failed to index {file_path.name}: {e}")

        # Index all chunks
        stats = self.index_documents(all_chunks)
        stats["files_indexed"] = file_count
        stats["codebase_path"] = codebase_path

        return stats


# Usage
code_indexer = CodeIndexer(collection_name="todo_app_code")

stats = code_indexer.index_codebase(
    codebase_path="./backend",
    file_extensions=[".py", ".js", ".ts"]
)

print(f"\n✓ Indexed {stats['files_indexed']} code files")
print(f"  - Total chunks: {stats['chunks_created']}")
```

---

### Example 3: Advanced Indexer with Custom Metadata

```python
"""
Advanced indexer with custom metadata extraction.
"""

from datetime import datetime
import hashlib
from typing import Optional

class AdvancedIndexer(RAGIndexer):
    """Indexer with advanced metadata and deduplication."""

    def extract_metadata(self, document: Document) -> Dict[str, Any]:
        """Extract comprehensive metadata from document."""
        source = document.metadata.get("source", "")
        path = Path(source)

        metadata = {
            # File info
            "filename": path.name,
            "extension": path.suffix,
            "directory": str(path.parent),

            # Timestamps
            "indexed_at": datetime.utcnow().isoformat(),

            # Content hash for deduplication
            "content_hash": hashlib.sha256(
                document.page_content.encode()
            ).hexdigest()[:16],

            # Statistics
            "char_count": len(document.page_content),
            "word_count": len(document.page_content.split()),
            "line_count": document.page_content.count("\n") + 1,
        }

        # Add file stats if available
        if path.exists():
            stat = path.stat()
            metadata["file_size"] = stat.st_size
            metadata["modified_at"] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Merge with existing metadata
        document.metadata.update(metadata)
        return document.metadata

    def deduplicate_chunks(self, chunks: List[Document]) -> List[Document]:
        """Remove duplicate chunks based on content hash."""
        seen_hashes = set()
        unique_chunks = []

        for chunk in chunks:
            self.extract_metadata(chunk)
            content_hash = chunk.metadata["content_hash"]

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_chunks.append(chunk)

        removed = len(chunks) - len(unique_chunks)
        if removed > 0:
            print(f"✓ Removed {removed} duplicate chunks")

        return unique_chunks

    def index_with_metadata(
        self,
        directory: str,
        glob_pattern: str = "**/*.md",
        deduplicate: bool = True
    ) -> Dict[str, Any]:
        """Index with enhanced metadata and deduplication."""
        # Load documents
        documents = self.load_directory(directory, glob_pattern)

        # Chunk
        chunks = self.chunk_documents(documents)

        # Extract metadata
        for chunk in chunks:
            self.extract_metadata(chunk)

        # Deduplicate if requested
        if deduplicate:
            chunks = self.deduplicate_chunks(chunks)

        # Index
        stats = self.index_documents(chunks)

        return stats


# Usage
advanced_indexer = AdvancedIndexer(
    collection_name="todo_app_advanced"
)

stats = advanced_indexer.index_with_metadata(
    directory="./specs",
    glob_pattern="**/*.md",
    deduplicate=True
)
```

---

### Example 4: Incremental Indexing

```python
"""
Incremental indexer that only indexes changed files.
"""

import json
from typing import Set

class IncrementalIndexer(AdvancedIndexer):
    """Indexer that tracks changes and only indexes new/modified content."""

    def __init__(self, *args, index_state_file: str = ".rag_index_state.json", **kwargs):
        super().__init__(*args, **kwargs)
        self.index_state_file = Path(index_state_file)
        self.index_state = self._load_index_state()

    def _load_index_state(self) -> Dict[str, str]:
        """Load previous indexing state."""
        if self.index_state_file.exists():
            with open(self.index_state_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_index_state(self):
        """Save current indexing state."""
        with open(self.index_state_file, 'w') as f:
            json.dump(self.index_state, f, indent=2)

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def get_changed_files(self, directory: str, glob_pattern: str) -> List[Path]:
        """Get list of new or modified files."""
        changed_files = []

        for file_path in Path(directory).rglob(glob_pattern):
            if not file_path.is_file():
                continue

            file_str = str(file_path)
            current_hash = self._get_file_hash(file_path)
            previous_hash = self.index_state.get(file_str)

            if current_hash != previous_hash:
                changed_files.append(file_path)
                self.index_state[file_str] = current_hash

        return changed_files

    def incremental_index(
        self,
        directory: str,
        glob_pattern: str = "**/*.md"
    ) -> Dict[str, Any]:
        """Index only changed files."""
        # Get changed files
        changed_files = self.get_changed_files(directory, glob_pattern)

        if not changed_files:
            print("✓ No changes detected - index is up to date")
            return {"changed_files": 0, "indexed": 0}

        print(f"Found {len(changed_files)} changed files")

        # Load and chunk changed files
        all_chunks = []
        for file_path in changed_files:
            try:
                content = file_path.read_text()
                doc = Document(
                    page_content=content,
                    metadata={"source": str(file_path)}
                )
                chunks = self.chunk_documents([doc])
                all_chunks.extend(chunks)
                print(f"✓ Chunked {file_path.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"✗ Failed to process {file_path.name}: {e}")

        # Index chunks
        if all_chunks:
            stats = self.index_documents(all_chunks)
            stats["changed_files"] = len(changed_files)

            # Save state
            self._save_index_state()
            print("✓ Index state saved")
        else:
            stats = {"changed_files": len(changed_files), "indexed": 0}

        return stats


# Usage
incremental_indexer = IncrementalIndexer(
    collection_name="todo_app_incremental"
)

# First run - indexes everything
stats = incremental_indexer.incremental_index("./specs")
print(f"Indexed {stats['changed_files']} files")

# Second run - indexes only changes
stats = incremental_indexer.incremental_index("./specs")
print(f"Indexed {stats['changed_files']} changed files")
```

---

## Chunking Strategies

### Fixed-Size Chunking
```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separator="\n"
)
```

### Recursive Chunking (Recommended)
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]  # Try in order
)
```

### Semantic Chunking
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile"  # or "standard_deviation"
)
```

### Markdown-Aware Chunking
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
```

---

## Embedding Models

### OpenAI Embeddings (Recommended for Production)
```python
from langchain_openai import OpenAIEmbeddings

# Latest models (recommended)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # $0.02/1M tokens
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # $0.13/1M tokens

# Legacy models
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")  # $0.10/1M tokens
```

### Open-Source Embeddings (Free, Local)
```python
from langchain_community.embeddings import HuggingFaceEmbeddings

# Fast and lightweight (384 dimensions)
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Higher quality (768 dimensions)
embeddings = HuggingFaceEmbeddings(
    model_name="all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'}
)
```

---

## Vector Database Options

### Chroma (Recommended for MVP)
```python
from langchain_community.vectorstores import Chroma

vectorstore = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
```

### Pinecone (Recommended for Production)
```python
from langchain_community.vectorstores import Pinecone
import pinecone

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp"
)

vectorstore = Pinecone.from_documents(
    documents,
    embeddings,
    index_name="todo-app"
)
```

### FAISS (Fastest for Local)
```python
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(documents, embeddings)
vectorstore.save_local("faiss_index")

# Load later
vectorstore = FAISS.load_local("faiss_index", embeddings)
```

---

## CLI Tool

```python
"""
CLI for RAG indexing operations.
"""

import typer
from rich.console import Console
from rich.progress import track

app = typer.Typer(name="rag-index", help="RAG Indexing Tool")
console = Console()

@app.command("index")
def index_directory(
    directory: str = typer.Argument(..., help="Directory to index"),
    pattern: str = typer.Option("**/*.md", help="File pattern"),
    collection: str = typer.Option("documents", help="Collection name"),
    chunk_size: int = typer.Option(1000, help="Chunk size"),
):
    """Index a directory of documents."""
    console.print(f"[cyan]Indexing {directory}...[/cyan]")

    indexer = RAGIndexer(collection_name=collection)
    stats = indexer.index_directory(directory, pattern, chunk_size)

    console.print(f"[green]✓ Indexing complete![/green]")
    console.print(f"  Documents: {stats['original_documents']}")
    console.print(f"  Chunks: {stats['chunks_created']}")

@app.command("stats")
def show_stats(collection: str = typer.Option("documents", help="Collection name")):
    """Show collection statistics."""
    indexer = RAGIndexer(collection_name=collection)
    stats = indexer.get_collection_stats()

    console.print(f"[cyan]Collection: {stats['collection_name']}[/cyan]")
    console.print(f"  Documents: {stats['document_count']}")
    console.print(f"  Location: {stats['persist_directory']}")

if __name__ == "__main__":
    app()
```

Usage:
```bash
# Index specs directory
python rag_index.py index ./specs --pattern "**/*.md"

# Show stats
python rag_index.py stats --collection documents
```

---

## Best Practices

1. **Chunking**:
   - Use recursive splitter for most cases
   - Keep chunks 500-1000 characters for general text
   - Use 1000-2000 for code
   - Overlap 10-20% for context continuity

2. **Embeddings**:
   - Start with OpenAI text-embedding-3-small (good quality, low cost)
   - Use open-source models for sensitive data or offline use
   - Cache embeddings to avoid re-computation

3. **Metadata**:
   - Include source file path
   - Add timestamps for freshness
   - Include document type/category
   - Add custom fields for filtering

4. **Performance**:
   - Batch process for large datasets
   - Use incremental indexing for updates
   - Deduplicate chunks
   - Monitor token usage and costs

5. **Vector Databases**:
   - Chroma for local development and MVP
   - Pinecone for production scale
   - FAISS for offline/embedded systems

---

## Quality Checklist

Before considering RAG indexing complete:
- [ ] Documents loaded from all required sources
- [ ] Appropriate chunking strategy selected
- [ ] Embedding model configured and tested
- [ ] Vector database persisted correctly
- [ ] Metadata extracted and included
- [ ] Deduplication applied if needed
- [ ] Incremental indexing working for updates
- [ ] Collection statistics available
- [ ] Error handling for failed documents
- [ ] Cost/performance optimized
- [ ] CLI or API available for operations

---

## Integration with Todo App

### Phase III: AI Task Assistant

```python
# Index task-related documentation
indexer = RAGIndexer(collection_name="task_knowledge")

# Index specs
indexer.index_directory("./specs/features", "**/*.md")

# Index API docs
indexer.index_directory("./specs/api", "**/*.md")

# Index code (for code-aware assistant)
code_indexer = CodeIndexer(collection_name="task_code")
code_indexer.index_codebase("./backend", [".py"])

print("✓ Task knowledge base ready for RAG")
```

This creates a searchable knowledge base that the AI assistant can query to answer questions about tasks, features, and implementation details.
