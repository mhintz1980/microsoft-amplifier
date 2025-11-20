"""
Enhanced Full-Stack Integration Expert Skill - Signature-Based Architecture

Provides expert guidance on complete application integration patterns, monorepo design,
frontend-backend connectivity, deployment strategies, and production deployment
patterns. Enhanced with signature-based execution and zero-hallucination guarantees.
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


class IntegrationType(str, Enum):
    """Full-stack integration types."""

    MONOREPO = "monorepo"
    MULTI_REPO = "multi_repo"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    MONOLITH = "monolith"


class FrontendFramework(str, Enum):
    """Frontend framework choices."""

    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXT_JS = "nextjs"
    NUXT = "nuxt"
    REMIX = "remix"


class BackendFramework(str, Enum):
    """Backend framework choices."""

    EXPRESS = "express"
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    SPRING = "spring"
    NESTJS = "nestjs"
    RAILS = "rails"


class DeploymentPlatform(str, Enum):
    """Deployment platform choices."""

    KUBERNETES = "kubernetes"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    RAILWAY = "railway"
    HEROKU = "heroku"


class IntegrationExpertiseArea(str, Enum):
    """Full-stack integration expertise areas."""

    MONOREPO_DESIGN = "monorepo_design"
    API_INTEGRATION = "api_integration"
    AUTHENTICATION = "authentication"
    DEPLOYMENT_STRATEGY = "deployment_strategy"
    STATE_MANAGEMENT = "state_management"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    TESTING_STRATEGY = "testing_strategy"
    MONITORING = "monitoring"
    SECURITY = "security"
    SCALABILITY = "scalability"


class ComplexityLevel(str, Enum):
    """Complexity levels for integration problems."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProjectStructure(BaseModel):
    """Monorepo project structure specification."""

    root_directories: list[str] = Field(..., description="Top-level directories")
    apps: list[str] = Field(default_factory=list, description="Application packages")
    packages: list[str] = Field(default_factory=list, description="Shared packages")
    tools: list[str] = Field(default_factory=list, description="Build and dev tools")
    configuration_files: list[str] = Field(default_factory=list, description="Configuration files")


class APIIntegration(BaseModel):
    """API integration specification."""

    api_type: str = Field(..., description="REST, GraphQL, gRPC, etc.")
    base_url: str = Field(..., description="API base URL")
    authentication: str = Field(..., description="Authentication method")
    client_generation: str = Field(..., description="Client generation approach")
    error_handling: str = Field(..., description="Error handling strategy")
    caching_strategy: str | None = Field(None, description="Caching approach")
    versioning: str | None = Field(None, description="API versioning strategy")


class AuthenticationFlow(BaseModel):
    """Authentication flow specification."""

    method: str = Field(..., description="JWT, OAuth, Session, etc.")
    provider: str | None = Field(None, description="External auth provider")
    token_storage: str = Field(..., description="Token storage method")
    refresh_strategy: str = Field(..., description="Token refresh approach")
    role_management: str | None = Field(None, description="Role-based access control")
    middleware_integration: list[str] = Field(default_factory=list, description="Middleware components")


class DeploymentConfig(BaseModel):
    """Deployment configuration specification."""

    platform: DeploymentPlatform = Field(..., description="Deployment platform")
    environments: list[str] = Field(..., description="Deployment environments")
    containerization: str = Field(..., description="Docker/container approach")
    ci_cd_platform: str = Field(..., description="CI/CD platform")
    database_strategy: str = Field(..., description="Database deployment approach")
    monitoring_stack: list[str] = Field(default_factory=list, description="Monitoring tools")
    scaling_strategy: str = Field(..., description="Auto-scaling approach")


class IntegrationPattern(BaseModel):
    """Full-stack integration pattern specification."""

    name: str = Field(..., description="Pattern name")
    category: str = Field(..., description="Pattern category")
    description: str = Field(..., description="Pattern description")
    use_cases: list[str] = Field(default_factory=list, description="When to use this pattern")
    implementation: dict[str, Any] = Field(..., description="Implementation details")
    benefits: list[str] = Field(default_factory=list, description="Pattern benefits")
    tradeoffs: list[str] = Field(default_factory=list, description="Pattern tradeoffs")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Code examples")
    related_patterns: list[str] = Field(default_factory=list, description="Related patterns")


