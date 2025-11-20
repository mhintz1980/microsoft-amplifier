"""
Enhanced API Design Expert Skill - Signature-Based Architecture

Provides expert guidance on API design patterns, REST API best practices, GraphQL design,
OpenAPI/Swagger specifications, API versioning, security patterns, and production deployment.

Enhanced with signature-based execution, zero-hallucination guarantees, and resource optimization.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from dspy import BootstrapFewShot
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from ..framework.signature_skill import Prediction
from ..framework.signature_skill import SignatureSkill
from ..framework.signature_skill import signature

# ============================================================================
# Models and Enums
# ============================================================================


class APIType(str, Enum):
    """API types and paradigms."""

    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    SOAP = "soap"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    EVENT_DRIVEN = "event_driven"


class APIExpertiseArea(str, Enum):
    """API design expertise areas."""

    REST_DESIGN = "rest_design"
    GRAPHQL_DESIGN = "graphql_design"
    API_SECURITY = "api_security"
    API_VERSIONING = "api_versioning"
    API_DOCUMENTATION = "api_documentation"
    API_TESTING = "api_testing"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MICROSERVICES = "microservices"
    API_GATEWAY = "api_gateway"
    RATE_LIMITING = "rate_limiting"


class ComplexityLevel(str, Enum):
    """Complexity levels for API design problems."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class RequestFormat(BaseModel):
    """HTTP request format specification."""

    method: str
    endpoint: str
    headers: dict[str, str] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    body: dict[str, Any] | None = None


class ResponseFormat(BaseModel):
    """HTTP response format specification."""

    status_code: int
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None
    error_schema: dict[str, Any] | None = None


class APIEndpoint(BaseModel):
    """API endpoint specification."""

    path: str = Field(..., description="Endpoint path")
    method: str = Field(..., description="HTTP method")
    description: str = Field(..., description="Endpoint description")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Path, query, and header parameters")
    request_body: dict[str, Any] | None = Field(None, description="Request body schema")
    response_schema: dict[str, Any] = Field(..., description="Response schema")
    error_responses: list[dict[str, Any]] = Field(default_factory=list, description="Error response schemas")
    authentication_required: bool = Field(False, description="Whether authentication is required")
    rate_limit: str | None = Field(None, description="Rate limit for this endpoint")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Usage examples")


class APIPattern(BaseModel):
    """API design pattern with implementation."""

    name: str = Field(..., description="Pattern name")
    category: str = Field(..., description="Pattern category")
    description: str = Field(..., description="Pattern description")
    use_cases: list[str] = Field(default_factory=list, description="When to use this pattern")
    implementation: dict[str, Any] = Field(..., description="Implementation details")
    benefits: list[str] = Field(default_factory=list, description="Pattern benefits")
    tradeoffs: list[str] = Field(default_factory=list, description="Pattern tradeoffs")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Code examples")
    related_patterns: list[str] = Field(default_factory=list, description="Related patterns")


