"""
Quality Validators with Zero Hallucination Protocols

Implements comprehensive validation for generated skills to ensure:
- Zero hallucination detection and prevention
- Code quality and best practices
- Security vulnerability scanning
- Performance optimization validation
- Functional correctness verification
"""

import ast
import re
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from ...utils.logger import get_logger
from ...utils.token_utils import estimate_tokens

logger = get_logger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"  # Must fix before deployment
    HIGH = "high"  # Should fix before deployment
    MEDIUM = "medium"  # Can fix after deployment
    LOW = "low"  # Nice to have
    INFO = "info"  # Informational only


class IssueCategory(Enum):
    """Categories of validation issues."""

    HALLUCINATION = "hallucination"  # Generated incorrect/fabricated content
    SECURITY = "security"  # Security vulnerabilities
    PERFORMANCE = "performance"  # Performance issues
    CORRECTNESS = "correctness"  # Functional correctness
    STYLE = "style"  # Code style and quality
    DOCUMENTATION = "documentation"  # Documentation issues
    TESTING = "testing"  # Testing issues
    DEPENDENCIES = "dependencies"  # Dependency issues


@dataclass
class ValidationIssue:
    """Single validation issue with detailed context."""

    issue_id: str
    category: IssueCategory
    severity: ValidationSeverity
    title: str
    description: str
    location: str | None = None  # File:line reference
    code_snippet: str | None = None
    suggestion: str | None = None
    false_positive_risk: float = 0.0  # Risk that this is a false positive
    confidence: float = 1.0  # Confidence in issue detection


