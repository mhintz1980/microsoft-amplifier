"""
GitHub Repository Analyzer and Integration

This module provides comprehensive GitHub repository analysis capabilities including:
- Repository cloning and analysis
- Code structure analysis
- Documentation extraction
- README and markdown processing
- Commit history analysis
- Issue and PR analysis
- Dependency analysis
- License detection
- Code quality metrics
"""

import asyncio
import json
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

# GitHub API client
try:
    import httpx
except ImportError:
    httpx = None
    logging.warning("httpx not available - GitHub API features will be limited")

# Git operations
try:
    import git
except ImportError:
    git = None
    logging.warning("GitPython not available - repository cloning will be limited")

# YAML/JSON parsing
try:
    import yaml
except ImportError:
    yaml = None
    logging.warning("PyYAML not available - YAML file processing will be limited")


class RepositoryType(Enum):
    """Types of GitHub repositories."""

    PUBLIC = "public"
    PRIVATE = "private"
    FORK = "fork"
    ARCHIVED = "archived"


class AnalysisDepth(Enum):
    """Depth of repository analysis."""

    BASIC = "basic"  # README, basic structure
    STANDARD = "standard"  # Include documentation, main code files
    COMPREHENSIVE = "comprehensive"  # Full analysis including history
    DEEP = "deep"  # Deep analysis with all files and detailed metrics


