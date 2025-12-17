# RAG Answerer Skill

## Metadata
```yaml
name: rag-answerer
description: Generates answers from retrieved context using LLMs. Handles source citation, hallucination reduction, confidence scoring, and streaming responses for RAG applications.
version: 1.0.0
category: ai-ml
tags: [rag, llm, answer-generation, question-answering, claude, openai]
dependencies: [langchain, langchain-openai, langchain-anthropic]
```

## When to Use This Skill

Use this skill when:
- User says "Generate answer from documents" or "Answer with sources"
- Phase III: AI assistant needs to answer user questions
- Building Q&A system with citations
- Need to ground LLM responses in documents
- Want to reduce hallucinations with retrieved context
- Implementing chatbot with knowledge base
- Need confidence scores for answers

## What This Skill Provides

### 1. Answer Generation
- **Context-grounded responses**: Answers based only on retrieved documents
- **Source citation**: Cite specific documents/chunks
- **Confidence scoring**: Quantify answer quality
- **Hallucination detection**: Flag unsupported claims
- **Streaming responses**: Real-time answer generation

### 2. LLM Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus/Haiku
- **Local models**: Ollama, llama.cpp
- **Azure OpenAI**: Enterprise deployments

### 3. Prompting Strategies
- **Zero-shot**: Direct question answering
- **Few-shot**: Example-based prompting
- **Chain-of-Thought**: Step-by-step reasoning
- **ReAct**: Reasoning + Acting pattern
- **Self-consistency**: Multiple reasoning paths

### 4. Response Formats
- **Plain text**: Simple answers
- **Markdown**: Formatted responses
- **JSON**: Structured data
- **Citations**: Inline source references
- **Follow-up questions**: Clarification prompts

### 5. Quality Controls
- **Relevance checking**: Ensure answer addresses question
- **Source verification**: Validate citations
- **Confidence thresholds**: Filter low-quality answers
- **Fallback responses**: Handle insufficient context

---

## Installation

### Core Dependencies
```bash
# Using uv (recommended)
uv add langchain langchain-community
uv add langchain-openai  # For OpenAI models
uv add langchain-anthropic  # For Claude models

# Using pip
pip install langchain langchain-community
pip install langchain-openai langchain-anthropic
```

### Optional LLM Providers
```bash
# Local models with Ollama
uv add langchain-ollama

# Azure OpenAI
uv add langchain-openai azure-identity
```

---

## Implementation Examples

### Example 1: Basic RAG Answer Generator

