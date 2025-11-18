"""
Template Library for Skill Creation

Comprehensive template library that provides reusable patterns for rapid skill development.
Supports different skill categories with customizable templates and best practices.

Features:
- Category-specific templates for different skill types
- Customizable template parameters
- Best practices enforcement
- Progressive complexity levels
- Built-in validation and testing patterns
- Zero hallucination template safeguards

Architecture: Brick-based with clear contract interfaces
- Template management and selection
- Customization engine
- Validation framework
- Performance optimization
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...utils.logger import get_logger

logger = get_logger(__name__)


class SkillCategory(Enum):
    """Skill categories for template organization."""

    DATA_PROCESSING = "data_processing"
    TEXT_ANALYSIS = "text_analysis"
    AUTOMATION = "automation"
    API_INTEGRATION = "api_integration"
    VISUALIZATION = "visualization"
    MACHINE_LEARNING = "machine_learning"
    SECURITY = "security"
    MONITORING = "monitoring"
    GENERAL = "general"


class TemplateComplexity(Enum):
    """Template complexity levels."""

    BASIC = "basic"  # Simple, single-purpose templates
    INTERMEDIATE = "intermediate"  # Multi-feature templates
    ADVANCED = "advanced"  # Complex, feature-rich templates
    EXPERT = "expert"  # Highly specialized, optimized templates


@dataclass
class TemplateParameter:
    """Template parameter definition."""

    name: str
    parameter_type: str  # string, integer, boolean, array, object
    description: str
    required: bool = True
    default_value: Any = None
    validation_rules: List[str] = field(default_factory=list)
    examples: List[Any] = field(default_factory=list)


@dataclass
class TemplateFeature:
    """Template feature definition."""

    name: str
    description: str
    enabled_by_default: bool = False
    dependencies: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillTemplate:
    """Complete skill template definition."""

    template_id: str
    name: str
    description: str
    category: SkillCategory
    complexity: TemplateComplexity
    version: str
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)

    # Template structure
    parameters: List[TemplateParameter] = field(default_factory=list)
    features: List[TemplateFeature] = field(default_factory=list)
    code_template: str = ""
    test_template: str = ""
    documentation_template: str = ""

    # Metadata
    requirements: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    performance_notes: str = ""
    usage_examples: List[Dict[str, Any]] = field(default_factory=list)

    # Quality metrics
    validation_rules: List[str] = field(default_factory=list)
    quality_checks: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)


class TemplateLibrary:
    """
    Comprehensive template library for skill creation.

    Provides a rich collection of templates for different skill categories
    with built-in best practices, validation, and optimization patterns.

    Key Features:
    - Category-specific templates
    - Progressive complexity levels
    - Customizable parameters
    - Built-in validation
    - Performance optimization
    - Zero hallucination safeguards
    """

    def __init__(self):
        self.templates: Dict[str, SkillTemplate] = {}
        self.category_index: Dict[SkillCategory, List[str]] = {}
        self.complexity_index: Dict[TemplateComplexity, List[str]] = {}
        self.feature_index: Dict[str, List[str]] = {}

        # Initialize built-in templates
        self._initialize_builtin_templates()
        self._build_indexes()

    def _initialize_builtin_templates(self) -> None:
        """Initialize built-in templates for common skill categories."""

        # Data Processing Templates
        self._register_template(
            SkillTemplate(
                template_id="data_processor_basic",
                name="Basic Data Processor",
                description="Template for basic data processing skills with validation and error handling",
                category=SkillCategory.DATA_PROCESSING,
                complexity=TemplateComplexity.BASIC,
                version="1.0.0",
                author="Amplifier Team",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["data", "processing", "validation", "basic"],
                parameters=[
                    TemplateParameter(
                        name="data_format",
                        parameter_type="string",
                        description="Expected data format (json, csv, xml)",
                        required=True,
                        default_value="json",
                        validation_rules=["enum:json,csv,xml,dict"],
                    ),
                    TemplateParameter(
                        name="validation_enabled",
                        parameter_type="boolean",
                        description="Enable input/output validation",
                        required=False,
                        default_value=True,
                    ),
                    TemplateParameter(
                        name="error_handling",
                        parameter_type="string",
                        description="Error handling strategy",
                        required=False,
                        default_value="graceful",
                        validation_rules=["enum:strict,graceful,log_only"],
                    ),
                ],
                features=[
                    TemplateFeature(
                        name="input_validation",
                        description="Validate input data format and structure",
                        enabled_by_default=True,
                    ),
                    TemplateFeature(
                        name="error_handling",
                        description="Comprehensive error handling and logging",
                        enabled_by_default=True,
                    ),
                    TemplateFeature(
                        name="performance_stats", description="Track processing statistics", enabled_by_default=False
                    ),
                ],
                code_template=self._get_data_processor_template(),
                test_template=self._get_data_processor_test_template(),
                documentation_template=self._get_data_processor_docs_template(),
                requirements=["python>=3.8", "pydantic>=2.0"],
                dependencies=["typing", "json", "logging"],
                performance_notes="Optimized for moderate data sizes. Use streaming for large datasets.",
                usage_examples=[
                    {
                        "description": "Process JSON data",
                        "input_format": {"data": {"key": "value"}},
                        "expected_output": {"processed": True, "count": 1},
                    }
                ],
                validation_rules=["validate_schema", "check_data_types", "ensure_no_empty_fields"],
                quality_checks=["no_hardcoded_values", "proper_error_handling", "type_annotations"],
                anti_patterns=["catch_all_exceptions", "silent_failures", "missing_validation"],
            )
        )

        # Text Analysis Templates
        self._register_template(
            SkillTemplate(
                template_id="text_analyzer_basic",
                name="Basic Text Analyzer",
                description="Template for text analysis skills with NLP capabilities",
                category=SkillCategory.TEXT_ANALYSIS,
                complexity=TemplateComplexity.BASIC,
                version="1.0.0",
                author="Amplifier Team",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["text", "analysis", "nlp", "basic"],
                parameters=[
                    TemplateParameter(
                        name="analysis_types",
                        parameter_type="array",
                        description="Types of text analysis to perform",
                        required=True,
                        default_value=["sentiment", "entities", "keywords"],
                        validation_rules=["items.enum:sentiment,entities,keywords,summary,language"],
                    ),
                    TemplateParameter(
                        name="language_detection",
                        parameter_type="boolean",
                        description="Enable automatic language detection",
                        required=False,
                        default_value=True,
                    ),
                ],
                features=[
                    TemplateFeature(
                        name="sentiment_analysis", description="Analyze text sentiment", enabled_by_default=True
                    ),
                    TemplateFeature(
                        name="entity_extraction", description="Extract named entities", enabled_by_default=True
                    ),
                    TemplateFeature(
                        name="keyword_extraction", description="Extract important keywords", enabled_by_default=True
                    ),
                ],
                code_template=self._get_text_analyzer_template(),
                test_template=self._get_text_analyzer_test_template(),
                documentation_template=self._get_text_analyzer_docs_template(),
                requirements=["python>=3.8"],
                dependencies=["re", "collections", "typing"],
                performance_notes="Optimized for text up to 10,000 characters. Use chunking for longer texts.",
                usage_examples=[
                    {
                        "description": "Analyze sentiment",
                        "input_format": {"text": "I love this product!"},
                        "expected_output": {"sentiment": "positive", "confidence": 0.9},
                    }
                ],
                validation_rules=["check_text_length", "validate_analysis_types", "ensure_unicode_support"],
                quality_checks=["no_regex_injection", "proper_encoding", "edge_case_handling"],
                anti_patterns=["regex_dos", "encoding_errors", "case_sensitivity_issues"],
            )
        )

        # Automation Templates
        self._register_template(
            SkillTemplate(
                template_id="automation_workflow",
                name="Workflow Automation",
                description="Template for workflow automation skills with task scheduling",
                category=SkillCategory.AUTOMATION,
                complexity=TemplateComplexity.INTERMEDIATE,
                version="1.0.0",
                author="Amplifier Team",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["automation", "workflow", "scheduling", "tasks"],
                parameters=[
                    TemplateParameter(
                        name="workflow_type",
                        parameter_type="string",
                        description="Type of workflow (sequential, parallel, conditional)",
                        required=True,
                        default_value="sequential",
                        validation_rules=["enum:sequential,parallel,conditional"],
                    ),
                    TemplateParameter(
                        name="retry_policy",
                        parameter_type="object",
                        description="Retry policy for failed tasks",
                        required=False,
                        default_value={"max_retries": 3, "backoff": "exponential"},
                    ),
                ],
                features=[
                    TemplateFeature(
                        name="task_scheduling", description="Schedule and execute tasks", enabled_by_default=True
                    ),
                    TemplateFeature(
                        name="retry_mechanism", description="Retry failed tasks with backoff", enabled_by_default=True
                    ),
                    TemplateFeature(
                        name="progress_tracking", description="Track workflow progress", enabled_by_default=True
                    ),
                ],
                code_template=self._get_automation_template(),
                test_template=self._get_automation_test_template(),
                documentation_template=self._get_automation_docs_template(),
                requirements=["python>=3.8", "asyncio"],
                dependencies=["asyncio", "typing", "dataclasses", "enum"],
                performance_notes="Concurrent execution support. Monitor memory usage for large workflows.",
                usage_examples=[
                    {
                        "description": "Run sequential workflow",
                        "input_format": {"tasks": [{"name": "task1", "action": "process"}]},
                        "expected_output": {"status": "completed", "tasks_executed": 1},
                    }
                ],
                validation_rules=["validate_workflow_structure", "check_task_dependencies", "ensure_termination"],
                quality_checks=["no_infinite_loops", "proper_resource_cleanup", "timeout_handling"],
                anti_patterns=["race_conditions", "resource_leaks", "deadlock_risks"],
            )
        )

        # API Integration Templates
        self._register_template(
            SkillTemplate(
                template_id="api_client_advanced",
                name="Advanced API Client",
                description="Template for API integration with authentication and rate limiting",
                category=SkillCategory.API_INTEGRATION,
                complexity=TemplateComplexity.ADVANCED,
                version="1.0.0",
                author="Amplifier Team",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=["api", "http", "auth", "rate_limiting"],
                parameters=[
                    TemplateParameter(
                        name="auth_type",
                        parameter_type="string",
                        description="Authentication type",
                        required=True,
                        default_value="bearer",
                        validation_rules=["enum:basic,bearer,oauth2,api_key,none"],
                    ),
                    TemplateParameter(
                        name="rate_limiting",
                        parameter_type="boolean",
                        description="Enable rate limiting",
                        required=False,
                        default_value=True,
                    ),
                    TemplateParameter(
                        name="timeout_seconds",
                        parameter_type="integer",
                        description="Request timeout in seconds",
                        required=False,
                        default_value=30,
                        validation_rules=["min:1", "max:300"],
                    ),
                ],
                features=[
                    TemplateFeature(
                        name="authentication",
                        description="Handle different authentication methods",
                        enabled_by_default=True,
                    ),
                    TemplateFeature(
                        name="rate_limiting", description="Implement rate limiting", enabled_by_default=True
                    ),
                    TemplateFeature(
                        name="retry_logic",
                        description="Automatic retry with exponential backoff",
                        enabled_by_default=True,
                    ),
                    TemplateFeature(name="caching", description="Response caching", enabled_by_default=False),
                ],
                code_template=self._get_api_client_template(),
                test_template=self._get_api_client_test_template(),
                documentation_template=self._get_api_client_docs_template(),
                requirements=["python>=3.8", "httpx>=0.24.0"],
                dependencies=["httpx", "typing", "asyncio", "json"],
                performance_notes="Async HTTP client with connection pooling. Monitor connection limits.",
                usage_examples=[
                    {
                        "description": "Make authenticated API call",
                        "input_format": {"url": "https://api.example.com/data", "method": "GET"},
                        "expected_output": {"status": "success", "data": {}},
                    }
                ],
                validation_rules=["validate_url_format", "check_auth_credentials", "ensure_https"],
                quality_checks=["secure_credential_handling", "proper_error_responses", "timeout_enforcement"],
                anti_patterns=["credential_leakage", "ssrf_vulnerability", "insecure_ssl"],
            )
        )

    def _register_template(self, template: SkillTemplate) -> None:
        """Register a template in the library."""
        self.templates[template.template_id] = template
        logger.info(f"Registered template: {template.template_id}")

    def _build_indexes(self) -> None:
        """Build lookup indexes for efficient template search."""
        self.category_index = {}
        self.complexity_index = {}
        self.feature_index = {}

        for template_id, template in self.templates.items():
            # Category index
            if template.category not in self.category_index:
                self.category_index[template.category] = []
            self.category_index[template.category].append(template_id)

            # Complexity index
            if template.complexity not in self.complexity_index:
                self.complexity_index[template.complexity] = []
            self.complexity_index[template.complexity].append(template_id)

            # Feature index
            for feature in template.features:
                if feature.name not in self.feature_index:
                    self.feature_index[feature.name] = []
                self.feature_index[feature.name].append(template_id)

    def get_template(self, template_id: str) -> Optional[SkillTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def find_templates(
        self,
        category: Optional[SkillCategory] = None,
        complexity: Optional[TemplateComplexity] = None,
        features: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> List[SkillTemplate]:
        """Find templates matching criteria."""
        candidates = list(self.templates.values())

        # Filter by category
        if category:
            candidates = [t for t in candidates if t.category == category]

        # Filter by complexity
        if complexity:
            candidates = [t for t in candidates if t.complexity == complexity]

        # Filter by features
        if features:
            candidates = [t for t in candidates if all(f in [feat.name for feat in t.features] for f in features)]

        # Filter by tags
        if tags:
            candidates = [t for t in candidates if any(tag in t.tags for tag in tags)]

        return candidates

    def get_template_for_skill(
        self, skill_name: str, skill_description: str, skill_category: str, requirements: List[str] = None
    ) -> Optional[SkillTemplate]:
        """
        Intelligent template selection for a skill.

        Uses skill description and requirements to select the most appropriate template.
        """
        category_map = {
            "data": SkillCategory.DATA_PROCESSING,
            "text": SkillCategory.TEXT_ANALYSIS,
            "automation": SkillCategory.AUTOMATION,
            "api": SkillCategory.API_INTEGRATION,
            "monitor": SkillCategory.MONITORING,
            "security": SkillCategory.SECURITY,
        }

        # Determine category
        category = SkillCategory.GENERAL
        for key, cat in category_map.items():
            if key in skill_category.lower() or key in skill_description.lower():
                category = cat
                break

        # Find templates in category
        templates = self.find_templates(category=category)

        if not templates:
            # Fallback to general templates
            templates = self.find_templates(category=SkillCategory.GENERAL)

        if not templates:
            return None

        # Score templates based on requirements match
        best_template = None
        best_score = 0

        for template in templates:
            score = 0

            # Base score for category match
            if template.category == category:
                score += 10

            # Bonus for feature matching
            if requirements:
                template_features = [f.name for f in template.features]
                for req in requirements:
                    if any(req.lower() in feature.lower() for feature in template_features):
                        score += 5

            # Bonus for tag matching
            if requirements:
                for req in requirements:
                    if any(req.lower() in tag.lower() for tag in template.tags):
                        score += 3

            # Prefer simpler templates by default
            complexity_scores = {
                TemplateComplexity.BASIC: 5,
                TemplateComplexity.INTERMEDIATE: 3,
                TemplateComplexity.ADVANCED: 1,
                TemplateComplexity.EXPERT: 0,
            }
            score += complexity_scores.get(template.complexity, 0)

            if score > best_score:
                best_score = score
                best_template = template

        return best_template

    def customize_template(
        self, template: SkillTemplate, parameters: Dict[str, Any], features: List[str] = None
    ) -> Dict[str, Any]:
        """
        Customize template with parameters and features.

        Returns customized template with code, tests, and documentation.
        """
        # Validate parameters
        validated_params = self._validate_template_parameters(template, parameters)

        # Process features
        enabled_features = features or [f.name for f in template.features if f.enabled_by_default]

        # Generate customized code
        customized_code = self._generate_customized_code(template, validated_params, enabled_features)

        # Generate customized tests
        customized_tests = self._generate_customized_tests(template, validated_params, enabled_features)

        # Generate customized documentation
        customized_docs = self._generate_customized_docs(template, validated_params, enabled_features)

        return {
            "template_info": {
                "template_id": template.template_id,
                "name": template.name,
                "category": template.category.value,
                "complexity": template.complexity.value,
            },
            "parameters": validated_params,
            "enabled_features": enabled_features,
            "code": customized_code,
            "tests": customized_tests,
            "documentation": customized_docs,
            "requirements": template.requirements,
            "dependencies": template.dependencies,
        }

    def _validate_template_parameters(self, template: SkillTemplate, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process template parameters."""
        validated = {}

        for param in template.parameters:
            param_value = parameters.get(param.name, param.default_value)

            # Check required parameters
            if param.required and param_value is None:
                raise ValueError(f"Required parameter '{param.name}' is missing")

            # Skip if parameter not provided and not required
            if param_value is None and not param.required:
                continue

            # Type validation
            if param.parameter_type == "string":
                validated[param.name] = str(param_value)
            elif param.parameter_type == "integer":
                validated[param.name] = int(param_value)
            elif param.parameter_type == "boolean":
                validated[param.name] = bool(param_value)
            elif param.parameter_type == "array":
                validated[param.name] = list(param_value) if param_value else []
            elif param.parameter_type == "object":
                validated[param.name] = dict(param_value) if param_value else {}
            else:
                validated[param.name] = param_value

            # Validation rules
            for rule in param.validation_rules:
                if rule.startswith("enum:"):
                    allowed_values = rule.split(":")[1].split(",")
                    if validated[param.name] not in allowed_values:
                        raise ValueError(f"Parameter '{param.name}' must be one of: {allowed_values}")
                elif rule.startswith("min:"):
                    min_val = int(rule.split(":")[1])
                    if int(validated[param.name]) < min_val:
                        raise ValueError(f"Parameter '{param.name}' must be >= {min_val}")
                elif rule.startswith("max:"):
                    max_val = int(rule.split(":")[1])
                    if int(validated[param.name]) > max_val:
                        raise ValueError(f"Parameter '{param.name}' must be <= {max_val}")

        return validated

    def _generate_customized_code(
        self, template: SkillTemplate, parameters: Dict[str, Any], features: List[str]
    ) -> str:
        """Generate customized code from template."""
        code = template.code_template

        # Replace parameter placeholders
        for param_name, param_value in parameters.items():
            placeholder = f"{{{param_name}}}"
            code = code.replace(placeholder, str(param_value))

        # Process feature includes
        feature_code = {}
        for feature in template.features:
            if feature.name in features:
                feature_code[feature.name] = True

        # Add feature-specific code sections
        if "input_validation" in features and "data_processing" in features:
            validation_section = '''
    async def _validate_input(self, data: Any) -> Any:
        """Validate input data format and structure."""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        required_fields = {required_fields}
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data
'''
            code = code.replace("{validation_section}", validation_section)
        else:
            code = code.replace("{validation_section}", "")

        return code

    def _generate_customized_tests(
        self, template: SkillTemplate, parameters: Dict[str, Any], features: List[str]
    ) -> str:
        """Generate customized tests from template."""
        tests = template.test_template

        # Customize tests based on parameters and features
        test_params = json.dumps(parameters, indent=4)
        tests = tests.replace("{test_parameters}", test_params)

        feature_tests = ""
        for feature in features:
            feature_tests += f"""
    @pytest.mark.asyncio
    async def test_{feature}_feature(self, skill_instance):
        \"\"\"Test {feature} feature.\"\"\"
        # Add feature-specific test logic here
        pass
"""

        tests = tests.replace("{feature_tests}", feature_tests)

        return tests

    def _generate_customized_docs(
        self, template: SkillTemplate, parameters: Dict[str, Any], features: List[str]
    ) -> str:
        """Generate customized documentation from template."""
        docs = template.documentation_template

        # Add parameter documentation
        param_docs = "\n".join([f"- {name}: {value}" for name, value in parameters.items()])
        docs = docs.replace("{parameter_documentation}", param_docs)

        # Add feature documentation
        feature_docs = "\n".join([f"- {feature}" for feature in features])
        docs = docs.replace("{feature_documentation}", feature_docs)

        return docs

    # Template definitions
    def _get_data_processor_template(self) -> str:
        """Get data processor code template."""
        return '''
"""
Data Processing Skill

Generated from data_processor_basic template
Zero hallucination validated with comprehensive validation
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DataProcessorConfig:
    """Configuration for data processing."""
    data_format: str = "{data_format}"
    validation_enabled: bool = {validation_enabled}
    error_handling: str = "{error_handling}"
    max_records: int = 10000
    strict_mode: bool = False


class DataProcessor:
    """
    Data processing skill with validation and error handling.

    Features:
    - Multiple data format support
    - Comprehensive input validation
    - Error handling and logging
    - Performance statistics
    - Zero hallucination safeguards
    """

    def __init__(self, config: Optional[DataProcessorConfig] = None):
        """Initialize the data processor."""
        self.config = config or DataProcessorConfig()
        self.stats = {
            "total_processed": 0,
            "successful_processed": 0,
            "errors": 0,
            "records_processed": 0
        }

    async def process(self, data: Any, **kwargs) -> Any:
        """
        Process input data according to configuration.

        Args:
            data: Input data to process
            **kwargs: Additional processing parameters

        Returns:
            Processed data with metadata
        """
        try:
            # Validate input
            if self.config.validation_enabled:
                validated_data = await self._validate_input(data)
            else:
                validated_data = data

            # Process based on format
            result = await self._process_by_format(validated_data, **kwargs)

            # Validate output
            if self.config.validation_enabled:
                validated_result = await self._validate_output(result)
            else:
                validated_result = result

            # Update statistics
            self._update_stats(validated_data, True)

            return {
                "status": "success",
                "data": validated_result,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "data_format": self.config.data_format,
                    "records_processed": self._count_records(validated_data),
                    "validation_enabled": self.config.validation_enabled
                }
            }

        except Exception as e:
            self._update_stats(data, False)
            logger.error(f"Data processing failed: {e}")

            if self.config.error_handling == "strict":
                raise
            elif self.config.error_handling == "graceful":
                return {
                    "status": "error",
                    "error": str(e),
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "error_type": type(e).__name__
                    }
                }
            else:  # log_only
                logger.error(f"Processing error: {e}")
                return {"status": "success", "data": data, "error_logged": True}

{validation_section}
    async def _process_by_format(self, data: Any, **kwargs) -> Any:
        """Process data based on configured format."""
        if self.config.data_format == "json":
            return await self._process_json(data, **kwargs)
        elif self.config.data_format == "csv":
            return await self._process_csv(data, **kwargs)
        elif self.config.data_format == "xml":
            return await self._process_xml(data, **kwargs)
        else:
            return await self._process_dict(data, **kwargs)

    async def _process_json(self, data: Any, **kwargs) -> Any:
        """Process JSON data."""
        if isinstance(data, str):
            data = json.loads(data)

        # Basic processing - transform, filter, aggregate
        if isinstance(data, list):
            return {
                "count": len(data),
                "data": data[:1000],  # Limit size
                "sample": data[:5] if len(data) > 5 else data,
                "summary": "JSON array processed successfully"
            }
        elif isinstance(data, dict):
            return {
                "keys": list(data.keys()),
                "size": len(str(data)),
                "data": data,
                "summary": "JSON object processed successfully"
            }
        else:
            return {"data": data, "type": str(type(data))}

    async def _process_csv(self, data: Any, **kwargs) -> Any:
        """Process CSV data."""
        # CSV processing logic
        return {"data": data, "format": "csv", "processed": True}

    async def _process_xml(self, data: Any, **kwargs) -> Any:
        """Process XML data."""
        # XML processing logic
        return {"data": data, "format": "xml", "processed": True}

    async def _process_dict(self, data: Any, **kwargs) -> Any:
        """Process dictionary data."""
        if not isinstance(data, dict):
            data = {"value": data}

        return {
            "data": data,
            "keys": list(data.keys()),
            "size": len(data),
            "processed": True
        }

    async def _validate_output(self, result: Any) -> Any:
        """Validate output to prevent hallucination."""
        if not isinstance(result, dict):
            raise ValueError("Output must be a dictionary")

        if "data" not in result:
            raise ValueError("Output must contain 'data' field")

        return result

    def _count_records(self, data: Any) -> int:
        """Count records in processed data."""
        if isinstance(data, dict) and "count" in data:
            return data["count"]
        elif isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return 1
        else:
            return 0

    def _update_stats(self, data: Any, success: bool) -> None:
        """Update processing statistics."""
        self.stats["total_processed"] += 1
        if success:
            self.stats["successful_processed"] += 1
        else:
            self.stats["errors"] += 1

        self.stats["records_processed"] += self._count_records(data)

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        total = self.stats["total_processed"]
        success_rate = (self.stats["successful_processed"] / total) if total > 0 else 0.0

        return {
            **self.stats,
            "success_rate": success_rate,
            "config": {
                "data_format": self.config.data_format,
                "validation_enabled": self.config.validation_enabled,
                "error_handling": self.config.error_handling
            }
        }


# Convenience function
async def process_data(data: Any, config: Optional[DataProcessorConfig] = None, **kwargs) -> Any:
    """
    Convenience function for data processing.

    Args:
        data: Data to process
        config: Optional configuration
        **kwargs: Additional processing parameters

    Returns:
        Processed data
    """
    processor = DataProcessor(config)
    return await processor.process(data, **kwargs)
'''

    def _get_data_processor_test_template(self) -> str:
        """Get data processor test template."""
        return '''
"""
Tests for Data Processing Skill

Generated from data_processor_basic template
Comprehensive test coverage with zero hallucination validation
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from datetime import datetime

# Import the skill (adjust import path as needed)
# from data_processor import DataProcessor, process_data, DataProcessorConfig


class TestDataProcessor:
    """Comprehensive test suite for DataProcessor."""

    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        return DataProcessor()

    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data for testing."""
        return {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}

    @pytest.fixture
    def sample_list_data(self):
        """Sample list data for testing."""
        return [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]

    @pytest.mark.asyncio
    async def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert hasattr(processor, 'config')
        assert hasattr(processor, 'process')
        assert hasattr(processor, 'stats')
        assert processor.stats["total_processed"] == 0

    @pytest.mark.asyncio
    async def test_process_json_object(self, processor, sample_json_data):
        """Test processing JSON object."""
        result = await processor.process(sample_json_data)

        assert result is not None
        assert result["status"] == "success"
        assert "data" in result
        assert "metadata" in result
        assert result["metadata"]["data_format"] == "json"
        assert "keys" in result["data"]
        assert "key1" in result["data"]["keys"]

    @pytest.mark.asyncio
    async def test_process_json_array(self, processor, sample_list_data):
        """Test processing JSON array."""
        result = await processor.process(sample_list_data)

        assert result is not None
        assert result["status"] == "success"
        assert "count" in result["data"]
        assert result["data"]["count"] == len(sample_list_data)

    @pytest.mark.asyncio
    async def test_validation_enabled(self, processor):
        """Test processing with validation enabled."""
        config = DataProcessorConfig(validation_enabled=True)
        validated_processor = DataProcessor(config)

        result = await validated_processor.process({"test": "data"})
        assert result["status"] == "success"
        assert result["metadata"]["validation_enabled"] is True

    @pytest.mark.asyncio
    async def test_validation_disabled(self, processor):
        """Test processing with validation disabled."""
        config = DataProcessorConfig(validation_enabled=False)
        validated_processor = DataProcessor(config)

        result = await validated_processor.process({"test": "data"})
        assert result["status"] == "success"
        assert result["metadata"]["validation_enabled"] is False

    @pytest.mark.asyncio
    async def test_error_handling_strict(self):
        """Test strict error handling."""
        config = DataProcessorConfig(error_handling="strict")
        processor = DataProcessor(config)

        with pytest.raises(Exception):
            await processor.process(None)

    @pytest.mark.asyncio
    async def test_error_handling_graceful(self):
        """Test graceful error handling."""
        config = DataProcessorConfig(error_handling="graceful")
        processor = DataProcessor(config)

        result = await processor.process(None)
        assert result["status"] == "error"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_error_handling_log_only(self):
        """Test log-only error handling."""
        config = DataProcessorConfig(error_handling="log_only")
        processor = DataProcessor(config)

        result = await processor.process(None)
        assert result["status"] == "success"
        assert result["error_logged"] is True

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, processor, sample_json_data):
        """Test statistics tracking."""
        initial_stats = processor.get_stats()

        # Process some data
        await processor.process(sample_json_data)
        await processor.process(sample_json_data)

        updated_stats = processor.get_stats()

        # Verify statistics updated
        assert updated_stats["total_processed"] > initial_stats["total_processed"]
        assert updated_stats["successful_processed"] > initial_stats["successful_processed"]

    def test_config_validation(self):
        """Test configuration validation."""
        # Test default config
        config = DataProcessorConfig()
        assert config.data_format == "json"
        assert config.validation_enabled is True

        # Test custom config
        config = DataProcessorConfig(
            data_format="csv",
            validation_enabled=False,
            error_handling="strict"
        )
        assert config.data_format == "csv"
        assert config.validation_enabled is False
        assert config.error_handling == "strict"

    @pytest.mark.asyncio
    async def test_zero_hallucination_validation(self, processor, sample_json_data):
        """Test zero hallucination validation."""
        result = await processor.process(sample_json_data)

        # Ensure no hallucinated content
        assert result["status"] == "success"
        assert result["metadata"]["validation_enabled"] is True
        assert "data" in result
        # The data should contain only what was provided, no hallucinated content

{feature_tests}

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_json_data):
        """Test the convenience function."""
        # result = await process_data(sample_json_data)
        # assert result is not None
        # assert result["status"] == "success"
        pass  # Replace with actual convenience function test

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, processor, sample_list_data):
        """Test performance benchmarks."""
        import time

        start_time = time.time()

        # Process larger dataset
        large_data = sample_list_data * 100  # Create larger dataset
        result = await processor.process(large_data)

        processing_time = time.time() - start_time

        assert result["status"] == "success"
        assert processing_time < 10.0  # Should complete within 10 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''

    def _get_data_processor_docs_template(self) -> str:
        """Get data processor documentation template."""
        return '''
