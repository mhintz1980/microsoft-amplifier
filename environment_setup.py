#!/usr/bin/env python3
"""
Automatic Virtual Environment Setup and Validation

Critical system component that ensures proper virtual environment
activation before any Python execution to prevent file corruption
and maintain system integrity.

MUST BE RUN BEFORE ANY OTHER PYTHON OPERATIONS
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import warnings


class EnvironmentSetup:
    """
    Automatic virtual environment detection and activation system.

    Prevents the critical file corruption issues discovered on 2025-11-20
    where missing virtual environment activation caused Python files to be
    corrupted with markdown content and syntax errors.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.venv_path = self.project_root / ".venv"
        self.python_executable = None
        self.activated = False
        self.validation_results = {}

    def detect_virtual_environment(self) -> bool:
        """Detect if virtual environment exists and is accessible."""
        if self.venv_path.exists():
            # Check for Python executable
            python_exe = self.venv_path / "bin" / "python"
            if sys.platform == "win32":
                python_exe = self.venv_path / "Scripts" / "python.exe"

            if python_exe.exists():
                self.python_executable = python_exe
                return True

        return False

    def validate_environment(self) -> Dict[str, Any]:
        """Comprehensive environment validation."""
        results = {
            "venv_exists": False,
            "python_executable": None,
            "python_version": None,
            "pip_available": False,
            "dependencies_ok": False,
            "path_correct": False,
            "issues": [],
            "warnings": [],
        }

        # Check virtual environment exists
        if self.detect_virtual_environment():
            results["venv_exists"] = True
            results["python_executable"] = str(self.python_executable)

            try:
                # Check Python version
                version_result = subprocess.run(
                    [str(self.python_executable), "--version"], capture_output=True, text=True, timeout=10
                )
                if version_result.returncode == 0:
                    results["python_version"] = version_result.stdout.strip()

                # Check pip availability
                pip_result = subprocess.run(
                    [str(self.python_executable), "-m", "pip", "--version"], capture_output=True, text=True, timeout=10
                )
                results["pip_available"] = pip_result.returncode == 0

                # Check critical dependencies
                critical_deps = ["pydantic", "aiofiles", "click", "anthropic"]
                missing_deps = []

                for dep in critical_deps:
                    dep_result = subprocess.run(
                        [str(self.python_executable), "-c", f"import {dep}"], capture_output=True, text=True, timeout=5
                    )
                    if dep_result.returncode != 0:
                        missing_deps.append(dep)

                results["dependencies_ok"] = len(missing_deps) == 0
                if missing_deps:
                    results["issues"].append(f"Missing dependencies: {', '.join(missing_deps)}")

                # Check path configuration
                current_python = sys.executable
                expected_python = str(self.python_executable)

                results["path_correct"] = current_python == expected_python
                if not results["path_correct"]:
                    results["warnings"].append(f"Current Python ({current_python}) != Expected ({expected_python})")

            except subprocess.TimeoutExpired:
                results["issues"].append("Environment validation timed out")
            except Exception as e:
                results["issues"].append(f"Validation error: {e}")
        else:
            results["issues"].append("Virtual environment not found")

        self.validation_results = results
        return results

    def activate_environment(self) -> bool:
        """
        Activate virtual environment and configure Python path.

        This is the CRITICAL function that prevents file corruption.
        """
        if not self.detect_virtual_environment():
            raise RuntimeError("Virtual environment not found. Cannot proceed safely.")

        # Update sys.path to use project root
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))

        # Set PYTHONPATH environment variable
        env_pythonpath = os.environ.get("PYTHONPATH", "")
        project_path_str = str(self.project_root)

        if project_path_str not in env_pythonpath:
            os.environ["PYTHONPATH"] = f"{project_path_str}:{env_pythonpath}" if env_pythonpath else project_path_str

        self.activated = True
        return True

    def run_with_environment(self, command: str, **kwargs) -> subprocess.CompletedProcess:
        """
        Run command with virtual environment properly activated.

        Always use this for Python execution to prevent corruption.
        """
        if not self.python_executable:
            raise RuntimeError("Virtual environment not properly detected")

        # Prepare environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)

        # Ensure we're using the virtual environment Python
        if command.startswith("python "):
            command = str(self.python_executable) + command[6:]

        return subprocess.run(command, shell=True, env=env, cwd=self.project_root, **kwargs)

    def get_safe_python_command(self) -> str:
        """Get the safe Python command that uses virtual environment."""
        if not self.python_executable:
            raise RuntimeError("Virtual environment not properly detected")
        return str(self.python_executable)

    def print_environment_status(self):
        """Print detailed environment status for debugging."""
        print("🔍 VIRTUAL ENVIRONMENT STATUS")
        print("=" * 50)

        if not self.validation_results:
            self.validate_environment()

        results = self.validation_results

        # Virtual Environment Status
        venv_status = "✅ FOUND" if results["venv_exists"] else "❌ NOT FOUND"
        print(f"Virtual Environment: {venv_status}")

        if results["venv_exists"]:
            print(f"Python Executable: {results['python_executable']}")
            print(f"Python Version: {results['python_version']}")

            pip_status = "✅ AVAILABLE" if results["pip_available"] else "❌ NOT AVAILABLE"
            print(f"Pip: {pip_status}")

            deps_status = "✅ OK" if results["dependencies_ok"] else "❌ MISSING"
            print(f"Dependencies: {deps_status}")

            path_status = "✅ CORRECT" if results["path_correct"] else "⚠️ INCORRECT"
            print(f"Python Path: {path_status}")

        # Issues and Warnings
        if results["issues"]:
            print(f"\n❌ ISSUES FOUND:")
            for issue in results["issues"]:
                print(f"   • {issue}")

        if results["warnings"]:
            print(f"\n⚠️ WARNINGS:")
            for warning in results["warnings"]:
                print(f"   • {warning}")

        print("\n" + "=" * 50)

    def ensure_safe_environment(self) -> bool:
        """
        Ensure environment is safe for Python operations.

        Returns True if safe, raises exception if unsafe.
        """
        validation = self.validate_environment()

        # Critical checks that must pass
        critical_failures = []

        if not validation["venv_exists"]:
            critical_failures.append("Virtual environment not found")

        if not validation["python_executable"]:
            critical_failures.append("Python executable not found")

        if not validation["dependencies_ok"]:
            critical_failures.append("Critical dependencies missing")

        if critical_failures:
            error_msg = "ENVIRONMENT SAFETY CHECK FAILED:\n" + "\n".join(f"• {fail}" for fail in critical_failures)
            error_msg += "\n\n⚠️ PROCEEDING MAY CAUSE FILE CORRUPTION ⚠️"
            raise RuntimeError(error_msg)

        # Activate environment if not already active
        if not self.activated:
            self.activate_environment()

        return True