```python
"""
Basic RAG answer generator with OpenAI GPT-4.
"""

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import Dict, Any, List, Optional
import os

class RAGAnswerer:
    """Generate answers from retrieved context."""

    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0,
        provider: str = "openai"
    ):
        """
        Initialize answer generator.

        Args:
            model_name: LLM model to use
            temperature: Creativity (0=deterministic, 1=creative)
            provider: LLM provider (openai, anthropic, ollama)
        """
        self.model_name = model_name
        self.temperature = temperature

        # Initialize LLM
        if provider == "openai":
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model=model_name,
                temperature=temperature,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def create_qa_prompt(self) -> PromptTemplate:
        """Create prompt template for QA."""
        template = """You are a helpful AI assistant. Use the following context to answer the question at the end.

If you don't know the answer based on the context, say "I don't have enough information to answer that question."

Always cite your sources using [Source: filename] format.

Context:
{context}

Question: {question}

Answer:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

    def answer(
        self,
        question: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate answer from question and context.

        Args:
            question: User's question
            context_docs: Retrieved documents with content and metadata

        Returns:
            Answer with sources and metadata
        """
        # Format context
        context_parts = []
        sources = []

        for i, doc in enumerate(context_docs, 1):
            source_name = doc.get('source', f"Document {i}")
            content = doc.get('content', '')

            context_parts.append(f"[Source {i}: {source_name}]\n{content}")
            sources.append({
                "id": i,
                "name": source_name,
                "score": doc.get('score', 0)
            })

        context_text = "\n\n".join(context_parts)

        # Create prompt
        prompt = self.create_qa_prompt()
        formatted_prompt = prompt.format(context=context_text, question=question)

        # Generate answer
        response = self.llm.invoke(formatted_prompt)
        answer_text = response.content

        # Parse citations from answer
        cited_sources = []
        for source in sources:
            if f"Source {source['id']}" in answer_text or source['name'] in answer_text:
                cited_sources.append(source)

        return {
            "answer": answer_text,
            "question": question,
            "sources": cited_sources,
            "all_sources": sources,
            "model": self.model_name,
            "has_sufficient_context": "don't have enough information" not in answer_text.lower()
        }

    def answer_with_confidence(
        self,
        question: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Answer with confidence score.

        Args:
            question: User's question
            context_docs: Retrieved documents

        Returns:
            Answer with confidence score (0-1)
        """
        result = self.answer(question, context_docs)

        # Calculate confidence based on:
        # 1. Number of relevant sources
        # 2. Average source scores
        # 3. Whether answer indicates uncertainty

        num_sources = len(result['cited_sources'])
        avg_score = sum(s['score'] for s in result['sources']) / len(result['sources']) if result['sources'] else 0

        # Confidence heuristic
        if not result['has_sufficient_context']:
            confidence = 0.2
        elif num_sources == 0:
            confidence = 0.3
        elif num_sources == 1:
            confidence = 0.5 + (avg_score * 0.3)
        else:
            confidence = 0.6 + (avg_score * 0.4)

        confidence = min(confidence, 1.0)

        result['confidence'] = confidence

        return result


# Usage Example
if __name__ == "__main__":
    from rag_retriever import RerankingRetriever

    # Initialize retriever
    retriever = RerankingRetriever(
        collection_name="todo_app_docs",
        persist_directory="./chroma_db"
    )

    # Initialize answerer
    answerer = RAGAnswerer(
        model_name="gpt-4-turbo-preview",
        temperature=0
    )

    # User question
    question = "How do I create a new task with high priority?"

    # Retrieve context
    print(f"Question: {question}\n")
    print("Retrieving context...")
    context_docs = retriever.search_with_reranking(question, k=3, fetch_k=10)
    print(f"✓ Retrieved {len(context_docs)} documents\n")

    # Generate answer
    print("Generating answer...")
    result = answerer.answer_with_confidence(question, context_docs)

    print(f"\n{'='*60}")
    print(f"ANSWER (Confidence: {result['confidence']:.1%}):")
    print(f"{'='*60}")
    print(result['answer'])
    print(f"\n{'='*60}")
    print(f"SOURCES CITED ({len(result['cited_sources'])}):")
    print(f"{'='*60}")
    for source in result['cited_sources']:
        print(f"  - {source['name']} (score: {source['score']:.3f})")
```

---

### Example 2: RAG with Claude (Anthropic)

```python
"""
RAG answer generator using Claude for higher quality responses.
"""

from langchain_anthropic import ChatAnthropic

class ClaudeRAGAnswerer(RAGAnswerer):
    """RAG answerer using Claude models."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0
    ):
        """Initialize with Claude."""
        self.model_name = model_name
        self.temperature = temperature

        self.llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def create_detailed_prompt(self) -> PromptTemplate:
        """Create detailed prompt for Claude."""
        template = """You are a knowledgeable AI assistant helping users with the Todo App.

Use the provided context to answer the question. Follow these guidelines:
1. Base your answer ONLY on the provided context
2. If the context doesn't contain enough information, explicitly say so
3. Cite sources using [Source: filename] format
4. Be concise but complete
5. If applicable, provide code examples from the context
6. Suggest related topics if relevant

Context:
{context}

Question: {question}

Please provide a helpful, accurate answer based on the context above."""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

    def answer_with_examples(
        self,
        question: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Answer with code examples if available."""
        result = self.answer(question, context_docs)

        # Extract code blocks from answer
        import re
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', result['answer'], re.DOTALL)

        result['code_examples'] = [
            {
                "language": lang or "text",
                "code": code.strip()
            }
            for lang, code in code_blocks
        ]

        return result


# Usage with Claude
claude_answerer = ClaudeRAGAnswerer(
    model_name="claude-3-5-sonnet-20241022"
)

result = claude_answerer.answer_with_examples(question, context_docs)

print(result['answer'])
if result['code_examples']:
    print(f"\n✓ Includes {len(result['code_examples'])} code examples")
```