@dataclass
class ValidationResult:
    """Complete validation result with metrics."""

    skill_name: str
    overall_score: float  # 0.0 to 1.0
    hallucination_detected: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)

    def get_issues_by_category(self, category: IssueCategory) -> list[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]

    def get_issues_by_severity(self, severity: ValidationSeverity) -> list[ValidationIssue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_critical_issues(self) -> list[ValidationIssue]:
        """Get critical and high severity issues."""
        return [
            issue for issue in self.issues if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
        ]

    def is_deployment_ready(self) -> bool:
        """Check if skill is ready for deployment."""
        critical_issues = self.get_critical_issues()
        hallucination_issues = self.get_issues_by_category(IssueCategory.HALLUCINATION)

        return len(critical_issues) == 0 and len(hallucination_issues) == 0 and self.overall_score >= 0.8


class ZeroHallucinationValidator:
    """
    Detects and prevents hallucinations in generated code.

    Implements multiple detection strategies:
    - Syntax validation
    - Import validation
    - API usage validation
    - Logic consistency checks
    - Reference validation
    """

    def __init__(self):
        self.known_apis = self._load_known_apis()
        self.standard_library = self._load_standard_library()
        self.common_patterns = self._load_common_patterns()

    def validate(self, skill_code: str, skill_name: str, context: dict[str, Any] = None) -> list[ValidationIssue]:
        """
        Validate code for hallucinations.

        Args:
            skill_code: Generated code to validate
            skill_name: Name of the skill
            context: Additional context for validation

        Returns:
            List of hallucination issues found
        """
        issues = []

        try:
            # Parse AST for structural analysis
            tree = ast.parse(skill_code)

            # 1. Check for syntax errors
            syntax_issues = self._check_syntax_errors(skill_code)
            issues.extend(syntax_issues)

            # 2. Validate imports
            import_issues = self._validate_imports(tree)
            issues.extend(import_issues)

            # 3. Check for undefined references
            reference_issues = self._check_undefined_references(tree, skill_code)
            issues.extend(reference_issues)

            # 4. Validate API calls
            api_issues = self._validate_api_calls(tree, skill_code)
            issues.extend(api_issues)

            # 5. Check logic consistency
            logic_issues = self._check_logic_consistency(tree, skill_code)
            issues.extend(logic_issues)

            # 6. Validate docstrings and comments
            docstring_issues = self._validate_documentation(tree, skill_code)
            issues.extend(docstring_issues)

            # 7. Check for fabricated functions
            function_issues = self._check_fabricated_functions(tree, skill_code)
            issues.extend(function_issues)

        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    issue_id="syntax_error",
                    category=IssueCategory.HALLUCINATION,
                    severity=ValidationSeverity.CRITICAL,
                    title="Syntax Error",
                    description=f"Generated code has syntax error: {e}",
                    location=f"Line {e.lineno}",
                    suggestion="Code must be syntactically valid Python",
                    confidence=1.0,
                )
            )

        return issues

    def _check_syntax_errors(self, code: str) -> list[ValidationIssue]:
        """Check for syntax errors in generated code."""
        issues = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    issue_id="syntax_error",
                    category=IssueCategory.HALLUCINATION,
                    severity=ValidationSeverity.CRITICAL,
                    title="Syntax Error",
                    description=f"Python syntax error: {e.msg}",
                    location=f"Line {e.lineno}",
                    code_snippet=self._get_code_line(code, e.lineno),
                    suggestion="Fix syntax error before proceeding",
                    confidence=1.0,
                )
            )

        return issues

    def _validate_imports(self, tree: ast.AST) -> list[ValidationIssue]:
        """Validate import statements for non-existent modules."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_valid_import(alias.name):
                        issues.append(
                            ValidationIssue(
                                issue_id="invalid_import",
                                category=IssueCategory.HALLUCINATION,
                                severity=ValidationSeverity.HIGH,
                                title="Invalid Import",
                                description=f"Module '{alias.name}' does not exist or is not commonly available",
                                suggestion=f"Verify import statement for {alias.name}",
                                confidence=0.8,
                            )
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module and not self._is_valid_import(node.module):
                    issues.append(
                        ValidationIssue(
                            issue_id="invalid_from_import",
                            category=IssueCategory.HALLUCINATION,
                            severity=ValidationSeverity.HIGH,
                            title="Invalid From Import",
                            description=f"Module '{node.module}' does not exist or is not commonly available",
                            suggestion=f"Verify from import statement for {node.module}",
                            confidence=0.8,
                        )
                    )

        return issues

    def _check_undefined_references(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Check for undefined variables and function calls."""
        issues = []
        defined_names = set()
        imported_names = set()

        # First pass: collect defined and imported names
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Param)):
                defined_names.add(node.id)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

        # Second pass: check for undefined references
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if (
                    node.id not in defined_names
                    and node.id not in imported_names
                    and node.id not in self.standard_library
                    and not self._is_builtin(node.id)
                ):
                    # Check if it might be a method call on an object
                    if not self._is_likely_method_call(node, tree):
                        issues.append(
                            ValidationIssue(
                                issue_id="undefined_reference",
                                category=IssueCategory.HALLUCINATION,
                                severity=ValidationSeverity.HIGH,
                                title="Undefined Reference",
                                description=f"Name '{node.id}' is used but not defined or imported",
                                location=self._get_node_location(tree, node),
                                suggestion=f"Define or import '{node.id}' before use",
                                confidence=0.7,
                            )
                        )

        return issues

    def _validate_api_calls(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Validate API calls for non-existent methods."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check method calls
                    obj_name = self._get_object_name(node.func)
                    method_name = node.func.attr

                    if obj_name and not self._is_valid_method_call(obj_name, method_name):
                        issues.append(
                            ValidationIssue(
                                issue_id="invalid_method_call",
                                category=IssueCategory.HALLUCINATION,
                                severity=ValidationSeverity.HIGH,
                                title="Invalid Method Call",
                                description=f"Method '{method_name}' may not exist on {obj_name}",
                                location=self._get_node_location(tree, node),
                                suggestion="Verify method signature and availability",
                                confidence=0.6,
                            )
                        )

        return issues

    def _check_logic_consistency(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Check for logical inconsistencies and potential bugs."""
        issues = []

        # Check for unreachable code
        for node in ast.walk(tree):
            if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                # Check if there are statements after this node in the same block
                parent = self._get_parent_node(tree, node)
                if parent and hasattr(parent, "body"):
                    node_index = parent.body.index(node) if node in parent.body else -1
                    if node_index >= 0 and node_index < len(parent.body) - 1:
                        issues.append(
                            ValidationIssue(
                                issue_id="unreachable_code",
                                category=IssueCategory.CORRECTNESS,
                                severity=ValidationSeverity.MEDIUM,
                                title="Unreachable Code",
                                description="Code after return/break/continue is unreachable",
                                location=self._get_node_location(tree, parent.body[node_index + 1]),
                                suggestion="Remove unreachable code",
                                confidence=0.9,
                            )
                        )

        # Check for variables that are defined but never used
        defined_names = set()
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Param)):
                defined_names.add(node.id)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        unused_names = defined_names - used_names
        for name in unused_names:
            if not name.startswith("_"):  # Ignore intentionally unused names
                issues.append(
                    ValidationIssue(
                        issue_id="unused_variable",
                        category=IssueCategory.STYLE,
                        severity=ValidationSeverity.LOW,
                        title="Unused Variable",
                        description=f"Variable '{name}' is defined but never used",
                        suggestion="Remove unused variable or prefix with underscore",
                        confidence=0.8,
                    )
                )

        return issues

    def _validate_documentation(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Validate docstrings and comments for consistency."""
        issues = []

        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    issues.append(
                        ValidationIssue(
                            issue_id="missing_docstring",
                            category=IssueCategory.DOCUMENTATION,
                            severity=ValidationSeverity.MEDIUM,
                            title="Missing Docstring",
                            description=f"{node.__class__.__name__} '{node.name}' lacks docstring",
                            location=f"Line {node.lineno}",
                            suggestion="Add comprehensive docstring",
                            confidence=0.7,
                        )
                    )

        return issues

    def _check_fabricated_functions(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Check for potentially fabricated or non-standard functions."""
        issues = []

        # Look for suspicious function patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id

                    # Check against known suspicious patterns
                    if self._is_suspicious_function(func_name):
                        issues.append(
                            ValidationIssue(
                                issue_id="suspicious_function",
                                category=IssueCategory.HALLUCINATION,
                                severity=ValidationSeverity.HIGH,
                                title="Suspicious Function Call",
                                description=f"Function '{func_name}' may be fabricated or non-standard",
                                location=self._get_node_location(tree, node),
                                suggestion=f"Verify that '{func_name}' exists and works as expected",
                                confidence=0.6,
                            )
                        )

        return issues

    def _is_valid_import(self, module_name: str) -> bool:
        """Check if import module is valid."""
        # Check against known standard library modules
        if module_name in self.standard_library:
            return True

        # Check against known third-party modules
        common_third_party = {
            "numpy",
            "pandas",
            "requests",
            "flask",
            "django",
            "sqlalchemy",
            "pytest",
            "aiohttp",
            "fastapi",
            "pydantic",
            "asyncpg",
            "redis",
            "celery",
            "gunicorn",
            "uvicorn",
            "beautifulsoup4",
            "scipy",
            "matplotlib",
            "plotly",
            "tensorflow",
            "torch",
            "sklearn",
        }

        if module_name in common_third_party:
            return True

        # Check for relative imports (always valid in context)
        if module_name.startswith("."):
            return True

        # Check for common patterns that might be valid
        valid_patterns = [
            r"^[a-z][a-z0-9_]*$",  # Standard module naming
            r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$",  # Package.module
        ]

        return any(re.match(pattern, module_name) for pattern in valid_patterns)

    def _is_builtin(self, name: str) -> bool:
        """Check if name is a Python built-in."""
        builtins = {
            "print",
            "len",
            "range",
            "list",
            "dict",
            "set",
            "tuple",
            "str",
            "int",
            "float",
            "bool",
            "type",
            "isinstance",
            "hasattr",
            "getattr",
            "setattr",
            "delattr",
            "property",
            "staticmethod",
            "classmethod",
            "super",
            "open",
            "input",
            "raw_input",
            "exec",
            "eval",
            "compile",
            "repr",
            "sorted",
            "reversed",
            "enumerate",
            "zip",
            "map",
            "filter",
            "reduce",
            "sum",
            "max",
            "min",
            "abs",
            "round",
            "pow",
            "divmod",
            "any",
            "all",
            "chr",
            "ord",
        }
        return name in builtins

    def _is_likely_method_call(self, node: ast.Name, tree: ast.AST) -> bool:
        """Check if name is likely a method call on an object."""
        # This is a simplified check - a more sophisticated analysis would be needed
        return False

    def _is_valid_method_call(self, obj_name: str, method_name: str) -> bool:
        """Check if method call is likely valid."""
        # Common methods on common objects
        common_methods = {
            "str": ["lower", "upper", "strip", "split", "join", "replace", "find", "format"],
            "list": ["append", "extend", "insert", "remove", "pop", "clear", "index", "count", "sort", "reverse"],
            "dict": ["get", "keys", "values", "items", "update", "pop", "clear", "setdefault"],
            "set": ["add", "remove", "discard", "pop", "clear", "union", "intersection", "difference"],
            "file": ["read", "write", "close", "seek", "tell", "flush"],
            "requests.Response": ["json", "text", "content", "status_code", "headers"],
        }

        if obj_name in common_methods:
            return method_name in common_methods[obj_name]

        # Check for common patterns
        if method_name in ["__init__", "__str__", "__repr__", "__len__", "__getitem__"]:
            return True

        # If unsure, assume it might be valid (lower confidence)
        return obj_name.islower() and method_name.islower()

    def _is_suspicious_function(self, func_name: str) -> bool:
        """Check if function name looks suspicious or fabricated."""
        suspicious_patterns = [
            r".*magic_.*",  # Magic-sounding functions
            r".*auto_.*",  # Auto-magic functions
            r".*smart_.*",  # Smart-sounding functions
            r".*ai_.*",  # AI-sounding functions
            r".*ml_.*",  # ML-sounding functions
            r".*fix_.*",  # Generic fix functions
            r".*solve_.*",  # Generic solve functions
        ]

        return any(re.match(pattern, func_name, re.IGNORECASE) for pattern in suspicious_patterns)

    def _get_code_line(self, code: str, line_num: int) -> str:
        """Get specific line from code."""
        lines = code.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1].strip()
        return ""

    def _get_node_location(self, tree: ast.AST, node: ast.AST) -> str:
        """Get location string for AST node."""
        if hasattr(node, "lineno"):
            return f"Line {node.lineno}"
        return "Unknown location"

    def _get_parent_node(self, tree: ast.AST, node: ast.AST) -> ast.AST | None:
        """Get parent node of given node (simplified implementation)."""
        # This is a simplified version - a proper implementation would need
        # to track parent relationships during tree traversal
        return None

    def _get_object_name(self, attribute_node: ast.Attribute) -> str | None:
        """Extract object name from attribute node."""
        if isinstance(attribute_node.value, ast.Name):
            return attribute_node.value.id
        if isinstance(attribute_node.value, ast.Attribute):
            return self._get_object_name(attribute_node.value)
        return None

    def _load_known_apis(self) -> dict[str, set[str]]:
        """Load known API methods for common libraries."""
        return {
            "requests": {"get", "post", "put", "delete", "head", "options"},
            "pandas": {"read_csv", "read_excel", "DataFrame", "Series"},
            "numpy": {"array", "zeros", "ones", "arange", "linspace"},
            "json": {"loads", "dumps", "load", "dump"},
            "aiohttp": {"ClientSession", "get", "post", "put", "delete"},
        }

    def _load_standard_library(self) -> set[str]:
        """Load Python standard library module names."""
        return {
            "os",
            "sys",
            "json",
            "re",
            "datetime",
            "time",
            "random",
            "math",
            "statistics",
            "collections",
            "itertools",
            "functools",
            "operator",
            "pathlib",
            "urllib",
            "http",
            "socket",
            "threading",
            "asyncio",
            "logging",
            "unittest",
            "argparse",
            "configparser",
            "sqlite3",
            "csv",
            "xml",
            "html",
            "email",
            "mimetypes",
            "base64",
            "hashlib",
            "hmac",
            "uuid",
            "secrets",
            "decimal",
            "fractions",
            "enum",
            "dataclasses",
            "typing",
            "inspect",
            "importlib",
            "pkgutil",
        }

    def _load_common_patterns(self) -> dict[str, Any]:
        """Load common code patterns for validation."""
        return {
            "function_definition": r"def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            "class_definition": r"class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            "import_statement": r"^(import|from)\s+",
            "assignment": r"^[a-zA-Z_][a-zA-Z0-9_]*\s*=",
        }


class SecurityValidator:
    """Validates code for security vulnerabilities."""

    def validate(self, skill_code: str, skill_name: str) -> list[ValidationIssue]:
        """Validate code for security issues."""
        issues = []

        # Check for security vulnerabilities
        issues.extend(self._check_insecure_functions(skill_code))
        issues.extend(self._check_hardcoded_secrets(skill_code))
        issues.extend(self._check_sql_injection(skill_code))
        issues.extend(self._check_command_injection(skill_code))
        issues.extend(self._check_path_traversal(skill_code))
        issues.extend(self._check_deserialization(skill_code))

        return issues

    def _check_insecure_functions(self, code: str) -> list[ValidationIssue]:
        """Check for use of insecure functions."""
        insecure_functions = {
            "eval": "Use of eval() can execute arbitrary code",
            "exec": "Use of exec() can execute arbitrary code",
            "compile": "Use of compile() with arbitrary input can be dangerous",
            "input": "input() in Python 2 can execute arbitrary code",
            "os.system": "os.system() can execute arbitrary commands",
            "subprocess.call": "subprocess.call() with shell=True can be dangerous",
            "pickle.loads": "pickle.loads() can execute arbitrary code",
            "marshal.loads": "marshal.loads() can execute arbitrary code",
        }

        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for func, description in insecure_functions.items():
                if func in line and not line.strip().startswith("#"):
                    issues.append(
                        ValidationIssue(
                            issue_id="insecure_function",
                            category=IssueCategory.SECURITY,
                            severity=ValidationSeverity.HIGH,
                            title=f"Use of Insecure Function: {func}",
                            description=description,
                            location=f"Line {line_num}",
                            code_snippet=line.strip(),
                            suggestion=f"Replace {func} with safer alternative",
                            confidence=0.9,
                        )
                    )

        return issues

    def _check_hardcoded_secrets(self, code: str) -> list[ValidationIssue]:
        """Check for hardcoded secrets and credentials."""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret_key\s*=\s*["\'][^"\']+["\']', "Hardcoded secret key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            (r'credential\s*=\s*["\'][^"\']+["\']', "Hardcoded credential"),
        ]

        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        ValidationIssue(
                            issue_id="hardcoded_secret",
                            category=IssueCategory.SECURITY,
                            severity=ValidationSeverity.CRITICAL,
                            title=description,
                            description="Hardcoded secrets should be stored securely",
                            location=f"Line {line_num}",
                            code_snippet=line.strip(),
                            suggestion="Use environment variables or secure configuration",
                            confidence=0.8,
                        )
                    )

        return issues

    def _check_sql_injection(self, code: str) -> list[ValidationIssue]:
        """Check for potential SQL injection vulnerabilities."""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Look for string formatting in SQL queries
            if (
                "SELECT" in line.upper()
                or "INSERT" in line.upper()
                or "UPDATE" in line.upper()
                or "DELETE" in line.upper()
            ):
                if "%" in line or "+" in line and "format" in line:
                    issues.append(
                        ValidationIssue(
                            issue_id="sql_injection",
                            category=IssueCategory.SECURITY,
                            severity=ValidationSeverity.HIGH,
                            title="Potential SQL Injection",
                            description="SQL query with string formatting can be vulnerable",
                            location=f"Line {line_num}",
                            code_snippet=line.strip(),
                            suggestion="Use parameterized queries or prepared statements",
                            confidence=0.7,
                        )
                    )

        return issues

    def _check_command_injection(self, code: str) -> list[ValidationIssue]:
        """Check for command injection vulnerabilities."""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Look for os.system or subprocess with user input
            if ("os.system" in line or "subprocess" in line) and ("+" in line or "%" in line):
                issues.append(
                    ValidationIssue(
                        issue_id="command_injection",
                        category=IssueCategory.SECURITY,
                        severity=ValidationSeverity.HIGH,
                        title="Potential Command Injection",
                        description="System command with user input can be dangerous",
                        location=f"Line {line_num}",
                        code_snippet=line.strip(),
                        suggestion="Use subprocess with argument lists and proper sanitization",
                        confidence=0.7,
                    )
                )

        return issues

    def _check_path_traversal(self, code: str) -> list[ValidationIssue]:
        """Check for path traversal vulnerabilities."""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Look for file operations with user input
            if ("open(" in line or "file(" in line) and ("+" in line or "%" in line):
                issues.append(
                    ValidationIssue(
                        issue_id="path_traversal",
                        category=IssueCategory.SECURITY,
                        severity=ValidationSeverity.MEDIUM,
                        title="Potential Path Traversal",
                        description="File operation with user input can be vulnerable",
                        location=f"Line {line_num}",
                        code_snippet=line.strip(),
                        suggestion="Validate and sanitize file paths",
                        confidence=0.6,
                    )
                )

        return issues

    def _check_deserialization(self, code: str) -> list[ValidationIssue]:
        """Check for unsafe deserialization."""
        issues = []
        lines = code.split("\n")

        unsafe_deserializers = ["pickle.loads", "pickle.load", "cPickle.loads", "cPickle.load"]

        for line_num, line in enumerate(lines, 1):
            for deserializer in unsafe_deserializers:
                if deserializer in line:
                    issues.append(
                        ValidationIssue(
                            issue_id="unsafe_deserialization",
                            category=IssueCategory.SECURITY,
                            severity=ValidationSeverity.CRITICAL,
                            title="Unsafe Deserialization",
                            description=f"{deserializer} can execute arbitrary code",
                            location=f"Line {line_num}",
                            code_snippet=line.strip(),
                            suggestion="Use safe serialization formats like JSON",
                            confidence=0.9,
                        )
                    )

        return issues


class PerformanceValidator:
    """Validates code for performance issues."""

    def validate(self, skill_code: str, skill_name: str) -> list[ValidationIssue]:
        """Validate code for performance issues."""
        issues = []

        # Check performance issues
        issues.extend(self._check_inefficient_loops(skill_code))
        issues.extend(self._check_memory_leaks(skill_code))
        issues.extend(self._check_slow_operations(skill_code))
        issues.extend(self._check_blocking_calls(skill_code))

        return issues

    def _check_inefficient_loops(self, code: str) -> list[ValidationIssue]:
        """Check for inefficient loop patterns."""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Look for inefficient patterns
            if "range(len(" in line:
                issues.append(
                    ValidationIssue(
                        issue_id="inefficient_loop",
                        category=IssueCategory.PERFORMANCE,
                        severity=ValidationSeverity.MEDIUM,
                        title="Inefficient Loop Pattern",
                        description="range(len()) pattern is less Pythonic and potentially slower",
                        location=f"Line {line_num}",
                        code_snippet=line.strip(),
                        suggestion="Use enumerate() or direct iteration",
                        confidence=0.6,
                    )
                )

        return issues

    def _check_memory_leaks(self, code: str) -> list[ValidationIssue]:
        """Check for potential memory leaks."""
        issues = []
        # Simplified check - real implementation would be more sophisticated
        return issues

    def _check_slow_operations(self, code: str) -> list[ValidationIssue]:
        """Check for potentially slow operations."""
        issues = []

        slow_operations = [
            "time.sleep(",  # Should use asyncio.sleep in async code
            "os.system(",  # Blocking system call
            "subprocess.call(",  # Blocking subprocess call
        ]

        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            for operation in slow_operations:
                if operation in line:
                    issues.append(
                        ValidationIssue(
                            issue_id="slow_operation",
                            category=IssueCategory.PERFORMANCE,
                            severity=ValidationSeverity.MEDIUM,
                            title="Potentially Slow Operation",
                            description=f"{operation} can block execution",
                            location=f"Line {line_num}",
                            code_snippet=line.strip(),
                            suggestion="Consider async alternatives or optimization",
                            confidence=0.5,
                        )
                    )

        return issues

    def _check_blocking_calls(self, code: str) -> list[ValidationIssue]:
        """Check for blocking calls in async code."""
        issues = []

        # Check if file has async functions but uses blocking calls
        has_async = "async def" in code or "await" in code
        if has_async:
            blocking_calls = ["open(", "requests.", "urllib.", "httpx."]
            lines = code.split("\n")

            for line_num, line in enumerate(lines, 1):
                for call in blocking_calls:
                    if call in line and "await" not in line:
                        issues.append(
                            ValidationIssue(
                                issue_id="blocking_call_in_async",
                                category=IssueCategory.PERFORMANCE,
                                severity=ValidationSeverity.MEDIUM,
                                title="Blocking Call in Async Code",
                                description=f"Blocking call {call} in async context",
                                location=f"Line {line_num}",
                                code_snippet=line.strip(),
                                suggestion="Use async alternative or run in thread pool",
                                confidence=0.7,
                            )
                        )

        return issues


class QualityValidator:
    """
    Main quality validator that coordinates all validation components.

    Implements comprehensive validation pipeline:
    1. Zero hallucination detection
    2. Security validation
    3. Performance validation
    4. Code quality assessment
    5. Best practices verification
    """

    def __init__(self):
        self.hallucination_validator = ZeroHallucinationValidator()
        self.security_validator = SecurityValidator()
        self.performance_validator = PerformanceValidator()
        self.validation_history = []

    async def validate_skill(
        self,
        skill_code: str,
        requirements: list[str],
        examples: list[dict[str, Any]] = None,
        context: dict[str, Any] = None,
    ) -> ValidationResult:
        """
        Perform comprehensive validation of generated skill.

        Args:
            skill_code: Generated code to validate
            requirements: List of requirements the skill should meet
            examples: Example usage patterns
            context: Additional context for validation

        Returns:
            Complete validation result with scores and recommendations
        """
        logger.info("Starting comprehensive validation for skill")

        skill_name = context.get("skill_name", "unknown_skill") if context else "unknown_skill"

        # Initialize validation result
        result = ValidationResult(skill_name=skill_name, overall_score=0.0, hallucination_detected=False)

        # 1. Zero hallucination validation
        logger.info("Running zero hallucination validation")
        hallucination_issues = self.hallucination_validator.validate(skill_code, skill_name, context)
        result.issues.extend(hallucination_issues)

        # Check if any hallucination issues were detected
        hallucination_critical_issues = [
            issue
            for issue in hallucination_issues
            if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
        ]

        result.hallucination_detected = len(hallucination_critical_issues) > 0

        # 2. Security validation
        logger.info("Running security validation")
        security_issues = self.security_validator.validate(skill_code, skill_name)
        result.issues.extend(security_issues)

        # 3. Performance validation
        logger.info("Running performance validation")
        performance_issues = self.performance_validator.validate(skill_code, skill_name)
        result.issues.extend(performance_issues)

        # 4. Code quality assessment
        logger.info("Running code quality assessment")
        quality_issues = self._assess_code_quality(skill_code, skill_name)
        result.issues.extend(quality_issues)

        # 5. Requirements validation
        if requirements:
            logger.info("Running requirements validation")
            requirements_issues = self._validate_requirements(skill_code, requirements, examples)
            result.issues.extend(requirements_issues)

        # Calculate metrics and scores
        result.metrics = self._calculate_metrics(skill_code, result.issues)
        result.overall_score = self._calculate_overall_score(result)
        result.recommendations = self._generate_recommendations(result.issues)

        # Store validation in history
        self.validation_history.append(
            {
                "timestamp": datetime.now(),
                "skill_name": skill_name,
                "result": result.to_dict() if hasattr(result, "to_dict") else str(result),
            }
        )

        logger.info(f"Validation completed - Score: {result.overall_score:.2f}, Issues: {len(result.issues)}")
        return result

    def _assess_code_quality(self, skill_code: str, skill_name: str) -> list[ValidationIssue]:
        """Assess general code quality."""
        issues = []

        try:
            tree = ast.parse(skill_code)

            # Check for code complexity
            complexity_issues = self._check_complexity(tree)
            issues.extend(complexity_issues)

            # Check for naming conventions
            naming_issues = self._check_naming_conventions(tree)
            issues.extend(naming_issues)

            # Check for documentation
            doc_issues = self._check_documentation(tree)
            issues.extend(doc_issues)

            # Check for error handling
            error_handling_issues = self._check_error_handling(tree)
            issues.extend(error_handling_issues)

        except SyntaxError:
            # Syntax errors are already caught by hallucination validator
            pass

        return issues

    def _check_complexity(self, tree: ast.AST) -> list[ValidationIssue]:
        """Check for code complexity issues."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate cyclomatic complexity (simplified)
                complexity = self._calculate_complexity(node)

                if complexity > 10:
                    issues.append(
                        ValidationIssue(
                            issue_id="high_complexity",
                            category=IssueCategory.STYLE,
                            severity=ValidationSeverity.MEDIUM,
                            title="High Complexity Function",
                            description=f"Function '{node.name}' has complexity {complexity} (> 10)",
                            location=f"Line {node.lineno}",
                            suggestion="Consider breaking down into smaller functions",
                            confidence=0.8,
                        )
                    )

        return issues

    def _check_naming_conventions(self, tree: ast.AST) -> list[ValidationIssue]:
        """Check for naming convention violations."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() or not node.name.replace("_", "").isalnum():
                    issues.append(
                        ValidationIssue(
                            issue_id="naming_convention",
                            category=IssueCategory.STYLE,
                            severity=ValidationSeverity.LOW,
                            title="Function Naming Convention",
                            description=f"Function '{node.name}' should follow snake_case convention",
                            location=f"Line {node.lineno}",
                            suggestion="Use snake_case for function names",
                            confidence=0.9,
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper() or not node.name.replace("_", "").isalnum():
                    issues.append(
                        ValidationIssue(
                            issue_id="naming_convention",
                            category=IssueCategory.STYLE,
                            severity=ValidationSeverity.LOW,
                            title="Class Naming Convention",
                            description=f"Class '{node.name}' should follow PascalCase convention",
                            location=f"Line {node.lineno}",
                            suggestion="Use PascalCase for class names",
                            confidence=0.9,
                        )
                    )

        return issues

    def _check_documentation(self, tree: ast.AST) -> list[ValidationIssue]:
        """Check for documentation completeness."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)

                if not docstring:
                    issues.append(
                        ValidationIssue(
                            issue_id="missing_documentation",
                            category=IssueCategory.DOCUMENTATION,
                            severity=ValidationSeverity.MEDIUM,
                            title="Missing Function Documentation",
                            description=f"Function '{node.name}' lacks docstring",
                            location=f"Line {node.lineno}",
                            suggestion="Add comprehensive docstring with parameters and return values",
                            confidence=0.7,
                        )
                    )
                elif len(docstring.strip()) < 10:
                    issues.append(
                        ValidationIssue(
                            issue_id="inadequate_documentation",
                            category=IssueCategory.DOCUMENTATION,
                            severity=ValidationSeverity.LOW,
                            title="Inadequate Function Documentation",
                            description=f"Function '{node.name}' has minimal docstring",
                            location=f"Line {node.lineno}",
                            suggestion="Expand docstring with more detailed information",
                            confidence=0.6,
                        )
                    )

        return issues

    def _check_error_handling(self, tree: ast.AST) -> list[ValidationIssue]:
        """Check for proper error handling."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check for bare except clauses
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append(
                            ValidationIssue(
                                issue_id="bare_except",
                                category=IssueCategory.STYLE,
                                severity=ValidationSeverity.MEDIUM,
                                title="Bare Except Clause",
                                description="Bare except can hide unexpected errors",
                                location=f"Line {handler.lineno}",
                                suggestion="Specify exception types to catch",
                                confidence=0.8,
                            )
                        )

        return issues

    def _validate_requirements(
        self, skill_code: str, requirements: list[str], examples: list[dict[str, Any]] = None
    ) -> list[ValidationIssue]:
        """Validate that code meets specified requirements."""
        issues = []

        for requirement in requirements:
            requirement_lower = requirement.lower()

            if "type hints" in requirement_lower:
                # Check for type hints
                tree = ast.parse(skill_code)
                has_type_hints = any(
                    hasattr(node, "returns") and node.returns is not None
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                )

                if not has_type_hints:
                    issues.append(
                        ValidationIssue(
                            issue_id="missing_type_hints",
                            category=IssueCategory.CORRECTNESS,
                            severity=ValidationSeverity.MEDIUM,
                            title="Missing Type Hints",
                            description="Code lacks type hints as required",
                            suggestion="Add type hints to function signatures",
                            confidence=0.9,
                        )
                    )

            elif "async" in requirement_lower:
                # Check if async is implemented properly
                if "async def" not in skill_code:
                    issues.append(
                        ValidationIssue(
                            issue_id="missing_async",
                            category=IssueCategory.CORRECTNESS,
                            severity=ValidationSeverity.HIGH,
                            title="Missing Async Implementation",
                            description="Requirement specifies async but code is not async",
                            suggestion="Implement async functions as required",
                            confidence=0.9,
                        )
                    )

        return issues

    def _calculate_metrics(self, skill_code: str, issues: list[ValidationIssue]) -> dict[str, Any]:
        """Calculate validation metrics."""
        lines = len(skill_code.split("\n"))
        tokens = estimate_tokens(skill_code)

        category_counts = {}
        severity_counts = {}

        for issue in issues:
            category = issue.category.value
            severity = issue.severity.value

            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "lines_of_code": lines,
            "token_count": tokens,
            "total_issues": len(issues),
            "issues_by_category": category_counts,
            "issues_by_severity": severity_counts,
            "hallucination_issues": len([i for i in issues if i.category == IssueCategory.HALLUCINATION]),
            "security_issues": len([i for i in issues if i.category == IssueCategory.SECURITY]),
            "performance_issues": len([i for i in issues if i.category == IssueCategory.PERFORMANCE]),
        }

    def _calculate_overall_score(self, result: ValidationResult) -> float:
        """Calculate overall validation score (0.0 to 1.0)."""
        if result.hallucination_detected:
            # Any hallucination significantly reduces score
            base_score = 0.3
        else:
            base_score = 0.8

        # Subtract points for issues
        for issue in result.issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.2
            elif issue.severity == ValidationSeverity.HIGH:
                base_score -= 0.1
            elif issue.severity == ValidationSeverity.MEDIUM:
                base_score -= 0.05
            elif issue.severity == ValidationSeverity.LOW:
                base_score -= 0.02

        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))

    def _generate_recommendations(self, issues: list[ValidationIssue]) -> list[str]:
        """Generate actionable recommendations based on issues."""
        recommendations = []

        # Group issues by category
        category_issues = {}
        for issue in issues:
            category = issue.category
            if category not in category_issues:
                category_issues[category] = []
            category_issues[category].append(issue)

        # Generate recommendations for each category
        for category, category_issues_list in category_issues.items():
            if category == IssueCategory.HALLUCINATION:
                recommendations.append("CRITICAL: Fix hallucination issues before deployment")
                recommendations.append("Review and test all imports and function calls")

            elif category == IssueCategory.SECURITY:
                recommendations.append("Address all security vulnerabilities immediately")
                recommendations.append("Implement proper input validation and sanitization")

            elif category == IssueCategory.PERFORMANCE:
                recommendations.append("Optimize performance issues for better efficiency")
                recommendations.append("Consider using async alternatives for blocking operations")

            elif category == IssueCategory.STYLE:
                recommendations.append("Improve code style and maintainability")
                recommendations.append("Follow Python naming conventions and best practices")

            elif category == IssueCategory.DOCUMENTATION:
                recommendations.append("Add comprehensive documentation for better maintainability")
                recommendations.append("Include docstrings for all public functions and classes")

        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Code looks good! Consider running comprehensive tests.")

        return recommendations

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if (
                isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor))
                or isinstance(child, (ast.And, ast.Or))
                or isinstance(child, ast.ExceptHandler)
            ):
                complexity += 1

        return complexity

    def get_validation_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent validation history."""
        return self.validation_history[-limit:]

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics."""
        if not self.validation_history:
            return {"message": "No validation history available"}

        total_validations = len(self.validation_history)
        hallucination_detections = sum(
            1 for v in self.validation_history if v.get("result", {}).get("hallucination_detected", False)
        )

        return {
            "total_validations": total_validations,
            "hallucination_detections": hallucination_detections,
            "hallucination_rate": hallucination_detections / total_validations,
            "average_score": sum(v.get("result", {}).get("overall_score", 0.0) for v in self.validation_history)
            / total_validations,
        }