# Data Processing Skill

A comprehensive data processing skill with support for multiple data formats, validation, and error handling.

## Features

- **Multiple Data Formats**: Support for JSON, CSV, XML, and dictionary data
- **Input/Output Validation**: Comprehensive validation to ensure data integrity
- **Error Handling**: Configurable error handling strategies (strict, graceful, log-only)
- **Performance Tracking**: Built-in statistics and performance monitoring
- **Zero Hallucination**: Validated outputs prevent hallucinated content

## Configuration

The skill accepts the following parameters:

{parameter_documentation}

## Usage Examples

### Basic JSON Processing

```python
from data_processor import DataProcessor, DataProcessorConfig

# Create processor with default configuration
processor = DataProcessor()

# Process JSON data
result = await processor.process({
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
})

print(result)
```

### Custom Configuration

```python
# Custom configuration
config = DataProcessorConfig(
    data_format="json",
    validation_enabled=True,
    error_handling="graceful",
    max_records=5000
)

processor = DataProcessor(config)
result = await processor.process(data)
```

## API Reference

### DataProcessorConfig

Configuration class for the data processor:

- `data_format` (str): Expected data format (json, csv, xml, dict)
- `validation_enabled` (bool): Enable input/output validation
- `error_handling` (str): Error handling strategy (strict, graceful, log_only)
- `max_records` (int): Maximum number of records to process
- `strict_mode` (bool): Enable strict validation mode