---

### Example 3: Streaming RAG Answers

```python
"""
Stream RAG answers in real-time for better UX.
"""

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any

class StreamingRAGAnswerer(RAGAnswerer):
    """RAG answerer with streaming support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Enable streaming
        self.llm.streaming = True
        self.llm.callbacks = [StreamingStdOutCallbackHandler()]

    def stream_answer(
        self,
        question: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Stream answer generation."""
        # Format context
        context_parts = []
        sources = []

        for i, doc in enumerate(context_docs, 1):
            source_name = doc.get('source', f"Document {i}")
            content = doc.get('content', '')
            context_parts.append(f"[Source {i}: {source_name}]\n{content}")
            sources.append({"id": i, "name": source_name})

        context_text = "\n\n".join(context_parts)

        # Create prompt
        prompt = self.create_qa_prompt()
        formatted_prompt = prompt.format(context=context_text, question=question)

        print(f"Question: {question}\n")
        print("Answer: ", end="", flush=True)

        # Stream response
        response = self.llm.invoke(formatted_prompt)
        print("\n")

        return {
            "answer": response.content,
            "sources": sources,
            "streamed": True
        }


# Usage - answer streams to console in real-time
streaming_answerer = StreamingRAGAnswerer(
    model_name="gpt-4-turbo-preview",
    temperature=0
)

result = streaming_answerer.stream_answer(question, context_docs)
```

---

### Example 4: Chain-of-Thought RAG

```python
"""
Use chain-of-thought prompting for complex reasoning.
"""

class ChainOfThoughtRAGAnswerer(RAGAnswerer):
    """RAG with step-by-step reasoning."""

    def create_cot_prompt(self) -> PromptTemplate:
        """Create chain-of-thought prompt."""
        template = """You are a helpful AI assistant. Answer the question using the provided context.

Think through this step-by-step:
1. Identify the key parts of the question
2. Find relevant information in the context
3. Reason about how the information answers the question
4. Provide a clear, concise answer with citations

Context:
{context}

Question: {question}

Let's think step by step:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

    def answer_with_reasoning(
        self,
        question: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate answer with explicit reasoning."""
        # Use CoT prompt
        original_prompt = self.create_qa_prompt
        self.create_qa_prompt = self.create_cot_prompt

        result = self.answer(question, context_docs)

        # Restore original prompt
        self.create_qa_prompt = original_prompt

        # Parse reasoning steps from answer
        steps = []
        lines = result['answer'].split('\n')
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '-', '*')):
                steps.append(line.strip())

        result['reasoning_steps'] = steps

        return result


# Usage
cot_answerer = ChainOfThoughtRAGAnswerer()

result = cot_answerer.answer_with_reasoning(
    "What are all the steps to create and complete a task?",
    context_docs
)

print("Reasoning:")
for step in result['reasoning_steps']:
    print(f"  {step}")

print(f"\nAnswer:\n{result['answer']}")
```

---

### Example 5: Multi-Turn Conversation RAG

```python
"""
Handle multi-turn conversations with memory.
"""

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

class ConversationalRAGAnswerer:
    """RAG with conversation memory."""

    def __init__(
        self,
        retriever,
        model_name: str = "gpt-4-turbo-preview"
    ):
        """
        Initialize conversational RAG.

        Args:
            retriever: LangChain retriever object
            model_name: LLM model to use
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.retriever = retriever

        # Create memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        # Create conversational chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask question with conversation context.

        Args:
            question: User's question

        Returns:
            Answer with sources and chat history
        """
        result = self.chain({"question": question})

        return {
            "answer": result['answer'],
            "sources": [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get('source', 'Unknown')
                }
                for doc in result['source_documents']
            ],
            "chat_history": result.get('chat_history', [])
        }

    def clear_history(self):
        """Clear conversation history."""
        self.memory.clear()


# Usage - maintains context across questions
from langchain_community.vectorstores import Chroma

vectorstore = Chroma(
    persist_directory="./chroma_db",
    collection_name="todo_app_docs",
    embedding_function=OpenAIEmbeddings()
)

conv_answerer = ConversationalRAGAnswerer(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# First question
result1 = conv_answerer.ask("How do I create a task?")
print(f"Q1: {result1['answer']}\n")

# Follow-up (uses context from previous question)
result2 = conv_answerer.ask("Can I set its priority?")
print(f"Q2: {result2['answer']}\n")

# Another follow-up
result3 = conv_answerer.ask("What are the valid priority values?")
print(f"Q3: {result3['answer']}")
```

