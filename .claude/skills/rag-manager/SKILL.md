# RAG Manager Skill

## Metadata
```yaml
name: rag-manager
description: Orchestrates complete RAG pipelines with lifecycle management, performance monitoring, scheduled updates, health checks, and multi-collection coordination. Manages indexing, retrieval, and answering workflows.
version: 1.0.0
category: ai-ml
tags: [rag, orchestration, pipeline, monitoring, lifecycle, health-check]
dependencies: [langchain, chromadb, apscheduler, prometheus-client]
```

## When to Use This Skill

Use this skill when:
- User says "Set up RAG system" or "Manage RAG pipeline"
- Need complete RAG orchestration (index → retrieve → answer)
- Managing multiple knowledge bases/collections
- Need scheduled index updates
- Want performance monitoring and metrics
- Building production RAG system
- Need health checks and observability
- Coordinating rag-indexer, rag-retriever, rag-answerer

## What This Skill Provides

### 1. Pipeline Orchestration
- **End-to-end RAG**: Index → Retrieve → Answer workflow
- **Multi-collection management**: Handle multiple knowledge bases
- **Configuration management**: Centralized settings
- **Component coordination**: Manage indexer, retriever, answerer

### 2. Lifecycle Management
- **Index creation**: Initialize new collections
- **Incremental updates**: Update existing indexes
- **Index deletion**: Clean up old collections
- **Version control**: Track index versions
- **Rollback**: Revert to previous index versions

### 3. Scheduled Operations
- **Auto-refresh**: Periodic index updates
- **Scheduled crawling**: Regular document ingestion
- **Maintenance tasks**: Optimization, cleanup
- **Report generation**: Usage and performance reports

### 4. Monitoring & Observability
- **Performance metrics**: Latency, throughput, accuracy
- **Cost tracking**: Token usage, API costs
- **Health checks**: System status monitoring
- **Error tracking**: Failed operations log
- **Usage analytics**: Query patterns, popular topics

### 5. Production Features
- **Load balancing**: Distribute queries across replicas
- **Caching**: Query and embedding caching
- **Rate limiting**: Control API usage
- **A/B testing**: Compare RAG configurations
- **Feature flags**: Toggle capabilities

---

## Installation

### Core Dependencies
```bash
# Using uv (recommended)
uv add langchain langchain-community langchain-openai
uv add chromadb sentence-transformers
uv add apscheduler  # For scheduling
uv add prometheus-client  # For metrics
uv add pyyaml  # For configuration

# Using pip
pip install langchain langchain-community langchain-openai
pip install chromadb sentence-transformers
pip install apscheduler prometheus-client pyyaml
```

### Optional Monitoring
```bash
# Prometheus metrics server
uv add prometheus-fastapi-instrumentator

# Grafana Loki for logging
uv add python-logging-loki
```

---

## Implementation Examples

### Example 1: Basic RAG Manager