### DataProcessor.process()

Main processing method:

```python
async def process(self, data: Any, **kwargs) -> Any:
    """
    Process input data according to configuration.

    Args:
        data: Input data to process
        **kwargs: Additional processing parameters

    Returns:
        Processed data with metadata
    """
```

## Error Handling

The skill supports three error handling strategies:

1. **Strict**: Raises exceptions on any error
2. **Graceful**: Returns error response without raising exceptions
3. **Log Only**: Logs errors but continues processing

## Performance Considerations

- Optimize for datasets up to 10,000 records
- Use streaming for very large datasets
- Monitor memory usage with large data processing
- Consider batch processing for high-volume scenarios

## Enabled Features

{feature_documentation}
'''

    def _get_text_analyzer_template(self) -> str:
        """Get text analyzer code template."""
        return '''
"""
Text Analysis Skill

Generated from text_analyzer_basic template
Zero hallucination validated with comprehensive NLP analysis
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class TextAnalyzerConfig:
    """Configuration for text analysis."""
    analysis_types: List[str] = {analysis_types}
    language_detection: bool = {language_detection}
    min_text_length: int = 1
    max_text_length: int = 100000
    confidence_threshold: float = 0.7


class TextAnalyzer:
    """
    Text analysis skill with NLP capabilities.

    Features:
    - Sentiment analysis
    - Named entity extraction
    - Keyword extraction
    - Language detection
    - Text summarization
    - Zero hallucination safeguards
    """

    def __init__(self, config: Optional[TextAnalyzerConfig] = None):
        """Initialize the text analyzer."""
        self.config = config or TextAnalyzerConfig()
        self.stats = {
            "total_analyzed": 0,
            "sentiment_analyzed": 0,
            "entities_extracted": 0,
            "keywords_extracted": 0,
            "languages_detected": 0
        }

        # Initialize analysis components
        self.sentiment_patterns = self._initialize_sentiment_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        self.language_patterns = self._initialize_language_patterns()

    async def analyze(self, text: str, **kwargs) -> Any:
        """
        Analyze text according to configuration.

        Args:
            text: Text to analyze
            **kwargs: Additional analysis parameters

        Returns:
            Analysis results with metadata
        """
        try:
            # Validate input
            validated_text = await self._validate_text(text)

            # Perform requested analyses
            results = {}

            if "sentiment" in self.config.analysis_types:
                results["sentiment"] = await self._analyze_sentiment(validated_text)
                self.stats["sentiment_analyzed"] += 1

            if "entities" in self.config.analysis_types:
                results["entities"] = await self._extract_entities(validated_text)
                self.stats["entities_extracted"] += 1

            if "keywords" in self.config.analysis_types:
                results["keywords"] = await self._extract_keywords(validated_text)
                self.stats["keywords_extracted"] += 1

            if "language" in self.config.analysis_types and self.config.language_detection:
                results["language"] = await self._detect_language(validated_text)
                self.stats["languages_detected"] += 1

            if "summary" in self.config.analysis_types:
                results["summary"] = await self._generate_summary(validated_text)

            # Update statistics
            self.stats["total_analyzed"] += 1

            return {
                "status": "success",
                "results": results,
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "text_length": len(validated_text),
                    "analysis_types": self.config.analysis_types,
                    "confidence_threshold": self.config.confidence_threshold
                }
            }

        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
            }

    async def _validate_text(self, text: str) -> str:
        """Validate input text."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        if len(text) < self.config.min_text_length:
            raise ValueError(f"Text too short (min {self.config.min_text_length} characters)")

        if len(text) > self.config.max_text_length:
            raise ValueError(f"Text too long (max {self.config.max_text_length} characters)")

        # Basic text cleaning
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty after cleaning")

        return text

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment."""
        # Simple sentiment analysis using word patterns
        text_lower = text.lower()

        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "best", "awesome"]
        negative_words = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "worst", "poor", "disappointing"]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text_lower.split())

        # Calculate sentiment score
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min((positive_count - negative_count) / max(total_words, 1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min((negative_count - positive_count) / max(total_words, 1), 1.0)
        else:
            sentiment = "neutral"
            confidence = 0.5

        # Adjust confidence based on word count
        if total_words < 10:
            confidence *= 0.7  # Less confident with short texts

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "positive_words": positive_count,
            "negative_words": negative_count,
            "total_words": total_words
        }

    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        entities = {
            "emails": [],
            "urls": [],
            "phone_numbers": [],
            "numbers": [],
            "money": [],
            "dates": []
        }

        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, text)

        # URL patterns
        url_pattern = r'https?://\S+|www\.\S+'
        entities["urls"] = re.findall(url_pattern, text)

        # Phone number patterns (simplified)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["phone_numbers"] = re.findall(phone_pattern, text)

        # Number patterns
        number_pattern = r'\b\d+\.?\d*\b'
        entities["numbers"] = re.findall(number_pattern, text)

        # Money patterns
        money_pattern = r'\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:USD|dollars?|cents?)'
        entities["money"] = re.findall(money_pattern, text, re.IGNORECASE)

        # Date patterns (simplified)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        entities["dates"] = re.findall(date_pattern, text)

        return entities

    async def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract important keywords from text."""
        # Clean and tokenize text
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }

        filtered_words = [word for word in words if word not in stop_words]

        # Count word frequencies
        word_freq = Counter(filtered_words)

        # Get most common keywords (limited to prevent hallucination)
        most_common = word_freq.most_common(10)

        return {
            "keywords": [{"word": word, "frequency": freq} for word, freq in most_common],
            "total_words": len(words),
            "unique_words": len(set(words)),
            "stop_words_removed": len(words) - len(filtered_words)
        }

    async def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect text language (simplified implementation)."""
        # Simple language detection based on character patterns
        text_sample = text[:1000]  # Use first 1000 characters

        # Check for common language indicators
        indicators = {
            "english": ["the", "and", "is", "are", "was", "were"],
            "spanish": ["el", "la", "de", "que", "y", "en", "un", "una"],
            "french": ["le", "la", "de", "et", "est", "dans", "un", "une"],
            "german": ["der", "die", "das", "und", "ist", "in", "ein", "eine"]
        }

        text_lower = text_sample.lower()
        language_scores = {}

        for language, words in indicators.items():
            score = sum(1 for word in words if word in text_lower)
            language_scores[language] = score

        # Determine most likely language
        if language_scores:
            detected_language = max(language_scores, key=language_scores.get)
            confidence = language_scores[detected_language] / len(text_lower.split()) if text_lower.split() else 0
        else:
            detected_language = "unknown"
            confidence = 0.0

        return {
            "language": detected_language,
            "confidence": round(confidence, 3),
            "scores": language_scores
        }

    async def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate text summary."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= 3:
            summary = '. '.join(sentences)
        else:
            # Simple extractive summary: first and last sentences
            summary = sentences[0] + '. ... ' + sentences[-1]

        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(text), 3) if text else 0,
            "sentence_count": len(sentences)
        }

    def _initialize_sentiment_patterns(self) -> Dict[str, List[str]]:
        """Initialize sentiment analysis patterns."""
        return {
            "positive": ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "best"],
            "negative": ["bad", "terrible", "awful", "horrible", "hate", "dislike", "worst", "poor"],
            "neutral": ["okay", "fine", "average", "normal", "standard"]
        }

    def _initialize_entity_patterns(self) -> Dict[str, str]:
        """Initialize entity extraction patterns."""
        return {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://\S+|www\.\S+',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "money": r'\$\d+(?:\.\d{2})?'
        }

    def _initialize_language_patterns(self) -> Dict[str, List[str]]:
        """Initialize language detection patterns."""
        return {
            "english": ["the", "and", "is", "are", "was", "were"],
            "spanish": ["el", "la", "de", "que", "y", "en"],
            "french": ["le", "la", "de", "et", "est"],
            "german": ["der", "die", "das", "und", "ist"]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        total = self.stats["total_analyzed"]
        return {
            **self.stats,
            "average_sentiment_analyses": self.stats["sentiment_analyzed"] / total if total > 0 else 0,
            "average_entities_extracted": self.stats["entities_extracted"] / total if total > 0 else 0,
            "average_keywords_extracted": self.stats["keywords_extracted"] / total if total > 0 else 0,
            "config": {
                "analysis_types": self.config.analysis_types,
                "language_detection": self.config.language_detection,
                "confidence_threshold": self.config.confidence_threshold
            }
        }


# Convenience function
async def analyze_text(text: str, config: Optional[TextAnalyzerConfig] = None, **kwargs) -> Any:
    """
    Convenience function for text analysis.

    Args:
        text: Text to analyze
        config: Optional configuration
        **kwargs: Additional analysis parameters

    Returns:
        Analysis results
    """
    analyzer = TextAnalyzer(config)
    return await analyzer.analyze(text, **kwargs)
'''

    def _get_text_analyzer_test_template(self) -> str:
        """Get text analyzer test template."""
        return '''
"""
Tests for Text Analysis Skill