---

## Answer Quality Patterns

### Pattern 1: Fallback for Insufficient Context
```python
def answer_with_fallback(answerer, question, context_docs, min_confidence=0.5):
    """Answer with fallback if confidence too low."""
    result = answerer.answer_with_confidence(question, context_docs)

    if result['confidence'] < min_confidence:
        return {
            "answer": "I don't have enough reliable information to answer that question. Could you provide more context or rephrase your question?",
            "confidence": 0,
            "suggested_actions": [
                "Rephrase the question",
                "Provide more specific details",
                "Check if the information is in the knowledge base"
            ]
        }

    return result
```

### Pattern 2: Answer with Follow-up Questions
```python
def generate_followup_questions(answerer, question, answer_result):
    """Generate relevant follow-up questions."""
    followup_prompt = f"""Based on this Q&A, suggest 3 relevant follow-up questions:

Question: {question}
Answer: {answer_result['answer']}

Follow-up questions (numbered list):"""

    response = answerer.llm.invoke(followup_prompt)

    # Parse numbered list
    questions = []
    for line in response.content.split('\n'):
        line = line.strip()
        if line and line[0].isdigit():
            questions.append(line.split('.', 1)[1].strip())

    return questions[:3]
```

### Pattern 3: Multi-Answer Voting
```python
def answer_with_voting(answerer, question, context_docs, num_answers=3):
    """Generate multiple answers and select best via voting."""
    answers = []

    # Generate multiple answers with different temperatures
    for temp in [0, 0.3, 0.5]:
        answerer.llm.temperature = temp
        result = answerer.answer(question, context_docs)
        answers.append(result['answer'])

    # Use LLM to select best answer
    selection_prompt = f"""Given multiple answers to the same question, select the best one.

Question: {question}

Answer 1: {answers[0]}
Answer 2: {answers[1]}
Answer 3: {answers[2]}

Which answer is most accurate, complete, and well-cited? Respond with just the number (1, 2, or 3)."""

    answerer.llm.temperature = 0
    selection = answerer.llm.invoke(selection_prompt)
    best_idx = int(selection.content.strip()) - 1

    return answers[best_idx]
```

---

## FastAPI Integration

```python
"""
FastAPI endpoint for RAG Q&A.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Initialize RAG components globally
from rag_retriever import RerankingRetriever
from rag_answerer import RAGAnswerer

retriever = RerankingRetriever(collection_name="todo_app_docs")
answerer = RAGAnswerer(model_name="gpt-4-turbo-preview")

class Question(BaseModel):
    question: str
    k: int = 3
    min_confidence: float = 0.5

class Answer(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    has_sufficient_context: bool

@app.post("/api/v1/ask", response_model=Answer)
async def ask_question(question: Question):
    """Answer question using RAG."""
    try:
        # Retrieve context
        context_docs = retriever.search_with_reranking(
            question.question,
            k=question.k,
            fetch_k=question.k * 3
        )

        # Generate answer
        result = answerer.answer_with_confidence(
            question.question,
            context_docs
        )

        # Check confidence threshold
        if result['confidence'] < question.min_confidence:
            raise HTTPException(
                status_code=422,
                detail="Insufficient confidence in answer. Try rephrasing your question."
            )

        return Answer(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Usage:
# POST /api/v1/ask
# {"question": "How do I create a task?", "k": 3, "min_confidence": 0.5}
```

---

## CLI Tool

