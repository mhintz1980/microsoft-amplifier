# Agent Building Guide for Amplifier

This guide synthesizes Anthropic's latest research on agent building with the amplifier project's experience building effective AI agents. It provides practical patterns for creating tools, workflows, and agent systems that work seamlessly with both humans and AI.

## Core Principles

### 1. Agent-Computer Interface Design
Based on Anthropic's research, tools designed for agent consumption follow different principles than human-centric tools:

**✅ Agent-Optimized Tool Design:**
- **Response Format Enums**: Use structured responses with predictable formats
- **Natural Language Identifiers**: Replace technical UUIDs with descriptive names
- **Token Efficiency**: Minimize response size while maintaining information content
- **Consistent Error Handling**: Standardized error formats that agents can parse reliably
- **Progressive Disclosure**: Provide summary views with options for detailed expansion

**❌ Anti-Patterns to Avoid:**
- Verbose human-readable explanations
- Inconsistent response formats
- Technical identifiers without context
- Missing error handling or ambiguous error messages
- Overly complex nested structures

### 2. Systematic Tool Evaluation
Implement rigorous evaluation of all tools using the framework in `amplifier/utils/tool_evaluator.py`:

```python
from amplifier.utils.tool_evaluator import get_tool_evaluator, ToolTestCase

# Define test cases for your tool
test_cases = [
    ToolTestCase(
        name="basic_functionality",
        description="Test core tool functionality",
        input_data={"param": "value"},
        expected_output={"status": "success"},
        complexity="simple"
    )
]

# Evaluate tool performance
evaluator = get_tool_evaluator()
result = await evaluator.evaluate_tool("my_tool", tool_function, test_cases)

# Target metrics:
# - Success rate: >90%
# - Token usage: <1000 per call
# - Runtime: <5 seconds
# - Ergonomics: EXCELLENT or GOOD
```

### 3. Multi-Agent Workflow Patterns

#### Routing Pattern
Route tasks to specialized agents based on complexity and requirements:

```python
class TaskRouter:
    def route_task(self, task: Task) -> str:
        if task.complexity == "simple" and task.domain == "file_operations":
            return "file_handler_agent"
        elif task.requires_code_execution:
            return "code_execution_agent"
        elif task.domain == "analysis":
            return "analysis_agent"
        else:
            return "general_agent"
```

#### Parallelization Pattern
Execute independent tasks in parallel:

```python
async def process_documents_parallel(documents: List[str]) -> List[Result]:
    """Process multiple documents concurrently."""
    tasks = []
    for doc in documents:
        task = asyncio.create_task(process_single_document(doc))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

#### Evaluator-Optimizer Pattern
Add quality evaluation loops for critical outputs:

```python
async def generate_with_evaluation(prompt: str) -> str:
    """Generate output with quality evaluation."""
    # Generate initial output
    output = await generate_response(prompt)

    # Evaluate quality
    quality_score = await evaluate_quality(output, prompt)

    # Optimize if below threshold
    if quality_score < 0.8:
        output = await optimize_output(output, prompt)

    return output
```

## Context Engineering

### 1. Progressive Context Compression
Use the context compaction system in `amplifier/utils/context_compactor.py`:

```python
from amplifier.utils.context_compactor import get_context_compactor, ContextLevel

# Compress long conversations
compactor = get_context_compactor()
compressed = compactor.compress_context(
    context_chunks=chunks,
    target_level=ContextLevel.SUMMARY,
    max_tokens=20000
)

# Typical compression ratios:
# - FULL: 1.0x (no compression)
# - SUMMARY: 0.3x (70% reduction)
# - ESSENTIAL: 0.1x (90% reduction)
# - METADATA: 0.05x (95% reduction)
```

### 2. Just-in-Time Context Retrieval
Implement intelligent context loading:

```python
class ContextManager:
    async def get_relevant_context(self, query: str, max_tokens: int) -> str:
        """Retrieve most relevant context for query."""
        # Search memory for relevant chunks
        relevant_chunks = await self.search_memory(query)

        # Sort by relevance and importance
        sorted_chunks = sorted(relevant_chunks, key=lambda c: c.relevance_score)

        # Load until token limit reached
        context = ""
        current_tokens = 0
        for chunk in sorted_chunks:
            chunk_tokens = estimate_tokens(chunk.content)
            if current_tokens + chunk_tokens > max_tokens:
                break
            context += chunk.content + "\n\n"
            current_tokens += chunk_tokens

        return context
```

### 3. Memory Consolidation Patterns
Implement automatic memory consolidation:

```python
async def consolidate_session_memory(session_id: str):
    """Consolidate session memory into long-term storage."""
    # Get session messages
    messages = await get_session_messages(session_id)

    # Extract key insights and decisions
    insights = await extract_insights(messages)
    decisions = await extract_decisions(messages)

    # Store in long-term memory with metadata
    await store_insights(insights, session_id)
    await store_decisions(decisions, session_id)

    # Compress session context for future reference
    compressed = await compress_session_context(messages)
    await store_compressed_context(compressed, session_id)
```

## Code Execution with MCP

### 1. Secure Code Execution
Use the MCP code execution framework in `amplifier/mcp/code_execution.py`:

```python
from amplifier.mcp.code_execution import execute_code_safely, SecurityLevel

