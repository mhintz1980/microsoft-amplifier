#!/usr/bin/env python3
"""
ML File Organizer Demonstration

Demonstrates the Phase 2 ML-enhanced file organization capabilities.
Shows confidence scoring, content analysis, and learning from user feedback.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

from amplifier.skills.file_organizer import EnhancedFileOrganizer, FileInfo, CategoryType


async def create_test_files(temp_dir: Path) -> list[FileInfo]:
    """Create test files for demonstration."""
    test_files = []

    # Create a Python file
    py_file = temp_dir / "script.py"
    py_file.write_text("""
def calculate_total(items):
    '''Calculate total price from list of items.'''
    return sum(item.price for item in items)

import os
import sys

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")

    stat = py_file.stat()
    test_files.append(
        FileInfo(
            path=py_file,
            name=py_file.name,
            size=stat.st_size,
            is_file=True,
            is_directory=False,
            extension="py",
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )
    )

    # Create a document file
    doc_file = temp_dir / "report.pdf"
    doc_file.write_text("PDF content placeholder - would be binary in real file")

    stat = doc_file.stat()
    test_files.append(
        FileInfo(
            path=doc_file,
            name=doc_file.name,
            size=stat.st_size,
            is_file=True,
            is_directory=False,
            extension="pdf",
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )
    )

    # Create a configuration file
    config_file = temp_dir / "settings.cfg"
    config_file.write_text("""
# Application configuration
server_host = "localhost"
database_url = "sqlite:///app.db"
api_key = "your_api_key_here"
debug = true
""")

    stat = config_file.stat()
    test_files.append(
        FileInfo(
            path=config_file,
            name=config_file.name,
            size=stat.st_size,
            is_file=True,
            is_directory=False,
            extension="cfg",
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )
    )

    # Create a file with unknown extension
    unknown_file = temp_dir / "custom.data"
    unknown_file.write_text("""
# Custom data file with code-like content
function process_data() {
    var result = [];
    // Process data here
    return result;
}

config = {
    "debug": true,
    "timeout": 5000
};
""")

    stat = unknown_file.stat()
    test_files.append(
        FileInfo(
            path=unknown_file,
            name=unknown_file.name,
            size=stat.st_size,
            is_file=True,
            is_directory=False,
            extension="data",
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )
    )

    return test_files


async def demo_ml_categorization():
    """Demonstrate ML-enhanced file categorization."""
    print("🤖 ML File Organizer Demonstration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create enhanced file organizer with ML
        print("\n📁 Initializing Enhanced File Organizer with ML...")
        organizer = EnhancedFileOrganizer(enable_ml=True, confidence_threshold=0.7)

        # Create test files
        print("\n📄 Creating test files...")
        test_files = await create_test_files(temp_path)
        for file_info in test_files:
            print(f"  ✅ Created: {file_info.name} ({file_info.size} bytes)")

        # Test enhanced categorization
        print("\n🧠 Testing ML-Enhanced Categorization...")
        print("-" * 40)

        categorizer = organizer.categorizer
        categorized_results = categorizer.categorize_files_batch(test_files)

        for category_type, files_with_confidence in categorized_results.items():
            if not files_with_confidence:
                continue

            category_name = category_type.value.title()
            print(f"\n📂 Category: {category_name}")

            for file_info, confidence in files_with_confidence:
                status = (
                    "✅ Auto-categorized"
                    if confidence.overall >= organizer.confidence_threshold
                    else "❓ Low confidence"
                )
                print(f"  📄 {file_info.name}")
                print(f"     Confidence: {confidence.overall:.2f} {status}")
                print(
                    f"     Extension: {confidence.extension_match:.2f} | Pattern: {confidence.pattern_match:.2f} | Content: {confidence.content_match:.2f}"
                )

        # Demonstrate learning from user feedback
        print("\n🎓 Demonstrating Learning from User Feedback...")
        print("-" * 40)

        # Find the unknown extension file for demonstration
        unknown_file = None
        for file_info in test_files:
            if file_info.extension == "data":
                unknown_file = file_info
                break

        if unknown_file:
            # Get initial categorization
            initial_category, initial_confidence = categorizer.categorize_file_enhanced(unknown_file)
            print(f"\n📄 File: {unknown_file.name}")
            print(f"   Initial ML prediction: {initial_category.name} (confidence: {initial_confidence.overall:.2f})")

            # Simulate user correction
            print("   User says: 'This should be categorized as Code'")
            success = organizer.process_user_feedback(
                file_path=unknown_file.path,
                predicted_category=initial_category.type,
                correct_category=CategoryType.CODE,
                user_comment="This .data file contains JavaScript code and configuration",
            )

            if success:
                print("   ✅ Feedback processed successfully!")

                # Show updated statistics
                stats = organizer.get_categorization_statistics()
                print(f"   📊 Total corrections: {stats['user_corrections']}")
                print(f"   📊 Current accuracy: {stats['accuracy']:.2%}")

                # Test second categorization to see learning effect
                print(f"\n   Testing learning with similar file...")
                similar_file_info = FileInfo(
                    path=temp_path / "similar.data",
                    name="similar.data",
                    size=unknown_file.size,
                    is_file=True,
                    is_directory=False,
                    extension="data",
                    created_time=datetime.now(),
                    modified_time=datetime.now(),
                    accessed_time=datetime.now(),
                )

                new_category, new_confidence = categorizer.categorize_file_enhanced(similar_file_info)
                print(f"   New prediction: {new_category.name} (confidence: {new_confidence.overall:.2f})")

        # Show comprehensive statistics
        print("\n📊 Final Categorization Statistics")
        print("-" * 40)
        final_stats = organizer.get_categorization_statistics()

        key_metrics = [
            ("Files Processed", final_stats["total_processed"]),
            ("Auto-categorized", final_stats["auto_categorized"]),
            ("User Reviews Needed", final_stats["user_reviewed"]),
            ("User Corrections", final_stats["user_corrections"]),
            ("Current Accuracy", f"{final_stats['accuracy']:.2%}"),
            ("ML Enabled", final_stats["ml_enabled"]),
            ("Confidence Threshold", final_stats["confidence_threshold"]),
        ]

        for metric, value in key_metrics:
            print(f"  {metric:20}: {value}")

        # Show recommendations
        print("\n💡 ML System Recommendations")
        print("-" * 40)
        recommendations = organizer.get_recommendations()

        for category, items in recommendations.items():
            if items:
                print(f"\n{category.title()}:")
                for item in items:
                    print(f"  • {item}")

        # Test content analysis capabilities
        print("\n🔍 Content Analysis Demonstration")
        print("-" * 40)

        content_analyzer = categorizer.content_analyzer
        py_file = None
        for file_info in test_files:
            if file_info.extension == "py":
                py_file = file_info
                break

        if py_file:
            analysis_summary = content_analyzer.get_file_summary(py_file)
            print(f"\n📄 Analyzing: {py_file.name}")
            print(f"  Can analyze: {analysis_summary['can_analyze']}")
            print(f"  Content length: {analysis_summary.get('content_length', 'N/A')} characters")
            print(f"  Keywords found: {analysis_summary.get('keyword_count', 0)}")
            print(f"  Patterns detected: {analysis_summary.get('pattern_count', 0)}")

            if "top_keywords" in analysis_summary:
                print(f"  Top keywords: {analysis_summary['top_keywords']}")

        print("\n🎉 ML File Organizer Demo Complete!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(demo_ml_categorization())