```python
"""
Complete RAG manager orchestrating all components.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import json
from datetime import datetime
from dataclasses import dataclass, asdict

from rag_indexer import RAGIndexer, IncrementalIndexer
from rag_retriever import RerankingRetriever
from rag_answerer import ClaudeRAGAnswerer

@dataclass
class RAGConfig:
    """RAG system configuration."""
    collection_name: str
    persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_provider: str = "anthropic"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 3
    retrieval_fetch_k: int = 10
    min_confidence: float = 0.5

class RAGManager:
    """Manage complete RAG pipeline."""

    def __init__(self, config: RAGConfig):
        """
        Initialize RAG manager.

        Args:
            config: RAG system configuration
        """
        self.config = config
        self.metrics = {
            "queries_processed": 0,
            "documents_indexed": 0,
            "errors": 0,
            "total_cost_usd": 0.0
        }

        # Initialize components
        self.indexer = IncrementalIndexer(
            persist_directory=config.persist_directory,
            embedding_model=config.embedding_model,
            collection_name=config.collection_name
        )

        self.retriever = RerankingRetriever(
            persist_directory=config.persist_directory,
            collection_name=config.collection_name,
            embedding_model=config.embedding_model
        )

        self.answerer = ClaudeRAGAnswerer(
            model_name=config.llm_model,
            temperature=0
        )

        print(f"✓ RAG Manager initialized for collection: {config.collection_name}")

    @classmethod
    def from_yaml(cls, config_path: str) -> "RAGManager":
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        config = RAGConfig(**config_dict)
        return cls(config)

    def setup(
        self,
        document_paths: List[str],
        glob_pattern: str = "**/*.md"
    ) -> Dict[str, Any]:
        """
        Initial setup: Index documents.

        Args:
            document_paths: Directories to index
            glob_pattern: File pattern to match

        Returns:
            Setup statistics
        """
        print("Setting up RAG system...")

        total_docs = 0
        total_chunks = 0

        for path in document_paths:
            print(f"\nIndexing {path}...")

            stats = self.indexer.index_directory(
                directory=path,
                glob_pattern=glob_pattern,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )

            total_docs += stats['original_documents']
            total_chunks += stats['chunks_created']

        self.metrics['documents_indexed'] = total_chunks

        print(f"\n✓ Setup complete!")
        print(f"  Documents: {total_docs}")
        print(f"  Chunks: {total_chunks}")
        print(f"  Collection: {self.config.collection_name}")

        return {
            "documents": total_docs,
            "chunks": total_chunks,
            "collection": self.config.collection_name
        }

    def query(
        self,
        question: str,
        k: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve + answer.

        Args:
            question: User's question
            k: Number of context documents (default from config)
            min_confidence: Minimum confidence threshold

        Returns:
            Answer with metadata
        """
        k = k or self.config.retrieval_k
        min_confidence = min_confidence or self.config.min_confidence

        try:
            # Retrieve context
            context_docs = self.retriever.search_with_reranking(
                query=question,
                k=k,
                fetch_k=self.config.retrieval_fetch_k
            )

            # Generate answer
            result = self.answerer.answer_with_confidence(
                question=question,
                context_docs=context_docs
            )

            # Update metrics
            self.metrics['queries_processed'] += 1

            # Estimate cost (rough approximation)
            # Assuming ~1000 tokens total (context + answer)
            cost_per_query = 0.001  # $0.001 per query
            self.metrics['total_cost_usd'] += cost_per_query

            # Check confidence threshold
            if result['confidence'] < min_confidence:
                result['warning'] = f"Low confidence ({result['confidence']:.1%}). Answer may be unreliable."

            return result

        except Exception as e:
            self.metrics['errors'] += 1
            return {
                "error": str(e),
                "question": question,
                "answer": "I encountered an error processing your question. Please try again."
            }

    def update_index(
        self,
        document_paths: List[str],
        glob_pattern: str = "**/*.md"
    ) -> Dict[str, Any]:
        """
        Incrementally update index with new/changed documents.

        Args:
            document_paths: Directories to scan for changes
            glob_pattern: File pattern

        Returns:
            Update statistics
        """
        print("Updating index...")

        total_changed = 0

        for path in document_paths:
            stats = self.indexer.incremental_index(
                directory=path,
                glob_pattern=glob_pattern
            )
            total_changed += stats.get('changed_files', 0)

        print(f"✓ Updated {total_changed} changed files")

        return {
            "changed_files": total_changed,
            "timestamp": datetime.utcnow().isoformat()
        }

    def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        try:
            # Check collection exists and has documents
            collection_stats = self.indexer.get_collection_stats()

            # Test query
            test_result = self.retriever.search("test", k=1)

            return {
                "status": "healthy",
                "collection": collection_stats['collection_name'],
                "document_count": collection_stats['document_count'],
                "retrieval_working": len(test_result) > 0,
                "metrics": self.metrics,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        collection_stats = self.indexer.get_collection_stats()

        return {
            "queries_processed": self.metrics['queries_processed'],
            "documents_indexed": self.metrics['documents_indexed'],
            "errors": self.metrics['errors'],
            "total_cost_usd": self.metrics['total_cost_usd'],
            "collection_size": collection_stats['document_count'],
            "avg_cost_per_query": (
                self.metrics['total_cost_usd'] / self.metrics['queries_processed']
                if self.metrics['queries_processed'] > 0 else 0
            ),
            "timestamp": datetime.utcnow().isoformat()
        }

    def export_config(self, output_path: str):
        """Export current configuration to YAML."""
        config_dict = asdict(self.config)

        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

        print(f"✓ Configuration exported to {output_path}")


# Usage Example
if __name__ == "__main__":
    # Create configuration
    config = RAGConfig(
        collection_name="todo_app_kb",
        embedding_model="text-embedding-3-small",
        llm_model="claude-3-5-sonnet-20241022",
        retrieval_k=3
    )

    # Initialize manager
    manager = RAGManager(config)

    # Setup: Index documents
    manager.setup(
        document_paths=["./specs", "./docs"],
        glob_pattern="**/*.md"
    )

    # Query
    result = manager.query("How do I create a high-priority task?")
    print(f"\nAnswer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.1%}")

    # Health check
    health = manager.health_check()
    print(f"\nSystem Status: {health['status']}")
    print(f"Documents: {health['document_count']}")

    # Metrics
    metrics = manager.get_metrics()
    print(f"\nQueries: {metrics['queries_processed']}")
    print(f"Cost: ${metrics['total_cost_usd']:.4f}")
```

