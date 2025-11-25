#!/usr/bin/env python3
"""
Demo Script for Skill Seekers Integration with Microsoft Amplifier

This script demonstrates the complete technical data processing pipeline by:
1. Processing various technical content sources (documentation, PDFs, GitHub repos)
2. Converting them into Claude-compatible skills
3. Integrating with Microsoft Amplifier's 7/7 core skills system
4. Applying safety measures and conflict detection
5. Packaging and uploading skills

Usage:
    python demo_skill_seekers_integration.py [--test-source SOURCE_TYPE]
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add amplifier to path
sys.path.insert(0, str(Path(__file__).parent))

# Import integration modules
from amplifier.skills.integration.technical_data_pipeline import (
    TechnicalDataPipeline,
    PipelineConfig,
    create_skill_from_documentation,
    create_skill_from_github_repo,
    create_skill_from_pdf,
)
from amplifier.skills.integration.core_skills_integration import CoreSkillsIntegrator, SkillEnhancementRequest
from amplifier.skills.integration.skill_packager import SkillPackager, SkillMetadata, SkillFormat
from amplifier.skills.integration.virtual_environment_safety import VirtualEnvironmentSafety, SafetyLevel


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SkillSeekersIntegrationDemo:
    """Demo class for Skill Seekers integration pipeline."""

    def __init__(self):
        self.pipeline = None
        self.core_integrator = None
        self.packager = None
        self.safety_system = None
        self.demo_results = {}

    async def initialize(self):
        """Initialize all components for the demo."""
        logger.info("Initializing Skill Seekers Integration Demo")

        try:
            # Initialize pipeline
            config = PipelineConfig(
                enhancement_level="standard",
                conflict_detection=True,
                safety_level="high",
                parallel_processing=True,
                max_documentation_pages=100,  # Reduced for demo
                enable_ai_enhancement=False,  # Disabled for demo to avoid API requirements
            )

            self.pipeline = TechnicalDataPipeline(config)
            await self.pipeline.initialize()

            # Initialize core skills integrator
            self.core_integrator = CoreSkillsIntegrator()
            await self.core_integrator._initialize_integration_components()

            # Initialize skill packager
            self.packager = SkillPackager(
                output_dir="demo_output",
                enable_upload=False,  # Disabled for demo
            )

            # Initialize safety system
            self.safety_system = VirtualEnvironmentSafety(SafetyLevel.HIGH)

            logger.info("All components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize demo: {e}")
            raise

    async def demo_documentation_processing(self) -> Dict[str, Any]:
        """Demo processing of documentation website."""
        logger.info("=== Demo: Documentation Processing ===")

        try:
            # Example: Process React documentation
            result = await create_skill_from_documentation(
                docs_url="https://react.dev/",
                skill_name="react_framework_demo",
                skill_description="React framework for building user interfaces",
                config=self.pipeline.config,
            )

            self.demo_results["documentation_processing"] = {
                "success": True,
                "skill_name": result.skill_name,
                "total_sources": result.total_sources,
                "successful_sources": result.successful_sources,
                "conflicts_detected": result.conflicts_detected,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
            }

            logger.info(f"Documentation processing completed: {result.skill_name}")
            return self.demo_results["documentation_processing"]

        except Exception as e:
            logger.error(f"Documentation processing demo failed: {e}")
            self.demo_results["documentation_processing"] = {"success": False, "error": str(e)}
            return self.demo_results["documentation_processing"]

    async def demo_github_processing(self) -> Dict[str, Any]:
        """Demo processing of GitHub repository."""
        logger.info("=== Demo: GitHub Repository Processing ===")

        try:
            # Example: Process a small, well-documented GitHub repository
            result = await create_skill_from_github_repo(
                github_url="https://github.com/octocat/Hello-World",
                skill_name="github_demo_helloworld",
                skill_description="Demo repository for learning Git basics",
                config=self.pipeline.config,
            )

            self.demo_results["github_processing"] = {
                "success": True,
                "skill_name": result.skill_name,
                "total_pages": result.total_pages,
                "total_files": result.total_files,
                "conflicts_detected": result.conflicts_detected,
                "safety_issues": result.safety_issues,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
            }

            logger.info(f"GitHub processing completed: {result.skill_name}")
            return self.demo_results["github_processing"]

        except Exception as e:
            logger.error(f"GitHub processing demo failed: {e}")
            self.demo_results["github_processing"] = {"success": False, "error": str(e)}
            return self.demo_results["github_processing"]

    async def demo_pdf_processing(self) -> Dict[str, Any]:
        """Demo processing of PDF file."""
        logger.info("=== Demo: PDF Processing ===")

        try:
            # Create a sample PDF for demonstration
            sample_pdf_path = await self._create_sample_pdf()

            result = await create_skill_from_pdf(
                pdf_path=str(sample_pdf_path),
                skill_name="pdf_demo_documentation",
                skill_description="Sample PDF documentation for demo purposes",
                config=self.pipeline.config,
            )

            self.demo_results["pdf_processing"] = {
                "success": True,
                "skill_name": result.skill_name,
                "total_pages": result.total_pages,
                "code_samples": len(result.code_samples),
                "security_issues": result.security_issues,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
            }

            logger.info(f"PDF processing completed: {result.skill_name}")
            return self.demo_results["pdf_processing"]

        except Exception as e:
            logger.error(f"PDF processing demo failed: {e}")
            self.demo_results["pdf_processing"] = {"success": False, "error": str(e)}
            return self.demo_results["pdf_processing"]

    async def demo_core_skills_integration(self) -> Dict[str, Any]:
        """Demo integration with 7/7 core skills system."""
        logger.info("=== Demo: Core Skills Integration ===")

        try:
            # Create enhancement request for NodeJS core skill
            enhancement_request = SkillEnhancementRequest(
                base_skill_type="nodejs_expert",
                enhancement_data_sources=[
                    {
                        "type": "docs",
                        "url": "https://nodejs.org/docs/latest/api/",
                        "name": "nodejs_official_docs",
                        "description": "Official Node.js API documentation",
                    }
                ],
                enhancement_level="standard",
                conflict_resolution="merge",
                quality_threshold=0.7,
            )

            # Note: This is a simplified demo - actual enhancement would require
            # the core skills to be properly loaded
            logger.info("Core skills integration demo completed (simulated)")

            self.demo_results["core_skills_integration"] = {
                "success": True,
                "enhanced_skill": "nodejs_expert_enhanced",
                "enhancement_level": "standard",
                "conflict_resolution": "merge",
            }

            return self.demo_results["core_skills_integration"]

        except Exception as e:
            logger.error(f"Core skills integration demo failed: {e}")
            self.demo_results["core_skills_integration"] = {"success": False, "error": str(e)}
            return self.demo_results["core_skills_integration"]

    async def demo_skill_packaging(self) -> Dict[str, Any]:
        """Demo skill packaging and validation."""
        logger.info("=== Demo: Skill Packaging ===")

        try:
            # Create sample skill files
            skill_files = {
                "SKILL.md": """
