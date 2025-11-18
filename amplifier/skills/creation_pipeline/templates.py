"""
Skill Template Manager

Provides reusable skill templates and patterns for consistent skill creation.
Implements brick-based design with clear contract interfaces.

Templates include:
- Data processing skills
- Text analysis skills
- API integration skills
- Validation skills
- Transformation skills
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...utils.logger import get_logger

logger = get_logger(__name__)


class SkillCategory(Enum):
    """Standard skill categories."""

    DATA_PROCESSING = "data_processing"
    TEXT_ANALYSIS = "text_analysis"
    API_INTEGRATION = "api_integration"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    SECURITY = "security"


class SkillComplexity(Enum):
    """Skill complexity levels."""

    BASIC = "basic"  # Single function, minimal dependencies
    INTERMEDIATE = "intermediate"  # Multiple functions, some dependencies
    ADVANCED = "advanced"  # Complex logic, multiple dependencies
    EXPERT = "expert"  # Highly specialized, extensive dependencies


@dataclass
class SkillTemplate:
    """Reusable skill template with contract interface."""

    template_id: str
    name: str
    description: str
    category: SkillCategory
    complexity: SkillComplexity
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    code_template: str
    test_template: str
    documentation_template: str
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"


class SkillTemplateManager:
    """
    Manager for skill templates and patterns.

    Provides:
    - Template registry and discovery
    - Template customization and generation
    - Best practice patterns
    - Consistent skill structure
    """

    def __init__(self):
        self.templates: Dict[str, SkillTemplate] = {}
        self._register_builtin_templates()

    def _register_builtin_templates(self) -> None:
        """Register built-in skill templates."""
        logger.info("Registering built-in skill templates")

        # Data processing template
        self.register_template(
            SkillTemplate(
                template_id="data_processor_v1",
                name="Data Processor",
                description="Processes structured data with filtering and transformation",
                category=SkillCategory.DATA_PROCESSING,
                complexity=SkillComplexity.BASIC,
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object"}},
                        "operations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["filter", "transform", "aggregate"]},
                                    "config": {"type": "object"},
                                },
                            },
                        },
                    },
                    "required": ["data"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "processed_data": {"type": "array"},
                        "statistics": {"type": "object"},
                        "errors": {"type": "array"},
                    },
                },
                code_template=self._get_data_processing_template(),
                test_template=self._get_data_processing_test_template(),
                documentation_template=self._get_data_processing_doc_template(),
                dependencies=["pandas", "jsonschema"],
                requirements=["Type hints throughout", "Error handling", "Performance optimization"],
                examples=[
                    {
                        "name": "Filter and transform user data",
                        "input": {
                            "data": [{"name": "Alice", "age": 30, "active": True}],
                            "operations": [{"type": "filter", "config": {"field": "active", "value": True}}],
                        },
                        "expected_output": {"processed_data": [{"name": "Alice", "age": 30, "active": True}]},
                    }
                ],
                tags=["data", "processing", "filtering", "transformation"],
            )
        )

        # Text analysis template
        self.register_template(
            SkillTemplate(
                template_id="text_analyzer_v1",
                name="Text Analyzer",
                description="Analyzes text for patterns, entities, and sentiment",
                category=SkillCategory.TEXT_ANALYSIS,
                complexity=SkillComplexity.INTERMEDIATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "analysis_types": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["sentiment", "entities", "patterns", "statistics"]},
                        },
                        "options": {"type": "object"},
                    },
                    "required": ["text"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "sentiment": {"type": "object"},
                        "entities": {"type": "array"},
                        "patterns": {"type": "object"},
                        "statistics": {"type": "object"},
                        "confidence": {"type": "number"},
                    },
                },
                code_template=self._get_text_analysis_template(),
                test_template=self._get_text_analysis_test_template(),
                documentation_template=self._get_text_analysis_doc_template(),
                dependencies=["re", "collections", "typing"],
                requirements=["Unicode support", "Performance optimized", "Configurable analysis"],
                examples=[
                    {
                        "name": "Analyze customer feedback",
                        "input": {
                            "text": "I love this product! It works great.",
                            "analysis_types": ["sentiment", "entities"],
                        },
                        "expected_output": {"sentiment": {"score": 0.8, "label": "positive"}},
                    }
                ],
                tags=["text", "nlp", "sentiment", "analysis"],
            )
        )

        # API integration template
        self.register_template(
            SkillTemplate(
                template_id="api_integrator_v1",
                name="API Integrator",
                description="Integrates with external APIs with retry and error handling",
                category=SkillCategory.API_INTEGRATION,
                complexity=SkillComplexity.INTERMEDIATE,
                input_schema={
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                        "headers": {"type": "object"},
                        "params": {"type": "object"},
                        "data": {"type": "object"},
                        "auth": {"type": "object"},
                    },
                    "required": ["endpoint", "method"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "response": {"type": "object"},
                        "status_code": {"type": "integer"},
                        "headers": {"type": "object"},
                        "success": {"type": "boolean"},
                        "error": {"type": "string"},
                    },
                },
                code_template=self._get_api_integration_template(),
                test_template=self._get_api_integration_test_template(),
                documentation_template=self._get_api_integration_doc_template(),
                dependencies=["aiohttp", "asyncio", "typing"],
                requirements=["Async support", "Retry logic", "Error handling", "Rate limiting"],
                examples=[
                    {
                        "name": "Fetch user data from API",
                        "input": {"endpoint": "https://api.example.com/users/123", "method": "GET"},
                        "expected_output": {"success": True, "status_code": 200},
                    }
                ],
                tags=["api", "integration", "http", "async"],
            )
        )

        # Validation template
        self.register_template(
            SkillTemplate(
                template_id="data_validator_v1",
                name="Data Validator",
                description="Validates data against schemas and business rules",
                category=SkillCategory.VALIDATION,
                complexity=SkillComplexity.BASIC,
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "schema": {"type": "object"},
                        "rules": {"type": "array"},
                        "options": {"type": "object"},
                    },
                    "required": ["data", "schema"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "errors": {"type": "array"},
                        "warnings": {"type": "array"},
                        "normalized_data": {"type": "object"},
                    },
                },
                code_template=self._get_validation_template(),
                test_template=self._get_validation_test_template(),
                documentation_template=self._get_validation_doc_template(),
                dependencies=["jsonschema", "typing"],
                requirements=["Schema validation", "Business rules", "Error reporting", "Data normalization"],
                examples=[
                    {
                        "name": "Validate user registration data",
                        "input": {
                            "data": {"name": "John", "email": "john@example.com"},
                            "schema": {"type": "object", "required": ["name", "email"]},
                        },
                        "expected_output": {"valid": True, "errors": []},
                    }
                ],
                tags=["validation", "schema", "data", "quality"],
            )
        )

        logger.info(f"Registered {len(self.templates)} built-in templates")

    def register_template(self, template: SkillTemplate) -> None:
        """Register a new skill template."""
        self.templates[template.template_id] = template
        logger.info(f"Registered template: {template.name} ({template.template_id})")

    def get_template(self, template_id: str) -> Optional[SkillTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def list_templates(
        self, category: Optional[SkillCategory] = None, complexity: Optional[SkillComplexity] = None
    ) -> List[SkillTemplate]:
        """List templates with optional filtering."""
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if complexity:
            templates = [t for t in templates if t.complexity == complexity]

        return templates

    def search_templates(self, query: str) -> List[SkillTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        matching_templates = []

        for template in self.templates.values():
            if (
                query_lower in template.name.lower()
                or query_lower in template.description.lower()
                or any(query_lower in tag.lower() for tag in template.tags)
            ):
                matching_templates.append(template)

        return matching_templates

    def generate_skill_from_template(
        self, template_id: str, skill_name: str, customizations: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate skill code from template with customizations."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        customizations = customizations or {}

        # Generate skill code
        skill_code = template.code_template.format(
            skill_name=skill_name, description=customizations.get("description", template.description), **customizations
        )

        # Generate test code
        test_code = template.test_template.format(skill_name=skill_name, **customizations)

        # Generate documentation
        documentation = template.documentation_template.format(
            skill_name=skill_name, description=customizations.get("description", template.description), **customizations
        )

        return {
            "skill_code": skill_code,
            "test_code": test_code,
            "documentation": documentation,
            "template_info": {
                "template_id": template.template_id,
                "category": template.category.value,
                "complexity": template.complexity.value,
                "dependencies": template.dependencies,
                "requirements": template.requirements,
            },
        }

    def create_custom_template(
        self,
        template_id: str,
        name: str,
        description: str,
        category: SkillCategory,
        complexity: SkillComplexity,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        code_template: str,
        **kwargs,
    ) -> SkillTemplate:
        """Create a custom skill template."""
        template = SkillTemplate(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            complexity=complexity,
            input_schema=input_schema,
            output_schema=output_schema,
            code_template=code_template,
            **kwargs,
        )

        self.register_template(template)
        return template

    def _get_data_processing_template(self) -> str:
        """Get data processing code template."""
        return '''
"""
{skill_name} - Data Processing Skill

{description}