---

### Example 2: Scheduled Updates

```python
"""
RAG manager with scheduled index updates.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduledRAGManager(RAGManager):
    """RAG manager with automatic scheduled updates."""

    def __init__(self, config: RAGConfig):
        super().__init__(config)
        self.scheduler = BackgroundScheduler()
        self.document_paths = []

    def start_scheduler(
        self,
        document_paths: List[str],
        cron_schedule: str = "0 */6 * * *"  # Every 6 hours
    ):
        """
        Start scheduled index updates.

        Args:
            document_paths: Directories to monitor
            cron_schedule: Cron expression for schedule
        """
        self.document_paths = document_paths

        # Add update job
        self.scheduler.add_job(
            func=self._scheduled_update,
            trigger=CronTrigger.from_crontab(cron_schedule),
            id='rag_index_update',
            name='RAG Index Update',
            replace_existing=True
        )

        # Add metrics reporting job (daily)
        self.scheduler.add_job(
            func=self._report_metrics,
            trigger=CronTrigger.from_crontab("0 0 * * *"),  # Daily at midnight
            id='rag_metrics_report',
            name='RAG Metrics Report',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"✓ Scheduler started with cron: {cron_schedule}")

    def _scheduled_update(self):
        """Scheduled index update task."""
        logger.info("Running scheduled index update...")

        try:
            stats = self.update_index(self.document_paths)
            logger.info(f"✓ Update complete: {stats['changed_files']} files updated")

        except Exception as e:
            logger.error(f"✗ Scheduled update failed: {e}")
            self.metrics['errors'] += 1

    def _report_metrics(self):
        """Daily metrics reporting."""
        logger.info("Generating metrics report...")

        metrics = self.get_metrics()

        logger.info(f"Daily Metrics Report:")
        logger.info(f"  Queries: {metrics['queries_processed']}")
        logger.info(f"  Documents: {metrics['collection_size']}")
        logger.info(f"  Errors: {metrics['errors']}")
        logger.info(f"  Cost: ${metrics['total_cost_usd']:.2f}")

    def stop_scheduler(self):
        """Stop scheduler."""
        self.scheduler.shutdown()
        logger.info("✓ Scheduler stopped")


# Usage
config = RAGConfig(collection_name="todo_app_kb")
scheduled_manager = ScheduledRAGManager(config)

# Initial setup
scheduled_manager.setup(["./specs", "./docs"])

# Start scheduled updates (every 6 hours)
scheduled_manager.start_scheduler(
    document_paths=["./specs", "./docs"],
    cron_schedule="0 */6 * * *"
)

# Keep running
import time
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    scheduled_manager.stop_scheduler()
```