# Global environment instance
environment = EnvironmentSetup()


def setup_environment() -> EnvironmentSetup:
    """
    Setup and validate virtual environment before any operations.

    CRITICAL: Call this function at the start of every session
    before any Python execution to prevent file corruption.
    """
    print("🚀 INITIALIZING SAFE ENVIRONMENT...")

    try:
        # Ensure safe environment
        environment.ensure_safe_environment()

        print("✅ Environment validated and activated")
        print(f"📍 Project Root: {environment.project_root}")
        print(f"🐍 Python: {environment.python_executable}")

        return environment

    except RuntimeError as e:
        print(f"❌ CRITICAL: {e}")
        print("\n🛠️  SOLUTION OPTIONS:")
        print("1. Create virtual environment: python -m venv .venv")
        print("2. Activate virtual environment: source .venv/bin/activate")
        print("3. Install dependencies: pip install -e .")
        print("4. Try again")
        sys.exit(1)


def get_safe_python_command() -> str:
    """Get safe Python command that uses virtual environment."""
    return environment.get_safe_python_command()


def run_safe_command(command: str, **kwargs) -> subprocess.CompletedProcess:
    """Run command with virtual environment properly configured."""
    return environment.run_with_environment(command, **kwargs)


# Convenience decorator for functions that need safe environment
def requires_safe_environment(func):
    """Decorator that ensures safe environment before function execution."""

    def wrapper(*args, **kwargs):
        if not environment.activated:
            environment.ensure_safe_environment()
        return func(*args, **kwargs)

    return wrapper


# Auto-setup when imported (for critical safety)
if __name__ != "__main__":
    # Check if environment is already properly set up
    try:
        environment.ensure_safe_environment()
    except RuntimeError:
        # Don't fail on import, but warn
        warnings.warn(
            "Virtual environment not properly activated. "
            "Call setup_environment() before Python execution to prevent file corruption.",
            RuntimeWarning,
        )


if __name__ == "__main__":
    """Direct execution for environment validation and setup."""
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Environment Setup and Validation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--setup", action="store_true", help="Setup environment if needed")

    args = parser.parse_args()

    if args.verbose:
        environment.print_environment_status()

    if args.setup:
        try:
            setup_environment()
            print("\n🎉 ENVIRONMENT SETUP COMPLETE")
            print("✅ Safe to proceed with Python operations")
        except RuntimeError as e:
            print(f"\n💥 SETUP FAILED: {e}")
            sys.exit(1)
    else:
        validation = environment.validate_environment()
        environment.print_environment_status()

        if not any(validation["issues"]):
            print("\n✅ ENVIRONMENT IS SAFE")
        else:
            print("\n⚠️ ENVIRONMENT HAS ISSUES - Use --setup to fix")