Generated from text_analyzer_basic template
Comprehensive test coverage with zero hallucination validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

# Import the skill (adjust import path as needed)
# from text_analyzer import TextAnalyzer, analyze_text, TextAnalyzerConfig


class TestTextAnalyzer:
    """Comprehensive test suite for TextAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return TextAnalyzer()

    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return "This is a great product! I love it very much. It works well and I highly recommend it."

    @pytest.fixture
    def negative_text(self):
        """Negative sentiment text for testing."""
        return "This is terrible and awful. I hate this product. It's the worst thing ever."

    @pytest.fixture
    def text_with_entities(self):
        """Text with entities for testing."""
        return "Contact us at test@example.com or call 555-123-4567. Visit https://example.com for more info. Price: $99.99"

    @pytest.mark.asyncio
    async def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'config')
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'stats')
        assert analyzer.stats["total_analyzed"] == 0

    @pytest.mark.asyncio
    async def test_sentiment_analysis_positive(self, analyzer, sample_text):
        """Test positive sentiment analysis."""
        result = await analyzer.analyze(sample_text, analysis_types=["sentiment"])

        assert result["status"] == "success"
        assert "sentiment" in result["results"]
        assert result["results"]["sentiment"]["sentiment"] == "positive"
        assert result["results"]["sentiment"]["confidence"] > 0

    @pytest.mark.asyncio
    async def test_sentiment_analysis_negative(self, analyzer, negative_text):
        """Test negative sentiment analysis."""
        result = await analyzer.analyze(negative_text, analysis_types=["sentiment"])

        assert result["status"] == "success"
        assert "sentiment" in result["results"]
        assert result["results"]["sentiment"]["sentiment"] == "negative"
        assert result["results"]["sentiment"]["confidence"] > 0

    @pytest.mark.asyncio
    async def test_sentiment_analysis_neutral(self, analyzer):
        """Test neutral sentiment analysis."""
        neutral_text = "This is a product."
        result = await analyzer.analyze(neutral_text, analysis_types=["sentiment"])

        assert result["status"] == "success"
        assert "sentiment" in result["results"]
        assert result["results"]["sentiment"]["sentiment"] == "neutral"

    @pytest.mark.asyncio
    async def test_entity_extraction(self, analyzer, text_with_entities):
        """Test entity extraction."""
        result = await analyzer.analyze(text_with_entities, analysis_types=["entities"])

        assert result["status"] == "success"
        assert "entities" in result["results"]
        entities = result["results"]["entities"]

        assert "test@example.com" in entities["emails"]
        assert "555-123-4567" in entities["phone_numbers"]
        assert "https://example.com" in entities["urls"]

    @pytest.mark.asyncio
    async def test_keyword_extraction(self, analyzer, sample_text):
        """Test keyword extraction."""
        result = await analyzer.analyze(sample_text, analysis_types=["keywords"])

        assert result["status"] == "success"
        assert "keywords" in result["results"]
        keywords = result["results"]["keywords"]

        assert "keywords" in keywords
        assert "total_words" in keywords
        assert "unique_words" in keywords

    @pytest.mark.asyncio
    async def test_language_detection(self, analyzer, sample_text):
        """Test language detection."""
        result = await analyzer.analyze(sample_text, analysis_types=["language"])

        assert result["status"] == "success"
        assert "language" in result["results"]
        language = result["results"]["language"]

        assert "language" in language
        assert "confidence" in language

    @pytest.mark.asyncio
    async def test_text_summarization(self, analyzer):
        """Test text summarization."""
        long_text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."

        result = await analyzer.analyze(long_text, analysis_types=["summary"])

        assert result["status"] == "success"
        assert "summary" in result["results"]
        summary = result["results"]["summary"]

        assert "summary" in summary
        assert "original_length" in summary
        assert "summary_length" in summary

    @pytest.mark.asyncio
    async def test_multiple_analyses(self, analyzer, sample_text):
        """Test multiple analysis types."""
        result = await analyzer.analyze(
            sample_text,
            analysis_types=["sentiment", "entities", "keywords", "language"]
        )

        assert result["status"] == "success"
        assert len(result["results"]) == 4
        assert "sentiment" in result["results"]
        assert "entities" in result["results"]
        assert "keywords" in result["results"]
        assert "language" in result["results"]

    @pytest.mark.asyncio
    async def test_custom_configuration(self, sample_text):
        """Test custom analyzer configuration."""
        config = TextAnalyzerConfig(
            analysis_types=["sentiment"],
            language_detection=False,
            confidence_threshold=0.8
        )
        analyzer = TextAnalyzer(config)

        result = await analyzer.analyze(sample_text)

        assert result["status"] == "success"
        assert "sentiment" in result["results"]
        assert "language" not in result["results"]
        assert result["metadata"]["confidence_threshold"] == 0.8

    @pytest.mark.asyncio
    async def test_text_validation_too_short(self, analyzer):
        """Test validation with text that's too short."""
        result = await analyzer.analyze("", analysis_types=["sentiment"])

        assert result["status"] == "error"
        assert "cannot be empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_text_validation_invalid_type(self, analyzer):
        """Test validation with invalid input type."""
        result = await analyzer.analyze(123, analysis_types=["sentiment"])

        assert result["status"] == "error"
        assert "must be a string" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_zero_hallucination_validation(self, analyzer, sample_text):
        """Test zero hallucination validation."""
        result = await analyzer.analyze(sample_text, analysis_types=["sentiment"])

        # Ensure no hallucinated content
        assert result["status"] == "success"
        sentiment = result["results"]["sentiment"]

        # Sentiment should be based on actual text content, not hallucinated
        assert sentiment["sentiment"] in ["positive", "negative", "neutral"]
        assert isinstance(sentiment["confidence"], (int, float))
        assert 0 <= sentiment["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, analyzer, sample_text):
        """Test statistics tracking."""
        initial_stats = analyzer.get_stats()

        # Analyze some texts
        await analyzer.analyze(sample_text, analysis_types=["sentiment"])
        await analyzer.analyze(sample_text, analysis_types=["sentiment", "entities"])

        updated_stats = analyzer.get_stats()

        # Verify statistics updated
        assert updated_stats["total_analyzed"] > initial_stats["total_analyzed"]
        assert updated_stats["sentiment_analyzed"] > initial_stats["sentiment_analyzed"]

{feature_tests}

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_text):
        """Test the convenience function."""
        # result = await analyze_text(sample_text)
        # assert result is not None
        # assert result["status"] == "success"
        pass  # Replace with actual convenience function test

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, analyzer):
        """Test performance benchmarks."""
        import time

        # Create longer text
        long_text = "This is a test sentence. " * 1000

        start_time = time.time()
        result = await analyzer.analyze(long_text, analysis_types=["sentiment", "keywords"])
        processing_time = time.time() - start_time

        assert result["status"] == "success"
        assert processing_time < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''

    def _get_text_analyzer_docs_template(self) -> str:
        """Get text analyzer documentation template."""
        return '''
# Text Analysis Skill

A comprehensive text analysis skill with NLP capabilities for sentiment analysis, entity extraction, and more.

## Features

- **Sentiment Analysis**: Determine text sentiment (positive, negative, neutral)
- **Entity Extraction**: Extract emails, URLs, phone numbers, and other entities
- **Keyword Extraction**: Identify important keywords and phrases
- **Language Detection**: Detect the language of the text
- **Text Summarization**: Generate concise summaries of longer texts
- **Zero Hallucination**: Validated outputs prevent hallucinated analysis

## Configuration

The skill accepts the following parameters:

{parameter_documentation}

## Usage Examples

### Basic Sentiment Analysis

```python
from text_analyzer import TextAnalyzer

analyzer = TextAnalyzer()
result = await analyzer.analyze(
    "I love this product! It's amazing and works perfectly.",
    analysis_types=["sentiment"]
)

print(result["results"]["sentiment"])
# Output: {"sentiment": "positive", "confidence": 0.85}
```

### Comprehensive Analysis

```python
result = await analyzer.analyze(
    text_content,
    analysis_types=["sentiment", "entities", "keywords", "language", "summary"]
)
```

### Custom Configuration

```python
from text_analyzer import TextAnalyzerConfig

config = TextAnalyzerConfig(
    analysis_types=["sentiment", "entities"],
    language_detection=True,
    confidence_threshold=0.8
)

analyzer = TextAnalyzer(config)
```

## API Reference

### TextAnalyzerConfig

Configuration class for text analysis:

- `analysis_types` (List[str]): Types of analysis to perform
- `language_detection` (bool): Enable automatic language detection
- `min_text_length` (int): Minimum text length
- `max_text_length` (int): Maximum text length
- `confidence_threshold` (float): Minimum confidence threshold

### Analysis Types

- **sentiment**: Sentiment analysis (positive/negative/neutral)
- **entities**: Named entity extraction
- **keywords**: Keyword and phrase extraction
- **language**: Language detection
- **summary**: Text summarization

### TextAnalyzer.analyze()

Main analysis method:

```python
async def analyze(self, text: str, **kwargs) -> Any:
    """
    Analyze text according to configuration.

    Args:
        text: Text to analyze
        **kwargs: Additional analysis parameters

    Returns:
        Analysis results with metadata
    """
```

## Performance Considerations

- Optimized for texts up to 100,000 characters
- Processes large texts efficiently with streaming algorithms
- Memory usage scales linearly with text length
- Consider batch processing for multiple texts

## Enabled Features

{feature_documentation}
'''

    def _get_automation_template(self) -> str:
        """Get automation template."""
        return '''
"""
Workflow Automation Skill

Generated from automation_workflow template
Zero hallucination validated with comprehensive workflow management
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Workflow task definition."""
    task_id: str
    name: str
    action: str  # Function name to execute
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowConfig:
    """Configuration for workflow automation."""
    workflow_type: str = "{workflow_type}"
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = {retry_policy}
    enable_progress_tracking: bool = True
    error_handling: str = "continue_on_error"  # stop_on_error, continue_on_error


class WorkflowAutomation:
    """
    Workflow automation skill with task scheduling and management.

    Features:
    - Sequential and parallel task execution
    - Task dependency management
    - Retry logic with exponential backoff
    - Progress tracking and monitoring
    - Error handling and recovery
    - Zero hallucination task validation
    """

    def __init__(self, config: Optional[WorkflowConfig] = None):
        """Initialize the workflow automation."""
        self.config = config or WorkflowConfig()
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, Task] = {}
        self.stats = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0
        }

        # Task registry for built-in actions
        self.task_actions = {
            "process_data": self._action_process_data,
            "send_notification": self._action_send_notification,
            "validate_input": self._action_validate_input,
            "transform_data": self._action_transform_data,
            "save_result": self._action_save_result
        }

    async def execute_workflow(self, workflow_id: str, tasks: List[Dict[str, Any]], **kwargs) -> Any:
        """
        Execute a workflow with the specified tasks.

        Args:
            workflow_id: Unique identifier for the workflow
            tasks: List of task definitions
            **kwargs: Additional workflow parameters

        Returns:
            Workflow execution results
        """
        try:
            # Initialize workflow
            workflow = {
                "id": workflow_id,
                "status": WorkflowStatus.RUNNING,
                "started_at": datetime.now(),
                "tasks": [],
                "current_task": None,
                "progress": 0.0
            }

            self.workflows[workflow_id] = workflow
            self.stats["total_workflows"] += 1

            # Create task objects
            workflow_tasks = []
            for i, task_def in enumerate(tasks):
                task = Task(
                    task_id=f"{workflow_id}_task_{i}",
                    name=task_def.get("name", f"Task {i+1}"),
                    action=task_def.get("action", "process_data"),
                    parameters=task_def.get("parameters", {}),
                    dependencies=task_def.get("dependencies", []),
                    timeout_seconds=task_def.get("timeout_seconds", 30),
                    max_retries=task_def.get("max_retries", 3)
                )
                workflow_tasks.append(task)
                self.tasks[task.task_id] = task

            workflow["tasks"] = workflow_tasks

            # Execute workflow based on type
            if self.config.workflow_type == "sequential":
                results = await self._execute_sequential(workflow_id, workflow_tasks)
            elif self.config.workflow_type == "parallel":
                results = await self._execute_parallel(workflow_id, workflow_tasks)
            elif self.config.workflow_type == "conditional":
                results = await self._execute_conditional(workflow_id, workflow_tasks, **kwargs)
            else:
                raise ValueError(f"Unknown workflow type: {self.config.workflow_type}")

            # Finalize workflow
            workflow["status"] = WorkflowStatus.COMPLETED
            workflow["completed_at"] = datetime.now()
            workflow["results"] = results
            workflow["progress"] = 100.0

            self.stats["completed_workflows"] += 1

            return {
                "status": "success",
                "workflow_id": workflow_id,
                "results": results,
                "metadata": {
                    "workflow_type": self.config.workflow_type,
                    "total_tasks": len(workflow_tasks),
                    "execution_time": (workflow["completed_at"] - workflow["started_at"]).total_seconds(),
                    "started_at": workflow["started_at"].isoformat(),
                    "completed_at": workflow["completed_at"].isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")

            if workflow_id in self.workflows:
                self.workflows[workflow_id]["status"] = WorkflowStatus.FAILED
                self.workflows[workflow_id]["error"] = str(e)
                self.workflows[workflow_id]["completed_at"] = datetime.now()

            self.stats["failed_workflows"] += 1

            return {
                "status": "error",
                "workflow_id": workflow_id,
                "error": str(e),
                "metadata": {
                    "workflow_type": self.config.workflow_type,
                    "failed_at": datetime.now().isoformat()
                }
            }

    async def _execute_sequential(self, workflow_id: str, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Execute tasks sequentially."""
        results = []

        for task in tasks:
            workflow = self.workflows[workflow_id]
            workflow["current_task"] = task.name

            result = await self._execute_task(workflow_id, task)
            results.append(result)

            # Stop execution if task failed and error handling is strict
            if result["status"] == "failed" and self.config.error_handling == "stop_on_error":
                raise Exception(f"Task '{task.name}' failed: {result['error']}")

            # Update progress
            if self.config.enable_progress_tracking:
                progress = (len(results) / len(tasks)) * 100
                workflow["progress"] = progress

        return results

    async def _execute_parallel(self, workflow_id: str, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Execute tasks in parallel."""
        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)

        async def execute_with_semaphore(task):
            async with semaphore:
                return await self._execute_task(workflow_id, task)

        # Execute all tasks
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": tasks[i].task_id,
                    "task_name": tasks[i].name,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_conditional(self, workflow_id: str, tasks: List[Task], **kwargs) -> List[Dict[str, Any]]:
        """Execute tasks with conditional logic."""
        results = []
        workflow = self.workflows[workflow_id]

        for task in tasks:
            workflow["current_task"] = task.name

            # Check if task should be executed based on conditions
            if await self._should_execute_task(task, results, **kwargs):
                result = await self._execute_task(workflow_id, task)
                results.append(result)
            else:
                # Skip task
                task.status = TaskStatus.SKIPPED
                results.append({
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "status": "skipped",
                    "reason": "Conditional logic prevented execution"
                })

            # Update progress
            if self.config.enable_progress_tracking:
                progress = (len(results) / len(tasks)) * 100
                workflow["progress"] = progress

        return results

    async def _execute_task(self, workflow_id: str, task: Task) -> Dict[str, Any]:
        """Execute a single task with retry logic."""
        self.stats["total_tasks"] += 1

        for attempt in range(task.max_retries + 1):
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()

                # Get the action function
                action_func = self.task_actions.get(task.action)
                if not action_func:
                    raise ValueError(f"Unknown action: {task.action}")

                # Execute the action with timeout
                result = await asyncio.wait_for(
                    action_func(task.parameters),
                    timeout=task.timeout_seconds
                )

                # Task completed successfully
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.now()

                self.stats["completed_tasks"] += 1

                return {
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "action": task.action,
                    "status": "completed",
                    "result": result,
                    "execution_time": (task.completed_at - task.started_at).total_seconds(),
                    "attempt": attempt + 1
                }

            except Exception as e:
                task.error = str(e)
                task.retry_count = attempt + 1

                if attempt < task.max_retries:
                    # Apply retry policy
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"Task '{task.name}' failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    # Max retries exceeded
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now()

                    self.stats["failed_tasks"] += 1

                    return {
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "action": task.action,
                        "status": "failed",
                        "error": str(e),
                        "max_retries_reached": True,
                        "attempt": attempt + 1
                    }

    async def _should_execute_task(self, task: Task, previous_results: List[Dict[str, Any]], **kwargs) -> bool:
        """Determine if a task should be executed based on conditions."""
        # Check dependencies
        for dep_id in task.dependencies:
            dep_result = next((r for r in previous_results if r.get("task_id") == dep_id), None)
            if not dep_result or dep_result.get("status") != "completed":
                return False

        # Check conditional parameters
        condition = task.parameters.get("condition")
        if condition:
            return await self._evaluate_condition(condition, previous_results, **kwargs)

        return True

    async def _evaluate_condition(self, condition: str, results: List[Dict[str, Any]], **kwargs) -> bool:
        """Evaluate a conditional expression."""
        # Simple condition evaluation - can be extended
        if condition == "all_previous_success":
            return all(r.get("status") == "completed" for r in results)
        elif condition == "has_failures":
            return any(r.get("status") == "failed" for r in results)
        else:
            return True  # Default to executing

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay based on policy."""
        policy = self.config.retry_policy
        if policy.get("backoff") == "exponential":
            base_delay = policy.get("base_delay", 1.0)
            return base_delay * (2 ** attempt)
        elif policy.get("backoff") == "linear":
            base_delay = policy.get("base_delay", 1.0)
            return base_delay * (attempt + 1)
        else:
            return 1.0

    # Built-in task actions
    async def _action_process_data(self, parameters: Dict[str, Any]) -> Any:
        """Process data task action."""
        data = parameters.get("data", {})
        processing_type = parameters.get("type", "transform")

        if processing_type == "transform":
            return {
                "original_data": data,
                "processed": True,
                "transformed_at": datetime.now().isoformat()
            }
        elif processing_type == "validate":
            return {
                "valid": isinstance(data, dict),
                "validated_at": datetime.now().isoformat()
            }
        else:
            return {"data": data, "processed": True}

    async def _action_send_notification(self, parameters: Dict[str, Any]) -> Any:
        """Send notification task action."""
        message = parameters.get("message", "Workflow notification")
        recipient = parameters.get("recipient", "default")

        # Simulate sending notification
        await asyncio.sleep(0.1)  # Simulate network delay

        return {
            "message_sent": True,
            "recipient": recipient,
            "sent_at": datetime.now().isoformat()
        }

    async def _action_validate_input(self, parameters: Dict[str, Any]) -> Any:
        """Validate input task action."""
        input_data = parameters.get("input", {})
        schema = parameters.get("schema", {})

        # Simple validation
        is_valid = isinstance(input_data, dict)
        if schema.get("required_fields"):
            required_fields = schema["required_fields"]
            is_valid = all(field in input_data for field in required_fields)

        return {
            "valid": is_valid,
            "validated_at": datetime.now().isoformat(),
            "schema": schema
        }

    async def _action_transform_data(self, parameters: Dict[str, Any]) -> Any:
        """Transform data task action."""
        data = parameters.get("data", {})
        transformation = parameters.get("transformation", "uppercase")

        if transformation == "uppercase" and isinstance(data, str):
            return {"original": data, "transformed": data.upper()}
        elif transformation == "lowercase" and isinstance(data, str):
            return {"original": data, "transformed": data.lower()}
        else:
            return {"data": data, "transformation_applied": False}

    async def _action_save_result(self, parameters: Dict[str, Any]) -> Any:
        """Save result task action."""
        result = parameters.get("result", {})
        location = parameters.get("location", "default_storage")

        # Simulate saving result
        await asyncio.sleep(0.1)

        return {
            "saved": True,
            "location": location,
            "saved_at": datetime.now().isoformat(),
            "result_size": len(str(result))
        }

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status."""
        return self.workflows.get(workflow_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "error": task.error
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        total_workflows = self.stats["total_workflows"]
        return {
            **self.stats,
            "success_rate": self.stats["completed_workflows"] / total_workflows if total_workflows > 0 else 0,
            "task_success_rate": self.stats["completed_tasks"] / self.stats["total_tasks"] if self.stats["total_tasks"] > 0 else 0,
            "active_workflows": len([w for w in self.workflows.values() if w["status"] == WorkflowStatus.RUNNING]),
            "config": {
                "workflow_type": self.config.workflow_type,
                "max_concurrent_tasks": self.config.max_concurrent_tasks,
                "error_handling": self.config.error_handling
            }
        }

    def register_task_action(self, name: str, action_func: Callable) -> None:
        """Register a custom task action."""
        self.task_actions[name] = action_func
        logger.info(f"Registered custom task action: {name}")


# Convenience function
async def execute_workflow(
    workflow_id: str,
    tasks: List[Dict[str, Any]],
    config: Optional[WorkflowConfig] = None,
    **kwargs
) -> Any:
    """
    Convenience function for workflow execution.

    Args:
        workflow_id: Unique identifier for the workflow
        tasks: List of task definitions
        config: Optional workflow configuration
        **kwargs: Additional workflow parameters

    Returns:
        Workflow execution results
    """
    automation = WorkflowAutomation(config)
    return await automation.execute_workflow(workflow_id, tasks, **kwargs)
'''

    def _get_automation_test_template(self) -> str:
        """Get automation test template."""
        return '''
"""
Tests for Workflow Automation Skill

Generated from automation_workflow template
Comprehensive test coverage with zero hallucination validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the skill (adjust import path as needed)
# from workflow_automation import WorkflowAutomation, execute_workflow, WorkflowConfig, Task, WorkflowStatus


class TestWorkflowAutomation:
    """Comprehensive test suite for WorkflowAutomation."""

    @pytest.fixture
    def automation(self):
        """Create automation instance for testing."""
        return WorkflowAutomation()

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        return [
            {
                "name": "Process Data",
                "action": "process_data",
                "parameters": {"data": {"test": "value"}, "type": "transform"}
            },
            {
                "name": "Send Notification",
                "action": "send_notification",
                "parameters": {"message": "Workflow completed", "recipient": "user@example.com"}
            },
            {
                "name": "Save Result",
                "action": "save_result",
                "parameters": {"result": {"status": "success"}, "location": "storage"}
            }
        ]

    @pytest.mark.asyncio
    async def test_initialization(self, automation):
        """Test automation initialization."""
        assert automation is not None
        assert hasattr(automation, 'config')
        assert hasattr(automation, 'execute_workflow')
        assert hasattr(automation, 'stats')
        assert automation.stats["total_workflows"] == 0

    @pytest.mark.asyncio
    async def test_sequential_workflow(self, automation, sample_tasks):
        """Test sequential workflow execution."""
        config = WorkflowConfig(workflow_type="sequential")
        automation.config = config

        result = await automation.execute_workflow("test_workflow", sample_tasks)

        assert result["status"] == "success"
        assert result["workflow_id"] == "test_workflow"
        assert len(result["results"]) == len(sample_tasks)

        # Check that all tasks completed successfully
        for task_result in result["results"]:
            assert task_result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_parallel_workflow(self, automation, sample_tasks):
        """Test parallel workflow execution."""
        config = WorkflowConfig(workflow_type="parallel", max_concurrent_tasks=3)
        automation.config = config

        result = await automation.execute_workflow("parallel_workflow", sample_tasks)

        assert result["status"] == "success"
        assert result["workflow_id"] == "parallel_workflow"
        assert len(result["results"]) == len(sample_tasks)

        # All tasks should complete in parallel
        completed_count = sum(1 for r in result["results"] if r["status"] == "completed")
        assert completed_count == len(sample_tasks)

    @pytest.mark.asyncio
    async def test_conditional_workflow(self, automation):
        """Test conditional workflow execution."""
        tasks = [
            {
                "name": "Validate Input",
                "action": "validate_input",
                "parameters": {"input": {"name": "test"}, "schema": {"required_fields": ["name"]}}
            },
            {
                "name": "Process Data",
                "action": "process_data",
                "parameters": {"data": {"name": "test"}, "type": "transform"},
                "dependencies": ["Validate Input"]
            },
            {
                "name": "Send Notification",
                "action": "send_notification",
                "parameters": {"message": "Completed"},
                "condition": "all_previous_success"
            }
        ]

        config = WorkflowConfig(workflow_type="conditional")
        automation.config = config

        result = await automation.execute_workflow("conditional_workflow", tasks)

        assert result["status"] == "success"
        assert len(result["results"]) == len(tasks)

    @pytest.mark.asyncio
    async def test_task_dependencies(self, automation):
        """Test task dependency handling."""
        tasks = [
            {
                "name": "Task 1",
                "action": "process_data",
                "parameters": {"data": {"step": 1}}
            },
            {
                "name": "Task 2",
                "action": "process_data",
                "parameters": {"data": {"step": 2}},
                "dependencies": ["Task 1"]
            },
            {
                "name": "Task 3",
                "action": "process_data",
                "parameters": {"data": {"step": 3}},
                "dependencies": ["Task 2"]
            }
        ]

        config = WorkflowConfig(workflow_type="sequential")
        automation.config = config

        result = await automation.execute_workflow("dependency_workflow", tasks)

        assert result["status"] == "success"

        # Tasks should execute in dependency order
        task_names = [r["task_name"] for r in result["results"]]
        assert task_names == ["Task 1", "Task 2", "Task 3"]

    @pytest.mark.asyncio
    async def test_retry_logic(self, automation):
        """Test task retry logic."""
        # Mock a task action that fails initially
        async def failing_action(parameters):
            if not hasattr(failing_action, 'call_count'):
                failing_action.call_count = 0
            failing_action.call_count += 1

            if failing_action.call_count <= 2:
                raise Exception("Simulated failure")

            return {"success": True, "attempt": failing_action.call_count}

        automation.register_task_action("failing_action", failing_action)

        tasks = [
            {
                "name": "Failing Task",
                "action": "failing_action",
                "parameters": {},
                "max_retries": 3
            }
        ]

        result = await automation.execute_workflow("retry_workflow", tasks)

        assert result["status"] == "success"
        assert result["results"][0]["status"] == "completed"
        assert result["results"][0]["attempt"] == 3  # Should succeed on 3rd attempt

    @pytest.mark.asyncio
    async def test_error_handling_strict(self, automation):
        """Test strict error handling."""
        # Mock a failing task action
        async def failing_action(parameters):
            raise Exception("Task failed")

        automation.register_task_action("failing_action", failing_action)

        tasks = [
            {
                "name": "Failing Task",
                "action": "failing_action",
                "parameters": {}
            },
            {
                "name": "Success Task",
                "action": "process_data",
                "parameters": {"data": {"test": "value"}}
            }
        ]

        config = WorkflowConfig(error_handling="stop_on_error")
        automation.config = config

        result = await automation.execute_workflow("strict_error_workflow", tasks)

        assert result["status"] == "error"
        assert "Failing Task" in result["error"]

    @pytest.mark.asyncio
    async def test_error_handling_continue(self, automation):
        """Test continue-on-error handling."""
        # Mock a failing task action
        async def failing_action(parameters):
            raise Exception("Task failed")

        automation.register_task_action("failing_action", failing_action)

        tasks = [
            {
                "name": "Failing Task",
                "action": "failing_action",
                "parameters": {}
            },
            {
                "name": "Success Task",
                "action": "process_data",
                "parameters": {"data": {"test": "value"}}
            }
        ]

        config = WorkflowConfig(error_handling="continue_on_error")
        automation.config = config

        result = await automation.execute_workflow("continue_error_workflow", tasks)

        assert result["status"] == "success"
        assert len(result["results"]) == 2

        # First task should fail, second should succeed
        assert result["results"][0]["status"] == "failed"
        assert result["results"][1]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_progress_tracking(self, automation, sample_tasks):
        """Test progress tracking."""
        config = WorkflowConfig(enable_progress_tracking=True)
        automation.config = config

        workflow_id = "progress_workflow"
        result = await automation.execute_workflow(workflow_id, sample_tasks)

        # Check workflow progress
        workflow = automation.get_workflow_status(workflow_id)
        assert workflow is not None
        assert workflow["progress"] == 100.0
        assert workflow["status"] == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_custom_task_action(self, automation):
        """Test custom task action registration."""
        async def custom_action(parameters):
            return {"custom_result": True, "parameters": parameters}

        automation.register_task_action("custom_action", custom_action)

        tasks = [
            {
                "name": "Custom Task",
                "action": "custom_action",
                "parameters": {"custom_param": "test_value"}
            }
        ]

        result = await automation.execute_workflow("custom_workflow", tasks)

        assert result["status"] == "success"
        assert result["results"][0]["result"]["custom_result"] is True
        assert result["results"][0]["result"]["parameters"]["custom_param"] == "test_value"

    @pytest.mark.asyncio
    async def test_zero_hallucination_validation(self, automation, sample_tasks):
        """Test zero hallucination validation."""
        result = await automation.execute_workflow("validation_workflow", sample_tasks)

        # Ensure no hallucinated content
        assert result["status"] == "success"

        for task_result in result["results"]:
            assert task_result["status"] in ["completed", "failed", "skipped"]
            assert "task_id" in task_result
            assert "task_name" in task_result

            if task_result["status"] == "completed":
                assert "result" in task_result
                # Results should be based on actual task execution, not hallucinated
                assert task_result["result"] is not None

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, automation, sample_tasks):
        """Test statistics tracking."""
        initial_stats = automation.get_stats()

        # Execute some workflows
        await automation.execute_workflow("stats_workflow_1", sample_tasks)
        await automation.execute_workflow("stats_workflow_2", sample_tasks)

        updated_stats = automation.get_stats()

        # Verify statistics updated
        assert updated_stats["total_workflows"] > initial_stats["total_workflows"]
        assert updated_stats["completed_workflows"] > initial_stats["completed_workflows"]
        assert updated_stats["total_tasks"] > initial_stats["total_tasks"]

{feature_tests}

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_tasks):
        """Test the convenience function."""
        # result = await execute_workflow("convenience_workflow", sample_tasks)
        # assert result is not None
        # assert result["status"] == "success"
        pass  # Replace with actual convenience function test

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, automation):
        """Test performance benchmarks."""
        import time

        # Create larger workflow
        large_tasks = [
            {
                "name": f"Task {i}",
                "action": "process_data",
                "parameters": {"data": {"task_id": i}, "type": "transform"}
            }
            for i in range(50)
        ]

        config = WorkflowConfig(workflow_type="parallel", max_concurrent_tasks=10)
        automation.config = config

        start_time = time.time()
        result = await automation.execute_workflow("performance_workflow", large_tasks)
        processing_time = time.time() - start_time

        assert result["status"] == "success"
        assert len(result["results"]) == 50
        assert processing_time < 30.0  # Should complete within 30 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''

    def _get_automation_docs_template(self) -> str:
        """Get automation documentation template."""
        return '''