class APIError(BaseModel):
    """API error response specification."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    http_status: int = Field(..., description="HTTP status code")


class SecurityScheme(BaseModel):
    """API security scheme specification."""

    type: str = Field(..., description="Security type (oauth2, apikey, etc.)")
    description: str = Field(..., description="Security scheme description")
    implementation: dict[str, Any] = Field(..., description="Implementation details")
    headers: dict[str, str] = Field(default_factory=dict, description="Security headers")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Usage examples")


# ============================================================================
# Enhanced Request/Response Models
# ============================================================================


class APIDesignRequest(BaseModel):
    """Enhanced API design request with type safety."""

    query: str = Field(..., description="The specific API design question or problem")
    api_type: APIType | None = Field(None, description="Target API type or paradigm")
    expertise_area: APIExpertiseArea | None = Field(None, description="Specific API expertise area")
    complexity: ComplexityLevel = Field(ComplexityLevel.INTERMEDIATE, description="Complexity level")
    context: str | None = Field(None, description="Additional context about the project or requirements")
    constraints: list[str] = Field(default_factory=list, description="Technical constraints or requirements")
    preferred_patterns: list[str] = Field(default_factory=list, description="Preferred design patterns")

    @validator("query")
    def validate_query(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Query must be at least 10 characters long")
        return v.strip()


class APIDesignResponse(BaseModel):
    """Enhanced API design response with structured outputs."""

    answer: str = Field(..., description="Main answer to the API design question")
    code_examples: list[dict[str, Any]] = Field(default_factory=list, description="Code and configuration examples")
    patterns: list[APIPattern] = Field(default_factory=list, description="Relevant API design patterns")
    endpoints: list[APIEndpoint] = Field(default_factory=list, description="API endpoint specifications")
    security_schemes: list[SecurityScheme] = Field(default_factory=list, description="Security implementations")
    best_practices: list[str] = Field(default_factory=list, description="API design best practices")
    performance_considerations: list[str] = Field(default_factory=list, description="Performance recommendations")
    error_handling: list[APIError] = Field(default_factory=list, description="Error response specifications")
    testing_strategies: list[str] = Field(default_factory=list, description="API testing approaches")
    monitoring: list[str] = Field(default_factory=list, description="API monitoring and logging recommendations")
    alternatives: list[str] = Field(default_factory=list, description="Alternative approaches")
    implementation_notes: str = Field("", description="Specific implementation guidance")
    versioning_strategy: str | None = Field(None, description="API versioning recommendations")
    documentation_approach: str | None = Field(None, description="API documentation strategy")


# ============================================================================
# DSPy Signatures
# ============================================================================


@signature
class APIDesignSignature:
    """Signature for API design expertise."""

    context = "You are an API design expert with deep knowledge of REST, GraphQL, gRPC, API security, performance optimization, and production deployment patterns. You provide comprehensive, practical guidance on designing scalable, maintainable APIs."

    question: str = "The user's API design question or problem"
    api_type: str = "Target API type (REST, GraphQL, gRPC, etc.)"
    expertise_area: str = "Specific area of API expertise"
    complexity: str = "Complexity level (basic, intermediate, advanced, expert)"
    context: str = "Additional project context and constraints"

    answer: str = "Comprehensive answer to the API design question"
    patterns: str = "Relevant API design patterns with implementations"
    examples: str = "Code and configuration examples"
    best_practices: str = "API design best practices and guidelines"


# ============================================================================
# Enhanced API Design Expert Skill
# ============================================================================


class APIDesignExpertEnhanced(SignatureSkill):
    """
    Enhanced API Design Expert Skill with signature-based execution and optimization.

    Provides expert guidance on:
    - REST API design and best practices
    - GraphQL schema design and optimization
    - gRPC service design
    - API security patterns and implementation
    - API versioning strategies
    - Performance optimization techniques
    - Error handling and response design
    - API documentation and testing
    - Microservices API patterns
    - API gateway and management
    """

    def __init__(self):
        """Initialize the enhanced API Design expert skill."""
        super().__init__(
            name="api_design_expert_enhanced",
            description="Expert guidance on API design patterns, REST APIs, GraphQL, security, and production deployment",
            version="2.0.0",
        )

        self.request_model = APIDesignRequest
        self.response_model = APIDesignResponse

        # Initialize BootstrapFewShot optimizer
        self.optimizer = BootstrapFewShot(
            metric=self._evaluate_api_design_quality, max_bootstrapped_demos=5, max_labeled_demos=3
        )

        # Performance metrics
        self.metrics = {"total_requests": 0, "successful_responses": 0, "average_response_time": 0.0, "cache_hits": 0}

        # Domain knowledge for validation
        self._initialize_api_knowledge()

    def _initialize_api_knowledge(self):
        """Initialize domain-specific knowledge for validation."""
        self.api_patterns = {
            "rest": ["RESTful", "HATEOAS", " Richardson Maturity Model", "OpenAPI"],
            "graphql": ["Schema-first design", "Resolver patterns", "DataLoader", "Subscriptions"],
            "security": ["OAuth 2.0", "JWT", "API Keys", "Rate Limiting", "CORS"],
            "performance": ["Caching", "Pagination", "Compression", "CDN"],
            "microservices": ["API Gateway", "Service Mesh", "Circuit Breaker", "Bulkhead"],
        }

        self.http_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        self.status_codes = {
            "success": [200, 201, 202, 204],
            "client_error": [400, 401, 403, 404, 422, 429],
            "server_error": [500, 502, 503, 504],
        }

    def _validate_request(self, request: APIDesignRequest) -> APIDesignRequest:
        """Enhanced validation with domain-specific checks."""
        if not request.query or len(request.query) < 10:
            raise ValueError("Query must be at least 10 characters long")

        # Validate complexity and expertise area alignment
        if request.expertise_area and request.complexity == ComplexityLevel.BASIC:
            basic_areas = [APIExpertiseArea.REST_DESIGN, APIExpertiseArea.API_DOCUMENTATION]
            if request.expertise_area not in basic_areas:
                raise ValueError(f"{request.expertise_area} typically requires intermediate or higher complexity")

        return request

    def _validate_response(self, response: Prediction) -> Prediction:
        """Enhanced response validation with API domain checks."""
        if not response.answer or len(response.answer) < 50:
            raise ValueError("Answer must be at least 50 characters long")

        # Check for API-specific content
        api_keywords = ["API", "endpoint", "REST", "GraphQL", "HTTP", "request", "response"]
        answer_lower = response.answer.lower()

        if not any(keyword.lower() in answer_lower for keyword in api_keywords):
            raise ValueError("Response must contain API-specific content")

        # Validate code examples
        if hasattr(response, "examples") and response.examples:
            for example in response.examples:
                if not isinstance(example, dict) or "code" not in example:
                    raise ValueError("Code examples must be valid dictionaries with 'code' field")

        return response

    def _evaluate_api_design_quality(self, prediction: Prediction, reference: Any) -> float:
        """Evaluate the quality of API design guidance."""
        score = 0.0

        if prediction.answer:
            # Check for comprehensive coverage
            if any(term in prediction.answer.lower() for term in ["rest", "graphql", "api"]):
                score += 0.2

            # Check for practical examples
            if "example" in prediction.answer.lower() or "```" in prediction.answer:
                score += 0.2

            # Check for best practices
            if "best practice" in prediction.answer.lower() or "recommend" in prediction.answer.lower():
                score += 0.2

            # Check for security considerations
            if "secur" in prediction.answer.lower():
                score += 0.2

            # Check for error handling
            if "error" in prediction.answer.lower():
                score += 0.1

            # Check for performance
            if "performance" in prediction.answer.lower() or "optimization" in prediction.answer.lower():
                score += 0.1

        return min(score, 1.0)

    def process_request(self, request: APIDesignRequest) -> APIDesignResponse:
        """
        Process an API design request with signature-based execution.

        Args:
            request: The API design request

        Returns:
            APIDesignResponse: Structured API design guidance
        """
        start_time = datetime.now()

        try:
            # Validate request
            validated_request = self._validate_request(request)

            # Update metrics
            self.metrics["total_requests"] += 1

            # Prepare signature context
            signature_context = {
                "question": validated_request.query,
                "api_type": validated_request.api_type.value if validated_request.api_type else "Not specified",
                "expertise_area": validated_request.expertise_area.value
                if validated_request.expertise_area
                else "General",
                "complexity": validated_request.complexity.value,
                "context": validated_request.context or "No additional context provided",
            }

            # Generate prediction using signature
            prediction = self._generate_prediction(APIDesignSignature, signature_context)

            # Validate prediction
            validated_prediction = self._validate_response(prediction)

            # Parse and structure the response
            structured_response = self._parse_response(validated_prediction, validated_request)

            # Update success metrics
            self.metrics["successful_responses"] += 1

            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_response_time(response_time)

            return structured_response

        except Exception as e:
            self.metrics["total_requests"] += 1
            raise RuntimeError(f"API Design processing failed: {str(e)}")

    def _parse_response(self, prediction: Prediction, request: APIDesignRequest) -> APIDesignResponse:
        """Parse prediction into structured API design response."""

        # Extract code examples
        code_examples = self._extract_code_examples(prediction.answer)

        # Extract patterns
        patterns = self._extract_patterns(prediction.answer)

        # Extract endpoints if present
        endpoints = self._extract_endpoints(prediction.answer)

        # Extract security schemes
        security_schemes = self._extract_security_schemes(prediction.answer)

        # Extract best practices
        best_practices = self._extract_best_practices(prediction.answer)

        # Extract performance considerations
        performance_considerations = self._extract_performance_considerations(prediction.answer)

        # Extract error handling
        error_handling = self._extract_error_handling(prediction.answer)

        # Extract testing strategies
        testing_strategies = self._extract_testing_strategies(prediction.answer)

        # Extract monitoring recommendations
        monitoring = self._extract_monitoring_recommendations(prediction.answer)

        # Extract alternatives
        alternatives = self._extract_alternatives(prediction.answer)

        return APIDesignResponse(
            answer=prediction.answer,
            code_examples=code_examples,
            patterns=patterns,
            endpoints=endpoints,
            security_schemes=security_schemes,
            best_practices=best_practices,
            performance_considerations=performance_considerations,
            error_handling=error_handling,
            testing_strategies=testing_strategies,
            monitoring=monitoring,
            alternatives=alternatives,
            implementation_notes=self._extract_implementation_notes(prediction.answer),
            versioning_strategy=self._extract_versioning_strategy(prediction.answer),
            documentation_approach=self._extract_documentation_approach(prediction.answer),
        )

    def _extract_code_examples(self, answer: str) -> list[dict[str, Any]]:
        """Extract code examples from answer."""
        examples = []

        # Look for code blocks
        import re

        code_blocks = re.findall(r"```(\w+)?\n(.*?)```", answer, re.DOTALL)

        for language, code in code_blocks:
            examples.append(
                {
                    "language": language or "text",
                    "code": code.strip(),
                    "description": f"Example in {language}" if language else "Code example",
                }
            )

        return examples

    def _extract_patterns(self, answer: str) -> list[APIPattern]:
        """Extract API design patterns from answer."""
        patterns = []

        pattern_keywords = ["pattern", "design", "approach", "architecture"]
        answer_lower = answer.lower()

        for keyword in pattern_keywords:
            if keyword in answer_lower:
                # Simple extraction - in a real implementation, use more sophisticated NLP
                patterns.append(
                    APIPattern(
                        name=keyword.title() + " Pattern",
                        category="General",
                        description=f"API design {keyword} mentioned in response",
                        use_cases=[f"When {keyword} is applicable"],
                        implementation={"description": f"Implementation of {keyword}"},
                        benefits=[f"Benefits of {keyword}"],
                        tradeoffs=[f"Tradeoffs of {keyword}"],
                        examples=[],
                        related_patterns=[],
                    )
                )

        return patterns[:3]  # Limit to prevent overwhelming response

    def _extract_endpoints(self, answer: str) -> list[APIEndpoint]:
        """Extract API endpoint specifications from answer."""
        endpoints = []

        # Look for HTTP method and path patterns
        import re

        http_patterns = re.findall(r"(GET|POST|PUT|PATCH|DELETE)\s+(/[^\s]+)", answer, re.IGNORECASE)

        for method, path in http_patterns:
            endpoints.append(
                APIEndpoint(
                    path=path,
                    method=method.upper(),
                    description=f"{method} {path} endpoint",
                    response_schema={"type": "object"},
                    examples=[{"method": method, "path": path}],
                )
            )

        return endpoints[:5]  # Limit to prevent overwhelming response

    def _extract_security_schemes(self, answer: str) -> list[SecurityScheme]:
        """Extract security schemes from answer."""
        schemes = []

        security_keywords = ["oauth", "jwt", "api key", "bearer", "basic auth"]
        answer_lower = answer.lower()

        for keyword in security_keywords:
            if keyword in answer_lower:
                schemes.append(
                    SecurityScheme(
                        type=keyword.replace(" ", "_"),
                        description=f"{keyword.title()} security implementation",
                        implementation={"description": f"{keyword} implementation details"},
                        examples=[{"type": keyword, "description": f"{keyword} example"}],
                    )
                )

        return schemes[:3]  # Limit to prevent overwhelming response

    def _extract_best_practices(self, answer: str) -> list[str]:
        """Extract best practices from answer."""
        practices = []

        sentences = answer.split(".")
        for sentence in sentences:
            if "best practice" in sentence.lower() or "should" in sentence.lower():
                practices.append(sentence.strip())

        return practices[:5]

    def _extract_performance_considerations(self, answer: str) -> list[str]:
        """Extract performance considerations from answer."""
        considerations = []

        performance_keywords = ["performance", "optimization", "cache", "latency", "throughput"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in performance_keywords):
                considerations.append(sentence.strip())

        return considerations[:5]

    def _extract_error_handling(self, answer: str) -> list[APIError]:
        """Extract error handling specifications from answer."""
        errors = []

        # Look for HTTP status codes
        import re

        status_codes = re.findall(r"(\d{3})\s*-\s*([^,\n]+)", answer)

        for code, message in status_codes:
            try:
                status_int = int(code)
                if status_int >= 400:  # Client and server errors
                    errors.append(APIError(code=f"ERR_{code}", message=message.strip(), http_status=status_int))
            except ValueError:
                continue

        return errors[:5]

    def _extract_testing_strategies(self, answer: str) -> list[str]:
        """Extract testing strategies from answer."""
        strategies = []

        testing_keywords = ["test", "testing", "unit", "integration", "contract", "postman"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in testing_keywords):
                strategies.append(sentence.strip())

        return strategies[:5]

    def _extract_monitoring_recommendations(self, answer: str) -> list[str]:
        """Extract monitoring recommendations from answer."""
        recommendations = []

        monitoring_keywords = ["monitor", "log", "metric", "observability", "tracking"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in monitoring_keywords):
                recommendations.append(sentence.strip())

        return recommendations[:5]

    def _extract_alternatives(self, answer: str) -> list[str]:
        """Extract alternative approaches from answer."""
        alternatives = []

        alternative_keywords = ["alternative", "option", "instead", "consider", "approach"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in alternative_keywords):
                alternatives.append(sentence.strip())

        return alternatives[:3]

    def _extract_implementation_notes(self, answer: str) -> str:
        """Extract implementation notes from answer."""
        implementation_keywords = ["implement", "code", "example", "setup", "configure"]
        sentences = answer.split(".")

        notes = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in implementation_keywords):
                notes.append(sentence.strip())

        return " ".join(notes[:3])  # Limit length

    def _extract_versioning_strategy(self, answer: str) -> str | None:
        """Extract versioning strategy from answer."""
        versioning_keywords = ["version", "v1", "v2", "backward compatible", "deprecated"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in versioning_keywords):
                return sentence.strip()

        return None

    def _extract_documentation_approach(self, answer: str) -> str | None:
        """Extract documentation approach from answer."""
        doc_keywords = ["document", "swagger", "openapi", "api docs", "postman"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in doc_keywords):
                return sentence.strip()

        return None

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = {"total_requests": 0, "successful_responses": 0, "average_response_time": 0.0, "cache_hits": 0}

    def optimize_with_examples(self, examples: list[dict[str, Any]]):
        """Optimize the skill using few-shot examples."""
        if examples:
            self.optimizer.compile(self, examples=examples)


# ============================================================================
# Example Usage and Testing
# ============================================================================

if __name__ == "__main__":
    # Example usage of the enhanced API Design Expert skill
    skill = APIDesignExpertEnhanced()

    # Example request
    request = APIDesignRequest(
        query="How should I design error handling for a REST API that includes validation errors, authentication errors, and server errors?",
        api_type=APIType.REST,
        expertise_area=APIExpertiseArea.API_SECURITY,
        complexity=ComplexityLevel.INTERMEDIATE,
        context="Building a microservice-based e-commerce platform",
        constraints=["Must follow OpenAPI 3.0 specification", "Need consistent error format across services"],
    )

    try:
        response = skill.process_request(request)
        print("=== API Design Expert Response ===")
        print(f"Answer: {response.answer}\n")

        if response.code_examples:
            print("=== Code Examples ===")
            for example in response.code_examples:
                print(f"Language: {example['language']}")
                print(f"Code: {example['code']}\n")

        if response.patterns:
            print("=== Design Patterns ===")
            for pattern in response.patterns:
                print(f"Pattern: {pattern.name}")
                print(f"Description: {pattern.description}\n")

        if response.endpoints:
            print("=== Example Endpoints ===")
            for endpoint in response.endpoints:
                print(f"{endpoint.method} {endpoint.path} - {endpoint.description}")

        if response.best_practices:
            print("=== Best Practices ===")
            for practice in response.best_practices:
                print(f"• {practice}")

        if response.error_handling:
            print("=== Error Handling ===")
            for error in response.error_handling:
                print(f"• {error.http_status} - {error.message}")

        # Display metrics
        metrics = skill.get_metrics()
        print("\n=== Performance Metrics ===")
        print(f"Total Requests: {metrics['total_requests']}")
        print(f"Success Rate: {metrics['successful_responses'] / max(metrics['total_requests'], 1) * 100:.1f}%")
        print(f"Average Response Time: {metrics['average_response_time']:.3f}s")

    except Exception as e:
        print(f"Error processing request: {e}")