@dataclass
class GitHubRepo:
    """GitHub repository information."""

    owner: str
    name: str
    url: str
    clone_url: str
    default_branch: str
    description: str
    language: str
    stars: int
    forks: int
    open_issues: int
    created_at: str
    updated_at: str
    pushed_at: str
    size_kb: int
    is_private: bool
    is_fork: bool
    is_archived: bool
    license: Optional[str] = None
    topics: List[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RepositoryAnalysis:
    """Complete analysis of a GitHub repository."""

    repo_info: GitHubRepo
    file_structure: Dict[str, Any]
    documentation: Dict[str, str]
    code_files: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    quality_metrics: Dict[str, float]
    security_issues: List[Dict[str, Any]]
    commit_history: List[Dict[str, Any]] = None
    contributors: List[Dict[str, Any]] = None
    analysis_time: float = 0.0
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

    def get_skill_content(self) -> str:
        """Generate skill content from repository analysis."""
        content = []

        # Repository overview
        content.append(f"# {self.repo_info.name}")
        content.append(f"**Description:** {self.repo_info.description}")
        content.append(f"**Language:** {self.repo_info.language}")
        content.append(f"**Stars:** {self.repo_info.stars} | **Forks:** {self.repo_info.forks}")
        content.append(f"**License:** {self.repo_info.license or 'Not specified'}")
        content.append(f"**Topics:** {', '.join(self.repo_info.topics)}")
        content.append("")

        # Documentation
        if self.documentation:
            content.append("## Documentation")
            for doc_type, doc_content in self.documentation.items():
                content.append(f"### {doc_type.title()}")
                content.append(doc_content[:1000] + "..." if len(doc_content) > 1000 else doc_content)
                content.append("")

        # Code structure
        content.append("## Code Structure")
        content.append(f"**Total Files:** {len(self.code_files)}")
        content.append(f"**Main Language:** {self.repo_info.language}")
        content.append("")

        # Quality metrics
        content.append("## Quality Metrics")
        for metric, value in self.quality_metrics.items():
            content.append(f"**{metric.replace('_', ' ').title()}:** {value:.2f}")
        content.append("")

        # Dependencies
        if self.dependencies:
            content.append("## Dependencies")
            for dep_type, deps in self.dependencies.items():
                if deps:
                    content.append(f"### {dep_type.title()}")
                    content.append(", ".join(deps[:10]))  # Limit to first 10
                    if len(deps) > 10:
                        content.append(f"... and {len(deps) - 10} more")
                    content.append("")

        # Security issues
        if self.security_issues:
            content.append("## Security Considerations")
            for issue in self.security_issues[:5]:  # Limit to first 5
                content.append(f"- **{issue.get('type', 'Unknown')}:** {issue.get('description', 'No description')}")
            content.append("")

        return "\n".join(content)


class GitHubAnalyzer:
    """
    Advanced GitHub repository analyzer with comprehensive analysis capabilities.

    Features:
    - Repository metadata extraction
    - File structure analysis
    - Documentation processing
    - Code quality assessment
    - Security vulnerability scanning
    - Dependency analysis
    - Commit history analysis
    - Contributor analysis
    """

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Microsoft-Amplifier-Skill-Generator"}

        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

        self.temp_dir = None
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None

    async def analyze_repository(
        self, repo_url: str, depth: AnalysisDepth = AnalysisDepth.STANDARD, clone_locally: bool = True
    ) -> RepositoryAnalysis:
        """
        Analyze a GitHub repository comprehensively.

        Args:
            repo_url: GitHub repository URL
            depth: Analysis depth level
            clone_locally: Whether to clone repository for local analysis

        Returns:
            RepositoryAnalysis: Complete analysis result
        """
        start_time = datetime.now()

        try:
            # Parse repository URL
            owner, repo_name = self._parse_repo_url(repo_url)

            # Get repository information
            repo_info = await self._get_repository_info(owner, repo_name)

            # Clone repository if requested
            local_path = None
            if clone_locally:
                local_path = await self._clone_repository(repo_info.clone_url, owner, repo_name)

            # Perform analysis based on depth
            analysis = await self._perform_analysis(repo_info, local_path, depth)

            analysis.analysis_time = (datetime.now() - start_time).total_seconds()

            return analysis

        except Exception as e:
            logging.error(f"Failed to analyze repository {repo_url}: {e}")
            raise
        finally:
            await self._cleanup()

    def _parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """Parse owner and repository name from GitHub URL."""
        # Handle various GitHub URL formats
        patterns = [r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", r"github\.com/([^/]+)/([^/]+?)(?:/)?$"]

        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                owner, repo = match.groups()
                # Remove .git suffix if present
                repo = repo.replace(".git", "")
                return owner, repo

        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    async def _get_repository_info(self, owner: str, repo: str) -> GitHubRepo:
        """Get repository information from GitHub API."""
        if not httpx:
            raise RuntimeError("httpx not available for GitHub API calls")

        url = f"{self.api_base}/repos/{owner}/{repo}"

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            self._update_rate_limit(response)

            if response.status_code == 404:
                raise ValueError(f"Repository {owner}/{repo} not found")
            elif response.status_code != 200:
                raise RuntimeError(f"GitHub API error: {response.status_code} - {response.text}")

            data = response.json()

            return GitHubRepo(
                owner=owner,
                name=repo,
                url=data["html_url"],
                clone_url=data["clone_url"],
                default_branch=data["default_branch"],
                description=data.get("description", ""),
                language=data.get("language", ""),
                stars=data["stargazers_count"],
                forks=data["forks_count"],
                open_issues=data["open_issues_count"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                pushed_at=data["pushed_at"],
                size_kb=data["size"],
                is_private=data["private"],
                is_fork=data["fork"],
                is_archived=data["archived"],
                license=data.get("license", {}).get("name") if data.get("license") else None,
                topics=data.get("topics", []),
            )

    async def _clone_repository(self, clone_url: str, owner: str, repo: str) -> Path:
        """Clone repository locally for analysis."""
        if not git:
            raise RuntimeError("GitPython not available for repository cloning")

        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="github_analysis_"))
        local_path = self.temp_dir / f"{owner}_{repo}"

        try:
            # Clone repository
            logging.info(f"Cloning repository {owner}/{repo} to {local_path}")
            repo_obj = git.Repo.clone_from(clone_url, local_path, depth=1)

            logging.info(f"Repository cloned successfully")
            return local_path

        except Exception as e:
            logging.error(f"Failed to clone repository: {e}")
            raise

    async def _perform_analysis(
        self, repo_info: GitHubRepo, local_path: Optional[Path], depth: AnalysisDepth
    ) -> RepositoryAnalysis:
        """Perform repository analysis based on depth level."""
        analysis = RepositoryAnalysis(
            repo_info=repo_info,
            file_structure={},
            documentation={},
            code_files=[],
            dependencies={},
            quality_metrics={},
            security_issues=[],
        )

        if local_path and local_path.exists():
            # Local analysis
            analysis.file_structure = await self._analyze_file_structure(local_path)
            analysis.documentation = await self._extract_documentation(local_path)
            analysis.code_files = await self._analyze_code_files(local_path, depth)
            analysis.dependencies = await self._analyze_dependencies(local_path)
            analysis.quality_metrics = await self._calculate_quality_metrics(local_path, analysis.code_files)
            analysis.security_issues = await self._scan_for_security_issues(local_path, analysis.code_files)

            if depth in [AnalysisDepth.COMPREHENSIVE, AnalysisDepth.DEEP]:
                analysis.commit_history = await self._analyze_commit_history(local_path)
                analysis.contributors = await self._analyze_contributors(local_path)

        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)

        return analysis

    async def _analyze_file_structure(self, local_path: Path) -> Dict[str, Any]:
        """Analyze repository file structure."""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "file_extensions": {},
            "directory_structure": {},
            "main_files": [],
        }

        try:
            for root, dirs, files in os.walk(local_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [
                    d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__", ".git"]
                ]

                rel_root = Path(root).relative_to(local_path)
                structure["directory_structure"][str(rel_root)] = {
                    "files": files,
                    "subdirectories": dirs,
                    "file_count": len(files),
                    "dir_count": len(dirs),
                }

                structure["total_files"] += len(files)
                structure["total_directories"] += len(dirs)

                for file in files:
                    # Count file extensions
                    ext = Path(file).suffix.lower()
                    if ext:
                        structure["file_extensions"][ext] = structure["file_extensions"].get(ext, 0) + 1

                    # Identify main files
                    if file.lower() in [
                        "readme.md",
                        "setup.py",
                        "package.json",
                        "requirements.txt",
                        "main.py",
                        "index.js",
                    ]:
                        structure["main_files"].append(str(rel_root / file))

        except Exception as e:
            logging.warning(f"Failed to analyze file structure: {e}")

        return structure

    async def _extract_documentation(self, local_path: Path) -> Dict[str, str]:
        """Extract documentation from repository."""
        documentation = {}

        # Look for README files
        readme_patterns = ["README.md", "readme.md", "README.rst", "README.txt", "README"]
        for pattern in readme_patterns:
            readme_path = local_path / pattern
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding="utf-8", errors="ignore")
                    documentation["readme"] = content
                    break
                except Exception as e:
                    logging.warning(f"Failed to read {pattern}: {e}")

        # Look for documentation directory
        doc_dirs = ["docs", "documentation", "doc"]
        for doc_dir in doc_dirs:
            doc_path = local_path / doc_dir
            if doc_path.exists() and doc_path.is_dir():
                doc_files = []
                for ext in [".md", ".rst", ".txt"]:
                    doc_files.extend(doc_path.glob(f"**/*{ext}"))

                for doc_file in doc_files[:10]:  # Limit to first 10 files
                    try:
                        rel_path = doc_file.relative_to(local_path)
                        content = doc_file.read_text(encoding="utf-8", errors="ignore")
                        doc_key = str(rel_path).replace("/", "_").replace("\\", "_")
                        documentation[doc_key] = content
                    except Exception as e:
                        logging.warning(f"Failed to read documentation file {doc_file}: {e}")

        return documentation

    async def _analyze_code_files(self, local_path: Path, depth: AnalysisDepth) -> List[Dict[str, Any]]:
        """Analyze code files in the repository."""
        code_files = []
        code_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
        }

        max_files = 50 if depth == AnalysisDepth.BASIC else 200 if depth == AnalysisDepth.STANDARD else 1000
        file_count = 0

        try:
            for root, dirs, files in os.walk(local_path):
                # Skip certain directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".") and d not in ["node_modules", "__pycache__", ".git", "build", "dist"]
                ]

                for file in files:
                    if file_count >= max_files:
                        return code_files

                    ext = Path(file).suffix.lower()
                    if ext in code_extensions:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(local_path)

                        try:
                            content = file_path.read_text(encoding="utf-8", errors="ignore")
                            lines = content.split("\n")

                            code_files.append(
                                {
                                    "path": str(rel_path),
                                    "language": code_extensions[ext],
                                    "size_bytes": len(content),
                                    "lines_count": len(lines),
                                    "content_preview": content[:500] + "..." if len(content) > 500 else content,
                                    "has_tests": "test" in str(rel_path).lower(),
                                    "is_main": any(
                                        keyword in str(rel_path).lower() for keyword in ["main", "index", "app"]
                                    ),
                                }
                            )

                            file_count += 1

                        except Exception as e:
                            logging.warning(f"Failed to analyze code file {file_path}: {e}")

        except Exception as e:
            logging.warning(f"Failed to analyze code files: {e}")

        return code_files

    async def _analyze_dependencies(self, local_path: Path) -> Dict[str, List[str]]:
        """Analyze project dependencies."""
        dependencies = {"package_managers": [], "libraries": [], "frameworks": [], "dev_dependencies": []}

        try:
            # Python dependencies
            for req_file in ["requirements.txt", "requirements-dev.txt", "Pipfile", "pyproject.toml"]:
                req_path = local_path / req_file
                if req_path.exists():
                    try:
                        if req_file.endswith(".txt"):
                            content = req_path.read_text(encoding="utf-8")
                            deps = [
                                line.strip()
                                for line in content.split("\n")
                                if line.strip() and not line.startswith("#")
                            ]
                            dependencies["libraries"].extend(deps)
                        elif req_file == "pyproject.toml" and yaml:
                            content = req_path.read_text(encoding="utf-8")
                            # Basic parsing - would be better with a proper TOML parser
                            deps = re.findall(r"^([a-zA-Z0-9-_]+)\s*=", content, re.MULTILINE)
                            dependencies["libraries"].extend(deps)

                        dependencies["package_managers"].append("pip")
                    except Exception as e:
                        logging.warning(f"Failed to parse {req_file}: {e}")

            # Node.js dependencies
            package_json_path = local_path / "package.json"
            if package_json_path.exists():
                try:
                    content = package_json_path.read_text(encoding="utf-8")
                    package_data = json.loads(content)

                    dependencies["package_managers"].append("npm")

                    for dep_type in ["dependencies", "devDependencies"]:
                        if dep_type in package_data:
                            deps = list(package_data[dep_type].keys())
                            if dep_type == "devDependencies":
                                dependencies["dev_dependencies"].extend(deps)
                            else:
                                dependencies["libraries"].extend(deps)

                except Exception as e:
                    logging.warning(f"Failed to parse package.json: {e}")

        except Exception as e:
            logging.warning(f"Failed to analyze dependencies: {e}")

        return dependencies

    async def _calculate_quality_metrics(self, local_path: Path, code_files: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate code quality metrics."""
        metrics = {
            "documentation_score": 0.0,
            "test_coverage_estimate": 0.0,
            "code_complexity_estimate": 0.0,
            "maintainability_score": 0.0,
        }

        try:
            total_files = len(code_files)
            if total_files == 0:
                return metrics

            # Documentation score (based on README and doc files)
            doc_files = [f for f in code_files if any(keyword in f["path"] for keyword in ["readme", "doc", "guide"])]
            metrics["documentation_score"] = min(1.0, len(doc_files) / max(1, total_files * 0.1))

            # Test coverage estimate
            test_files = [f for f in code_files if f["has_tests"]]
            metrics["test_coverage_estimate"] = min(1.0, len(test_files) / max(1, total_files * 0.2))

            # Code complexity estimate (based on file sizes)
            avg_lines = sum(f["lines_count"] for f in code_files) / total_files
            metrics["code_complexity_estimate"] = min(1.0, avg_lines / 500)  # Normalize to 0-1

            # Maintainability score (combination of factors)
            metrics["maintainability_score"] = (
                metrics["documentation_score"] * 0.3
                + metrics["test_coverage_estimate"] * 0.3
                + (1.0 - metrics["code_complexity_estimate"]) * 0.4
            )

        except Exception as e:
            logging.warning(f"Failed to calculate quality metrics: {e}")

        return metrics

    async def _scan_for_security_issues(
        self, local_path: Path, code_files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Scan for security issues in code."""
        security_issues = []

        # Security patterns to look for
        dangerous_patterns = [
            (r"password\s*[:=]\s*[\"'][^\"']+[\"']", "Hardcoded password"),
            (r"api[_-]?key\s*[:=]\s*[\"'][^\"']+[\"']", "Hardcoded API key"),
            (r"secret\s*[:=]\s*[\"'][^\"']+[\"']", "Hardcoded secret"),
            (r"token\s*[:=]\s*[\"'][^\"']+[\"']", "Hardcoded token"),
            (r"eval\s*\(", "Use of eval() function"),
            (r"exec\s*\(", "Use of exec() function"),
            (r"subprocess\.call\s*\(", "Use of subprocess.call"),
            (r"os\.system\s*\(", "Use of os.system"),
            (r"shell\s*=\s*True", "Shell=True in subprocess"),
        ]

        try:
            for code_file in code_files:
                file_path = local_path / code_file["path"]
                if not file_path.exists():
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")

                    for pattern, issue_type in dangerous_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[: match.start()].count("\n") + 1
                            line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                            security_issues.append(
                                {
                                    "type": issue_type,
                                    "file": code_file["path"],
                                    "line": line_num,
                                    "content": line_content[:100],
                                    "severity": "high"
                                    if "password" in issue_type.lower() or "key" in issue_type.lower()
                                    else "medium",
                                }
                            )

                except Exception as e:
                    logging.warning(f"Failed to scan file {file_path}: {e}")

        except Exception as e:
            logging.warning(f"Failed security scan: {e}")

        return security_issues

    async def _analyze_commit_history(self, local_path: Path) -> List[Dict[str, Any]]:
        """Analyze commit history (requires local clone)."""
        commits = []

        try:
            if not git:
                return commits

            repo = git.Repo(local_path)

            # Get last 50 commits
            for commit in list(repo.iter_commits(max_count=50)):
                commits.append(
                    {
                        "hash": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "author": str(commit.author),
                        "date": commit.committed_datetime.isoformat(),
                        "files_changed": len(commit.stats.files),
                        "additions": commit.stats.total["files"] if hasattr(commit.stats, "total") else 0,
                    }
                )

        except Exception as e:
            logging.warning(f"Failed to analyze commit history: {e}")

        return commits

    async def _analyze_contributors(self, local_path: Path) -> List[Dict[str, Any]]:
        """Analyze repository contributors."""
        contributors = []

        try:
            if not git:
                return contributors

            repo = git.Repo(local_path)
            author_stats = {}

            for commit in repo.iter_commits():
                author = str(commit.author)
                if author not in author_stats:
                    author_stats[author] = {
                        "name": author,
                        "commits": 0,
                        "first_commit": commit.committed_datetime,
                        "last_commit": commit.committed_datetime,
                    }
                else:
                    author_stats[author]["commits"] += 1
                    author_stats[author]["last_commit"] = max(
                        author_stats[author]["last_commit"], commit.committed_datetime
                    )

            contributors = list(author_stats.values())
            contributors.sort(key=lambda x: x["commits"], reverse=True)

        except Exception as e:
            logging.warning(f"Failed to analyze contributors: {e}")

        return contributors

    def _generate_recommendations(self, analysis: RepositoryAnalysis) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Documentation recommendations
        if analysis.quality_metrics.get("documentation_score", 0) < 0.5:
            recommendations.append("Consider adding more comprehensive documentation (README, API docs, etc.)")

        # Testing recommendations
        if analysis.quality_metrics.get("test_coverage_estimate", 0) < 0.3:
            recommendations.append("Add unit tests to improve code reliability and maintainability")

        # Security recommendations
        if analysis.security_issues:
            high_sec_issues = [i for i in analysis.security_issues if i.get("severity") == "high"]
            if high_sec_issues:
                recommendations.append(f"Address {len(high_sec_issues)} high-priority security issues")

        # Dependency recommendations
        if analysis.dependencies.get("libraries"):
            deps_count = len(analysis.dependencies["libraries"])
            if deps_count > 50:
                recommendations.append("Consider reducing the number of dependencies to improve maintainability")

        # Code quality recommendations
        if analysis.quality_metrics.get("maintainability_score", 0) < 0.6:
            recommendations.append("Focus on improving code maintainability through refactoring and documentation")

        return recommendations

    def _update_rate_limit(self, response):
        """Update GitHub API rate limit information."""
        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
        if "X-RateLimit-Reset" in response.headers:
            self.rate_limit_reset = int(response.headers["X-RateLimit-Reset"])

    async def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil

                shutil.rmtree(self.temp_dir)
                logging.info("Cleaned up temporary files")
            except Exception as e:
                logging.warning(f"Failed to cleanup temporary files: {e}")


# Export main classes
__all__ = ["GitHubAnalyzer", "GitHubRepo", "RepositoryAnalysis", "AnalysisDepth", "RepositoryType"]
