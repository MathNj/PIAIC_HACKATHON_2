---
name: prompt-engineering
description: Design and optimize prompts for AI models with proven patterns for accuracy, consistency, and performance. Use when: (1) Creating system prompts for AI agents, (2) Designing few-shot examples for tasks, (3) Implementing chain-of-thought reasoning, (4) Optimizing prompt templates, (5) Reducing hallucinations and improving accuracy, (6) Testing and iterating on prompts, or (7) Building prompt libraries for consistent AI behavior. This skill provides production-ready prompt patterns for OpenAI models and agents.
---

# Prompt Engineering

This skill provides production-ready patterns for designing and optimizing prompts for AI models.

## Core Principles

1. **Be Specific**: Clear, detailed instructions > vague requests
2. **Provide Context**: Background information improves responses
3. **Use Examples**: Few-shot learning dramatically improves accuracy
4. **Structure Output**: Request specific formats (JSON, lists, etc.)
5. **Iterate**: Test and refine prompts based on results

## Pattern 1: System Prompts

### Basic System Prompt

```python
SYSTEM_PROMPT = """You are a helpful assistant that helps users manage their tasks.

Your responsibilities:
- Help users create, update, and organize tasks
- Provide task prioritization suggestions
- Send reminders about upcoming deadlines
- Answer questions about task status

Communication style:
- Be concise and actionable
- Use bullet points for lists
- Confirm actions clearly
- Ask clarifying questions when needed
"""
```

### Role-Based System Prompt

```python
CODE_REVIEWER_PROMPT = """You are a senior software engineer conducting code reviews.

Your review focus:
1. **Bugs**: Identify logic errors, edge cases, and potential crashes
2. **Performance**: Spot inefficient algorithms and resource leaks
3. **Security**: Check for vulnerabilities (SQL injection, XSS, etc.)
4. **Best Practices**: Verify coding standards and design patterns
5. **Maintainability**: Assess code readability and documentation

Review format:
- Start with overall assessment (approve/needs work/reject)
- List issues by severity (critical/major/minor)
- Provide specific code suggestions
- Be constructive and educational

Remember: Your goal is to improve code quality while helping the developer learn.
"""
```

### Constrained System Prompt

```python
DATA_ANALYST_PROMPT = """You are a data analyst assistant.

Constraints:
- ONLY answer questions about data in the provided dataset
- If data is missing, say "This information is not in the dataset"
- Do NOT make assumptions or extrapolate beyond the data
- Always cite specific data points in your answers
- Use numbers and statistics, not generalizations

Output format:
1. Direct answer to the question
2. Supporting data points
3. Confidence level (high/medium/low)
"""
```

## Pattern 2: Few-Shot Learning

### Few-Shot Examples

```python
FEW_SHOT_TASK_CLASSIFICATION = """Classify user messages as task commands or general chat.

Examples:

User: "Create a task to buy groceries"
Classification: TASK_COMMAND
Action: create_task
Parameters: {"title": "buy groceries"}

User: "What's the weather like?"
Classification: GENERAL_CHAT
Action: None

User: "Mark task 123 as complete"
Classification: TASK_COMMAND
Action: update_task
Parameters: {"task_id": 123, "status": "completed"}

User: "How are you doing?"
Classification: GENERAL_CHAT
Action: None

Now classify this message:
User: "{user_message}"
"""
```

### Structured Output with Examples

```python
EXTRACT_TASK_INFO = """Extract task information from user messages.

Examples:

Input: "Create a high priority task to finish the report by Friday"
Output: {
  "action": "create",
  "title": "finish the report",
  "priority": "high",
  "due_date": "Friday"
}

Input: "Add a task for grocery shopping"
Output: {
  "action": "create",
  "title": "grocery shopping",
  "priority": "medium",
  "due_date": null
}

Input: "Update task 5 to completed status"
Output: {
  "action": "update",
  "task_id": 5,
  "status": "completed"
}

Now extract information from:
Input: "{user_message}"
Output:
"""
```

## Pattern 3: Chain-of-Thought (CoT)

### Basic Chain-of-Thought