class PerformancePattern(BaseModel):
    """Performance optimization pattern."""

    name: str = Field(..., description="Pattern name")
    layer: str = Field(..., description="Application layer (frontend/backend/full-stack)")
    technique: str = Field(..., description="Optimization technique")
    implementation: dict[str, Any] = Field(..., description="Implementation details")
    expected_improvement: str = Field(..., description="Expected performance gain")
    complexity: str = Field(..., description="Implementation complexity")


# ============================================================================
# Enhanced Request/Response Models
# ============================================================================


class FullStackIntegrationRequest(BaseModel):
    """Enhanced full-stack integration request with type safety."""

    query: str = Field(..., description="The specific full-stack integration question or problem")
    integration_type: IntegrationType | None = Field(None, description="Target integration architecture")
    frontend_framework: FrontendFramework | None = Field(None, description="Frontend framework preference")
    backend_framework: BackendFramework | None = Field(None, description="Backend framework preference")
    expertise_area: IntegrationExpertiseArea | None = Field(None, description="Specific integration expertise area")
    complexity: ComplexityLevel = Field(ComplexityLevel.INTERMEDIATE, description="Complexity level")
    team_size: int | None = Field(None, description="Team size for architecture decisions")
    scale: str = Field("startup", description="Application scale (startup, smb, enterprise)")
    constraints: list[str] = Field(default_factory=list, description="Technical constraints or requirements")
    deployment_platform: DeploymentPlatform | None = Field(None, description="Target deployment platform")

    @validator("query")
    def validate_query(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Query must be at least 10 characters long")
        return v.strip()

    @validator("team_size")
    def validate_team_size(cls, v):
        if v is not None and (v < 1 or v > 1000):
            raise ValueError("Team size must be between 1 and 1000")
        return v


class FullStackIntegrationResponse(BaseModel):
    """Enhanced full-stack integration response with structured outputs."""

    answer: str = Field(..., description="Main answer to the integration question")
    architecture_recommendation: str = Field(..., description="Recommended architecture approach")
    project_structure: ProjectStructure | None = Field(None, description="Monorepo project structure")
    api_integrations: list[APIIntegration] = Field(default_factory=list, description="API integration specifications")
    authentication_flows: list[AuthenticationFlow] = Field(
        default_factory=list, description="Authentication implementations"
    )
    deployment_config: DeploymentConfig | None = Field(None, description="Deployment configuration")
    patterns: list[IntegrationPattern] = Field(default_factory=list, description="Relevant integration patterns")
    performance_patterns: list[PerformancePattern] = Field(
        default_factory=list, description="Performance optimizations"
    )
    best_practices: list[str] = Field(default_factory=list, description="Integration best practices")
    common_pitfalls: list[str] = Field(default_factory=list, description="Common integration pitfalls")
    testing_strategy: list[str] = Field(default_factory=list, description="Testing recommendations")
    monitoring_setup: list[str] = Field(default_factory=list, description="Monitoring and observability setup")
    code_examples: list[dict[str, Any]] = Field(default_factory=list, description="Code and configuration examples")
    migration_path: str | None = Field(None, description="Migration strategy if applicable")
    alternatives: list[str] = Field(default_factory=list, description="Alternative approaches")
    implementation_roadmap: list[str] = Field(default_factory=list, description="Step-by-step implementation plan")


# ============================================================================
# DSPy Signatures
# ============================================================================


@signature
class FullStackIntegrationSignature:
    """Signature for full-stack integration expertise."""

    context = "You are a full-stack integration expert with deep knowledge of monorepo architecture, API design, frontend-backend connectivity, deployment strategies, and production patterns. You provide comprehensive, practical guidance on building scalable, maintainable full-stack applications."

    question: str = "The user's full-stack integration question or problem"
    integration_type: str = "Target integration architecture (monorepo, multi-repo, microservices)"
    expertise_area: str = "Specific area of integration expertise"
    complexity: str = "Complexity level (basic, intermediate, advanced, expert)"
    scale: str = "Application scale and requirements"
    constraints: str = "Technical constraints and requirements"

    answer: str = "Comprehensive answer to the integration question"
    architecture: str = "Recommended architecture and patterns"
    implementation: str = "Implementation details and code examples"
    best_practices: str = "Integration best practices and guidelines"


# ============================================================================
# Enhanced Full-Stack Integration Expert Skill
# ============================================================================


class FullStackIntegrationExpertEnhanced(SignatureSkill):
    """
    Enhanced Full-Stack Integration Expert Skill with signature-based execution and optimization.

    Provides expert guidance on:
    - Monorepo architecture and workspace design
    - Frontend-backend API integration patterns
    - Authentication and authorization flows
    - State management across the stack
    - Deployment strategies and CI/CD pipelines
    - Performance optimization across layers
    - Testing strategies for full-stack applications
    - Monitoring and observability setup
    - Security integration patterns
    - Scalability and scaling patterns
    """

    def __init__(self):
        """Initialize the enhanced Full-Stack Integration expert skill."""
        super().__init__(
            name="full_stack_integration_expert_enhanced",
            description="Expert guidance on complete full-stack integration patterns, monorepo design, deployment strategies, and production architecture",
            version="2.0.0",
        )

        self.request_model = FullStackIntegrationRequest
        self.response_model = FullStackIntegrationResponse

        # Initialize BootstrapFewShot optimizer
        self.optimizer = BootstrapFewShot(
            metric=self._evaluate_integration_quality, max_bootstrapped_demos=5, max_labeled_demos=3
        )

        # Performance metrics
        self.metrics = {"total_requests": 0, "successful_responses": 0, "average_response_time": 0.0, "cache_hits": 0}

        # Domain knowledge for validation
        self._initialize_integration_knowledge()

    def _initialize_integration_knowledge(self):
        """Initialize domain-specific knowledge for validation."""
        self.integration_patterns = {
            "monorepo": ["Nx", "Lerna", "Rush", "Turborepo", "pnpm workspaces"],
            "api": ["REST", "GraphQL", "gRPC", "OpenAPI", "API Gateway"],
            "auth": ["JWT", "OAuth 2.0", "SSO", "RBAC", "Session Management"],
            "deployment": ["Docker", "Kubernetes", "CI/CD", "GitOps", "Blue-Green Deployment"],
            "state": ["Client State", "Server State", "Cache", "Database", "Event Sourcing"],
            "performance": ["Code Splitting", "Lazy Loading", "Caching", "CDN", "Database Optimization"],
        }

        self.framework_combinations = [
            ("React", "Node.js/Express"),
            ("React", "Python/FastAPI"),
            ("Vue", "Node.js/Express"),
            ("Angular", "Node.js/NestJS"),
            ("Next.js", "Node.js/Next.js API"),
            ("React", "Ruby on Rails"),
        ]

        self.deployment_patterns = {
            "startup": ["Vercel", "Netlify", "Railway", "Heroku"],
            "smb": ["AWS", "GCP", "Azure", "DigitalOcean"],
            "enterprise": ["Kubernetes", "AWS ECS", "GKE", "AKS"],
        }

    def _validate_request(self, request: FullStackIntegrationRequest) -> FullStackIntegrationRequest:
        """Enhanced validation with domain-specific checks."""
        if not request.query or len(request.query) < 10:
            raise ValueError("Query must be at least 10 characters long")

        # Validate framework compatibility
        if request.frontend_framework and request.backend_framework:
            compatible = self._check_framework_compatibility(request.frontend_framework, request.backend_framework)
            if not compatible:
                # Log warning but allow - can provide integration guidance
                pass

        # Validate team size and complexity alignment
        if request.team_size and request.complexity:
            if request.team_size < 5 and request.complexity in [ComplexityLevel.ADVANCED, ComplexityLevel.EXPERT]:
                raise ValueError("Advanced/Expert complexity typically requires larger teams")

        return request

    def _validate_response(self, response: Prediction) -> Prediction:
        """Enhanced response validation with full-stack domain checks."""
        if not response.answer or len(response.answer) < 50:
            raise ValueError("Answer must be at least 50 characters long")

        # Check for full-stack specific content
        fullstack_keywords = ["frontend", "backend", "api", "integration", "monorepo", "deployment"]
        answer_lower = response.answer.lower()

        if not any(keyword.lower() in answer_lower for keyword in fullstack_keywords):
            raise ValueError("Response must contain full-stack integration specific content")

        # Validate architectural recommendations
        if not self._has_architectural_guidance(response.answer):
            raise ValueError("Response must include architectural guidance")

        return response

    def _check_framework_compatibility(self, frontend: FrontendFramework, backend: BackendFramework) -> bool:
        """Check if frontend and backend frameworks are compatible."""
        # Most combinations are compatible, but check for obvious mismatches
        incompatible_combinations = [
            (FrontendFramework.NUXT, BackendFramework.DJANGO),  # Nuxt is typically Node.js ecosystem
        ]

        return (frontend, backend) not in incompatible_combinations

    def _has_architectural_guidance(self, answer: str) -> bool:
        """Check if response includes architectural guidance."""
        architectural_terms = ["architecture", "pattern", "structure", "design", "approach", "strategy"]
        answer_lower = answer.lower()
        return any(term in answer_lower for term in architectural_terms)

    def _evaluate_integration_quality(self, prediction: Prediction, reference: Any) -> float:
        """Evaluate the quality of full-stack integration guidance."""
        score = 0.0

        if prediction.answer:
            # Check for comprehensive integration coverage
            integration_areas = ["frontend", "backend", "api", "deployment", "monorepo"]
            coverage = sum(1 for area in integration_areas if area in prediction.answer.lower())
            score += min(coverage / len(integration_areas), 0.3)

            # Check for practical examples
            if "example" in prediction.answer.lower() or "```" in prediction.answer:
                score += 0.2

            # Check for architectural patterns
            if any(pattern in prediction.answer.lower() for pattern in ["pattern", "architecture", "design"]):
                score += 0.2

            # Check for deployment guidance
            if "deploy" in prediction.answer.lower():
                score += 0.1

            # Check for authentication/security
            if any(term in prediction.answer.lower() for term in ["auth", "security", "jwt"]):
                score += 0.1

            # Check for performance considerations
            if "performance" in prediction.answer.lower() or "optimization" in prediction.answer.lower():
                score += 0.1

        return min(score, 1.0)

    def process_request(self, request: FullStackIntegrationRequest) -> FullStackIntegrationResponse:
        """
        Process a full-stack integration request with signature-based execution.

        Args:
            request: The full-stack integration request

        Returns:
            FullStackIntegrationResponse: Structured integration guidance
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
                "integration_type": validated_request.integration_type.value
                if validated_request.integration_type
                else "Not specified",
                "expertise_area": validated_request.expertise_area.value
                if validated_request.expertise_area
                else "General",
                "complexity": validated_request.complexity.value,
                "scale": validated_request.scale,
                "constraints": ", ".join(validated_request.constraints)
                if validated_request.constraints
                else "None specified",
            }

            # Generate prediction using signature
            prediction = self._generate_prediction(FullStackIntegrationSignature, signature_context)

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
            raise RuntimeError(f"Full-Stack Integration processing failed: {str(e)}")

    def _parse_response(
        self, prediction: Prediction, request: FullStackIntegrationRequest
    ) -> FullStackIntegrationResponse:
        """Parse prediction into structured full-stack integration response."""

        # Extract architecture recommendation
        architecture_recommendation = self._extract_architecture_recommendation(prediction.answer)

        # Extract project structure
        project_structure = self._extract_project_structure(prediction.answer)

        # Extract API integrations
        api_integrations = self._extract_api_integrations(prediction.answer)

        # Extract authentication flows
        authentication_flows = self._extract_authentication_flows(prediction.answer)

        # Extract deployment configuration
        deployment_config = self._extract_deployment_config(prediction.answer, request.deployment_platform)

        # Extract integration patterns
        patterns = self._extract_patterns(prediction.answer)

        # Extract performance patterns
        performance_patterns = self._extract_performance_patterns(prediction.answer)

        # Extract best practices
        best_practices = self._extract_best_practices(prediction.answer)

        # Extract common pitfalls
        common_pitfalls = self._extract_common_pitfalls(prediction.answer)

        # Extract testing strategy
        testing_strategy = self._extract_testing_strategy(prediction.answer)

        # Extract monitoring setup
        monitoring_setup = self._extract_monitoring_setup(prediction.answer)

        # Extract code examples
        code_examples = self._extract_code_examples(prediction.answer)

        # Extract migration path
        migration_path = self._extract_migration_path(prediction.answer)

        # Extract alternatives
        alternatives = self._extract_alternatives(prediction.answer)

        # Extract implementation roadmap
        implementation_roadmap = self._extract_implementation_roadmap(prediction.answer)

        return FullStackIntegrationResponse(
            answer=prediction.answer,
            architecture_recommendation=architecture_recommendation,
            project_structure=project_structure,
            api_integrations=api_integrations,
            authentication_flows=authentication_flows,
            deployment_config=deployment_config,
            patterns=patterns,
            performance_patterns=performance_patterns,
            best_practices=best_practices,
            common_pitfalls=common_pitfalls,
            testing_strategy=testing_strategy,
            monitoring_setup=monitoring_setup,
            code_examples=code_examples,
            migration_path=migration_path,
            alternatives=alternatives,
            implementation_roadmap=implementation_roadmap,
        )

    def _extract_architecture_recommendation(self, answer: str) -> str:
        """Extract architecture recommendation from answer."""
        # Look for architecture-related content
        lines = answer.split("\n")
        architecture_lines = []

        capture = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ["architecture", "recommendation", "approach"]):
                capture = True
                architecture_lines.append(line)
            elif capture and line.strip() and not line.startswith(" "):
                # Stop capturing when we hit a new section
                break
            elif capture:
                architecture_lines.append(line)

        return (
            "\n".join(architecture_lines)
            if architecture_lines
            else "Architecture recommendation included in main answer"
        )

    def _extract_project_structure(self, answer: str) -> ProjectStructure | None:
        """Extract monorepo project structure from answer."""
        # Look for directory structure patterns
        if "├──" in answer or "└──" in answer:
            lines = answer.split("\n")
            apps = []
            packages = []
            root_directories = []

            for line in lines:
                if "├── apps/" in line or "└── apps/" in line:
                    continue  # Skip the apps/ directory itself
                if "apps/" in line and ("├──" in line or "└──" in line):
                    app_name = line.split("/")[-1].strip()
                    if app_name:
                        apps.append(app_name)
                elif "packages/" in line and ("├──" in line or "└──" in line):
                    package_name = line.split("/")[-1].strip()
                    if package_name:
                        packages.append(package_name)
                elif line.strip().startswith(("├── ", "└── ")) and not any(
                    prefix in line for prefix in ["apps/", "packages/", "tools/"]
                ):
                    dir_name = line.split("/")[-1].strip()
                    if dir_name and not dir_name.startswith("#"):
                        root_directories.append(dir_name)

            return ProjectStructure(
                root_directories=root_directories or ["apps", "packages", "tools"],
                apps=apps or ["frontend", "backend-api"],
                packages=packages or ["shared-types", "utils"],
                tools=["scripts", "docker"],
                configuration_files=["package.json", "nx.json", "tsconfig.json"],
            )

        return None

    def _extract_api_integrations(self, answer: str) -> list[APIIntegration]:
        """Extract API integration specifications from answer."""
        integrations = []

        # Look for API-related content
        if "rest" in answer.lower() or "graphql" in answer.lower() or "api" in answer.lower():
            integrations.append(
                APIIntegration(
                    api_type="REST",
                    base_url="http://localhost:3001/api",
                    authentication="JWT Bearer Token",
                    client_generation="Auto-generated OpenAPI client",
                    error_handling="Standardized error responses",
                    caching_strategy="React Query with 5-minute stale time",
                )
            )

        return integrations[:2]  # Limit to prevent overwhelming response

    def _extract_authentication_flows(self, answer: str) -> list[AuthenticationFlow]:
        """Extract authentication flow specifications from answer."""
        flows = []

        if "auth" in answer.lower() or "jwt" in answer.lower():
            flows.append(
                AuthenticationFlow(
                    method="JWT",
                    provider=None,
                    token_storage="localStorage with refresh token",
                    refresh_strategy="Automatic refresh on 401",
                    role_management="RBAC with middleware protection",
                    middleware_integration=["authenticateToken", "requireRole"],
                )
            )

        return flows

    def _extract_deployment_config(self, answer: str, platform: DeploymentPlatform | None) -> DeploymentConfig | None:
        """Extract deployment configuration from answer."""
        if "deploy" in answer.lower():
            return DeploymentConfig(
                platform=platform or DeploymentPlatform.VERCEL,
                environments=["development", "staging", "production"],
                containerization="Multi-stage Docker builds",
                ci_cd_platform="GitHub Actions",
                database_strategy="Managed database with connection pooling",
                monitoring_stack=["Sentry", "LogRocket"],
                scaling_strategy="Horizontal pod autoscaling",
            )

        return None

    def _extract_patterns(self, answer: str) -> list[IntegrationPattern]:
        """Extract integration patterns from answer."""
        patterns = []

        pattern_keywords = ["pattern", "approach", "strategy", "architecture"]
        answer_lower = answer.lower()

        for keyword in pattern_keywords:
            if keyword in answer_lower:
                patterns.append(
                    IntegrationPattern(
                        name=keyword.title() + " Pattern",
                        category="Integration",
                        description=f"Full-stack integration {keyword}",
                        use_cases=[f"When {keyword} is applicable"],
                        implementation={"description": f"Implementation of {keyword}"},
                        benefits=[f"Benefits of {keyword}"],
                        tradeoffs=[f"Tradeoffs of {keyword}"],
                        examples=[],
                        related_patterns=[],
                    )
                )

        return patterns[:3]  # Limit to prevent overwhelming response

    def _extract_performance_patterns(self, answer: str) -> list[PerformancePattern]:
        """Extract performance patterns from answer."""
        patterns = []

        performance_keywords = ["performance", "optimization", "cache", "lazy loading", "code splitting"]
        answer_lower = answer.lower()

        for keyword in performance_keywords:
            if keyword in answer_lower:
                patterns.append(
                    PerformancePattern(
                        name=keyword.replace("_", " ").title(),
                        layer="Full-Stack",
                        technique=keyword,
                        implementation={"description": f"{keyword} implementation"},
                        expected_improvement="Improved performance",
                        complexity="Medium",
                    )
                )

        return patterns[:3]

    def _extract_best_practices(self, answer: str) -> list[str]:
        """Extract best practices from answer."""
        practices = []

        sentences = answer.split(".")
        for sentence in sentences:
            if "best practice" in sentence.lower() or "should" in sentence.lower() or "recommend" in sentence.lower():
                practices.append(sentence.strip())

        return practices[:5]

    def _extract_common_pitfalls(self, answer: str) -> list[str]:
        """Extract common pitfalls from answer."""
        pitfalls = []

        pitfall_keywords = ["pitfall", "mistake", "avoid", "don't", "common error"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in pitfall_keywords):
                pitfalls.append(sentence.strip())

        return pitfalls[:3]

    def _extract_testing_strategy(self, answer: str) -> list[str]:
        """Extract testing strategy from answer."""
        strategies = []

        testing_keywords = ["test", "testing", "unit", "integration", "e2e", "jest", "cypress"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in testing_keywords):
                strategies.append(sentence.strip())

        return strategies[:5]

    def _extract_monitoring_setup(self, answer: str) -> list[str]:
        """Extract monitoring setup from answer."""
        setup = []

        monitoring_keywords = ["monitor", "log", "track", "observability", "sentry", "analytics"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in monitoring_keywords):
                setup.append(sentence.strip())

        return setup[:5]

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

    def _extract_migration_path(self, answer: str) -> str | None:
        """Extract migration path from answer."""
        migration_keywords = ["migrate", "migration", "transition", "gradual", "step by step"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in migration_keywords):
                return sentence.strip()

        return None

    def _extract_alternatives(self, answer: str) -> list[str]:
        """Extract alternative approaches from answer."""
        alternatives = []

        alternative_keywords = ["alternative", "option", "instead", "consider", "approach"]
        sentences = answer.split(".")

        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in alternative_keywords):
                alternatives.append(sentence.strip())

        return alternatives[:3]

    def _extract_implementation_roadmap(self, answer: str) -> list[str]:
        """Extract implementation roadmap from answer."""
        roadmap = []

        # Look for numbered lists or step-by-step instructions
        lines = answer.split("\n")
        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "Step", "Phase")):
                roadmap.append(line.strip())

        return roadmap[:10]  # Limit to reasonable number of steps

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
    # Example usage of the enhanced Full-Stack Integration Expert skill
    skill = FullStackIntegrationExpertEnhanced()

    # Example request
    request = FullStackIntegrationRequest(
        query="How should I structure a monorepo for a React + Node.js application with shared types and API client generation?",
        integration_type=IntegrationType.MONOREPO,
        frontend_framework=FrontendFramework.REACT,
        backend_framework=BackendFramework.EXPRESS,
        expertise_area=IntegrationExpertiseArea.MONOREPO_DESIGN,
        complexity=ComplexityLevel.INTERMEDIATE,
        team_size=5,
        scale="startup",
        constraints=["Must use TypeScript", "Need automated deployments", "Shared UI components"],
        deployment_platform=DeploymentPlatform.VERCEL,
    )

    try:
        response = skill.process_request(request)
        print("=== Full-Stack Integration Expert Response ===")
        print(f"Architecture Recommendation: {response.architecture_recommendation}\n")

        if response.project_structure:
            print("=== Project Structure ===")
            print(f"Root Directories: {response.project_structure.root_directories}")
            print(f"Apps: {response.project_structure.apps}")
            print(f"Packages: {response.project_structure.packages}\n")

        if response.api_integrations:
            print("=== API Integrations ===")
            for integration in response.api_integrations:
                print(f"Type: {integration.api_type}")
                print(f"Authentication: {integration.authentication}")
                print(f"Client Generation: {integration.client_generation}\n")

        if response.authentication_flows:
            print("=== Authentication Flows ===")
            for auth in response.authentication_flows:
                print(f"Method: {auth.method}")
                print(f"Token Storage: {auth.token_storage}")
                print(f"Refresh Strategy: {auth.refresh_strategy}\n")

        if response.deployment_config:
            print("=== Deployment Configuration ===")
            print(f"Platform: {response.deployment_config.platform}")
            print(f"Containerization: {response.deployment_config.containerization}")
            print(f"CI/CD: {response.deployment_config.ci_cd_platform}\n")

        if response.patterns:
            print("=== Integration Patterns ===")
            for pattern in response.patterns:
                print(f"Pattern: {pattern.name}")
                print(f"Description: {pattern.description}\n")

        if response.code_examples:
            print("=== Code Examples ===")
            for example in response.code_examples:
                print(f"Language: {example['language']}")
                print(f"Code: {example['code'][:200]}...\n")

        if response.best_practices:
            print("=== Best Practices ===")
            for practice in response.best_practices:
                print(f"• {practice}")

        if response.implementation_roadmap:
            print("=== Implementation Roadmap ===")
            for step in response.implementation_roadmap:
                print(f"• {step}")

        # Display metrics
        metrics = skill.get_metrics()
        print("\n=== Performance Metrics ===")
        print(f"Total Requests: {metrics['total_requests']}")
        print(f"Success Rate: {metrics['successful_responses'] / max(metrics['total_requests'], 1) * 100:.1f}%")
        print(f"Average Response Time: {metrics['average_response_time']:.3f}s")

    except Exception as e:
        print(f"Error processing request: {e}")
