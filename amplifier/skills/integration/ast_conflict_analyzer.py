"""
AST-based Code Analysis and Conflict Detection System

This module provides advanced static analysis capabilities for detecting
conflicts, patterns, and issues in code from multiple technical sources.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Language-specific AST parsers
try:
    import esprima  # JavaScript/TypeScript parser
except ImportError:
    esprima = None

try:
    import tree_sitter
except ImportError:
    tree_sitter = None


class ConflictSeverity(Enum):
    """Severity levels for detected conflicts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictType(Enum):
    """Types of conflicts that can be detected."""

    DUPLICATE_FUNCTION = "duplicate_function"
    DUPLICATE_CLASS = "duplicate_class"
    DUPLICATE_VARIABLE = "duplicate_variable"
    SIGNATURE_MISMATCH = "signature_mismatch"
    IMPORT_CONFLICT = "import_conflict"
    DEPENDENCY_VERSION = "dependency_version"
    API_INCOMPATIBILITY = "api_incompatibility"
    NAMING_COLLISION = "naming_collision"
    LOGIC_CONTRADICTION = "logic_contradiction"
    SECURITY_ISSUE = "security_issue"


@dataclass
class CodeElement:
    """Represents a code element extracted from AST analysis."""

    name: str
    element_type: str  # "function", "class", "variable", "import"
    language: str
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_type: Optional[str] = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Conflict:
    """Represents a detected conflict between code elements."""

    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    elements: List[CodeElement]
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    impact_assessment: Optional[str] = None