```python
COT_PROMPT = """Let's solve this step by step:

1. First, understand what the user is asking
2. Break down the problem into smaller parts
3. Solve each part systematically
4. Combine the solutions
5. Verify the answer makes sense

User question: {question}

Let's think through this:
"""
```

### Structured Reasoning

```python
TASK_PRIORITIZATION_COT = """Help me prioritize these tasks using structured reasoning.

Step 1: List all tasks with their properties
Step 2: Identify urgent tasks (due soon or overdue)
Step 3: Identify important tasks (high business value)
Step 4: Apply Eisenhower Matrix:
   - Urgent + Important = Do first
   - Important + Not Urgent = Schedule
   - Urgent + Not Important = Delegate
   - Neither = Eliminate or do later
Step 5: Provide final prioritized list with reasoning

Tasks:
{tasks}

Let's begin the analysis:
"""
```

## Pattern 4: Output Formatting

### JSON Output

```python
JSON_OUTPUT_PROMPT = """Extract information and return ONLY valid JSON.

User message: "{message}"

Return JSON in this exact format:
{
  "intent": "create_task|update_task|list_tasks|delete_task|chat",
  "entities": {
    "task_id": number or null,
    "title": string or null,
    "description": string or null,
    "priority": "low|medium|high" or null,
    "status": "pending|completed" or null
  },
  "confidence": 0.0 to 1.0
}

JSON:
"""
```

### Markdown Output

```python
MARKDOWN_REPORT_PROMPT = """Generate a task summary report in Markdown format.

Include:
1. # Task Summary header
2. ## Statistics section (total, pending, completed)
3. ## High Priority Tasks section (if any)
4. ## Overdue Tasks section (if any)
5. ## Recently Completed section (last 5)

Use:
- **Bold** for emphasis
- Bullet points for lists
- Tables for structured data

Tasks data: {tasks}

Generate the report:
"""
```

## Pattern 5: Prompt Templates

### Template Library

```python
# app/prompts/templates.py

PROMPT_TEMPLATES = {
    "task_assistant": {
        "system": """You are a helpful task management assistant.
        Help users create, update, and organize their tasks.
        Be concise and actionable.""",

        "create_task": """Create a task from this message: "{message}"
        Extract: title, description, priority, due date
        Return JSON: {{"title": "...", "description": "...", ...}}""",

        "summarize_tasks": """Summarize these tasks for the user:
        {tasks}
        Include: total count, pending count, urgent items."""
    },

    "code_reviewer": {
        "system": """You are a senior code reviewer.
        Focus on bugs, performance, security, and best practices.""",

        "review_code": """Review this code:
        ```{language}
        {code}
        ```
        Provide: overall assessment, issues by severity, suggestions."""
    },

    "data_analyst": {
        "system": """You are a data analyst.
        Answer questions using only the provided dataset.
        Cite specific data points.""",

        "analyze_data": """Analyze this data and answer the question.

        Data:
        {data}

        Question: {question}

        Provide: direct answer, supporting data, confidence level."""
    }
}

def get_prompt(category: str, template_name: str, **kwargs) -> str:
    """Get formatted prompt template"""
    template = PROMPT_TEMPLATES[category][template_name]
    return template.format(**kwargs)
```

### Dynamic Prompt Builder

```python
# app/services/prompt_builder.py

class PromptBuilder:
    """Build prompts dynamically"""

    def __init__(self):
        self.parts = []

    def add_system(self, content: str):
        """Add system prompt"""
        self.parts.append(f"System: {content}")
        return self

    def add_context(self, context: dict):
        """Add context information"""
        context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
        self.parts.append(f"Context:\n{context_str}")
        return self

    def add_examples(self, examples: list[dict]):
        """Add few-shot examples"""
        examples_str = "\n\n".join(
            f"Input: {ex['input']}\nOutput: {ex['output']}"
            for ex in examples
        )
        self.parts.append(f"Examples:\n{examples_str}")
        return self

    def add_task(self, task: str):
        """Add main task"""
        self.parts.append(f"Task: {task}")
        return self

    def add_constraints(self, constraints: list[str]):
        """Add constraints"""
        constraints_str = "\n".join(f"- {c}" for c in constraints)
        self.parts.append(f"Constraints:\n{constraints_str}")
        return self

    def build(self) -> str:
        """Build final prompt"""
        return "\n\n".join(self.parts)

# Usage
prompt = (PromptBuilder()
    .add_system("You are a helpful assistant")
    .add_context({"user_name": "Alice", "task_count": 5})
    .add_examples([
        {"input": "add task", "output": "Created task"},
        {"input": "list tasks", "output": "Showing 5 tasks"}
    ])
    .add_task("Create a task to buy groceries")
    .add_constraints(["Be concise", "Return JSON"])
    .build())
```