---

### Example 3: Multi-Collection Manager

```python
"""
Manage multiple RAG collections for different knowledge domains.
"""

class MultiCollectionRAGManager:
    """Manage multiple RAG collections."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize multi-collection manager."""
        self.persist_directory = persist_directory
        self.collections: Dict[str, RAGManager] = {}

    def create_collection(
        self,
        name: str,
        config: Optional[RAGConfig] = None
    ) -> RAGManager:
        """
        Create new RAG collection.

        Args:
            name: Collection name
            config: Optional configuration (uses defaults if not provided)

        Returns:
            RAG manager for the collection
        """
        if name in self.collections:
            raise ValueError(f"Collection '{name}' already exists")

        if config is None:
            config = RAGConfig(
                collection_name=name,
                persist_directory=self.persist_directory
            )

        manager = RAGManager(config)
        self.collections[name] = manager

        print(f"✓ Created collection: {name}")
        return manager

    def get_collection(self, name: str) -> RAGManager:
        """Get RAG manager for collection."""
        if name not in self.collections:
            raise ValueError(f"Collection '{name}' not found")

        return self.collections[name]

    def list_collections(self) -> List[str]:
        """List all collection names."""
        return list(self.collections.keys())

    def delete_collection(self, name: str):
        """Delete a collection."""
        if name in self.collections:
            # Clean up resources
            del self.collections[name]

            # Delete from vector DB
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_directory)
            try:
                client.delete_collection(name)
                print(f"✓ Deleted collection: {name}")
            except:
                print(f"⚠ Collection {name} not found in database")

    def query_best_collection(
        self,
        question: str,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Query all collections and return best answer.

        Args:
            question: User's question
            k: Number of results per collection

        Returns:
            Best answer across all collections
        """
        if not self.collections:
            return {"error": "No collections available"}

        results = []

        # Query each collection
        for name, manager in self.collections.items():
            result = manager.query(question, k=k)
            result['collection'] = name
            results.append(result)

        # Find best result by confidence
        best_result = max(results, key=lambda x: x.get('confidence', 0))

        return best_result

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get metrics across all collections."""
        total_queries = 0
        total_docs = 0
        total_cost = 0.0
        total_errors = 0

        collection_metrics = {}

        for name, manager in self.collections.items():
            metrics = manager.get_metrics()

            collection_metrics[name] = metrics

            total_queries += metrics['queries_processed']
            total_docs += metrics['collection_size']
            total_cost += metrics['total_cost_usd']
            total_errors += metrics['errors']

        return {
            "total_collections": len(self.collections),
            "total_queries": total_queries,
            "total_documents": total_docs,
            "total_cost_usd": total_cost,
            "total_errors": total_errors,
            "collections": collection_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }


# Usage - Managing multiple knowledge bases
multi_manager = MultiCollectionRAGManager()

# Create collections for different domains
docs_manager = multi_manager.create_collection("documentation")
docs_manager.setup(["./specs"], "**/*.md")

code_manager = multi_manager.create_collection("codebase")
code_manager.setup(["./backend", "./frontend"], "**/*.py")

api_manager = multi_manager.create_collection("api_docs")
api_manager.setup(["./specs/api"], "**/*.md")

# Query specific collection
result = docs_manager.query("How do I create a task?")

# Query all collections and get best answer
best_result = multi_manager.query_best_collection(
    "What is the authentication mechanism?"
)
print(f"Best answer from: {best_result['collection']}")
print(f"Answer: {best_result['answer']}")

# System-wide metrics
system_metrics = multi_manager.get_system_metrics()
print(f"\nSystem Metrics:")
print(f"  Collections: {system_metrics['total_collections']}")
print(f"  Documents: {system_metrics['total_documents']}")
print(f"  Queries: {system_metrics['total_queries']}")
```