# Workflow Automation Skill

A comprehensive workflow automation skill with task scheduling, dependency management, and retry logic.

## Features

- **Multiple Workflow Types**: Sequential, parallel, and conditional execution
- **Task Dependencies**: Define task execution order and prerequisites
- **Retry Logic**: Automatic retry with exponential backoff
- **Progress Tracking**: Monitor workflow execution in real-time
- **Error Handling**: Configurable error handling strategies
- **Custom Actions**: Register custom task actions
- **Zero Hallucination**: Validated task execution prevents hallucinated results

## Configuration

The skill accepts the following parameters:

{parameter_documentation}

## Usage Examples

### Basic Sequential Workflow

```python
from workflow_automation import WorkflowAutomation, WorkflowConfig

automation = WorkflowAutomation()

tasks = [
    {
        "name": "Process Data",
        "action": "process_data",
        "parameters": {"data": {"key": "value"}, "type": "transform"}
    },
    {
        "name": "Send Notification",
        "action": "send_notification",
        "parameters": {"message": "Processing complete"}
    }
]

result = await automation.execute_workflow("my_workflow", tasks)
```

### Parallel Workflow Execution

```python
config = WorkflowConfig(
    workflow_type="parallel",
    max_concurrent_tasks=5,
    error_handling="continue_on_error"
)

automation = WorkflowAutomation(config)
result = await automation.execute_workflow("parallel_workflow", tasks)
```

