"""
Basic Usage Examples

Demonstrates fundamental usage of the signature framework with simple skills.
"""

import asyncio
from typing import Any

from pydantic import BaseModel

from .. import SignatureSkill
from .. import create_execution_context
from .. import initialize_framework
from .. import signature_skill
from ..base_types import ValidationMode

# Initialize the framework
initialize_framework()


# Example 1: Basic string processing skill
class TextProcessor(SignatureSkill[str, str]):
    """Simple text processing skill"""

    async def execute_core(self, input_data: str, context) -> str:
        """Process text input"""
        return f"Processed: {input_data.upper()}"


# Example 2: Using the decorator for quick skill creation
@signature_skill(skill_id="reverse_processor", description="Reverses input text")
async def reverse_text(input_data: str, context) -> str:
    """Reverse the input text"""
    return input_data[::-1]


# Example 3: Skill with Pydantic models for type safety
class DocumentRequest(BaseModel):
    content: str
    title: str
    metadata: dict[str, Any] = {}


class DocumentResponse(BaseModel):
    processed_content: str
    word_count: int
    confidence: float
    processing_time: float = 0.0


class DocumentProcessor(SignatureSkill[DocumentRequest, DocumentResponse]):
    """Advanced document processing skill"""

    async def execute_core(self, input_data: DocumentRequest, context) -> DocumentResponse:
        """Process document with word count and confidence"""
        import time

        start_time = time.time()
        processed_content = f"[{input_data.title}] {input_data.content}"
        word_count = len(input_data.content.split())
        confidence = min(1.0, word_count / 100.0)  # Higher confidence for longer documents

        return DocumentResponse(
            processed_content=processed_content,
            word_count=word_count,
            confidence=confidence,
            processing_time=time.time() - start_time,
        )


# Example 4: Skill with error handling and validation
class SafeCalculator(SignatureSkill[dict[str, Any], dict[str, Any]]):
    """Safe calculator with validation"""

    async def execute_core(self, input_data: dict[str, Any], context) -> dict[str, Any]:
        """Perform safe calculation operations"""

        # Validate input structure
        if "operation" not in input_data:
            raise ValueError("Missing 'operation' field")

        if "operands" not in input_data or not isinstance(input_data["operands"], list):
            raise ValueError("Missing or invalid 'operands' field")

        operation = input_data["operation"]
        operands = input_data["operands"]

        # Perform operation safely
        try:
            if operation == "add":
                result = sum(operands)
            elif operation == "multiply":
                result = 1
                for operand in operands:
                    result *= operand
            elif operation == "average":
                result = sum(operands) / len(operands) if operands else 0
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            return {"success": True, "result": result, "operation": operation, "operands": operands}

        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation, "operands": operands}


async def demonstrate_basic_usage():
    """Demonstrate basic skill usage"""
    print("=== Basic Signature Framework Usage ===\n")

    # Create execution context
    context = create_execution_context(
        user_id="demo_user",
        session_id="demo_session",
        validation_mode=ValidationMode.STRICT,
        zero_hallucination=True,
        enable_optimization=True,
    )

    # Example 1: Basic text processing
    print("1. Basic Text Processing:")
    processor = TextProcessor()
    result = await processor.execute_with_signature("hello world", context)

    print(f"   Success: {result.success}")
    print(f"   Result: {result.data}")
    print(f"   Confidence: {result.confidence:.3f}")
    print(f"   Execution Time: {result.execution_time:.4f}s\n")

    # Example 2: Decorator-based skill
    print("2. Decorator-Based Skill:")
    reverse_skill = reverse_text()
    result = await reverse_skill.execute_with_signature("Hello, World!", context)

    print(f"   Success: {result.success}")
    print(f"   Result: {result.data}")
    print(f"   Optimization Applied: {result.optimization_applied}\n")

    # Example 3: Type-safe document processing
    print("3. Type-Safe Document Processing:")
    doc_processor = DocumentProcessor()

    # Create a document request
    document = DocumentRequest(
        content="This is a sample document for processing.",
        title="Sample Document",
        metadata={"author": "Demo User", "category": "example"},
    )

    result = await doc_processor.execute_with_signature(document, context)

    print(f"   Success: {result.success}")
    print(f"   Title: {result.data.title}")
    print(f"   Processed Content: {result.data.processed_content}")
    print(f"   Word Count: {result.data.word_count}")
    print(f"   Confidence: {result.data.confidence:.3f}")
    print(f"   Processing Time: {result.data.processing_time:.4f}s\n")

    # Example 4: Safe calculator
    print("4. Safe Calculator with Error Handling:")

    # Successful calculation
    calc_request = {"operation": "add", "operands": [1, 2, 3, 4, 5]}

    calculator = SafeCalculator()
    result = await calculator.execute_with_signature(calc_request, context)

    print(f"   Success: {result.success}")
    print(f"   Operation: {result.data['operation']}")
    print(f"   Result: {result.data['result']}")
    print(f"   Validation Result: {result.validation_result.is_valid if result.validation_result else 'N/A'}")

    # Error case
    error_request = {"operation": "invalid_op", "operands": [1, 2]}

    result = await calculator.execute_with_signature(error_request, context)
    print(f"   Error Case Success: {result.success}")
    print(f"   Error: {result.data.get('error', 'No error')}\n")

    # Show skill metrics
    print("5. Skill Performance Metrics:")
    metrics = processor.get_metrics()
    print(
        f"   Text Processor - Executions: {metrics.executions}, "
        f"Success Rate: {metrics.success_rate:.2%}, "
        f"Avg Time: {metrics.average_execution_time:.4f}s"
    )

    metrics = reverse_skill.get_metrics()
    print(
        f"   Reverse Skill - Executions: {metrics.executions}, "
        f"Success Rate: {metrics.success_rate:.2%}, "
        f"Avg Time: {metrics.average_execution_time:.4f}s"
    )

    # Show framework statistics
    print("\n6. Framework Statistics:")
    from .. import get_framework_stats

    stats = get_framework_stats()
    print(f"   Version: {stats['version']}")
    print(f"   Components Loaded: {len(stats['components'])}")
    print(f"   Capabilities: {list(stats['capabilities'].keys())}")