---

### Example 4: RAG with Prometheus Metrics

```python
"""
RAG manager with Prometheus metrics for production monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

class MonitoredRAGManager(RAGManager):
    """RAG manager with Prometheus metrics."""

    # Define metrics
    query_counter = Counter(
        'rag_queries_total',
        'Total number of RAG queries'
    )

    query_latency = Histogram(
        'rag_query_latency_seconds',
        'RAG query latency in seconds'
    )

    error_counter = Counter(
        'rag_errors_total',
        'Total number of errors',
        ['error_type']
    )

    confidence_gauge = Gauge(
        'rag_answer_confidence',
        'Confidence score of last answer'
    )

    cost_counter = Counter(
        'rag_cost_usd_total',
        'Total cost in USD'
    )

    collection_size = Gauge(
        'rag_collection_documents',
        'Number of documents in collection'
    )

    def __init__(self, config: RAGConfig, metrics_port: int = 8000):
        """
        Initialize with Prometheus metrics.

        Args:
            config: RAG configuration
            metrics_port: Port for metrics endpoint
        """
        super().__init__(config)

        # Start Prometheus metrics server
        start_http_server(metrics_port)
        print(f"✓ Metrics server started on port {metrics_port}")

        # Update collection size metric
        self._update_collection_metric()

    def _update_collection_metric(self):
        """Update collection size metric."""
        try:
            stats = self.indexer.get_collection_stats()
            self.collection_size.set(stats['document_count'])
        except:
            pass

    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """Query with metrics tracking."""
        # Start timer
        start_time = time.time()

        try:
            # Increment query counter
            self.query_counter.inc()

            # Execute query
            result = super().query(question, **kwargs)

            # Record latency
            latency = time.time() - start_time
            self.query_latency.observe(latency)

            # Record confidence
            if 'confidence' in result:
                self.confidence_gauge.set(result['confidence'])

            # Record cost (estimate)
            cost = 0.001  # $0.001 per query
            self.cost_counter.inc(cost)

            return result

        except Exception as e:
            # Record error
            self.error_counter.labels(error_type=type(e).__name__).inc()
            raise

    def update_index(self, *args, **kwargs) -> Dict[str, Any]:
        """Update index with metrics."""
        result = super().update_index(*args, **kwargs)

        # Update collection size metric
        self._update_collection_metric()

        return result


# Usage - Production monitoring
config = RAGConfig(collection_name="production_kb")
monitored_manager = MonitoredRAGManager(config, metrics_port=8000)

# Setup
monitored_manager.setup(["./specs", "./docs"])

# Metrics available at http://localhost:8000/metrics
# Can be scraped by Prometheus and visualized in Grafana
```

---

## Configuration File Format

### rag-config.yaml
```yaml
# RAG System Configuration

collection_name: "todo_app_knowledge"
persist_directory: "./chroma_db"

# Embeddings
embedding_model: "text-embedding-3-small"  # or text-embedding-3-large

# LLM
llm_model: "claude-3-5-sonnet-20241022"
llm_provider: "anthropic"  # or openai, ollama
temperature: 0

# Chunking
chunk_size: 1000
chunk_overlap: 200

# Retrieval
retrieval_k: 3
retrieval_fetch_k: 10
reranking_enabled: true

# Quality
min_confidence: 0.5
score_threshold: 0.7

# Scheduling
auto_update_enabled: true
update_schedule: "0 */6 * * *"  # Every 6 hours

# Monitoring
metrics_enabled: true
metrics_port: 8000

# Document sources
document_paths:
  - "./specs"
  - "./docs"
  - "./backend/README.md"

glob_patterns:
  - "**/*.md"
  - "**/*.rst"
```