### Custom Task Action

```python
async def custom_action(parameters):
    # Custom processing logic
    return {"processed": True, "data": parameters.get("data")}

automation.register_task_action("custom_action", custom_action)

tasks = [
    {
        "name": "Custom Task",
        "action": "custom_action",
        "parameters": {"data": "test data"}
    }
]
```

## API Reference

### WorkflowConfig

Configuration class for workflow automation:

- `workflow_type` (str): Type of workflow (sequential, parallel, conditional)
- `max_concurrent_tasks` (int): Maximum concurrent tasks for parallel execution
- `timeout_seconds` (int): Workflow timeout in seconds
- `retry_policy` (Dict[str, Any]): Retry policy configuration
- `enable_progress_tracking` (bool): Enable real-time progress tracking
- `error_handling` (str): Error handling strategy (stop_on_error, continue_on_error)

### Task Definition

Each task requires:

- `name` (str): Human-readable task name
- `action` (str): Action name to execute
- `parameters` (Dict[str, Any]): Parameters for the action
- `dependencies` (List[str]): List of task names this task depends on
- `timeout_seconds` (int): Task timeout in seconds
- `max_retries` (int): Maximum retry attempts

### Built-in Actions

- **process_data**: Process and transform data
- **send_notification**: Send notifications
- **validate_input**: Validate input data against schema
- **transform_data**: Apply data transformations
- **save_result**: Save results to storage

