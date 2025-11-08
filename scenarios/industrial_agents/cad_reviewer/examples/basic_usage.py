#!/usr/bin/env python3
"""
Basic usage example for CAD Reviewer Agent.

This example demonstrates how to use the CAD Reviewer to analyze a single CAD file
and generate design recommendations.
"""

import asyncio
from pathlib import Path

from cad_reviewer import AnalysisConfig, AnalysisType, CADReviewer, analyze_design


async def basic_analysis_example():
    """Example of basic CAD analysis."""
    print("=== CAD Reviewer Basic Usage Example ===\n")

    # Example 1: Simple analysis function
    print("1. Simple analysis function:")
    try:
        result = await analyze_design("examples/sample_design.step", analysis_type="comprehensive")
        print(f"   Overall Score: {result.overall_score:.2f}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Recommendations: {len(result.recommendations)}")
        print(f"   Processing Time: {result.processing_time:.2f}s\n")
    except FileNotFoundError:
        print("   Sample file not found - this is expected in the example\n")

    # Example 2: Using CADReviewer class with custom config
    print("2. Using CADReviewer class with custom configuration:")
    reviewer = CADReviewer()

    config = AnalysisConfig(
        analysis_type=AnalysisType.COMPREHENSIVE,
        confidence_threshold=0.8,  # Higher threshold for recommendations
        output_format="html",
        include_visualization=True,
        focus_areas=["acoustic", "structural"],
    )

    try:
        result = await reviewer.analyze_file("examples/sample_design.step", config)

        print(f"   File: {result.metadata.file_name}")
        print(f"   File Type: {result.metadata.file_type.value}")
        print(f"   File Size: {result.metadata.file_size:,} bytes")
        print(f"   Overall Score: {result.overall_score:.2f}")
        print(f"   Analysis Type: {result.config.analysis_type.value}")

        # Display recommendations by severity
        if result.recommendations:
            print("\n   Recommendations:")
            for i, rec in enumerate(result.recommendations[:3], 1):  # Show top 3
                print(f"   {i}. [{rec.severity.value.upper()}] {rec.title}")
                print(f"      Confidence: {rec.confidence:.2f}")
                print(f"      {rec.description[:100]}...")

        # Generate HTML report
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        report_path = await reviewer.generate_html_report(result, output_dir)
        print(f"\n   HTML Report: {report_path}")

    except FileNotFoundError:
        print("   Sample file not found - this is expected in the example")

    print("\n=== Example Complete ===")


async def batch_analysis_example():
    """Example of batch CAD analysis."""
    print("\n=== Batch Analysis Example ===\n")

    reviewer = CADReviewer()
    config = AnalysisConfig(analysis_type=AnalysisType.COMPREHENSIVE, confidence_threshold=0.7)

    # Example file paths (would be real files in practice)
    file_paths = [Path("examples/design1.step"), Path("examples/design2.step"), Path("examples/design3.iges")]

    print(f"Analyzing {len(file_paths)} files in parallel...")

    try:
        # Filter to existing files for the example
        existing_files = [f for f in file_paths if f.exists()]
        if not existing_files:
            print("No sample files found - this is expected in the example")
            return

        results = await reviewer.batch_analyze(existing_files, config, max_workers=4)

        print("\nBatch Analysis Results:")
        print(f"Files processed: {len(results)}/{len(existing_files)}")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result.metadata.file_name}")
            print(f"   Score: {result.overall_score:.2f}, Recs: {len(result.recommendations)}")

        # Generate batch summary
        summary = await reviewer.get_analysis_summary(results)
        print("\nBatch Summary:")
        print(f"Average Score: {summary.average_score:.2f}")
        print(f"Total Recommendations: {summary.total_recommendations}")

    except Exception as e:
        print(f"Batch analysis error: {e}")

    print("\n=== Batch Example Complete ===")


async def acoustic_focused_example():
    """Example focusing on acoustic analysis."""
    print("\n=== Acoustic Analysis Example ===\n")

    # Configure for acoustic-focused analysis
    AnalysisConfig(analysis_type=AnalysisType.ACOUSTIC, confidence_threshold=0.75, focus_areas=["acoustic"])

    try:
        result = await analyze_design("examples/acoustic_test.step", "acoustic")

        print("Acoustic Analysis Results:")
        if result.acoustic_analysis:
            acoustic = result.acoustic_analysis
            print(f"Predicted STC Rating: {acoustic.predicted_stc:.1f}")
            print(f"Overall Acoustic Rating: {acoustic.overall_rating:.1f}/10")
            print(f"Weak Points Identified: {len(acoustic.weak_points)}")
            print(f"Resonance Frequencies: {len(acoustic.resonance_frequencies)}")

            if acoustic.weak_points:
                print("\nAcoustic Weak Points:")
                for i, point in enumerate(acoustic.weak_points[:3], 1):
                    print(f"{i}. {point}")

        # Show acoustic-specific recommendations
        acoustic_recs = [r for r in result.recommendations if r.type.value == "acoustic_improvement"]

        if acoustic_recs:
            print(f"\nAcoustic Recommendations ({len(acoustic_recs)}):")
            for i, rec in enumerate(acoustic_recs[:3], 1):
                print(f"{i}. {rec.title}")
                print(f"   {rec.description}")

    except FileNotFoundError:
        print("Sample acoustic file not found - this is expected in the example")

    print("\n=== Acoustic Example Complete ===")


async def main():
    """Run all examples."""
    print("CAD Reviewer Agent - Usage Examples")
    print("====================================\n")

    await basic_analysis_example()
    await batch_analysis_example()
    await acoustic_focused_example()

    print("\n🎉 All examples completed!")
    print("\nTo run with real CAD files:")
    print("1. Place your CAD files in the examples/ directory")
    print("2. Run: python basic_usage.py")
    print("3. Check the output/ directory for analysis reports")


if __name__ == "__main__":
    asyncio.run(main())