---

## CLI Tool

```python
"""
Comprehensive CLI for RAG management.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

app = typer.Typer(name="rag", help="RAG System Manager")
console = Console()

@app.command("setup")
def setup(
    config: str = typer.Option("rag-config.yaml", help="Config file"),
    paths: List[str] = typer.Option(None, help="Paths to index")
):
    """Setup RAG system with initial indexing."""
    manager = RAGManager.from_yaml(config)

    if paths:
        stats = manager.setup(paths)
    else:
        console.print("[yellow]No paths specified. Use --paths to index documents.[/yellow]")
        return

    console.print(f"[green]✓ Setup complete![/green]")
    console.print(f"  Documents: {stats['documents']}")
    console.print(f"  Chunks: {stats['chunks']}")

@app.command("ask")
def ask(
    question: str = typer.Argument(..., help="Your question"),
    config: str = typer.Option("rag-config.yaml", help="Config file")
):
    """Ask a question using RAG."""
    manager = RAGManager.from_yaml(config)

    console.print(f"[cyan]Question:[/cyan] {question}\n")

    with Progress() as progress:
        task = progress.add_task("[cyan]Thinking...", total=None)
        result = manager.query(question)
        progress.update(task, completed=True)

    console.print(f"[green]Answer:[/green]")
    console.print(result['answer'])

    if result.get('cited_sources'):
        console.print(f"\n[cyan]Sources:[/cyan]")
        for source in result['cited_sources']:
            console.print(f"  • {source['name']}")

@app.command("update")
def update(
    config: str = typer.Option("rag-config.yaml", help="Config file"),
    paths: List[str] = typer.Option(None, help="Paths to update")
):
    """Update index with new/changed documents."""
    manager = RAGManager.from_yaml(config)

    if not paths:
        console.print("[yellow]No paths specified[/yellow]")
        return

    stats = manager.update_index(paths)

    console.print(f"[green]✓ Updated {stats['changed_files']} files[/green]")

@app.command("health")
def health_check(
    config: str = typer.Option("rag-config.yaml", help="Config file")
):
    """Check RAG system health."""
    manager = RAGManager.from_yaml(config)

    health = manager.health_check()

    status_color = "green" if health['status'] == "healthy" else "red"
    console.print(f"Status: [{status_color}]{health['status']}[/{status_color}]")
    console.print(f"Documents: {health.get('document_count', 0)}")
    console.print(f"Queries Processed: {health['metrics']['queries_processed']}")

@app.command("metrics")
def show_metrics(
    config: str = typer.Option("rag-config.yaml", help="Config file")
):
    """Show performance metrics."""
    manager = RAGManager.from_yaml(config)

    metrics = manager.get_metrics()

    table = Table(title="RAG System Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Queries Processed", str(metrics['queries_processed']))
    table.add_row("Documents Indexed", str(metrics['collection_size']))
    table.add_row("Errors", str(metrics['errors']))
    table.add_row("Total Cost", f"${metrics['total_cost_usd']:.4f}")
    table.add_row("Avg Cost/Query", f"${metrics['avg_cost_per_query']:.4f}")

    console.print(table)

if __name__ == "__main__":
    app()
```

Usage:
```bash
# Initial setup
python rag_manager.py setup --paths ./specs --paths ./docs

# Ask question
python rag_manager.py ask "How do I create a task?"

# Update index
python rag_manager.py update --paths ./specs

# Health check
python rag_manager.py health

# View metrics
python rag_manager.py metrics
```

---

## FastAPI Integration