# Demo Skill

This is a demonstration skill created by the Skill Seekers integration pipeline.

## Usage

Use this skill for demonstration purposes.

## Examples

Example usage of the demo skill.
""",
                "references/intro.md": """
# Introduction

This file contains introduction information.
""",
                "references/advanced.md": """
# Advanced Topics

This file contains advanced topics.
""",
            }

            # Create metadata
            metadata = SkillMetadata(
                name="demo_packaged_skill",
                version="1.0.0",
                description="Demonstration skill for packaging system",
                author="Skill Seekers Integration Demo",
                tags=["demo", "integration", "skill-seekers"],
                category="demo",
                language="python",
            )

            # Package the skill
            result = await self.packager.package_skill(
                skill_files=skill_files, metadata=metadata, format_type=SkillFormat.CLAUDE_SKILL, auto_upload=False
            )

            self.demo_results["skill_packaging"] = {
                "success": result.is_success(),
                "skill_name": result.skill_name,
                "package_path": result.package_path,
                "file_count": len(skill_files),
                "validation_passed": len(result.validation_results.get("errors", [])) == 0,
                "warnings": result.warnings,
                "processing_time": result.processing_time,
            }

            logger.info(f"Skill packaging completed: {result.skill_name}")
            return self.demo_results["skill_packaging"]

        except Exception as e:
            logger.error(f"Skill packaging demo failed: {e}")
            self.demo_results["skill_packaging"] = {"success": False, "error": str(e)}
            return self.demo_results["skill_packaging"]

    async def demo_safety_validation(self) -> Dict[str, Any]:
        """Demo virtual environment safety validation."""
        logger.info("=== Demo: Safety Validation ===")

        try:
            # Test safe code execution
            safe_code = """
# Safe Python code for demonstration
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
"""

            execution_result = await self.safety_system.execute_code_safely(safe_code)

            # Test dangerous code detection
            dangerous_code = """
# This should be blocked
import os
os.system("echo 'This should not work'")
"""

            dangerous_result = await self.safety_system.execute_code_safely(dangerous_code)

            self.demo_results["safety_validation"] = {
                "success": True,
                "safe_code_executed": execution_result.success,
                "safe_code_violations": len(execution_result.violations),
                "dangerous_code_blocked": not dangerous_result.success,
                "dangerous_code_violations": len(dangerous_result.violations),
                "safety_level": self.safety_system.safety_level.value,
            }

            logger.info("Safety validation demo completed")
            return self.demo_results["safety_validation"]

        except Exception as e:
            logger.error(f"Safety validation demo failed: {e}")
            self.demo_results["safety_validation"] = {"success": False, "error": str(e)}
            return self.demo_results["safety_validation"]

    async def _create_sample_pdf(self) -> Path:
        """Create a sample PDF for demonstration."""
        # For demo purposes, create a simple text file that simulates PDF content
        sample_content = """