async def demonstrate_bootstrap_learning():
    """Demonstrate BootstrapFewShot learning"""
    print("\n=== BootstrapFewShot Learning Demo ===\n")

    # Create a simple skill that learns from examples
    class Summarizer(SignatureSkill[str, str]):
        """Text summarization skill with BootstrapFewShot learning"""

        async def execute_core(self, input_data: str, context) -> str:
            """Summarize the input text"""
            # Simple summarization logic
            words = input_data.split()
            if len(words) <= 10:
                return input_data

            # Take first and last sentences for summary
            sentences = input_data.split(".")
            if len(sentences) > 2:
                return f"{sentences[0].strip()}. ... {sentences[-1].strip()}."
            return input_data

    # Create the skill
    summarizer = Summarizer()
    context = create_execution_context(enable_optimization=True)

    # Add bootstrap examples
    examples = [
        ("The quick brown fox jumps over the lazy dog.", "The quick brown fox jumps over the lazy dog."),
        (
            "This is a very long document that contains a lot of information. It has multiple sentences. The main point is important.",
            "This is a very long document... The main point is important.",
        ),
        (
            "AI is transforming technology. Machine learning is a subset of AI. Deep learning powers modern applications.",
            "AI is transforming technology... Deep learning powers modern applications.",
        ),
    ]

    for text, summary in examples:
        summarizer.add_bootstrap_example(text, summary)

    print("1. Bootstrap Examples Added:")
    print(f"   Examples: {len(summarizer.get_bootstrap_examples())}")

    # Test with new input
    test_text = "This is a new document that we want to summarize. It contains important information that should be captured in a concise summary."

    print("\n2. Testing with new input:")
    print(f"   Original: {test_text}")

    # First execution (no optimization)
    result1 = await summarizer.execute_with_signature(test_text, context)
    print(f"   Result: {result1.data}")
    print(f"   Optimization Applied: {result1.optimization_applied}")
    print(f"   Cache Hit: {result1.cache_hit}")

    # Second execution (should use optimization)
    result2 = await summarizer.execute_with_signature(test_text, context)
    print(f"   Result (cached): {result2.data}")
    print(f"   Optimization Applied: {result2.optimization_applied}")
    print(f"   Cache Hit: {result2.cache_hit}")

    # Show optimization info
    opt_info = summarizer.get_optimization_info()
    print("\n3. Optimization Information:")
    print(f"   Bootstrap Examples: {opt_info['bootstrap_examples_count']}")
    print(f"   Cache Size: {opt_info['cache_size']}")
    print(f"   Few-Shot Enabled: {opt_info['few_shot_enabled']}")
    print(f"   Compound Skills: {opt_info['compound_skills_count']}")


async def main():
    """Main demonstration function"""
    try:
        await demonstrate_basic_usage()
        await demonstrate_bootstrap_learning()

        print("\n=== Demo Completed Successfully ===")
        print("The signature framework is ready for use!")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