```python
"""
Production-ready FastAPI server for RAG system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="RAG System API")

# Global RAG manager
rag_manager: Optional[RAGManager] = None

@app.on_event("startup")
async def startup():
    """Initialize RAG system on startup."""
    global rag_manager

    config = RAGConfig.from_yaml("rag-config.yaml")
    rag_manager = MonitoredRAGManager(config, metrics_port=8000)

    print("✓ RAG system initialized")

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]

@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system."""
    if rag_manager is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    result = rag_manager.query(request.question, k=request.k)

    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])

    return QueryResponse(
        answer=result['answer'],
        confidence=result['confidence'],
        sources=result.get('cited_sources', [])
    )

@app.post("/api/v1/update")
async def update_index(background_tasks: BackgroundTasks):
    """Trigger index update (runs in background)."""
    if rag_manager is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    background_tasks.add_task(
        rag_manager.update_index,
        ["./specs", "./docs"]
    )

    return {"status": "Update started in background"}

@app.get("/api/v1/health")
async def health():
    """Health check endpoint."""
    if rag_manager is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    return rag_manager.health_check()

@app.get("/api/v1/metrics")
async def metrics():
    """Get system metrics."""
    if rag_manager is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    return rag_manager.get_metrics()

# Run with: uvicorn rag_api:app --reload
```

---

## Best Practices

1. **Configuration**:
   - Use YAML for environment-specific configs
   - Version control configurations
   - Separate dev/staging/prod settings
   - Document all configuration options

2. **Monitoring**:
   - Track query latency and throughput
   - Monitor embedding and LLM costs
   - Set up alerts for errors
   - Log all queries for analysis

3. **Maintenance**:
   - Schedule regular index updates
   - Monitor index freshness
   - Clean up old collections
   - Backup vector databases

4. **Performance**:
   - Cache frequent queries
   - Use batch operations
   - Monitor resource usage
   - Scale horizontally if needed

5. **Production**:
   - Implement health checks
   - Use structured logging
   - Set up metrics dashboards
   - Have rollback procedures

---

## Quality Checklist

Before deploying RAG system to production:
- [ ] Configuration management implemented
- [ ] All three components integrated (indexer, retriever, answerer)
- [ ] Health checks working
- [ ] Metrics collection enabled
- [ ] Scheduled updates configured
- [ ] Error handling comprehensive
- [ ] Logging structured and useful
- [ ] API endpoints secured
- [ ] Cost tracking implemented
- [ ] Documentation complete
- [ ] Monitoring dashboards set up
- [ ] Backup strategy defined

---

## Integration with Todo App

### Complete Production Setup

```python
# rag-config.yaml for Todo App
"""
collection_name: "todo_app_production"
persist_directory: "/var/lib/chroma_db"
embedding_model: "text-embedding-3-small"
llm_model: "claude-3-5-sonnet-20241022"
llm_provider: "anthropic"
chunk_size: 1000
chunk_overlap: 200
retrieval_k: 3
auto_update_enabled: true
update_schedule: "0 */6 * * *"
metrics_enabled: true
metrics_port: 8000
document_paths:
  - "/app/specs"
  - "/app/docs"
  - "/app/backend/README.md"
"""

# Production deployment
config = RAGConfig.from_yaml("/etc/todo-app/rag-config.yaml")
manager = MonitoredRAGManager(config, metrics_port=8000)

# Initial setup
manager.setup(config.document_paths)

# Start scheduled updates
scheduled_manager = ScheduledRAGManager(config)
scheduled_manager.start_scheduler(
    document_paths=config.document_paths,
    cron_schedule="0 */6 * * *"
)

# API integration
@app.post("/api/v1/ai/ask")
async def ai_assistant(question: str, user_id: int):
    """AI assistant endpoint for Todo App."""
    result = manager.query(question, k=3)

    # Log query for analytics
    log_ai_query(user_id, question, result)

    return {
        "answer": result['answer'],
        "confidence": result['confidence'],
        "sources": result['cited_sources']
    }
```

This creates a complete, production-ready RAG system for the Todo App's AI assistant feature in Phase III.