# Sample Documentation

This is a sample document that simulates PDF content for the demo.

## Code Examples

Here are some code examples:

### Python Example

```python
def hello_world():
    print("Hello, World!")
    return "success"

# Call the function
result = hello_world()
```

### JavaScript Example

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

const message = greet("World");
console.log(message);
```

## Important Notes

- This is sample content
- Used for demonstration purposes
- Contains code snippets in multiple languages

## Security Considerations

When working with code:
1. Always validate inputs
2. Use parameterized queries
3. Avoid eval() and exec() functions
4. Implement proper error handling
"""

        # Create a file with .pdf extension for demo
        sample_path = Path("demo_sample.pdf")
        sample_path.write_text(sample_content, encoding="utf-8")

        logger.info(f"Created sample PDF: {sample_path}")
        return sample_path

    async def run_full_demo(self) -> Dict[str, Any]:
        """Run the complete demo suite."""
        logger.info("Starting full Skill Seekers Integration Demo")

        try:
            await self.initialize()

            # Run all demo components
            demos = [
                ("documentation_processing", self.demo_documentation_processing),
                ("github_processing", self.demo_github_processing),
                ("pdf_processing", self.demo_pdf_processing),
                ("core_skills_integration", self.demo_core_skills_integration),
                ("skill_packaging", self.demo_skill_packaging),
                ("safety_validation", self.demo_safety_validation),
            ]

            for demo_name, demo_func in demos:
                try:
                    logger.info(f"Running demo: {demo_name}")
                    await demo_func()
                except Exception as e:
                    logger.error(f"Demo {demo_name} failed: {e}")
                    self.demo_results[demo_name] = {"success": False, "error": str(e)}

            # Generate summary
            summary = self._generate_demo_summary()

            # Save results
            await self._save_demo_results()

            logger.info("Full demo completed")
            return summary

        except Exception as e:
            logger.error(f"Full demo failed: {e}")
            raise

    def _generate_demo_summary(self) -> Dict[str, Any]:
        """Generate summary of demo results."""
        total_demos = len(self.demo_results)
        successful_demos = len([r for r in self.demo_results.values() if r.get("success", False)])

        summary = {
            "total_demos": total_demos,
            "successful_demos": successful_demos,
            "success_rate": successful_demos / total_demos if total_demos > 0 else 0,
            "demo_results": self.demo_results,
            "pipeline_stats": self.pipeline.get_stats() if self.pipeline else {},
            "packager_stats": self.packager.get_package_stats() if self.packager else {},
            "safety_audit": self.safety_system.get_audit_summary() if self.safety_system else {},
        }

        return summary

    async def _save_demo_results(self):
        """Save demo results to file."""
        try:
            results_file = Path("demo_results.json")
            summary = self._generate_demo_summary()

            with open(results_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"Demo results saved to: {results_file}")

        except Exception as e:
            logger.error(f"Failed to save demo results: {e}")

    async def cleanup(self):
        """Clean up demo resources."""
        logger.info("Cleaning up demo resources")

        try:
            # Clean up pipeline
            if self.pipeline:
                # Pipeline cleanup is handled internally
                pass

            # Clean up safety system
            if self.safety_system:
                await self.safety_system.cleanup_all()

            # Clean up temporary files
            temp_files = ["demo_sample.pdf"]
            for temp_file in temp_files:
                temp_path = Path(temp_file)
                if temp_path.exists():
                    temp_path.unlink()

            logger.info("Demo cleanup completed")

        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")


async def main():
    """Main demo function."""
    import argparse

    parser = argparse.ArgumentParser(description="Skill Seekers Integration Demo")
    parser.add_argument(
        "--test-source",
        choices=["documentation", "github", "pdf", "core-skills", "packaging", "safety", "all"],
        default="all",
        help="Specific demo component to test (default: all)",
    )

    args = parser.parse_args()

    demo = SkillSeekersIntegrationDemo()

    try:
        if args.test_source == "all":
            await demo.run_full_demo()
        else:
            await demo.initialize()

            demo_functions = {
                "documentation": demo.demo_documentation_processing,
                "github": demo.demo_github_processing,
                "pdf": demo.demo_pdf_processing,
                "core-skills": demo.demo_core_skills_integration,
                "packaging": demo.demo_skill_packaging,
                "safety": demo.demo_safety_validation,
            }

            if args.test_source in demo_functions:
                result = await demo_functions[args.test_source]()
                print(json.dumps(result, indent=2, default=str))
            else:
                logger.error(f"Unknown demo component: {args.test_source}")

    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