# Execute code securely
result = await execute_code_safely(
    code="print('Hello, World!')",
    language="python",
    security_level=SecurityLevel.MINIMAL
)

# Expected benefits:
# - 98.7% token reduction vs in-context execution
# - Automatic PII detection and tokenization
# - Docker-based sandboxing
# - Resource limits and monitoring
```

### 2. Skills System
Create reusable skills for common operations:

```python
from amplifier.mcp.code_execution import get_mcp_executor

# Register custom skill
executor = get_mcp_executor()
skill = Skill(
    name="data_analysis",
    code='''
import pandas as pd
import json

def analyze_data(data):
    df = pd.DataFrame(data)
    return {
        "summary": df.describe().to_dict(),
        "correlations": df.corr().to_dict()
    }

if __name__ == "__main__":
    with open("input.json", "r") as f:
        data = json.load(f)
    result = analyze_data(data)
    print(json.dumps(result, indent=2))
''',
    language="python"
)
executor.skill_registry.register_skill(skill, "data_analysis")

# Use skill
result = await executor.execute_skill("data_analysis", {"data": my_data})
```

### 3. Security Best Practices

#### PII Protection
```python
# Automatic PII detection and tokenization
pii_detector = PIIDetector()
pii_types = pii_detector.detect_pii(user_input)
if pii_types:
    # Tokenize PII before processing
    tokenized, mapping = pii_detector.tokenize_pii(user_input)
    # Process tokenized data
```

#### Resource Limits
```python
# Set appropriate resource limits
limits = ResourceLimits(
    max_runtime_seconds=30,
    max_memory_mb=512,
    max_cpu_percent=50.0,
    network_access=False  # Disable by default
)
```

## Tool Design Guidelines

### 1. Response Format Optimization

**Use Structured Responses:**
```python
# Good: Structured, token-efficient
{
    "status": "success",
    "files_processed": 25,
    "errors": [],
    "summary": "Processed 25 files successfully"
}

# Bad: Verbose, human-centric
{
    "result": "I have successfully processed your files. There were 25 files in total, and I was able to process all of them without encountering any errors. The processing went smoothly and all files have been handled according to your specifications."
}
```

**Natural Language Identifiers:**
```python
# Good: Descriptive identifiers
{
    "file_analyzer_result": {...},
    "validation_status": "passed",
    "next_action": "proceed_to_analysis"
}

# Bad: Technical identifiers
{
    "result_12345": {...},
    "status_abc": "passed",
    "action_def": "proceed"
}
```

### 2. Error Handling Patterns

**Consistent Error Format:**
```python
def handle_error(error: Exception, context: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "suggestions": get_error_suggestions(error)
    }
```

### 3. Performance Optimization

**Token Efficiency:**
```python
# Use enums for response formats
class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

# Instead of verbose status descriptions
return {"status": ResponseStatus.SUCCESS.value}
```

## Evaluation and Metrics

### 1. Tool Performance Metrics
Track these metrics for all tools:

- **Success Rate**: Percentage of successful executions (>90% target)
- **Token Efficiency**: Tokens used per execution (<1000 target)
- **Runtime**: Execution time in seconds (<5s target)
- **Ergonomics Score**: Agent-friendliness rating (EXCELLENT/GOOD target)

### 2. Context Management Metrics
- **Compression Ratio**: Tokens reduced through compression (>70% target)
- **Retrieval Accuracy**: Relevance of retrieved context (>85% target)
- **Memory Efficiency**: Storage optimization for long conversations

### 3. Agent Coordination Metrics
- **Task Routing Accuracy**: Correct agent selection (>95% target)
- **Parallelization Efficiency**: Speedup from concurrent execution
- **Quality Improvement**: Enhancement from evaluator-optimizer loops

## Implementation Checklist

### Tool Development
- [ ] Design agent-optimized interface
- [ ] Implement structured response formats
- [ ] Add comprehensive error handling
- [ ] Create evaluation test cases
- [ ] Measure performance metrics
- [ ] Optimize for token efficiency

### Context Management
- [ ] Implement progressive compression
- [ ] Set up just-in-time retrieval
- [ ] Configure memory consolidation
- [ ] Monitor compression ratios
- [ ] Validate context relevance

### Code Execution
- [ ] Configure Docker sandboxing
- [ ] Set up PII detection
- [ ] Define resource limits
- [ ] Create reusable skills
- [ ] Test security measures

### Multi-Agent Systems
- [ ] Implement task routing
- [ ] Set up parallelization
- [ ] Add evaluation loops
- [ ] Monitor coordination metrics
- [ ] Test failure recovery

## Best Practices Summary

1. **Design for Agents First**: Create tools that AI agents can use efficiently
2. **Measure Everything**: Track performance metrics and iterate based on data
3. **Embrace Parallelism**: Use concurrent execution where possible
4. **Prioritize Security**: Implement sandboxing and PII protection
5. **Optimize Context**: Use compression and intelligent retrieval
6. **Iterate Continuously**: Use evaluation frameworks to drive improvements

This guide provides the foundation for building effective agents in the amplifier project. By following these patterns and leveraging the implemented frameworks, you can create agent systems that are both powerful and efficient.