## Pattern 6: Prompt Optimization

### A/B Testing Prompts

```python
# tests/test_prompts.py
import pytest

PROMPT_A = "Create a task from: {message}"
PROMPT_B = """Extract task information from this message: {message}
Return JSON with: title, description, priority, due_date"""

@pytest.mark.parametrize("message,expected_fields", [
    ("Buy groceries tomorrow", ["title", "due_date"]),
    ("High priority: finish report", ["title", "priority"]),
])
def test_prompt_variants(message, expected_fields):
    """Test which prompt extracts information better"""

    # Test Prompt A
    result_a = call_llm(PROMPT_A.format(message=message))
    score_a = score_extraction(result_a, expected_fields)

    # Test Prompt B
    result_b = call_llm(PROMPT_B.format(message=message))
    score_b = score_extraction(result_b, expected_fields)

    # Log results for analysis
    print(f"Prompt A score: {score_a}, Prompt B score: {score_b}")
```

### Iterative Refinement

```python
# Version history
PROMPT_V1 = "Summarize the tasks"
# Issue: Too vague, inconsistent format

PROMPT_V2 = "Summarize the tasks. Include total count and status breakdown."
# Improvement: More specific, but format still varies

PROMPT_V3 = """Summarize the tasks in this format:
- Total: X tasks
- Pending: Y tasks
- Completed: Z tasks
- High priority: W tasks"""
# Better: Specific format

PROMPT_V4 = """Summarize the tasks.

Format:
- Total: {count} tasks
- Pending: {pending} ({percentage}%)
- Completed: {completed} ({percentage}%)
- High Priority: {high_priority} tasks

Add a one-sentence summary highlighting what needs attention."""
# Best: Exact format + actionable insight
```

## Pattern 7: Reducing Hallucinations

### Constrained Responses

```python
NO_HALLUCINATION_PROMPT = """Answer the question using ONLY information from the provided context.

Rules:
1. If the answer is not in the context, say "I don't have this information"
2. Quote specific parts of the context in your answer
3. Do NOT make assumptions or extrapolate
4. Do NOT use external knowledge

Context:
{context}

Question: {question}

Answer (with citations):
"""
```

### Confidence Scoring

```python
CONFIDENCE_PROMPT = """Answer the question and provide a confidence score.

Question: {question}
Context: {context}

Response format:
Answer: [your answer]
Confidence: [0-100]
Reasoning: [why this confidence level]
Sources: [which parts of context support this]

If confidence < 70, say "I'm not certain, but..."
"""
```

## Pattern 8: Multi-Step Workflows

### Sequential Prompts

```python
# Step 1: Classify intent
CLASSIFY = "Classify user intent: {message}"

# Step 2: Extract entities
EXTRACT = """Based on intent '{intent}', extract relevant information from: {message}
Return JSON."""

# Step 3: Validate
VALIDATE = """Validate this extracted data: {data}
Check: required fields present, values in valid ranges, data types correct
Return: validation_passed (true/false), errors (list)"""

# Step 4: Generate response
GENERATE = """User requested: {intent}
Extracted data: {data}
Generate a confirmation message for the user."""
```

## Production Best Practices

### 1. Version Control Prompts