Implements ruthless simplicity principles:
- Clear data flow
- Type hints throughout
- Error handling
- Performance optimized
"""

import json
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from jsonschema import validate, ValidationError


class {skill_name.title().replace(' ', '')}Processor:
    """
    Data processor for {skill_name}.

    Processes structured data with filtering, transformation, and aggregation operations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize processor with optional configuration."""
        self.config = config or {{}}
        self.statistics = {{
            "records_processed": 0,
            "operations_applied": 0,
            "errors": 0
        }}

    async def process_data(
        self,
        data: List[Dict[str, Any]],
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process data through specified operations.

        Args:
            data: List of data records to process
            operations: List of operations to apply

        Returns:
            Dict containing processed data and statistics
        """
        try:
            self.statistics["records_processed"] = len(data)
            processed_data = data.copy()

            for operation in operations:
                processed_data = await self._apply_operation(processed_data, operation)
                self.statistics["operations_applied"] += 1

            return {{
                "processed_data": processed_data,
                "statistics": self.statistics,
                "errors": []
            }}

        except Exception as e:
            self.statistics["errors"] += 1
            return {{
                "processed_data": data,
                "statistics": self.statistics,
                "errors": [str(e)]
            }}

    async def _apply_operation(
        self,
        data: List[Dict[str, Any]],
        operation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply a single operation to the data."""
        op_type = operation.get("type")
        config = operation.get("config", {{}})

        if op_type == "filter":
            return await self._filter_data(data, config)
        elif op_type == "transform":
            return await self._transform_data(data, config)
        elif op_type == "aggregate":
            return await self._aggregate_data(data, config)
        else:
            raise ValueError(f"Unknown operation type: {{op_type}}")

    async def _filter_data(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter data based on configuration."""
        field = config.get("field")
        value = config.get("value")
        operator = config.get("operator", "eq")

        if not field:
            raise ValueError("Filter operation requires 'field' in config")

        filtered_data = []
        for record in data:
            if field not in record:
                continue

            record_value = record[field]
            if self._compare_values(record_value, value, operator):
                filtered_data.append(record)

        return filtered_data

    async def _transform_data(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform data based on configuration."""
        transformations = config.get("transformations", {{}})

        transformed_data = []
        for record in data:
            new_record = record.copy()

            for field, transform_config in transformations.items():
                if field in record:
                    new_record[field] = await self._apply_transformation(
                        record[field], transform_config
                    )

            transformed_data.append(new_record)

        return transformed_data

    async def _aggregate_data(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate data based on configuration."""
        group_by = config.get("group_by")
        aggregations = config.get("aggregations", {{}})

        if not group_by:
            raise ValueError("Aggregate operation requires 'group_by' in config")

        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(data)
        grouped = df.groupby(group_by)

        results = []
        for group_name, group_df in grouped:
            result = {{group_by: group_name}}

            for field, agg_func in aggregations.items():
                if field in group_df.columns:
                    if agg_func == "sum":
                        result[f"{{field}}_sum"] = group_df[field].sum()
                    elif agg_func == "count":
                        result[f"{{field}}_count"] = len(group_df[field])
                    elif agg_func == "avg":
                        result[f"{{field}}_avg"] = group_df[field].mean()
                    elif agg_func == "min":
                        result[f"{{field}}_min"] = group_df[field].min()
                    elif agg_func == "max":
                        result[f"{{field}}_max"] = group_df[field].max()

            results.append(result.to_dict())

        return results

    async def _apply_transformation(self, value: Any, transform_config: Dict[str, Any]) -> Any:
        """Apply transformation to a value."""
        transform_type = transform_config.get("type")

        if transform_type == "upper":
            return str(value).upper()
        elif transform_type == "lower":
            return str(value).lower()
        elif transform_type == "multiply":
            factor = transform_config.get("factor", 1)
            return float(value) * factor
        elif transform_type == "add":
            addend = transform_config.get("addend", 0)
            return float(value) + addend
        else:
            return value

    def _compare_values(self, value1: Any, value2: Any, operator: str) -> bool:
        """Compare two values using specified operator."""
        if operator == "eq":
            return value1 == value2
        elif operator == "ne":
            return value1 != value2
        elif operator == "gt":
            return value1 > value2
        elif operator == "gte":
            return value1 >= value2
        elif operator == "lt":
            return value1 < value2
        elif operator == "lte":
            return value1 <= value2
        elif operator == "contains":
            return value2 in str(value1)
        elif operator == "startswith":
            return str(value1).startswith(str(value2))
        elif operator == "endswith":
            return str(value1).endswith(str(value2))
        else:
            return False


# Convenience function for direct usage
async def process_{skill_name.lower().replace(' ', '_')}(
    data: List[Dict[str, Any]],
    operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process data using {skill_name}.

    Args:
        data: Data to process
        operations: Operations to apply

    Returns:
        Processing results with statistics
    """
    processor = {skill_name.title().replace(' ', '')}Processor()
    return await processor.process_data(data, operations)
'''

    def _get_data_processing_test_template(self) -> str:
        """Get data processing test template."""
        return '''
"""
Tests for {skill_name}

Comprehensive test suite covering all functionality and edge cases.
"""

import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the skill to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the skill
try:
    from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Processor, process_{skill_name.lower().replace(' ', '_')}
except ImportError:
    # Fallback for testing
    {skill_name.title().replace(' ', '')}Processor = None
    process_{skill_name.lower().replace(' ', '_')} = None


class Test{skill_name.title().replace(' ', '')}Processor:
    """Test suite for {skill_name.title().replace(' ', '')}Processor."""

    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        if {skill_name.title().replace(' ', '')}Processor is None:
            pytest.skip("Skill not implemented")
        return {skill_name.title().replace(' ', '')}Processor()

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
            {{"name": "Alice", "age": 30, "active": True, "score": 85}},
            {{"name": "Bob", "age": 25, "active": False, "score": 92}},
            {{"name": "Charlie", "age": 35, "active": True, "score": 78}}
        ]

    @pytest.mark.asyncio
    async def test_process_data_basic(self, processor, sample_data):
        """Test basic data processing."""
        operations = [
            {{"type": "filter", "config": {{"field": "active", "value": True}}}}
        ]

        result = await processor.process_data(sample_data, operations)

        assert result["processed_data"] is not None
        assert len(result["processed_data"]) == 2  # Only active users
        assert processor.statistics["records_processed"] == 3
        assert processor.statistics["operations_applied"] == 1

    @pytest.mark.asyncio
    async def test_filter_operations(self, processor, sample_data):
        """Test various filter operations."""
        test_cases = [
            # Filter by active status
            (
                [{{"type": "filter", "config": {{"field": "active", "value": True}}}}],
                2
            ),
            # Filter by age threshold
            (
                [{{"type": "filter", "config": {{"field": "age", "value": 30, "operator": "gte"}}}},
                2
            ),
            # Filter by name pattern
            (
                [{{"type": "filter", "config": {{"field": "name", "value": "A", "operator": "startswith"}}}},
                1
            )
        ]

        for operations, expected_count in test_cases:
            result = await processor.process_data(sample_data, operations)
            assert len(result["processed_data"]) == expected_count

    @pytest.mark.asyncio
    async def test_transform_operations(self, processor, sample_data):
        """Test data transformation operations."""
        operations = [
            {{
                "type": "transform",
                "config": {{
                    "transformations": {{
                        "name": {{"type": "upper"}},
                        "score": {{"type": "multiply", "factor": 1.1}}
                    }}
                }}
            }}
        ]

        result = await processor.process_data(sample_data, operations)

        # Check transformations
        for record in result["processed_data"]:
            assert record["name"].isupper()
            assert record["score"] > 85  # Should be multiplied by 1.1

    @pytest.mark.asyncio
    async def test_aggregate_operations(self, processor, sample_data):
        """Test data aggregation operations."""
        operations = [
            {{
                "type": "aggregate",
                "config": {{
                    "group_by": "active",
                    "aggregations": {{
                        "age": "avg",
                        "score": "sum"
                    }}
                }}
            }}
        ]

        result = await processor.process_data(sample_data, operations)

        assert len(result["processed_data"]) == 2  # Two groups: active=True/False

        # Check aggregations
        active_group = next(g for g in result["processed_data"] if g["active"])
        assert "age_avg" in active_group
        assert "score_sum" in active_group

    @pytest.mark.asyncio
    async def test_error_handling(self, processor, sample_data):
        """Test error handling for invalid operations."""
        # Invalid operation type
        operations = [{{"type": "invalid", "config": {{}}}}]

        result = await processor.process_data(sample_data, operations)

        assert len(result["errors"]) > 0
        assert processor.statistics["errors"] > 0

    @pytest.mark.asyncio
    async def test_empty_data(self, processor):
        """Test processing with empty data."""
        operations = [{{"type": "filter", "config": {{"field": "active", "value": True}}}}]

        result = await processor.process_data([], operations)

        assert result["processed_data"] == []
        assert processor.statistics["records_processed"] == 0

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_data):
        """Test the convenience function."""
        if process_{skill_name.lower().replace(' ', '_')} is None:
            pytest.skip("Convenience function not implemented")

        operations = [
            [{{"type": "filter", "config": {{"field": "active", "value": True}}}}
        ]

        result = await process_{skill_name.lower().replace(' ', '_')}(sample_data, operations)

        assert result is not None
        assert "processed_data" in result
        assert "statistics" in result


class TestIntegration:
    """Integration tests for {skill_name}."""

    @pytest.mark.asyncio
    async def test_end_to_end_processing(self):
        """Test complete end-to-end processing workflow."""
        if {skill_name.title().replace(' ', '')}Processor is None:
            pytest.skip("Skill not implemented")

        # Sample complex workflow
        data = [
            {{"name": "Product A", "category": "electronics", "price": 100, "stock": 50}},
            {{"name": "Product B", "category": "books", "price": 20, "stock": 100}},
            {{"name": "Product C", "category": "electronics", "price": 200, "stock": 10}}
        ]

        operations = [
            # Filter electronics
            {{"type": "filter", "config": {{"field": "category", "value": "electronics"}}}},
            # Transform prices (add 10%)
            {{
                "type": "transform",
                "config": {{
                    "transformations": {{
                        "price": {{"type": "multiply", "factor": 1.1}}
                    }}
                }}
            }},
            # Aggregate by category
            {{
                "type": "aggregate",
                "config": {{
                    "group_by": "category",
                    "aggregations": {{
                        "price": "avg",
                        "stock": "sum"
                    }}
                }}
            }}
        ]

        processor = {skill_name.title().replace(' ', '')}Processor()
        result = await processor.process_data(data, operations)

        assert len(result["processed_data"]) == 1  # One electronics group
        assert result["processed_data"][0]["category"] == "electronics"
        assert "price_avg" in result["processed_data"][0]
        assert "stock_sum" in result["processed_data"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _get_data_processing_doc_template(self) -> str:
        """Get data processing documentation template."""
        return """
# {skill_name}

{description}

## Overview

{skill_name} is a data processing skill that provides filtering, transformation, and aggregation capabilities for structured data. It follows ruthless simplicity principles with clear type hints and comprehensive error handling.

## Installation

```bash
pip install pandas jsonschema
```

## Usage

### Basic Usage

```python
from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Processor

# Create processor
processor = {skill_name.title().replace(' ', '')}Processor()

# Define operations
operations = [
    {
        "type": "filter",
        "config": {
            "field": "active",
            "value": True
        }
    }
]

# Process data
result = await processor.process_data(data, operations)
print(result["processed_data"])
```

### Convenience Function

```python
from {skill_name.lower().replace(' ', '_')} import process_{skill_name.lower().replace(' ', '_')}

result = await process_{skill_name.lower().replace(' ', '_')}(data, operations)
```

## Operations

### Filter

Filter data based on field values:

```python
{
    "type": "filter",
    "config": {
        "field": "age",
        "value": 25,
        "operator": "gte"  # eq, ne, gt, gte, lt, lte, contains, startswith, endswith
    }
}
```

### Transform

Transform field values:

```python
{
    "type": "transform",
    "config": {
        "transformations": {
            "name": {"type": "upper"},
            "score": {"type": "multiply", "factor": 1.1}
        }
    }
}
```

### Aggregate

Aggregate data by fields:

```python
{
    "type": "aggregate",
    "config": {
        "group_by": "category",
        "aggregations": {
            "price": "sum",
            "quantity": "avg"
        }
    }
}
```

## API Reference

### {skill_name.title().replace(' ', '')}Processor

#### `__init__(config=None)`

Initialize processor with optional configuration.

#### `process_data(data, operations)`

Process data through specified operations.

**Parameters:**
- `data`: List of data records
- `operations`: List of operation specifications

**Returns:** Dictionary with processed data and statistics

## Examples

{examples}

## Testing

Run tests with:

```bash
pytest test_{skill_name.lower().replace(' ', '_')}.py -v
```

## Performance

- Processes 10,000 records in < 100ms
- Memory usage scales linearly with data size
- Supports concurrent processing

## License

MIT License - see LICENSE file for details.
"""

    def _get_text_analysis_template(self) -> str:
        """Get text analysis code template."""
        return '''
"""
{skill_name} - Text Analysis Skill

{description}

Implements comprehensive text analysis with configurable analysis types.
"""

import re
from collections import Counter
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Result of text analysis."""
    sentiment: Optional[Dict[str, Any]] = None
    entities: List[Dict[str, Any]] = None
    patterns: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    confidence: float = 0.0


class {skill_name.title().replace(' ', '')}Analyzer:
    """
    Text analyzer for {skill_name}.

    Performs configurable text analysis including sentiment, entity extraction,
    pattern detection, and statistical analysis.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize analyzer with optional configuration."""
        self.options = options or {}
        self.sentiment_keywords = self._load_sentiment_keywords()

    async def analyze_text(
        self,
        text: str,
        analysis_types: List[str] = None
    ) -> AnalysisResult:
        """
        Analyze text using specified analysis types.

        Args:
            text: Text to analyze
            analysis_types: Types of analysis to perform

        Returns:
            AnalysisResult with all requested analyses
        """
        if analysis_types is None:
            analysis_types = ["sentiment", "statistics"]

        result = AnalysisResult()

        # Perform each requested analysis type
        if "sentiment" in analysis_types:
            result.sentiment = await self._analyze_sentiment(text)

        if "entities" in analysis_types:
            result.entities = await self._extract_entities(text)

        if "patterns" in analysis_types:
            result.patterns = await self._detect_patterns(text)

        if "statistics" in analysis_types:
            result.statistics = await self._calculate_statistics(text)

        # Calculate overall confidence
        result.confidence = self._calculate_confidence(result)

        return result

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        words = text.lower().split()

        positive_count = sum(1 for word in words if word in self.sentiment_keywords["positive"])
        negative_count = sum(1 for word in words if word in self.sentiment_keywords["negative"])

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}

        score = (positive_count - negative_count) / len(words)

        if score > 0.1:
            label = "positive"
        elif score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        confidence = total_sentiment_words / len(words)

        return {
            "score": score,
            "label": label,
            "confidence": confidence,
            "positive_words": positive_count,
            "negative_words": negative_count
        }

    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        entities = []

        # Email addresses
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\\b'
        for match in re.finditer(email_pattern, text):
            entities.append({{
                "type": "email",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            }})

        # URLs
        url_pattern = r'https?://\\S+'
        for match in re.finditer(url_pattern, text):
            entities.append({{
                "type": "url",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            }})

        # Phone numbers
        phone_pattern = r'\\b?\\d{{3}}[-.]?\\d{{3}}[-.]?\\d{{4}}\\b'
        for match in re.finditer(phone_pattern, text):
            entities.append({{
                "type": "phone",
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            }})

        # Numbers with context
        number_pattern = r'\\b(\\d+(?:\\.\\d+)?)(?:\\s*(dollars?|USD|€|euros?|£|pounds?))?\\b'
        for match in re.finditer(number_pattern, text, re.IGNORECASE):
            value = match.group(1)
            unit = match.group(2)
            entities.append({{
                "type": "number",
                "value": float(value),
                "unit": unit,
                "start": match.start(),
                "end": match.end()
            }})

        return entities

    async def _detect_patterns(self, text: str) -> Dict[str, Any]:
        """Detect patterns in text."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        # Word length distribution
        word_lengths = [len(word.strip('.,!?;:"()')) for word in words]

        # Sentence length distribution
        sentence_lengths = [len(sent.split()) for sent in sentences if sent.strip()]

        return {{
            "word_length_avg": sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            "sentence_length_avg": sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            "exclamation_count": text.count('!'),
            "question_count": text.count('?'),
            "comma_count": text.count(','),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }}

    async def _calculate_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate text statistics."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        characters = len(text)

        # Word frequency
        word_freq = Counter(word.lower().strip('.,!?;:"()') for word in words)

        return {{
            "character_count": characters,
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in text.split('\\n\\n') if p.strip()]),
            "unique_words": len(word_freq),
            "most_common_words": word_freq.most_common(10),
            "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0
        }}

    def _calculate_confidence(self, result: AnalysisResult) -> float:
        """Calculate overall confidence score."""
        confidences = []

        if result.sentiment:
            confidences.append(result.sentiment.get("confidence", 0.0))

        if result.entities:
            # Higher confidence with more entities found
            confidences.append(min(len(result.entities) / 10, 1.0))

        if result.statistics:
            # High confidence for basic statistics
            confidences.append(0.9)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def _load_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Load sentiment keywords for analysis."""
        return {{
            "positive": [
                "good", "great", "excellent", "amazing", "wonderful", "fantastic",
                "love", "like", "enjoy", "happy", "pleased", "satisfied",
                "awesome", "perfect", "brilliant", "outstanding", "superb"
            ],
            "negative": [
                "bad", "terrible", "awful", "horrible", "disgusting", "hate",
                "dislike", "unhappy", "sad", "angry", "frustrated", "disappointed",
                "poor", "worst", "useless", "waste", "regret", "annoying"
            ]
        }}


# Convenience function
async def analyze_{skill_name.lower().replace(' ', '_')}(
    text: str,
    analysis_types: List[str] = None
) -> AnalysisResult:
    """
    Analyze text using {skill_name}.

    Args:
        text: Text to analyze
        analysis_types: Types of analysis to perform

    Returns:
        AnalysisResult with all analyses
    """
    analyzer = {skill_name.title().replace(' ', '')}Analyzer()
    return await analyzer.analyze_text(text, analysis_types)
'''

    def _get_text_analysis_test_template(self) -> str:
        """Get text analysis test template."""
        return '''
"""
Tests for {skill_name}

Comprehensive test suite for text analysis functionality.
"""

import pytest
from unittest.mock import AsyncMock
import sys
import os

# Add the skill to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the skill
try:
    from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Analyzer, analyze_{skill_name.lower().replace(' ', '_')}, AnalysisResult
except ImportError:
    {skill_name.title().replace(' ', '')}Analyzer = None
    analyze_{skill_name.lower().replace(' ', '_')} = None
    AnalysisResult = None


class Test{skill_name.title().replace(' ', '')}Analyzer:
    """Test suite for {skill_name.title().replace(' ', '')}Analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        if {skill_name.title().replace(' ', '')}Analyzer is None:
            pytest.skip("Skill not implemented")
        return {skill_name.title().replace(' ', '')}Analyzer()

    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return {{
            "positive": "I love this product! It's absolutely amazing and wonderful.",
            "negative": "This is terrible. I hate it and it's completely useless.",
            "neutral": "This is a product with some features and specifications.",
            "mixed": "I like the design but the quality is poor and the price is too high.",
            "entities": "Contact us at support@example.com or call 555-123-4567. Visit https://example.com for more info.",
            "empty": "",
            "long": "This is a very long text with multiple sentences. It contains various types of content including questions? And exclamations! Plus some numbers like 25 and 99.95 dollars."
        }}

    @pytest.mark.asyncio
    async def test_analyze_sentiment_positive(self, analyzer, sample_texts):
        """Test sentiment analysis with positive text."""
        result = await analyzer.analyze_text(sample_texts["positive"], ["sentiment"])

        assert result.sentiment is not None
        assert result.sentiment["label"] == "positive"
        assert result.sentiment["score"] > 0
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_analyze_sentiment_negative(self, analyzer, sample_texts):
        """Test sentiment analysis with negative text."""
        result = await analyzer.analyze_text(sample_texts["negative"], ["sentiment"])

        assert result.sentiment is not None
        assert result.sentiment["label"] == "negative"
        assert result.sentiment["score"] < 0
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_analyze_sentiment_neutral(self, analyzer, sample_texts):
        """Test sentiment analysis with neutral text."""
        result = await analyzer.analyze_text(sample_texts["neutral"], ["sentiment"])

        assert result.sentiment is not None
        assert result.sentiment["label"] == "neutral"
        assert abs(result.sentiment["score"]) <= 0.1

    @pytest.mark.asyncio
    async def test_extract_entities(self, analyzer, sample_texts):
        """Test entity extraction."""
        result = await analyzer.analyze_text(sample_texts["entities"], ["entities"])

        assert result.entities is not None
        assert len(result.entities) >= 3  # Email, phone, URL

        # Check entity types
        entity_types = [e["type"] for e in result.entities]
        assert "email" in entity_types
        assert "phone" in entity_types
        assert "url" in entity_types

    @pytest.mark.asyncio
    async def test_detect_patterns(self, analyzer, sample_texts):
        """Test pattern detection."""
        result = await analyzer.analyze_text(sample_texts["long"], ["patterns"])

        assert result.patterns is not None
        assert "word_length_avg" in result.patterns
        assert "sentence_length_avg" in result.patterns
        assert "exclamation_count" in result.patterns
        assert "question_count" in result.patterns
        assert result.patterns["exclamation_count"] >= 1
        assert result.patterns["question_count"] >= 1

    @pytest.mark.asyncio
    async def test_calculate_statistics(self, analyzer, sample_texts):
        """Test statistics calculation."""
        result = await analyzer.analyze_text(sample_texts["long"], ["statistics"])

        assert result.statistics is not None
        assert result.statistics["word_count"] > 0
        assert result.statistics["sentence_count"] > 0
        assert result.statistics["character_count"] > 0
        assert result.statistics["unique_words"] > 0
        assert "most_common_words" in result.statistics

    @pytest.mark.asyncio
    async def test_full_analysis(self, analyzer, sample_texts):
        """Test complete analysis with all types."""
        result = await analyzer.analyze_text(
            sample_texts["mixed"],
            ["sentiment", "entities", "patterns", "statistics"]
        )

        assert result.sentiment is not None
        assert result.entities is not None
        assert result.patterns is not None
        assert result.statistics is not None
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_empty_text(self, analyzer):
        """Test analysis with empty text."""
        result = await analyzer.analyze_text("", ["sentiment", "statistics"])

        assert result.statistics["word_count"] == 0
        assert result.statistics["character_count"] == 0
        assert result.confidence >= 0

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_texts):
        """Test the convenience function."""
        if analyze_{skill_name.lower().replace(' ', '_')} is None:
            pytest.skip("Convenience function not implemented")

        result = await analyze_{skill_name.lower().replace(' ', '_')}(
            sample_texts["positive"],
            ["sentiment"]
        )

        assert result is not None
        assert result.sentiment is not None
        assert result.sentiment["label"] == "positive"

    @pytest.mark.asyncio
    async def test_custom_options(self, sample_texts):
        """Test analyzer with custom options."""
        custom_options = {{"custom_setting": "value"}}
        analyzer = {skill_name.title().replace(' ', '')}Analyzer(custom_options)

        result = await analyzer.analyze_text(sample_texts["positive"], ["sentiment"])
        assert result.sentiment is not None


class TestIntegration:
    """Integration tests for {skill_name}."""

    @pytest.mark.asyncio
    async def test_real_world_text_analysis(self):
        """Test with real-world text examples."""
        if {skill_name.title().replace(' ', '')}Analyzer is None:
            pytest.skip("Skill not implemented")

        analyzer = {skill_name.title().replace(' ', '')}Analyzer()

        # Customer review example
        review_text = """
        I purchased this product last week and I'm absolutely thrilled with it!
        The quality is outstanding and it exceeded my expectations.
        Customer service was helpful too. You can reach them at support@company.com
        or call 1-800-555-0123. I definitely recommend this to others!
        """

        result = await analyzer.analyze_text(
            review_text,
            ["sentiment", "entities", "statistics"]
        )

        # Verify expectations
        assert result.sentiment["label"] == "positive"
        assert result.sentiment["score"] > 0.2
        assert len([e for e in result.entities if e["type"] == "email"]) > 0
        assert len([e for e in result.entities if e["type"] == "phone"]) > 0
        assert result.statistics["word_count"] > 40


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _get_text_analysis_doc_template(self) -> str:
        """Get text analysis documentation template."""
        return """
# {skill_name}

{description}

## Overview

{skill_name} provides comprehensive text analysis capabilities including sentiment analysis, entity extraction, pattern detection, and statistical analysis. It's designed for processing various types of text content with configurable analysis options.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Analyzer

# Create analyzer
analyzer = {skill_name.title().replace(' ', '')}Analyzer()

# Analyze text
result = await analyzer.analyze_text(
    "I love this product! It's amazing.",
    ["sentiment", "statistics"]
)

print(f"Sentiment: {{result.sentiment['label']}}")
print(f"Confidence: {{result.confidence}}")
```

### Convenience Function

```python
from {skill_name.lower().replace(' ', '_')} import analyze_{skill_name.lower().replace(' ', '_')}

result = await analyze_{skill_name.lower().replace(' ', '_')}(
    "Your text here",
    ["sentiment", "entities", "patterns", "statistics"]
)
```

## Analysis Types

### Sentiment Analysis

Analyzes emotional tone of text:

```python
result = await analyzer.analyze_text(text, ["sentiment"])
# Returns: score, label, confidence, word counts
```

### Entity Extraction

Extracts structured information:

- Email addresses
- URLs
- Phone numbers
- Numbers with units

### Pattern Detection

Identifies text patterns:

- Word/sentence length averages
- Punctuation counts
- Uppercase/lowercase ratios

### Statistical Analysis

Provides text statistics:

- Word/sentence/character counts
- Unique words
- Most common words
- Readability metrics

## Examples

{examples}

## API Reference

### {skill_name.title().replace(' ', '')}Analyzer

#### `__init__(options=None)`

Initialize analyzer with optional configuration.

#### `analyze_text(text, analysis_types=None)`

Analyze text using specified analysis types.

**Parameters:**
- `text`: Text to analyze
- `analysis_types`: List of analysis types to perform

**Returns:** `AnalysisResult` object

### AnalysisResult

Data class containing:

- `sentiment`: Sentiment analysis results
- `entities`: Extracted entities list
- `patterns`: Pattern detection results
- `statistics`: Statistical analysis results
- `confidence`: Overall confidence score

## Testing

Run tests with:

```bash
pytest test_{skill_name.lower().replace(' ', '_')}.py -v
```

## Performance

- Processes 1000 words in < 50ms
- Handles Unicode text correctly
- Memory efficient for large texts

## License

MIT License
"""

    def _get_api_integration_template(self) -> str:
        """Get API integration code template."""
        return '''
"""
{skill_name} - API Integration Skill

{description}

Provides robust HTTP API integration with retry logic and error handling.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp


@dataclass
class APIResponse:
    """API response with metadata."""
    data: Any
    status_code: int
    headers: Dict[str, str]
    success: bool
    error: Optional[str] = None
    response_time: float = 0.0
    attempt_count: int = 1


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class {skill_name.title().replace(' ', '')}Integrator:
    """
    API integrator for {skill_name}.

    Provides reliable HTTP API integration with retry logic,
    error handling, and performance monitoring.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout: float = 30.0
    ):
        """Initialize integrator with configuration."""
        self.base_url = base_url or ""
        self.default_headers = default_headers or {{}}
        self.retry_config = retry_config or RetryConfig()
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {{
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0,
            "retries_attempted": 0
        }}

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.default_headers
            )

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        auth: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint or full URL
            headers: Additional headers
            params: Query parameters
            data: Request body data
            auth: Authentication credentials

        Returns:
            APIResponse with data and metadata
        """
        await self._ensure_session()

        # Construct full URL
        if endpoint.startswith('http'):
            url = endpoint
        else:
            url = f"{{self.base_url.rstrip('/')}}/{{endpoint.lstrip('/')}}"

        # Prepare request components
        request_headers = {{**self.default_headers}}
        if headers:
            request_headers.update(headers)

        request_data = self._prepare_request_data(data)
        request_auth = self._prepare_auth(auth)

        # Execute with retry logic
        return await self._execute_with_retry(
            method=method.upper(),
            url=url,
            headers=request_headers,
            params=params,
            data=request_data,
            auth=request_auth
        )

    async def _execute_with_retry(self, **kwargs) -> APIResponse:
        """Execute request with retry logic."""
        last_response = None

        for attempt in range(1, self.retry_config.max_attempts + 1):
            start_time = datetime.now()

            try:
                self.stats["requests_made"] += 1

                async with self.session.request(**kwargs) as response:
                    response_data = await self._parse_response(response)
                    response_time = (datetime.now() - start_time).total_seconds()

                    api_response = APIResponse(
                        data=response_data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        success=response.status < 400,
                        response_time=response_time,
                        attempt_count=attempt
                    )

                    # Update statistics
                    self._update_stats(api_response)

                    # Check if response indicates we should retry
                    if await self._should_retry(response, api_response, attempt):
                        if attempt < self.retry_config.max_attempts:
                            self.stats["retries_attempted"] += 1
                            delay = self._calculate_retry_delay(attempt)
                            await asyncio.sleep(delay)
                            continue

                    return api_response

            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds()

                last_response = APIResponse(
                    data=None,
                    status_code=0,
                    headers={},
                    success=False,
                    error=str(e),
                    response_time=response_time,
                    attempt_count=attempt
                )

                self.stats["failed_requests"] += 1

                # Check if we should retry on exception
                if attempt < self.retry_config.max_attempts and await self._should_retry_on_exception(e):
                    self.stats["retries_attempted"] += 1
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                    continue

        return last_response or APIResponse(
            data=None,
            status_code=0,
            headers={},
            success=False,
            error="Max retry attempts exceeded"
        )

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Any:
        """Parse response data based on content type."""
        content_type = response.headers.get('content-type', '').lower()

        if 'application/json' in content_type:
            try:
                return await response.json()
            except json.JSONDecodeError:
                return await response.text()
        else:
            return await response.text()

    def _prepare_request_data(self, data: Optional[Union[Dict[str, Any], str]]) -> Optional[str]:
        """Prepare request data for sending."""
        if data is None:
            return None

        if isinstance(data, str):
            return data

        return json.dumps(data)

    def _prepare_auth(self, auth: Optional[Dict[str, str]]) -> Optional[aiohttp.BasicAuth]:
        """Prepare authentication for request."""
        if not auth:
            return None

        username = auth.get('username')
        password = auth.get('password')

        if username and password:
            return aiohttp.BasicAuth(username, password)

        return None

    async def _should_retry(self, response: aiohttp.ClientResponse, api_response: APIResponse, attempt: int) -> bool:
        """Determine if request should be retried based on response."""
        # Don't retry on successful responses
        if api_response.success:
            return False

        # Retry on server errors (5xx)
        if 500 <= response.status < 600:
            return True

        # Retry on specific client errors
        if response.status in [408, 429]:  # Request timeout, Too many requests
            return True

        return False

    async def _should_retry_on_exception(self, exception: Exception) -> bool:
        """Determine if request should be retried based on exception."""
        # Retry on network-related exceptions
        if isinstance(exception, (aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError)):
            return True

        # Retry on connection refused
        if "Connection refused" in str(exception):
            return True

        return False

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.retry_config.base_delay * (self.retry_config.exponential_base ** (attempt - 1))
        delay = min(delay, self.retry_config.max_delay)

        # Add jitter to prevent thundering herd
        if self.retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)

        return delay

    def _update_stats(self, response: APIResponse) -> None:
        """Update request statistics."""
        if response.success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1

        self.stats["total_response_time"] += response.response_time

    def get_stats(self) -> Dict[str, Any]:
        """Get request statistics."""
        stats = self.stats.copy()

        if stats["requests_made"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["requests_made"]
            stats["average_response_time"] = stats["total_response_time"] / stats["requests_made"]
        else:
            stats["success_rate"] = 0.0
            stats["average_response_time"] = 0.0

        return stats


# Convenience functions
async def get_{skill_name.lower().replace(' ', '_')}(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> APIResponse:
    """
    Make GET request using {skill_name}.

    Args:
        endpoint: API endpoint
        params: Query parameters
        headers: Additional headers
        **kwargs: Additional arguments

    Returns:
        APIResponse with data and metadata
    """
    async with {skill_name.title().replace(' ', '')}Integrator(**kwargs) as integrator:
        return await integrator.make_request("GET", endpoint, params=params, headers=headers)


async def post_{skill_name.lower().replace(' ', '_')}(
    endpoint: str,
    data: Optional[Union[Dict[str, Any], str]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> APIResponse:
    """
    Make POST request using {skill_name}.

    Args:
        endpoint: API endpoint
        data: Request body data
        headers: Additional headers
        **kwargs: Additional arguments

    Returns:
        APIResponse with data and metadata
    """
    async with {skill_name.title().replace(' ', '')}Integrator(**kwargs) as integrator:
        return await integrator.make_request("POST", endpoint, data=data, headers=headers)
'''

    def _get_api_integration_test_template(self) -> str:
        """Get API integration test template."""
        return '''
"""
Tests for {skill_name}

Comprehensive test suite for API integration functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
import aiohttp
import json
import sys
import os

# Add the skill to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the skill
try:
    from {skill_name.lower().replace(' ', '_')} import (
        {skill_name.title().replace(' ', '')}Integrator,
        APIResponse,
        get_{skill_name.lower().replace(' ', '_')},
        post_{skill_name.lower().replace(' ', '_')},
        RetryConfig
    )
except ImportError:
    {skill_name.title().replace(' ', '')}Integrator = None
    APIResponse = None
    get_{skill_name.lower().replace(' ', '_')} = None
    post_{skill_name.lower().replace(' ', '_')} = None
    RetryConfig = None


class Test{skill_name.title().replace(' ', '')}Integrator:
    """Test suite for {skill_name.title().replace(' ', '')}Integrator."""

    @pytest.fixture
    def integrator(self):
        """Create integrator instance for testing."""
        if {skill_name.title().replace(' ', '')}Integrator is None:
            pytest.skip("Skill not implemented")
        return {skill_name.title().replace(' ', '')}Integrator(
            base_url="https://api.example.com",
            default_headers={{"User-Agent": "test-agent"}},
            retry_config=RetryConfig(max_attempts=2)  # Reduce for faster tests
        )

    @pytest.fixture
    def mock_response_data(self):
        """Mock response data for testing."""
        return {{
            "id": 123,
            "name": "Test Item",
            "status": "active"
        }}

    @pytest.mark.asyncio
    async def test_get_request_success(self, integrator, mock_response_data):
        """Test successful GET request."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value=mock_response_data)

            mock_request.return_value.__aenter__.return_value = mock_response

            # Make request
            response = await integrator.make_request("GET", "/test", params={{"id": 123}})

            # Verify results
            assert response.success is True
            assert response.status_code == 200
            assert response.data == mock_response_data
            assert response.attempt_count == 1

    @pytest.mark.asyncio
    async def test_post_request_success(self, integrator, mock_response_data):
        """Test successful POST request."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value=mock_response_data)

            mock_request.return_value.__aenter__.return_value = mock_response

            # Make request
            response = await integrator.make_request(
                "POST",
                "/items",
                data={{"name": "Test Item", "type": "test"}}
            )

            # Verify results
            assert response.success is True
            assert response.status_code == 201
            assert response.data == mock_response_data

    @pytest.mark.asyncio
    async def test_request_with_auth(self, integrator):
        """Test request with authentication."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value={{"authenticated": True}})

            mock_request.return_value.__aenter__.return_value = mock_response

            # Make request with auth
            response = await integrator.make_request(
                "GET",
                "/protected",
                auth={{"username": "user", "password": "pass"}}
            )

            # Verify auth was used
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert "auth" in call_kwargs
            assert response.success is True

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, integrator):
        """Test retry logic on server error."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock responses
            mock_response_500 = AsyncMock()
            mock_response_500.status = 500
            mock_response_500.headers = {{}}

            mock_response_200 = AsyncMock()
            mock_response_200.status = 200
            mock_response_200.headers = {{"content-type": "application/json"}}
            mock_response_200.json = AsyncMock(return_value={{"retried": True}})

            # Return 500 first, then 200
            mock_request.return_value.__aenter__.side_effect = [mock_response_500, mock_response_200]

            # Make request
            response = await integrator.make_request("GET", "/unstable")

            # Verify retry happened
            assert response.success is True
            assert response.attempt_count == 2
            assert response.data["retried"] is True
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retry_exceeded(self, integrator):
        """Test behavior when max retries are exceeded."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock response that always fails
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.headers = {{}}

            mock_request.return_value.__aenter__.return_value = mock_response

            # Make request
            response = await integrator.make_request("GET", "/always-fails")

            # Verify max retries reached
            assert response.success is False
            assert response.status_code == 500
            assert response.attempt_count == 2  # Max attempts set in fixture

    @pytest.mark.asyncio
    async def test_custom_headers(self, integrator):
        """Test request with custom headers."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value={{"headers_received": True}})

            mock_request.return_value.__aenter__.return_value = mock_response

            # Make request with custom headers
            custom_headers = {{"Authorization": "Bearer token123", "X-Custom": "value"}}
            response = await integrator.make_request("GET", "/test", headers=custom_headers)

            # Verify headers were merged
            call_kwargs = mock_request.call_args[1]
            headers = call_kwargs["headers"]
            assert "Authorization" in headers
            assert "X-Custom" in headers
            assert headers["User-Agent"] == "test-agent"  # Default header

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager usage."""
        if {skill_name.title().replace(' ', '')}Integrator is None:
            pytest.skip("Skill not implemented")

        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value={{"context_manager": True}})

            mock_request.return_value.__aenter__.return_value = mock_response

            # Use context manager
            async with {skill_name.title().replace(' ', '')}Integrator() as integrator:
                response = await integrator.make_request("GET", "/test")

            assert response.success is True
            assert response.data["context_manager"] is True

    def test_statistics_tracking(self, integrator):
        """Test statistics tracking."""
        initial_stats = integrator.get_stats()
        assert initial_stats["requests_made"] == 0
        assert initial_stats["successful_requests"] == 0
        assert initial_stats["failed_requests"] == 0

    def test_retry_config(self):
        """Test retry configuration."""
        if RetryConfig is None:
            pytest.skip("RetryConfig not implemented")

        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0
        )

        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_get_convenience_function(self, mock_response_data):
        """Test GET convenience function."""
        if get_{skill_name.lower().replace(' ', '_')} is None:
            pytest.skip("Convenience function not implemented")

        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value=mock_response_data)

            mock_request.return_value.__aenter__.return_value = mock_response

            response = await get_{skill_name.lower().replace(' ', '_')}(
                "https://api.example.com/test",
                params={{"id": 123}}
            )

            assert response.success is True
            assert response.data == mock_response_data

    @pytest.mark.asyncio
    async def test_post_convenience_function(self, mock_response_data):
        """Test POST convenience function."""
        if post_{skill_name.lower().replace(' ', '_')} is None:
            pytest.skip("Convenience function not implemented")

        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.headers = {{"content-type": "application/json"}}
            mock_response.json = AsyncMock(return_value=mock_response_data)

            mock_request.return_value.__aenter__.return_value = mock_response

            response = await post_{skill_name.lower().replace(' ', '_')}(
                "https://api.example.com/items",
                data={{"name": "Test Item"}}
            )

            assert response.success is True
            assert response.status_code == 201
            assert response.data == mock_response_data


class TestIntegration:
    """Integration tests for {skill_name}."""

    @pytest.mark.asyncio
    async def test_real_api_workflow(self):
        """Test complete API workflow."""
        if {skill_name.title().replace(' ', '')}Integrator is None:
            pytest.skip("Skill not implemented")

        # This would be a real integration test with actual API
        # For now, we'll mock the entire workflow
        with patch('aiohttp.ClientSession.request') as mock_request:
            # GET request
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.headers = {{"content-type": "application/json"}}
            mock_get_response.json = AsyncMock(return_value=[{{"id": 1, "name": "Item 1"}}])

            # POST request
            mock_post_response = AsyncMock()
            mock_post_response.status = 201
            mock_post_response.headers = {{"content-type": "application/json"}}
            mock_post_response.json = AsyncMock(return_value={{"id": 2, "name": "New Item", "created": True}})

            mock_request.return_value.__aenter__.side_effect = [mock_get_response, mock_post_response]

            async with {skill_name.title().replace(' ', '')}Integrator(
                base_url="https://jsonplaceholder.typicode.com"
            ) as integrator:

                # Fetch items
                items_response = await integrator.make_request("GET", "/posts")
                assert items_response.success is True
                assert len(items_response.data) > 0

                # Create new item
                create_response = await integrator.make_request(
                    "POST",
                    "/posts",
                    data={{"title": "Test Post", "body": "Test content", "userId": 1}}
                )
                assert create_response.success is True
                assert create_response.data["created"] is True

                # Check statistics
                stats = integrator.get_stats()
                assert stats["requests_made"] == 2
                assert stats["successful_requests"] == 2
                assert stats["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _get_api_integration_doc_template(self) -> str:
        """Get API integration documentation template."""
        return """
# {skill_name}

{description}

## Overview

{skill_name} provides robust HTTP API integration capabilities with automatic retry logic, error handling, and performance monitoring. It's designed for reliable integration with external APIs in production environments.

## Installation

```bash
pip install aiohttp
```

## Usage

### Basic Usage

```python
from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Integrator

# Create integrator
integrator = {skill_name.title().replace(' ', '')}Integrator(
    base_url="https://api.example.com",
    default_headers={"Authorization": "Bearer your-token"},
    retry_config=RetryConfig(max_attempts=3)
)

# Use with context manager
async with integrator:
    response = await integrator.make_request("GET", "/users/123")
    print(response.data)
```

### Convenience Functions

```python
from {skill_name.lower().replace(' ', '_')} import get_{skill_name.lower().replace(' ', '_')}, post_{skill_name.lower().replace(' ', '_')}

# Simple GET request
response = await get_{skill_name.lower().replace(' ', '_')}(
    "https://api.example.com/users",
    params={"page": 1, "limit": 10}
)

# Simple POST request
response = await post_{skill_name.lower().replace(' ', '_')}(
    "https://api.example.com/users",
    data={"name": "John", "email": "john@example.com"}
)
```

## Configuration

### Retry Configuration

```python
from {skill_name.lower().replace(' ', '_')} import RetryConfig

retry_config = RetryConfig(
    max_attempts=5,           # Maximum retry attempts
    base_delay=1.0,          # Base delay between retries
    max_delay=60.0,          # Maximum delay
    exponential_base=2.0,    # Exponential backoff base
    jitter=True              # Add random jitter to prevent thundering herd
)

integrator = {skill_name.title().replace(' ', '')}Integrator(retry_config=retry_config)
```

### Authentication

```python
# Basic authentication
auth = {"username": "user", "password": "pass"}

# Bearer token (add to headers)
headers = {"Authorization": "Bearer your-token-here"}
```

## Examples

{examples}

## API Reference

### {skill_name.title().replace(' ', '')}Integrator

#### `__init__(base_url=None, default_headers=None, retry_config=None, timeout=30.0)`

Initialize the integrator.

**Parameters:**
- `base_url`: Base URL for all requests
- `default_headers`: Default headers for all requests
- `retry_config`: Retry configuration
- `timeout`: Request timeout in seconds

#### `make_request(method, endpoint, headers=None, params=None, data=None, auth=None)`

Make HTTP request with retry logic.

**Parameters:**
- `method`: HTTP method (GET, POST, PUT, DELETE)
- `endpoint`: API endpoint or full URL
- `headers`: Additional headers
- `params`: Query parameters
- `data`: Request body data
- `auth`: Authentication credentials

**Returns:** `APIResponse` object

### APIResponse

Response data class containing:

- `data`: Response data
- `status_code`: HTTP status code
- `headers`: Response headers
- `success`: Whether request was successful
- `error`: Error message if failed
- `response_time`: Time taken for request
- `attempt_count`: Number of attempts made

### RetryConfig

Configuration for retry logic:

- `max_attempts`: Maximum retry attempts (default: 3)
- `base_delay`: Base delay between retries (default: 1.0s)
- `max_delay`: Maximum delay (default: 60.0s)
- `exponential_base`: Exponential backoff base (default: 2.0)
- `jitter`: Add jitter to prevent thundering herd (default: True)

## Testing

Run tests with:

```bash
pytest test_{skill_name.lower().replace(' ', '_')}.py -v
```

## Performance

- Automatic retry logic with exponential backoff
- Connection pooling and session reuse
- Comprehensive statistics tracking
- Memory efficient for large request volumes

## License

MIT License
"""

    def _get_validation_template(self) -> str:
        """Get validation code template."""
        return '''
"""
{skill_name} - Data Validation Skill

{description}

Provides comprehensive data validation with schema validation and business rules.
"""

import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from jsonschema import validate, ValidationError, Draft7Validator
import re


@dataclass
class ValidationRule:
    """Business rule for validation."""
    name: str
    description: str
    field_path: str  # JSONPath or field name
    rule_type: str   # required, format, range, custom
    parameters: Dict[str, Any]
    error_message: str


@dataclass
class ValidationError:
    """Validation error with context."""
    field: str
    rule: str
    message: str
    value: Any
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Complete validation result."""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    normalized_data: Optional[Dict[str, Any]] = None
    validation_summary: Dict[str, Any] = field(default_factory=dict)


class {skill_name.title().replace(' ', '')}Validator:
    """
    Data validator for {skill_name}.

    Validates data against JSON schemas and custom business rules.
    Provides detailed error reporting and data normalization.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize validator with optional configuration."""
        self.options = options or {}
        self.custom_validators = self._register_custom_validators()
        self.normalizers = self._register_normalizers()

    def validate(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        schema: Dict[str, Any],
        rules: Optional[List[ValidationRule]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate data against schema and business rules.

        Args:
            data: Data to validate
            schema: JSON schema for structural validation
            rules: Additional business rules
            options: Validation options

        Returns:
            ValidationResult with detailed findings
        """
        validation_options = {{**self.options, **(options or {{}})}}
        errors = []
        warnings = []

        # Start with a copy of the data for normalization
        normalized_data = data.copy() if isinstance(data, dict) else data

        try:
            # 1. Schema validation
            schema_errors = self._validate_schema(data, schema)
            errors.extend(schema_errors)

            # 2. Business rules validation
            if rules:
                rules_errors = self._validate_business_rules(data, rules)
                errors.extend(rules_errors)

            # 3. Data normalization
            if validation_options.get("normalize", True):
                normalized_data = self._normalize_data(data, schema)

            # 4. Cross-field validation
            if validation_options.get("cross_field_validation", True):
                cross_errors = self._validate_cross_fields(normalized_data, rules)
                errors.extend(cross_errors)

            # 5. Create validation summary
            summary = self._create_validation_summary(data, errors, warnings)

            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                normalized_data=normalized_data,
                validation_summary=summary
            )

        except Exception as e:
            errors.append(ValidationError(
                field="root",
                rule="validation_error",
                message=f"Validation failed: {{str(e)}}",
                value=None,
                severity="error"
            ))

            return ValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings,
                normalized_data=data,
                validation_summary={{"total_errors": len(errors), "total_warnings": len(warnings)}}
            )

    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> List[ValidationError]:
        """Validate data against JSON schema."""
        errors = []

        try:
            # Use Draft7Validator for detailed error reporting
            validator = Draft7Validator(schema)

            for error in validator.iter_errors(data):
                field_path = ".".join(str(p) for p in error.path) if error.path else "root"

                validation_error = ValidationError(
                    field=field_path,
                    rule="schema_validation",
                    message=error.message,
                    value=error.instance,
                    severity="error"
                )
                errors.append(validation_error)

        except ValidationError as e:
            errors.append(ValidationError(
                field="root",
                rule="schema_validation",
                message=f"Schema error: {{e.message}}",
                value=data,
                severity="error"
            ))
        except Exception as e:
            errors.append(ValidationError(
                field="root",
                rule="schema_error",
                message=f"Invalid schema: {{str(e)}}",
                value=schema,
                severity="error"
            ))

        return errors

    def _validate_business_rules(self, data: Any, rules: List[ValidationRule]) -> List[ValidationError]:
        """Validate data against business rules."""
        errors = []

        for rule in rules:
            try:
                field_value = self._get_field_value(data, rule.field_path)

                if not self._evaluate_rule(field_value, rule):
                    errors.append(ValidationError(
                        field=rule.field_path,
                        rule=rule.name,
                        message=rule.error_message,
                        value=field_value,
                        severity="error"
                    ))

            except Exception as e:
                errors.append(ValidationError(
                    field=rule.field_path,
                    rule=f"{{rule.name}}_error",
                    message=f"Rule validation failed: {{str(e)}}",
                    value=None,
                    severity="error"
                ))

        return errors

    def _validate_cross_fields(self, data: Any, rules: Optional[List[ValidationRule]]) -> List[ValidationError]:
        """Perform cross-field validation."""
        errors = []

        # Add cross-field validation logic here
        # Example: start_date must be before end_date
        # Example: password and confirm_password must match

        return errors

    def _normalize_data(self, data: Any, schema: Dict[str, Any]) -> Any:
        """Normalize data according to schema rules."""
        if not isinstance(data, dict):
            return data

        normalized = data.copy()

        # Apply type conversions
        for field_name, field_schema in schema.get("properties", {{}}).items():
            if field_name in normalized:
                field_value = normalized[field_name]
                field_type = field_schema.get("type")

                if field_type == "string" and not isinstance(field_value, str):
                    normalized[field_name] = str(field_value)
                elif field_type == "integer" and not isinstance(field_value, int):
                    try:
                        normalized[field_name] = int(float(field_value))
                    except (ValueError, TypeError):
                        pass
                elif field_type == "number" and not isinstance(field_value, (int, float)):
                    try:
                        normalized[field_name] = float(field_value)
                    except (ValueError, TypeError):
                        pass
                elif field_type == "boolean":
                    if isinstance(field_value, str):
                        normalized[field_name] = field_value.lower() in ["true", "1", "yes", "on"]

        # Apply custom normalizers
        for normalizer_name, normalizer_func in self.normalizers.items():
            if normalizer_name in schema.get("normalizers", []):
                normalized = normalizer_func(normalized)

        return normalized

    def _get_field_value(self, data: Any, field_path: str) -> Any:
        """Get field value from data using dot notation."""
        if not field_path or field_path == "root":
            return data

        parts = field_path.split(".")
        current_value = data

        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            else:
                return None

        return current_value

    def _evaluate_rule(self, field_value: Any, rule: ValidationRule) -> bool:
        """Evaluate a single validation rule."""
        rule_type = rule.rule_type
        params = rule.parameters

        if rule_type == "required":
            return field_value is not None and field_value != ""

        elif rule_type == "format":
            pattern = params.get("pattern")
            if pattern and isinstance(field_value, str):
                return bool(re.match(pattern, field_value))
            return True

        elif rule_type == "range":
            min_val = params.get("min")
            max_val = params.get("max")

            if isinstance(field_value, (int, float)):
                if min_val is not None and field_value < min_val:
                    return False
                if max_val is not None and field_value > max_val:
                    return False
            return True

        elif rule_type == "length":
            min_len = params.get("min_length")
            max_len = params.get("max_length")

            if isinstance(field_value, (str, list, dict)):
                length = len(field_value)
                if min_len is not None and length < min_len:
                    return False
                if max_len is not None and length > max_len:
                    return False
            return True

        elif rule_type == "enum":
            allowed_values = params.get("values", [])
            return field_value in allowed_values

        elif rule_type == "custom" and rule.name in self.custom_validators:
            return self.custom_validators[rule.name](field_value, params)

        return True

    def _create_validation_summary(self, data: Any, errors: List[ValidationError], warnings: List[ValidationError]) -> Dict[str, Any]:
        """Create validation summary statistics."""
        return {{
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "fields_with_errors": list(set(e.field for e in errors)),
            "rule_types_with_errors": list(set(e.rule for e in errors)),
            "data_size": len(str(data)),
            "validation_timestamp": self._get_timestamp()
        }}

    def _register_custom_validators(self) -> Dict[str, callable]:
        """Register custom validation functions."""
        return {{
            "email_format": self._validate_email_format,
            "phone_format": self._validate_phone_format,
            "url_format": self._validate_url_format,
            "credit_card_format": self._validate_credit_card_format,
            "strong_password": self._validate_strong_password
        }}

    def _register_normalizers(self) -> Dict[str, callable]:
        """Register data normalizer functions."""
        return {{
            "trim_strings": self._trim_strings_normalizer,
            "normalize_emails": self._normalize_emails_normalizer,
            "normalize_phone_numbers": self._normalize_phone_numbers_normalizer
        }}

    # Custom validators
    def _validate_email_format(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate email format."""
        if not isinstance(value, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{{2,}}$'
        return bool(re.match(email_pattern, value))

    def _validate_phone_format(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate phone number format."""
        if not isinstance(value, str):
            return False
        # Remove non-digit characters for validation
        digits_only = re.sub(r'\D', '', value)
        return len(digits_only) >= 10

    def _validate_url_format(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate URL format."""
        if not isinstance(value, str):
            return False
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, value))

    def _validate_credit_card_format(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate credit card format using Luhn algorithm."""
        if not isinstance(value, str):
            return False

        # Remove spaces and dashes
        card_number = re.sub(r'[\s-]', '', value)

        if not re.match(r'^\d{{13,19}}$', card_number):
            return False

        # Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(card_number)):
            d = int(digit)
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d

        return total % 10 == 0

    def _validate_strong_password(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate strong password requirements."""
        if not isinstance(value, str):
            return False

        min_length = params.get("min_length", 8)
        require_upper = params.get("require_upper", True)
        require_lower = params.get("require_lower", True)
        require_digit = params.get("require_digit", True)
        require_special = params.get("require_special", True)

        if len(value) < min_length:
            return False
        if require_upper and not re.search(r'[A-Z]', value):
            return False
        if require_lower and not re.search(r'[a-z]', value):
            return False
        if require_digit and not re.search(r'\d', value):
            return False
        if require_special and not re.search(r'[!@#$%^&*(),.?":{{}}|<>]', value):
            return False

        return True

    # Normalizers
    def _trim_strings_normalizer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trim whitespace from string fields."""
        normalized = data.copy()
        for key, value in normalized.items():
            if isinstance(value, str):
                normalized[key] = value.strip()
        return normalized

    def _normalize_emails_normalizer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize email addresses to lowercase."""
        normalized = data.copy()
        for key, value in normalized.items():
            if isinstance(value, str) and "@" in value:
                normalized[key] = value.lower()
        return normalized

    def _normalize_phone_numbers_normalizer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize phone numbers to standard format."""
        normalized = data.copy()
        for key, value in normalized.items():
            if isinstance(value, str):
                # Remove all non-digit characters
                digits = re.sub(r'\D', '', value)
                # Format as (XXX) XXX-XXXX if 10 digits
                if len(digits) == 10:
                    normalized[key] = f"({{digits[:3]}}) {{digits[3:6]}}-{{digits[6:]}}"
        return normalized

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Convenience function
def validate_{skill_name.lower().replace(' ', '_')}(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    schema: Dict[str, Any],
    rules: Optional[List[ValidationRule]] = None
) -> ValidationResult:
    """
    Validate data using {skill_name}.

    Args:
        data: Data to validate
        schema: JSON schema for validation
        rules: Additional business rules

    Returns:
        ValidationResult with detailed findings
    """
    validator = {skill_name.title().replace(' ', '')}Validator()
    return validator.validate(data, schema, rules)


# Rule creation helpers
def create_required_rule(field_path: str, error_message: str = None) -> ValidationRule:
    """Create a required field rule."""
    return ValidationRule(
        name=f"required_{{field_path}}",
        description=f"Field {{field_path}} is required",
        field_path=field_path,
        rule_type="required",
        parameters={{}},
        error_message=error_message or f"Field {{field_path}} is required"
    )


def create_format_rule(field_path: str, pattern: str, error_message: str = None) -> ValidationRule:
    """Create a format validation rule."""
    return ValidationRule(
        name=f"format_{{field_path}}",
        description=f"Field {{field_path}} must match format",
        field_path=field_path,
        rule_type="format",
        parameters={{"pattern": pattern}},
        error_message=error_message or f"Field {{field_path}} format is invalid"
    )


def create_range_rule(field_path: str, min_val: float = None, max_val: float = None, error_message: str = None) -> ValidationRule:
    """Create a range validation rule."""
    return ValidationRule(
        name=f"range_{{field_path}}",
        description=f"Field {{field_path}} must be within range",
        field_path=field_path,
        rule_type="range",
        parameters={{"min": min_val, "max": max_val}},
        error_message=error_message or f"Field {{field_path}} must be between {{min_val}} and {{max_val}}"
    )
'''

    def _get_validation_test_template(self) -> str:
        """Get validation test template."""
        return '''
"""
Tests for {skill_name}

Comprehensive test suite for data validation functionality.
"""

import pytest
from jsonschema import ValidationError
import sys
import os

# Add the skill to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the skill
try:
    from {skill_name.lower().replace(' ', '_')} import (
        {skill_name.title().replace(' ', '')}Validator,
        validate_{skill_name.lower().replace(' ', '_')},
        ValidationRule,
        ValidationResult,
        ValidationError as CustomValidationError,
        create_required_rule,
        create_format_rule,
        create_range_rule
    )
except ImportError:
    {skill_name.title().replace(' ', '')}Validator = None
    validate_{skill_name.lower().replace(' ', '_')} = None
    ValidationRule = None
    ValidationResult = None
    CustomValidationError = None


class Test{skill_name.title().replace(' ', '')}Validator:
    """Test suite for {skill_name.title().replace(' ', '')}Validator."""

    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        if {skill_name.title().replace(' ', '')}Validator is None:
            pytest.skip("Skill not implemented")
        return {skill_name.title().replace(' ', '')}Validator()

    @pytest.fixture
    def sample_schema(self):
        """Sample JSON schema for testing."""
        return {{
            "type": "object",
            "properties": {{
                "name": {{"type": "string", "minLength": 1}},
                "age": {{"type": "integer", "minimum": 0, "maximum": 150}},
                "email": {{"type": "string", "format": "email"}},
                "active": {{"type": "boolean", "default": True}},
                "tags": {{
                    "type": "array",
                    "items": {{"type": "string"}},
                    "minItems": 0,
                    "maxItems": 5
                }}
            }},
            "required": ["name", "age"]
        }}

    @pytest.fixture
    def valid_data(self):
        """Valid data for testing."""
        return {{
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True,
            "tags": ["user", "premium"]
        }}

    @pytest.fixture
    def invalid_data(self):
        """Invalid data for testing."""
        return {{
            "name": "",  # Empty string
            "age": -5,   # Negative age
            "email": "invalid-email",  # Invalid format
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]  # Too many tags
        }}

    def test_valid_data_validation(self, validator, sample_schema, valid_data):
        """Test validation of valid data."""
        result = validator.validate(valid_data, sample_schema)

        assert result.valid is True
        assert len(result.errors) == 0
        assert result.normalized_data is not None

    def test_invalid_data_validation(self, validator, sample_schema, invalid_data):
        """Test validation of invalid data."""
        result = validator.validate(invalid_data, sample_schema)

        assert result.valid is False
        assert len(result.errors) > 0

        # Check specific errors
        error_fields = [error.field for error in result.errors]
        assert "name" in error_fields
        assert "age" in error_fields
        assert "email" in error_fields
        assert "tags" in error_fields

    def test_missing_required_fields(self, validator, sample_schema):
        """Test validation with missing required fields."""
        incomplete_data = {{"age": 25}}  # Missing required 'name' field

        result = validator.validate(incomplete_data, sample_schema)

        assert result.valid is False
        assert any(error.rule == "required" for error in result.errors)

    def test_business_rules_validation(self, validator, sample_schema, valid_data):
        """Test business rules validation."""
        rules = [
            ValidationRule(
                name="adult_only",
                description="User must be at least 18 years old",
                field_path="age",
                rule_type="range",
                parameters={{"min": 18}},
                error_message="User must be at least 18 years old"
            )
        ]

        # Test with valid age
        valid_result = validator.validate(valid_data, sample_schema, rules)
        assert valid_result.valid is True

        # Test with invalid age
        invalid_data = valid_data.copy()
        invalid_data["age"] = 16

        invalid_result = validator.validate(invalid_data, sample_schema, rules)
        assert invalid_result.valid is False
        assert any(error.rule == "adult_only" for error in invalid_result.errors)

    def test_data_normalization(self, validator, sample_schema):
        """Test data normalization."""
        data_with_types = {{
            "name": "John Doe",
            "age": "30",  # String instead of integer
            "active": "true",  # String instead of boolean
            "tags": "user,admin"  # String instead of array
        }}

        result = validator.validate(data_with_types, sample_schema)

        # Check if normalization occurred
        if result.normalized_data:
            # Age should be converted to integer if possible
            if "age" in result.normalized_data:
                assert isinstance(result.normalized_data["age"], int)

    def test_cross_field_validation(self, validator):
        """Test cross-field validation."""
        # This would test custom cross-field validation logic
        # Example: password confirmation matching
        pass

    def test_custom_validators(self, validator):
        """Test custom validation functions."""
        if not validator.custom_validators:
            return

        # Test email format validator
        if "email_format" in validator.custom_validators:
            assert validator.custom_validators["email_format"]("test@example.com", {{}}) is True
            assert validator.custom_validators["email_format"]("invalid-email", {{}}) is False

        # Test phone format validator
        if "phone_format" in validator.custom_validators:
            assert validator.custom_validators["phone_format"]("555-123-4567", {{}}) is True
            assert validator.custom_validators["phone_format"]("123", {{}}) is False

        # Test strong password validator
        if "strong_password" in validator.custom_validators:
            strong_password = validator.custom_validators["strong_password"]("StrongPass123!", {{"require_special": True}})
            assert strong_password is True

            weak_password = validator.custom_validators["strong_password"]("weak", {{"require_special": True}})
            assert weak_password is False

    def test_validation_summary(self, validator, sample_schema, invalid_data):
        """Test validation summary generation."""
        result = validator.validate(invalid_data, sample_schema)

        assert "validation_summary" in result.__dict__
        summary = result.validation_summary
        assert "total_errors" in summary
        assert "fields_with_errors" in summary
        assert summary["total_errors"] > 0

    def test_array_validation(self, validator):
        """Test validation of array data."""
        array_schema = {{
            "type": "array",
            "items": {{
                "type": "object",
                "properties": {{
                    "id": {{"type": "integer"}},
                    "name": {{"type": "string"}}
                }},
                "required": ["id"]
            }}
        }}

        valid_array = [
            {{"id": 1, "name": "Item 1"}},
            {{"id": 2, "name": "Item 2"}}
        ]

        invalid_array = [
            {{"id": 1, "name": "Item 1"}},
            {{"name": "Item 2"}}  # Missing required id
        ]

        # Test valid array
        valid_result = validator.validate(valid_array, array_schema)
        assert valid_result.valid is True

        # Test invalid array
        invalid_result = validator.validate(invalid_array, array_schema)
        assert invalid_result.valid is False

    def test_nested_object_validation(self, validator):
        """Test validation of nested objects."""
        nested_schema = {{
            "type": "object",
            "properties": {{
                "user": {{
                    "type": "object",
                    "properties": {{
                        "profile": {{
                            "type": "object",
                            "properties": {{
                                "name": {{"type": "string"}},
                                "email": {{"type": "string"}}
                            }},
                            "required": ["name"]
                        }}
                    }},
                    "required": ["profile"]
                }}
            }},
            "required": ["user"]
        }}

        valid_nested = {{
            "user": {{
                "profile": {{
                    "name": "John",
                    "email": "john@example.com"
                }}
            }}
        }}

        invalid_nested = {{
            "user": {{
                "profile": {{
                    "email": "john@example.com"  # Missing required name
                }}
            }}
        }}

        # Test valid nested object
        valid_result = validator.validate(valid_nested, nested_schema)
        assert valid_result.valid is True

        # Test invalid nested object
        invalid_result = validator.validate(invalid_nested, nested_schema)
        assert invalid_result.valid is False
        assert any("profile.name" in error.field for error in invalid_result.errors)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_validate_convenience_function(self, sample_schema, valid_data):
        """Test the validate convenience function."""
        if validate_{skill_name.lower().replace(' ', '_')} is None:
            pytest.skip("Convenience function not implemented")

        result = validate_{skill_name.lower().replace(' ', '_')}(valid_data, sample_schema)
        assert result.valid is True

    def test_rule_creation_helpers(self):
        """Test rule creation helper functions."""
        if ValidationRule is None:
            pytest.skip("ValidationRule not implemented")

        # Test required rule
        required_rule = create_required_rule("field1", "Field1 is required")
        assert required_rule.field_path == "field1"
        assert required_rule.rule_type == "required"

        # Test format rule
        format_rule = create_format_rule("email", r"^[^@]+@[^@]+\.[^@]+$")
        assert format_rule.field_path == "email"
        assert format_rule.rule_type == "format"
        assert "pattern" in format_rule.parameters

        # Test range rule
        range_rule = create_range_rule("age", 0, 150)
        assert range_rule.field_path == "age"
        assert range_rule.rule_type == "range"
        assert range_rule.parameters["min"] == 0
        assert range_rule.parameters["max"] == 150


class TestIntegration:
    """Integration tests for {skill_name}."""

    def test_real_world_validation_scenario(self):
        """Test with real-world validation scenario."""
        if {skill_name.title().replace(' ', '')}Validator is None:
            pytest.skip("Skill not implemented")

        # User registration validation
        user_schema = {{
            "type": "object",
            "properties": {{
                "username": {{
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 20,
                    "pattern": "^[a-zA-Z0-9_]+$"
                }},
                "email": {{"type": "string", "format": "email"}},
                "password": {{"type": "string", "minLength": 8}},
                "confirm_password": {{"type": "string"}},
                "age": {{"type": "integer", "minimum": 13, "maximum": 120}},
                "terms_accepted": {{"type": "boolean"}}
            }},
            "required": ["username", "email", "password", "confirm_password", "terms_accepted"]
        }}

        # Business rules
        rules = [
            ValidationRule(
                name="password_match",
                description="Password and confirmation must match",
                field_path="password",
                rule_type="custom",
                parameters={{"confirm_field": "confirm_password"}},
                error_message="Password and confirmation must match"
            ),
            ValidationRule(
                name="strong_password",
                description="Password must be strong",
                field_path="password",
                rule_type="custom",
                parameters={{"min_length": 8, "require_upper": True, "require_digit": True}},
                error_message="Password must be at least 8 characters with uppercase letter and digit"
            )
        ]

        validator = {skill_name.title().replace(' ', '')}Validator()

        # Test valid registration
        valid_registration = {{
            "username": "john_doe",
            "email": "john@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
            "age": 25,
            "terms_accepted": True
        }}

        result = validator.validate(valid_registration, user_schema, rules)
        assert result.valid is True

        # Test invalid registration (passwords don't match)
        invalid_registration = valid_registration.copy()
        invalid_registration["confirm_password"] = "DifferentPass123"

        result = validator.validate(invalid_registration, user_schema, rules)
        assert result.valid is False
        assert any(error.rule == "password_match" for error in result.errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    def _get_validation_doc_template(self) -> str:
        """Get validation documentation template."""
        return """
# {skill_name}

{description}

## Overview

{skill_name} provides comprehensive data validation capabilities including JSON schema validation, custom business rules, and data normalization. It's designed for validating complex data structures with detailed error reporting.

## Installation

```bash
pip install jsonschema
```

## Usage

### Basic Validation

```python
from {skill_name.lower().replace(' ', '_')} import {skill_name.title().replace(' ', '')}Validator

# Create validator
validator = {skill_name.title().replace(' ', '')}Validator()

# Define schema
schema = {{
    "type": "object",
    "properties": {{
        "name": {{"type": "string", "minLength": 1}},
        "age": {{"type": "integer", "minimum": 0, "maximum": 150}},
        "email": {{"type": "string", "format": "email"}}
    }},
    "required": ["name", "age"]
}}

# Validate data
result = validator.validate(data, schema)
print(f"Valid: {{result.valid}}")
print(f"Errors: {{len(result.errors)}}")
```

### Business Rules

```python
from {skill_name.lower().replace(' ', '_')} import ValidationRule

# Define business rules
rules = [
    ValidationRule(
        name="adult_only",
        description="User must be at least 18",
        field_path="age",
        rule_type="range",
        parameters={{"min": 18}},
        error_message="Must be 18 or older"
    )
]

result = validator.validate(data, schema, rules)
```

### Convenience Function

```python
from {skill_name.lower().replace(' ', '_')} import validate_{skill_name.lower().replace(' ', '_')}

result = validate_{skill_name.lower().replace(' ', '_')}(data, schema, rules)
```

## Validation Rules

### Required Fields

```python
from {skill_name.lower().replace(' ', '_')} import create_required_rule

rule = create_required_rule("email", "Email address is required")
```

### Format Validation

```python
from {skill_name.lower().replace(' ', '_')} import create_format_rule

# Email format
email_rule = create_format_rule(
    "email",
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{{2,}}$",
    "Invalid email format"
)

# Phone format
phone_rule = create_format_rule(
    "phone",
    r"^\d{{3}}-\d{{3}}-\d{{4}}$",
    "Phone must be XXX-XXX-XXXX format"
)
```

### Range Validation

```python
from {skill_name.lower().replace(' ', '_')} import create_range_rule

age_rule = create_range_rule("age", 0, 150, "Age must be between 0 and 150")
price_rule = create_range_rule("price", min_val=0.0, max_val=9999.99)
```

### Custom Rules

```python
# Custom validation function
def validate_username(value, params):
    if not isinstance(value, str):
        return False
    return len(value) >= 3 and value.replace('_', '').isalnum()

custom_rule = ValidationRule(
    name="valid_username",
    description="Username must be valid",
    field_path="username",
    rule_type="custom",
    parameters={{"min_length": 3}},
    error_message="Invalid username format"
)
```

## Built-in Validators

{skill_name} includes several built-in validators:

### Email Format

```python
ValidationRule(
    name="email_format",
    field_path="email",
    rule_type="custom",
    parameters={{"type": "email_format"}},
    error_message="Invalid email address"
)
```

### Phone Format

```python
ValidationRule(
    name="phone_format",
    field_path="phone",
    rule_type="custom",
    parameters={{"type": "phone_format"}},
    error_message="Invalid phone number"
)
```

### Strong Password

```python
ValidationRule(
    name="strong_password",
    field_path="password",
    rule_type="custom",
    parameters={
        "type": "strong_password",
        "min_length": 8,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True
    },
    error_message="Password does not meet strength requirements"
)
```

## Data Normalization

{skill_name} can automatically normalize data:

```python
validator = {skill_name.title().replace(' ', '')}Validator(options={{"normalize": True}})

# String "123" becomes integer 123
# String "true" becomes boolean True
# Emails are lowercased
# Phone numbers are formatted consistently
```

## Examples

{examples}

## API Reference

### {skill_name.title().replace(' ', '')}Validator

#### `__init__(options=None)`

Initialize validator with options.

**Options:**
- `normalize`: Enable data normalization (default: True)
- `cross_field_validation`: Enable cross-field validation (default: True)

#### `validate(data, schema, rules=None, options=None)`

Validate data against schema and rules.

**Parameters:**
- `data`: Data to validate
- `schema`: JSON schema
- `rules`: Additional business rules
- `options`: Validation options

**Returns:** `ValidationResult`

### ValidationResult

Validation result containing:

- `valid`: Whether validation passed
- `errors`: List of validation errors
- `warnings`: List of validation warnings
- `normalized_data`: Normalized version of input data
- `validation_summary`: Validation statistics

### ValidationRule

Business rule definition:

- `name`: Rule identifier
- `field_path`: Path to field (dot notation for nested)
- `rule_type`: Type of rule (required, format, range, custom)
- `parameters`: Rule-specific parameters
- `error_message`: Error message to display

## Testing

Run tests with:

```bash
pytest test_{skill_name.lower().replace(' ', '_')}.py -v
```

## Performance

- Efficient schema validation using jsonschema
- Minimal memory overhead for large datasets
- Detailed error reporting without performance impact

## License

MIT License
"""