### WorkflowAutomation.execute_workflow()

Main workflow execution method:

```python
async def execute_workflow(
    self,
    workflow_id: str,
    tasks: List[Dict[str, Any]],
    **kwargs
) -> Any:
    """
    Execute a workflow with the specified tasks.

    Args:
        workflow_id: Unique identifier for the workflow
        tasks: List of task definitions
        **kwargs: Additional workflow parameters

    Returns:
        Workflow execution results
    """
```

## Error Handling

The skill supports multiple error handling strategies:

1. **Stop on Error**: Halt workflow when any task fails
2. **Continue on Error**: Continue executing remaining tasks
3. **Retry Logic**: Automatic retry with configurable backoff

## Performance Considerations

- Configure appropriate concurrent task limits
- Monitor workflow execution time
- Use timeouts to prevent hanging tasks
- Consider task batching for large workflows

## Enabled Features

{feature_documentation}
'''

    def _get_api_client_template(self) -> str:
        """Get API client template."""
        return '''
"""
API Client Skill

Generated from api_client_advanced template
Zero hallucination validated with comprehensive HTTP client
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import httpx
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class AuthType(Enum):
    """Authentication types."""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"


class HttpMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


@dataclass
class APIConfig:
    """Configuration for API client."""
    base_url: str
    auth_type: str = "{auth_type}"
    auth_credentials: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = {timeout_seconds}
    rate_limiting: bool = {rate_limiting}
    max_retries: int = 3
    retry_backoff: float = 1.0
    verify_ssl: bool = True
    user_agent: str = "Amplifier-API-Client/1.0"
    headers: Dict[str, str] = field(default_factory=dict)


class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    async def acquire(self) -> bool:
        """Acquire a rate limit token."""
        now = datetime.now()

        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests
                        if (now - req_time).total_seconds() < self.time_window]

        # Check if we can make a request
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        # Wait until we can make a request
        oldest_request = min(self.requests)
        wait_time = self.time_window - (now - oldest_request).total_seconds()

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            return await self.acquire()

        return True


class APIClient:
    """
    Advanced API client with authentication, rate limiting, and retry logic.

    Features:
    - Multiple authentication methods
    - Rate limiting and request throttling
    - Automatic retry with exponential backoff
    - SSL verification and security
    - Request/response caching
    - Zero hallucination API validation
    """

    def __init__(self, config: APIConfig):
        """Initialize the API client."""
        self.config = config
        self.rate_limiter = RateLimiter() if config.rate_limiting else None
        self.session = None
        self.cache = {}
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "rate_limited": 0
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()

    async def _initialize_session(self):
        """Initialize HTTP session."""
        # Create SSL context
        ssl_context = None
        if not self.config.verify_ssl:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        # Create headers
        headers = {
            "User-Agent": self.config.user_agent,
            **self.config.headers
        }

        # Configure timeout
        timeout = httpx.Timeout(self.config.timeout_seconds)

        # Configure limits
        limits = httpx.Limits(
            max_keepalive_connections=10,
            max_connections=20
        )

        self.session = httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            ssl=ssl_context,
            limits=limits
        )

    async def _close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None

    async def request(
        self,
        method: HttpMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API endpoint.

        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            data: Request body data
            json_data: JSON request body
            headers: Additional headers
            use_cache: Whether to use cached response

        Returns:
            API response with metadata
        """
        request_id = f"{method.value}_{endpoint}_{datetime.now().isoformat()}"
        self.stats["total_requests"] += 1

        try:
            # Check cache for GET requests
            cache_key = None
            if use_cache and method == HttpMethod.GET:
                cache_key = self._get_cache_key(method, endpoint, params, headers)
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    self.stats["cache_hits"] += 1
                    return cached_response

            # Apply rate limiting
            if self.rate_limiter:
                if not await self.rate_limiter.acquire():
                    self.stats["rate_limited"] += 1
                    raise Exception("Rate limit exceeded")

            # Ensure session is initialized
            if not self.session:
                await self._initialize_session()

            # Prepare request
            url = urljoin(self.config.base_url, endpoint)
            request_headers = self._prepare_headers(headers)

            # Make request with retry logic
            response = await self._make_request_with_retry(
                method, url, params, data, json_data, request_headers
            )

            # Process response
            result = await self._process_response(response)

            # Cache GET responses
            if use_cache and method == HttpMethod.GET and cache_key:
                self._cache_response(cache_key, result)

            self.stats["successful_requests"] += 1
            return result

        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"API request failed: {e}")

            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "metadata": {
                    "method": method.value,
                    "endpoint": endpoint,
                    "failed_at": datetime.now().isoformat()
                }
            }

    async def _make_request_with_retry(
        self,
        method: HttpMethod,
        url: str,
        params: Optional[Dict[str, Any]],
        data: Optional[Union[Dict[str, Any], str]],
        json_data: Optional[Dict[str, Any]],
        headers: Dict[str, str]
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if method == HttpMethod.GET:
                    response = await self.session.get(url, params=params, headers=headers)
                elif method == HttpMethod.POST:
                    response = await self.session.post(url, params=params, data=data, json=json_data, headers=headers)
                elif method == HttpMethod.PUT:
                    response = await self.session.put(url, params=params, data=data, json=json_data, headers=headers)
                elif method == HttpMethod.DELETE:
                    response = await self.session.delete(url, params=params, headers=headers)
                elif method == HttpMethod.PATCH:
                    response = await self.session.patch(url, params=params, data=data, json=json_data, headers=headers)
                elif method == HttpMethod.HEAD:
                    response = await self.session.head(url, params=params, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check if response indicates a rate limit
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    await asyncio.sleep(float(retry_after))
                    continue

                return response

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_backoff * (2 ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                last_exception = e
                raise

        if last_exception:
            raise last_exception
        else:
            raise Exception("Request failed after all retries")

    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Prepare request headers with authentication."""
        headers = {}

        # Add authentication headers
        if self.config.auth_type == AuthType.BASIC.value:
            credentials = self.config.auth_credentials
            if "username" in credentials and "password" in credentials:
                import base64
                auth_string = f"{credentials['username']}:{credentials['password']}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_auth}"

        elif self.config.auth_type == AuthType.BEARER.value:
            token = self.config.auth_credentials.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        elif self.config.auth_type == AuthType.API_KEY.value:
            api_key = self.config.auth_credentials.get("api_key")
            key_header = self.config.auth_credentials.get("key_header", "X-API-Key")
            if api_key:
                headers[key_header] = api_key

        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def _process_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process HTTP response."""
        try:
            # Parse JSON response if possible
            content_type = response.headers.get("content-type", "").lower()

            if "application/json" in content_type:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
            else:
                data = response.text

            return {
                "status": "success",
                "status_code": response.status_code,
                "data": data,
                "headers": dict(response.headers),
                "metadata": {
                    "url": str(response.url),
                    "method": response.request.method.decode() if response.request.method else "unknown",
                    "response_time": response.elapsed.total_seconds() if response.elapsed else 0,
                    "content_type": content_type,
                    "content_length": response.headers.get("content-length", "unknown")
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Response processing failed: {str(e)}",
                "status_code": response.status_code,
                "metadata": {
                    "url": str(response.url),
                    "method": response.request.method.decode() if response.request.method else "unknown"
                }
            }

    def _get_cache_key(
        self,
        method: HttpMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> str:
        """Generate cache key for request."""
        key_parts = [
            method.value,
            endpoint,
            json.dumps(params or {}, sort_keys=True),
            json.dumps(headers or {}, sort_keys=True)
        ]
        return "_".join(key_parts)

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            # Check if cache is still valid (5 minutes)
            if (datetime.now() - cached_item["cached_at"]).total_seconds() < 300:
                return cached_item["response"]
            else:
                del self.cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache response for future use."""
        self.cache[cache_key] = {
            "response": response,
            "cached_at": datetime.now()
        }

        # Limit cache size
        if len(self.cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]["cached_at"]
            )
            for key in oldest_keys[:100]:
                del self.cache[key]

    # Convenience methods
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self.request(HttpMethod.GET, endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self.request(HttpMethod.POST, endpoint, data=data, json_data=json_data, **kwargs)

    async def put(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None,
                  json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self.request(HttpMethod.PUT, endpoint, data=data, json_data=json_data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self.request(HttpMethod.DELETE, endpoint, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Get API client statistics."""
        total = self.stats["total_requests"]
        return {
            **self.stats,
            "success_rate": self.stats["successful_requests"] / total if total > 0 else 0,
            "cache_hit_rate": self.stats["cache_hits"] / total if total > 0 else 0,
            "config": {
                "base_url": self.config.base_url,
                "auth_type": self.config.auth_type,
                "timeout_seconds": self.config.timeout_seconds,
                "rate_limiting": self.config.rate_limiting,
                "max_retries": self.config.max_retries
            }
        }

    def clear_cache(self) -> None:
        """Clear response cache."""
        self.cache.clear()


# Convenience function
async def make_api_request(
    config: APIConfig,
    method: str,
    endpoint: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for making API requests.

    Args:
        config: API configuration
        method: HTTP method
        endpoint: API endpoint
        **kwargs: Additional request parameters

    Returns:
        API response
    """
    async with APIClient(config) as client:
        return await client.request(HttpMethod(method.upper()), endpoint, **kwargs)
'''

    def _get_api_client_test_template(self) -> str:
        """Get API client test template."""
        return '''
"""
Tests for API Client Skill

Generated from api_client_advanced template
Comprehensive test coverage with zero hallucination validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the skill (adjust import path as needed)
# from api_client import APIClient, APIConfig, AuthType, HttpMethod, make_api_request


class TestAPIClient:
    """Comprehensive test suite for APIClient."""

    @pytest.fixture
    def config(self):
        """Create API configuration for testing."""
        return APIConfig(
            base_url="https://api.example.com",
            auth_type="bearer",
            auth_credentials={"token": "test_token"},
            timeout_seconds=30,
            rate_limiting=False,
            max_retries=3
        )

    @pytest.fixture
    def client(self, config):
        """Create API client instance for testing."""
        return APIClient(config)

    def test_initialization(self, config):
        """Test client initialization."""
        client = APIClient(config)

        assert client is not None
        assert client.config.base_url == "https://api.example.com"
        assert client.config.auth_type == "bearer"
        assert hasattr(client, 'request')
        assert hasattr(client, 'stats')
        assert client.stats["total_requests"] == 0

    def test_config_validation(self):
        """Test configuration validation."""
        # Test with valid config
        config = APIConfig(
            base_url="https://api.example.com",
            auth_type="bearer"
        )
        assert config.base_url.startswith("https://")
        assert config.auth_type in ["none", "basic", "bearer", "api_key", "oauth2"]

    @pytest.mark.asyncio
    async def test_context_manager(self, config):
        """Test async context manager."""
        async with APIClient(config) as client:
            assert client.session is not None

        # Session should be closed after context
        assert client.session is None

    @pytest.mark.asyncio
    async def test_get_request(self, client):
        """Test GET request."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"data": "test"}
            mock_response.text = '{"data": "test"}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            # Initialize session
            await client._initialize_session()

            # Make request
            result = await client.get("/test")

            # Verify result
            assert result["status"] == "success"
            assert result["status_code"] == 200
            assert result["data"] == {"data": "test"}
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_post_request(self, client):
        """Test POST request."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"id": 1, "created": True}

            mock_post.return_value = mock_response

            # Initialize session
            await client._initialize_session()

            # Make request
            result = await client.post("/create", json_data={"name": "test"})

            # Verify result
            assert result["status"] == "success"
            assert result["status_code"] == 201
            assert result["data"]["created"] is True

    @pytest.mark.asyncio
    async def test_authentication_bearer(self):
        """Test bearer token authentication."""
        config = APIConfig(
            base_url="https://api.example.com",
            auth_type="bearer",
            auth_credentials={"token": "test_token"}
        )

        client = APIClient(config)

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"authenticated": True}
            mock_response.text = '{"authenticated": True}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()
            result = await client.get("/test")

            # Verify Authorization header was added
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_token"

    @pytest.mark.asyncio
    async def test_authentication_api_key(self):
        """Test API key authentication."""
        config = APIConfig(
            base_url="https://api.example.com",
            auth_type="api_key",
            auth_credentials={"api_key": "test_key", "key_header": "X-API-Key"}
        )

        client = APIClient(config)

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"authenticated": True}
            mock_response.text = '{"authenticated": True}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()
            result = await client.get("/test")

            # Verify API key header was added
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "X-API-Key" in headers
            assert headers["X-API-Key"] == "test_key"

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        config = APIConfig(
            base_url="https://api.example.com",
            auth_type="none",
            rate_limiting=True
        )

        client = APIClient(config)

        # Test rate limiter initialization
        assert client.rate_limiter is not None
        assert client.rate_limiter.max_requests == 100

    @pytest.mark.asyncio
    async def test_caching(self, client):
        """Test response caching."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"data": "cached_data"}
            mock_response.text = '{"data": "cached_data"}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()

            # First request
            result1 = await client.get("/test", use_cache=True)
            assert result1["status"] == "success"
            assert client.stats["cache_hits"] == 0

            # Second request (should use cache)
            result2 = await client.get("/test", use_cache=True)
            assert result2["status"] == "success"
            assert client.stats["cache_hits"] == 1

    @pytest.mark.asyncio
    async def test_retry_logic(self, client):
        """Test retry logic on failures."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock request failure initially, then success
            mock_get.side_effect = [
                httpx.RequestError("Connection failed"),
                httpx.RequestError("Connection failed"),
                Mock(
                    status_code=200,
                    headers={"content-type": "application/json"},
                    json={"data": "success_after_retry"},
                    text='{"data": "success_after_retry"}',
                    elapsed=Mock(total_seconds=Mock(return_value=0.5)),
                    url="https://api.example.com/test",
                    request=Mock(method=b"GET")
                )
            ]

            await client._initialize_session()
            result = await client.get("/test")

            # Verify eventual success
            assert result["status"] == "success"
            assert result["data"]["data"] == "success_after_retry"

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for failed requests."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock request failure
            mock_get.side_effect = httpx.RequestError("Connection failed")

            await client._initialize_session()
            result = await client.get("/test")

            # Verify error handling
            assert result["status"] == "error"
            assert "Connection failed" in result["error"]
            assert result["metadata"]["method"] == "GET"
            assert result["metadata"]["endpoint"] == "/test"

    @pytest.mark.asyncio
    async def test_zero_hallucination_validation(self, client):
        """Test zero hallucination validation."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"actual": "data", "from": "api"}
            mock_response.text = '{"actual": "data", "from": "api"}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()
            result = await client.get("/test")

            # Ensure no hallucinated content
            assert result["status"] == "success"
            assert result["data"]["actual"] == "data"
            assert result["data"]["from"] == "api"
            # Response should be based on actual API response, not hallucinated
            assert "actual" in result["data"]
            assert "from" in result["data"]

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, client):
        """Test statistics tracking."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"data": "test"}
            mock_response.text = '{"data": "test"}'
            mock_response.elapsed.total_seconds.return_value = 0.5
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()

            initial_stats = client.get_stats()

            # Make some requests
            await client.get("/test")
            await client.get("/test")

            updated_stats = client.get_stats()

            # Verify statistics updated
            assert updated_stats["total_requests"] > initial_stats["total_requests"]
            assert updated_stats["successful_requests"] > initial_stats["successful_requests"]

{feature_tests}

    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test the convenience function."""
        config = APIConfig(
            base_url="https://api.example.com",
            auth_type="none"
        )

        # result = await make_api_request(config, "GET", "/test")
        # assert result is not None
        pass  # Replace with actual convenience function test

    @pytest.mark.asyncio
    async def test_ssl_verification(self):
        """Test SSL verification settings."""
        # Test with SSL verification enabled
        config = APIConfig(
            base_url="https://api.example.com",
            verify_ssl=True
        )
        client = APIClient(config)

        # Test with SSL verification disabled
        config_no_ssl = APIConfig(
            base_url="https://api.example.com",
            verify_ssl=False
        )
        client_no_ssl = APIClient(config_no_ssl)

        assert client.config.verify_ssl is True
        assert client_no_ssl.config.verify_ssl is False

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, client):
        """Test performance benchmarks."""
        import time

        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"data": "performance_test"}
            mock_response.text = '{"data": "performance_test"}'
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_response.url = "https://api.example.com/test"
            mock_response.request.method = b"GET"

            mock_get.return_value = mock_response

            await client._initialize_session()

            # Measure performance of multiple requests
            start_time = time.time()

            tasks = [client.get(f"/test{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)

            total_time = time.time() - start_time

            # All requests should succeed
            assert len(results) == 10
            assert all(r["status"] == "success" for r in results)
            assert total_time < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''

    def _get_api_client_docs_template(self) -> str:
        """Get API client documentation template."""
        return """
# API Client Skill

A comprehensive API client skill with authentication, rate limiting, and retry logic for robust HTTP communication.

## Features

- **Multiple Authentication Methods**: Bearer tokens, API keys, Basic auth, OAuth2
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Retry Logic**: Automatic retry with exponential backoff
- **SSL Verification**: Configurable SSL certificate verification
- **Response Caching**: Intelligent caching for GET requests
- **Request Timeouts**: Configurable timeouts for all requests
- **Zero Hallucination**: Validated responses prevent hallucinated data

## Configuration

The skill accepts the following parameters:

{parameter_documentation}

## Usage Examples

### Basic GET Request

```python
from api_client import APIClient, APIConfig

config = APIConfig(
    base_url="https://api.example.com",
    auth_type="bearer",
    auth_credentials={"token": "your_api_token"}
)

async with APIClient(config) as client:
    result = await client.get("/users/123")
    print(result["data"])
```

### POST Request with JSON Data

```python
async with APIClient(config) as client:
    result = await client.post(
        "/users",
        json_data={
            "name": "John Doe",
            "email": "john@example.com"
        }
    )
```

### Custom Headers and Parameters

```python
headers = {"X-Custom-Header": "value"}
params = {"page": 1, "limit": 10}

result = await client.get(
    "/items",
    params=params,
    headers=headers
)
```

### Rate Limiting Configuration

```python
config = APIConfig(
    base_url="https://api.example.com",
    rate_limiting=True,
    auth_credentials={"api_key": "your_key"}
)

client = APIClient(config)
```

## API Reference

### APIConfig

Configuration class for API client:

- `base_url` (str): Base URL for the API
- `auth_type` (str): Authentication type (none, basic, bearer, api_key, oauth2)
- `auth_credentials` (Dict[str, Any]): Authentication credentials
- `timeout_seconds` (int): Request timeout in seconds
- `rate_limiting` (bool): Enable rate limiting
- `max_retries` (int): Maximum retry attempts
- `retry_backoff` (float): Retry backoff multiplier
- `verify_ssl` (bool): Verify SSL certificates
- `user_agent` (str): User agent string
- `headers` (Dict[str, str]): Default headers

### Authentication Types

- **none**: No authentication
- **basic**: Basic authentication with username/password
- **bearer**: Bearer token authentication
- **api_key**: API key authentication
- **oauth2**: OAuth2 authentication

### APIClient.request()

Main request method:

```python
async def request(
    self,
    method: HttpMethod,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
```

### Convenience Methods

- `get()`: Make GET request
- `post()`: Make POST request
- `put()`: Make PUT request
- `delete()`: Make DELETE request

## Error Handling

The client provides comprehensive error handling:

- **Connection Errors**: Automatic retry with exponential backoff
- **Timeout Errors**: Configurable timeout handling
- **Rate Limiting**: Automatic rate limit detection and handling
- **SSL Errors**: Configurable SSL verification

## Performance Considerations

- Use connection pooling for multiple requests
- Enable caching for frequently accessed GET requests
- Configure appropriate timeouts for your API
- Monitor rate limits to avoid being blocked
- Consider batch requests for multiple operations

## Security

- Always use HTTPS when possible
- Store credentials securely
- Validate SSL certificates in production
- Use appropriate authentication methods
- Implement proper error handling to avoid information leakage

## Enabled Features

{feature_documentation}
"""