```python
# app/prompts/versions.py

PROMPTS = {
    "task_assistant": {
        "v1": "...",  # Original
        "v2": "...",  # Added examples
        "v3": "...",  # Improved format
        "current": "v3"
    }
}

def get_prompt_version(name: str, version: str = "current") -> str:
    """Get specific prompt version"""
    if version == "current":
        version = PROMPTS[name]["current"]
    return PROMPTS[name][version]
```

### 2. Prompt Metrics

```python
# app/services/prompt_metrics.py

class PromptMetrics:
    """Track prompt performance"""

    def __init__(self):
        self.metrics = defaultdict(lambda: {"total": 0, "success": 0, "tokens": 0})

    def record(self, prompt_name: str, success: bool, tokens: int):
        """Record prompt execution"""
        self.metrics[prompt_name]["total"] += 1
        if success:
            self.metrics[prompt_name]["success"] += 1
        self.metrics[prompt_name]["tokens"] += tokens

    def get_success_rate(self, prompt_name: str) -> float:
        """Get success rate for prompt"""
        m = self.metrics[prompt_name]
        return m["success"] / m["total"] if m["total"] > 0 else 0.0

    def get_avg_tokens(self, prompt_name: str) -> float:
        """Get average tokens per call"""
        m = self.metrics[prompt_name]
        return m["tokens"] / m["total"] if m["total"] > 0 else 0.0
```

### 3. Prompt Testing

```python
# tests/test_prompts.py

@pytest.mark.parametrize("input,expected", [
    ("Create a task to buy milk", {"action": "create", "title": "buy milk"}),
    ("Mark task 5 complete", {"action": "update", "task_id": 5}),
    ("List all my tasks", {"action": "list"}),
])
def test_prompt_accuracy(input, expected):
    """Test prompt extracts correct information"""
    result = call_llm_with_prompt(EXTRACT_PROMPT, input)
    assert result["action"] == expected["action"]
```

## Common Patterns

### Task Management Prompts

```python
CREATE_TASK_PROMPT = """Extract task creation details:

Message: "{message}"

Extract:
- title (required): Main task description
- description (optional): Additional details
- priority (optional): low/medium/high, default medium
- due_date (optional): Parse date references (tomorrow, Friday, etc.)

Return JSON."""

UPDATE_TASK_PROMPT = """Extract task update information:

Message: "{message}"

Identify:
- task_id: Which task (number or "current"/"last")
- updates: What fields to change (status, priority, title, etc.)

Return JSON."""
```

### Conversational Prompts

```python
CONVERSATIONAL_AGENT = """You are a friendly task assistant.

Conversation style:
- Greet users warmly
- Confirm actions clearly
- Offer helpful suggestions
- Ask clarifying questions when needed
- Use emojis sparingly and appropriately

Previous context: {context}
User message: {message}

Respond naturally:"""
```

## Troubleshooting

**Issue**: Inconsistent output format
**Solution**: Use explicit format instructions, provide examples, request JSON output

**Issue**: Hallucinations (making up information)
**Solution**: Add "use only provided information" constraint, implement confidence scoring

**Issue**: Missing information in responses
**Solution**: Use chain-of-thought, break down task into steps, add examples

**Issue**: Prompt too long/expensive
**Solution**: Remove redundant instructions, use shorter examples, optimize system prompt

**Issue**: Low accuracy on specific tasks
**Solution**: Add few-shot examples, increase temperature, test prompt variants

## Prompt Library Structure

```
app/prompts/
├── __init__.py
├── system/
│   ├── task_assistant.py
│   ├── code_reviewer.py
│   └── data_analyst.py
├── templates/
│   ├── classification.py
│   ├── extraction.py
│   └── generation.py
├── examples/
│   ├── few_shot_task.py
│   └── few_shot_code.py
└── utils/
    ├── builder.py
    ├── metrics.py
    └── versioning.py
```

## Testing Checklist

- [ ] Prompt produces correct output format
- [ ] Handles edge cases (empty input, invalid data)
- [ ] Consistent across multiple runs
- [ ] Doesn't hallucinate information
- [ ] Token usage is reasonable
- [ ] Performance meets requirements (accuracy, latency)
- [ ] Works with expected input variations
- [ ] Error messages are clear and helpful