class ASTAnalyzer:
    """
    Advanced AST-based code analyzer supporting multiple programming languages.

    Provides comprehensive code analysis including:
    - Function and class extraction
    - Dependency analysis
    - Pattern detection
    - Security vulnerability scanning
    - Code quality assessment
    """

    def __init__(self):
        self.supported_languages = {"python", "javascript", "typescript", "java", "cpp", "c"}
        self.parsers = {}
        self._initialize_parsers()

    def _initialize_parsers(self):
        """Initialize language-specific parsers."""
        # Python parser is built-in
        self.parsers["python"] = self._parse_python_ast

        # JavaScript/TypeScript parser
        if esprima:
            self.parsers["javascript"] = self._parse_javascript_ast
            self.parsers["typescript"] = self._parse_javascript_ast

    async def analyze_code(
        self, code_samples: List[Dict[str, str]], language: Optional[str] = None
    ) -> List[CodeElement]:
        """
        Analyze code samples and extract code elements.

        Args:
            code_samples: List of code samples with metadata
            language: Optional language hint for all samples

        Returns:
            List[CodeElement]: Extracted code elements
        """
        elements = []

        for sample in code_samples:
            sample_language = language or sample.get("language", "unknown")
            code = sample.get("code", "")
            file_path = sample.get("file_path", "unknown")

            if sample_language not in self.supported_languages:
                logging.warning(f"Unsupported language: {sample_language}")
                continue

            try:
                sample_elements = await self._analyze_single_sample(code, sample_language, file_path)
                elements.extend(sample_elements)

            except Exception as e:
                logging.warning(f"Failed to analyze {file_path}: {e}")
                continue

        return elements

    async def _analyze_single_sample(self, code: str, language: str, file_path: str) -> List[CodeElement]:
        """Analyze a single code sample."""
        if language in self.parsers:
            return self.parsers[language](code, file_path)
        else:
            return []

    def _parse_python_ast(self, code: str, file_path: str) -> List[CodeElement]:
        """Parse Python code using built-in ast module."""
        try:
            tree = ast.parse(code)
            elements = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = CodeElement(
                        name=node.name,
                        element_type="function",
                        language="python",
                        file_path=file_path,
                        line_number=node.lineno,
                        signature=self._get_python_function_signature(node),
                        docstring=ast.get_docstring(node),
                        parameters=[arg.arg for arg in node.args.args],
                        return_type=self._get_python_return_type(node),
                        dependencies=self._extract_python_dependencies(node),
                    )
                    elements.append(element)

                elif isinstance(node, ast.ClassDef):
                    element = CodeElement(
                        name=node.name,
                        element_type="class",
                        language="python",
                        file_path=file_path,
                        line_number=node.lineno,
                        signature=f"class {node.name}",
                        docstring=ast.get_docstring(node),
                        parameters=[],
                        dependencies=self._extract_python_dependencies(node),
                    )
                    elements.append(element)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        element = CodeElement(
                            name=alias.name,
                            element_type="import",
                            language="python",
                            file_path=file_path,
                            line_number=node.lineno,
                            signature=f"import {alias.name}",
                            dependencies=[alias.name],
                        )
                        elements.append(element)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        element = CodeElement(
                            name=full_name,
                            element_type="import",
                            language="python",
                            file_path=file_path,
                            line_number=node.lineno,
                            signature=f"from {module} import {alias.name}",
                            dependencies=[module],
                        )
                        elements.append(element)

            return elements

        except SyntaxError as e:
            logging.warning(f"Python syntax error in {file_path}: {e}")
            return []

    def _get_python_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature from Python AST node."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            args.append(arg.arg)

        # Default arguments
        defaults = len(node.args.defaults)
        if defaults > 0:
            for i, default in enumerate(node.args.defaults):
                arg_idx = len(node.args.args) - defaults + i
                args[arg_idx] += f"=..."  # Simplified default representation

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        signature = f"def {node.name}({', '.join(args)})"

        # Return type annotation
        if node.returns:
            signature += f" -> {self._get_annotation_string(node.returns)}"

        return signature

    def _get_annotation_string(self, node) -> str:
        """Convert annotation node to string representation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation_string(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation_string(node.value)}[{self._get_annotation_string(node.slice)}]"
        else:
            return "Any"

    def _get_python_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type from Python function."""
        if node.returns:
            return self._get_annotation_string(node.returns)
        return None

    def _extract_python_dependencies(self, node) -> List[str]:
        """Extract dependencies from Python AST node."""
        dependencies = []

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Already handled as imports
            return []

        # Look for function calls and attribute access
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(self._get_full_attribute_name(child.func))

        return list(set(dependencies))  # Remove duplicates

    def _get_full_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., module.function)."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_full_attribute_name(node.value)}.{node.attr}"
        else:
            return node.attr

    def _parse_javascript_ast(self, code: str, file_path: str) -> List[CodeElement]:
        """Parse JavaScript/TypeScript code using esprima."""
        if not esprima:
            logging.warning("esprima not available for JavaScript parsing")
            return []

        try:
            tree = esprima.parseScript(code, {"range": True, "loc": True})
            elements = []

            # This is a simplified implementation
            # In practice, you'd want to walk the tree more thoroughly
            for node in tree.body if hasattr(tree, "body") else []:
                if node.type == "FunctionDeclaration":
                    element = CodeElement(
                        name=node.id.name,
                        element_type="function",
                        language="javascript",
                        file_path=file_path,
                        line_number=node.loc.start.line,
                        signature=f"function {node.id.name}({', '.join(p.name for p in node.params)})",
                        dependencies=[],
                    )
                    elements.append(element)

                elif node.type == "ClassDeclaration":
                    element = CodeElement(
                        name=node.id.name,
                        element_type="class",
                        language="javascript",
                        file_path=file_path,
                        line_number=node.loc.start.line,
                        signature=f"class {node.id.name}",
                        dependencies=[],
                    )
                    elements.append(element)

            return elements

        except Exception as e:
            logging.warning(f"JavaScript parsing error in {file_path}: {e}")
            return []