```python
"""
CLI for RAG question answering.
"""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

app = typer.Typer(name="rag-ask", help="RAG Question Answering")
console = Console()

@app.command("ask")
def ask_question(
    question: str = typer.Argument(..., help="Your question"),
    collection: str = typer.Option("documents", help="Collection name"),
    k: int = typer.Option(3, help="Number of context docs"),
    model: str = typer.Option("gpt-4-turbo-preview", help="LLM model")
):
    """Ask a question using RAG."""
    console.print(f"[cyan]Question:[/cyan] {question}\n")

    # Initialize components
    console.print("[dim]Retrieving context...[/dim]")
    retriever = RerankingRetriever(collection_name=collection)
    context_docs = retriever.search_with_reranking(question, k=k, fetch_k=k*3)

    console.print(f"[dim]✓ Retrieved {len(context_docs)} documents[/dim]\n")

    # Generate answer
    console.print("[dim]Generating answer...[/dim]")
    answerer = RAGAnswerer(model_name=model)
    result = answerer.answer_with_confidence(question, context_docs)

    # Display answer
    answer_panel = Panel(
        Markdown(result['answer']),
        title=f"Answer (Confidence: {result['confidence']:.0%})",
        border_style="green" if result['confidence'] > 0.7 else "yellow"
    )
    console.print(answer_panel)

    # Display sources
    if result['cited_sources']:
        console.print(f"\n[cyan]Sources ({len(result['cited_sources'])}):[/cyan]")
        for source in result['cited_sources']:
            console.print(f"  • {source['name']} (score: {source['score']:.3f})")

if __name__ == "__main__":
    app()
```

Usage:
```bash
# Ask a question
python rag_ask.py ask "How do I create a task?"

# With custom settings
python rag_ask.py ask "What is authentication?" --k 5 --model gpt-4
```

---

## Best Practices

1. **Context Management**:
   - Keep context under LLM token limits
   - Order context by relevance (best first)
   - Include metadata for citations
   - Remove redundant information

2. **Prompt Engineering**:
   - Instruct model to cite sources
   - Request structured output if needed
   - Set clear boundaries (answer only from context)
   - Include examples for complex tasks

3. **Quality Control**:
   - Always return confidence scores
   - Detect and flag hallucinations
   - Provide fallback for low-confidence answers
   - Include source citations

4. **Performance**:
   - Use streaming for better UX
   - Cache frequent questions
   - Use faster models for simple questions
   - Batch process when possible

5. **User Experience**:
   - Format answers with Markdown
   - Suggest follow-up questions
   - Provide source links for verification
   - Handle conversational context

---

## Quality Checklist

Before considering RAG answering complete:
- [ ] LLM integration working (OpenAI/Claude/local)
- [ ] Context correctly formatted for prompts
- [ ] Source citations included in answers
- [ ] Confidence scoring implemented
- [ ] Fallback for insufficient context
- [ ] Streaming responses (optional but recommended)
- [ ] Error handling for API failures
- [ ] Token limits respected
- [ ] Answer quality validated with test questions
- [ ] API or CLI interface available

---

## Integration with Todo App

### Phase III: Complete RAG Pipeline

```python
# Complete RAG pipeline for Todo App AI assistant

from rag_indexer import RAGIndexer
from rag_retriever import RerankingRetriever
from rag_answerer import ClaudeRAGAnswerer

# 1. Index knowledge base (one-time setup)
indexer = RAGIndexer(collection_name="todo_app_kb")
indexer.index_directory("./specs", "**/*.md")
indexer.index_directory("./docs", "**/*.md")

# 2. Initialize RAG components
retriever = RerankingRetriever(collection_name="todo_app_kb")
answerer = ClaudeRAGAnswerer(model_name="claude-3-5-sonnet-20241022")

# 3. User asks question
user_question = "How do I filter tasks by priority and status?"

# 4. Retrieve relevant context
context_docs = retriever.search_with_reranking(
    user_question,
    k=3,
    fetch_k=10
)

# 5. Generate answer
result = answerer.answer_with_confidence(user_question, context_docs)

# 6. Return to user
print(f"Answer (Confidence: {result['confidence']:.0%}):")
print(result['answer'])
print(f"\nSources: {', '.join(s['name'] for s in result['cited_sources'])}")
```

This creates a complete RAG system for the Todo App AI assistant that can answer user questions about tasks, features, and usage with cited sources.