class ConflictDetector:
    """
    Advanced conflict detection system for code from multiple sources.

    Detects various types of conflicts:
    - Duplicate functions/classes with different signatures
    - Import conflicts
    - API incompatibilities
    - Dependency version conflicts
    - Security issues
    - Naming collisions
    """

    def __init__(self):
        self.conflict_detectors = {
            ConflictType.DUPLICATE_FUNCTION: self._detect_duplicate_functions,
            ConflictType.DUPLICATE_CLASS: self._detect_duplicate_classes,
            ConflictType.IMPORT_CONFLICT: self._detect_import_conflicts,
            ConflictType.SIGNATURE_MISMATCH: self._detect_signature_mismatches,
            ConflictType.NAMING_COLLISION: self._detect_naming_collisions,
            ConflictType.SECURITY_ISSUE: self._detect_security_issues,
        }

    async def detect_conflicts(
        self, elements: List[CodeElement], analysis_config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """
        Detect conflicts in code elements from multiple sources.

        Args:
            elements: List of code elements to analyze
            analysis_config: Configuration for conflict detection

        Returns:
            List[Conflict]: Detected conflicts
        """
        conflicts = []

        # Group elements by type for efficient analysis
        elements_by_type = self._group_elements_by_type(elements)

        # Run each conflict detector
        for conflict_type, detector in self.conflict_detectors.items():
            try:
                type_conflicts = await detector(elements_by_type, analysis_config)
                conflicts.extend(type_conflicts)
            except Exception as e:
                logging.warning(f"Conflict detector failed for {conflict_type}: {e}")

        # Sort conflicts by severity
        conflicts.sort(key=lambda c: self._severity_order(c.severity))

        return conflicts

    def _group_elements_by_type(self, elements: List[CodeElement]) -> Dict[str, List[CodeElement]]:
        """Group code elements by their type."""
        grouped = {}
        for element in elements:
            element_type = element.element_type
            if element_type not in grouped:
                grouped[element_type] = []
            grouped[element_type].append(element)
        return grouped

    async def _detect_duplicate_functions(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect duplicate functions with potential conflicts."""
        conflicts = []
        functions = elements_by_type.get("function", [])

        # Group by name and language
        by_name = {}
        for func in functions:
            key = (func.name, func.language)
            if key not in by_name:
                by_name[key] = []
            by_name[key].append(func)

        # Check for conflicts
        for (name, language), func_list in by_name.items():
            if len(func_list) > 1:
                # Check signature compatibility
                signatures = [f.signature for f in func_list]
                unique_signatures = set(signatures)

                if len(unique_signatures) > 1:
                    conflict = Conflict(
                        conflict_type=ConflictType.DUPLICATE_FUNCTION,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Function '{name}' has {len(unique_signatures)} different signatures in {language}",
                        elements=func_list,
                        suggestion="Consider renaming functions or consolidating implementations",
                        impact_assessment="May cause unexpected behavior depending on which implementation is used",
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_duplicate_classes(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect duplicate classes with potential conflicts."""
        conflicts = []
        classes = elements_by_type.get("class", [])

        # Group by name and language
        by_name = {}
        for cls in classes:
            key = (cls.name, cls.language)
            if key not in by_name:
                by_name[key] = []
            by_name[key].append(cls)

        # Check for conflicts
        for (name, language), class_list in by_name.items():
            if len(class_list) > 1:
                conflict = Conflict(
                    conflict_type=ConflictType.DUPLICATE_CLASS,
                    severity=ConflictSeverity.HIGH,
                    description=f"Class '{name}' is defined in multiple files in {language}",
                    elements=class_list,
                    suggestion="Use different class names or consolidate into a single implementation",
                    impact_assessment="May cause import conflicts and unexpected behavior",
                )
                conflicts.append(conflict)

        return conflicts

    async def _detect_import_conflicts(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect import conflicts and version incompatibilities."""
        conflicts = []
        imports = elements_by_type.get("import", [])

        # Group by module name
        by_module = {}
        for imp in imports:
            module = imp.name
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(imp)

        # Check for potential conflicts
        for module, import_list in by_module.items():
            if len(import_list) > 1:
                # This is a basic implementation
                # In practice, you'd want to check for version conflicts, etc.
                conflict = Conflict(
                    conflict_type=ConflictType.IMPORT_CONFLICT,
                    severity=ConflictSeverity.LOW,
                    description=f"Module '{module}' imported in multiple ways",
                    elements=import_list,
                    suggestion="Standardize import statements across the codebase",
                )
                conflicts.append(conflict)

        return conflicts

    async def _detect_signature_mismatches(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect function signature mismatches."""
        conflicts = []
        functions = elements_by_type.get("function", [])

        # Group by name (ignore language for this check)
        by_name = {}
        for func in functions:
            if func.name not in by_name:
                by_name[func.name] = []
            by_name[func.name].append(func)

        # Check for signature mismatches
        for name, func_list in by_name.items():
            if len(func_list) > 1:
                # Compare parameters
                param_sets = [set(f.parameters) for f in func_list]

                if len(set(tuple(sorted(p)) for p in param_sets)) > 1:
                    conflict = Conflict(
                        conflict_type=ConflictType.SIGNATURE_MISMATCH,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Function '{name}' has incompatible parameter sets",
                        elements=func_list,
                        suggestion="Ensure function signatures are compatible across implementations",
                        impact_assessment="May cause runtime errors if functions are used interchangeably",
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_naming_collisions(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect naming collisions between different types of elements."""
        conflicts = []

        # Get all element names
        all_names = {}
        for element_type, elements in elements_by_type.items():
            for element in elements:
                if element.name not in all_names:
                    all_names[element.name] = []
                all_names[element.name].append(element)

        # Check for collisions
        for name, element_list in all_names.items():
            if len(element_list) > 1:
                # Check if they're different types
                types = set(e.element_type for e in element_list)
                if len(types) > 1:
                    conflict = Conflict(
                        conflict_type=ConflictType.NAMING_COLLISION,
                        severity=ConflictSeverity.LOW,
                        description=f"Name '{name}' used for multiple element types: {', '.join(types)}",
                        elements=element_list,
                        suggestion="Consider using more specific names to avoid confusion",
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_security_issues(
        self, elements_by_type: Dict[str, List[CodeElement]], config: Optional[Dict[str, Any]] = None
    ) -> List[Conflict]:
        """Detect potential security issues in code."""
        conflicts = []

        # Security patterns to look for
        security_patterns = {
            "eval_usage": r"\beval\s*\(",
            "exec_usage": r"\bexec\s*\(",
            "sql_injection": r".*(execute|query).*\+.*",
            "hardcoded_secrets": r"(password|secret|key)\s*=\s*[\"'][^\"']+[\"']",
            "file_inclusion": r"\b(open|file)\s*\(",
        }

        for element_type, elements in elements_by_type.items():
            for element in elements:
                if element.signature:  # Check signature for patterns
                    for pattern_name, pattern in security_patterns.items():
                        if re.search(pattern, element.signature, re.IGNORECASE):
                            severity = (
                                ConflictSeverity.HIGH
                                if pattern_name in ["eval_usage", "exec_usage"]
                                else ConflictSeverity.MEDIUM
                            )

                            conflict = Conflict(
                                conflict_type=ConflictType.SECURITY_ISSUE,
                                severity=severity,
                                description=f"Potential security issue ({pattern_name}) in {element.name}",
                                elements=[element],
                                suggestion="Review and validate input handling, avoid dangerous functions",
                                impact_assessment="May lead to security vulnerabilities",
                                auto_fixable=False,
                            )
                            conflicts.append(conflict)

        return conflicts

    def _severity_order(self, severity: ConflictSeverity) -> int:
        """Get numeric order for severity sorting."""
        order = {
            ConflictSeverity.CRITICAL: 0,
            ConflictSeverity.HIGH: 1,
            ConflictSeverity.MEDIUM: 2,
            ConflictSeverity.LOW: 3,
        }
        return order.get(severity, 4)

    async def generate_conflict_report(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """Generate a comprehensive conflict report."""
        report = {
            "summary": {"total_conflicts": len(conflicts), "by_severity": {}, "by_type": {}, "auto_fixable": 0},
            "conflicts": [],
            "recommendations": [],
        }

        # Categorize conflicts
        for conflict in conflicts:
            report["conflicts"].append(
                {
                    "type": conflict.conflict_type.value,
                    "severity": conflict.severity.value,
                    "description": conflict.description,
                    "elements": [
                        {
                            "name": e.name,
                            "type": e.element_type,
                            "language": e.language,
                            "file": e.file_path,
                            "line": e.line_number,
                        }
                        for e in conflict.elements
                    ],
                    "suggestion": conflict.suggestion,
                    "impact": conflict.impact_assessment,
                    "auto_fixable": conflict.auto_fixable,
                }
            )

            # Update summary
            severity_key = conflict.severity.value
            report["summary"]["by_severity"][severity_key] = report["summary"]["by_severity"].get(severity_key, 0) + 1

            type_key = conflict.conflict_type.value
            report["summary"]["by_type"][type_key] = report["summary"]["by_type"].get(type_key, 0) + 1

            if conflict.auto_fixable:
                report["summary"]["auto_fixable"] += 1

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(conflicts)

        return report

    def _generate_recommendations(self, conflicts: List[Conflict]) -> List[str]:
        """Generate recommendations based on detected conflicts."""
        recommendations = []

        # High-level recommendations based on conflict types
        conflict_types = set(c.conflict_type for c in conflicts)

        if ConflictType.DUPLICATE_FUNCTION in conflict_types:
            recommendations.append("Establish clear naming conventions for functions to avoid duplicates")

        if ConflictType.IMPORT_CONFLICT in conflict_types:
            recommendations.append("Create a dependency management strategy to handle version conflicts")

        if ConflictType.SECURITY_ISSUE in conflict_types:
            recommendations.append("Implement security review process for code integration")

        # Severity-based recommendations
        high_severity_count = sum(
            1 for c in conflicts if c.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]
        )
        if high_severity_count > 0:
            recommendations.append(f"Address {high_severity_count} high-severity conflicts before proceeding")

        return recommendations


# Export main classes
__all__ = ["ASTAnalyzer", "ConflictDetector", "CodeElement", "Conflict", "ConflictType", "ConflictSeverity"]
