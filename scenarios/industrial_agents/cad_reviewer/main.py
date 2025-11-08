#!/usr/bin/env python3
"""
CAD Design Review Agent CLI

Command-line interface for analyzing SolidWorks designs of industrial dewatering pumps
and sound-attenuating enclosures.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .core.models import AnalysisConfig, AnalysisType
from .core.reviewer import CADReviewer
from .ml.trainer import ModelTrainer
from .utils.logger import get_logger

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="cad-reviewer", description="CAD Design Review Agent for industrial pumps and enclosures"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a CAD design")
    analyze_parser.add_argument("file", help="Path to CAD file (STEP, IGES, or image)")
    analyze_parser.add_argument("--output", "-o", default="output/", help="Output directory for analysis report")
    analyze_parser.add_argument(
        "--type",
        "-t",
        choices=["comprehensive", "acoustic", "structural", "manufacturing"],
        default="comprehensive",
        help="Type of analysis to perform",
    )
    analyze_parser.add_argument("--format", "-f", choices=["json", "html", "pdf"], default="json", help="Output format")
    analyze_parser.add_argument(
        "--confidence-threshold", type=float, default=0.7, help="Minimum confidence threshold for recommendations"
    )

    # Batch review command
    batch_parser = subparsers.add_parser("batch-review", help="Review multiple CAD designs")
    batch_parser.add_argument("directory", help="Directory containing CAD files")
    batch_parser.add_argument(
        "--format", "-f", choices=["step", "iges", "png", "jpg", "all"], default="all", help="File format to process"
    )
    batch_parser.add_argument("--output", "-o", default="batch_output/", help="Output directory for reports")
    batch_parser.add_argument("--parallel", "-p", type=int, default=4, help="Number of parallel processes")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train ML models")
    train_parser.add_argument("--data", "-d", required=True, help="Training data directory")
    train_parser.add_argument("--model", "-m", default="models/", help="Model output directory")
    train_parser.add_argument("--epochs", "-e", type=int, default=100, help="Number of training epochs")
    train_parser.add_argument("--validation-split", type=float, default=0.2, help="Validation data split ratio")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate model performance")
    validate_parser.add_argument("--model", "-m", required=True, help="Model directory to validate")
    validate_parser.add_argument("--test-data", "-t", required=True, help="Test data directory")

    return parser


async def analyze_command(args) -> int:
    """Execute analyze command."""
    try:
        reviewer = CADReviewer()

        # Configure analysis
        config = AnalysisConfig(
            analysis_type=AnalysisType(args.type),
            confidence_threshold=args.confidence_threshold,
            output_format=args.format,
        )

        # Perform analysis
        logger.info(f"Analyzing {args.file}...")
        result = await reviewer.analyze_file(args.file, config)

        # Save results
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            report_path = output_path / f"{Path(args.file).stem}_analysis.json"
            with open(report_path, "w") as f:
                json.dump(result.model_dump(), f, indent=2)
        elif args.format == "html":
            report_path = await reviewer.generate_html_report(result, output_path)
        elif args.format == "pdf":
            report_path = await reviewer.generate_pdf_report(result, output_path)

        logger.info(f"Analysis complete. Report saved to: {report_path}")

        # Print summary
        print("\n🔍 CAD Analysis Summary")
        print(f"File: {args.file}")
        print(f"Overall Score: {result.overall_score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Recommendations: {len(result.recommendations)}")
        print(f"Report: {report_path}")

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


async def batch_review_command(args) -> int:
    """Execute batch review command."""
    try:
        reviewer = CADReviewer()

        # Find CAD files
        input_dir = Path(args.directory)
        if not input_dir.exists():
            logger.error(f"Directory not found: {input_dir}")
            return 1

        # Collect files based on format
        extensions = {
            "step": [".stp", ".step"],
            "iges": [".igs", ".iges"],
            "png": [".png"],
            "jpg": [".jpg", ".jpeg"],
            "all": [".stp", ".step", ".igs", ".iges", ".png", ".jpg", ".jpeg"],
        }

        files = []
        for ext in extensions[args.format]:
            files.extend(input_dir.glob(f"**/*{ext}"))

        if not files:
            logger.warning(f"No files found matching format: {args.format}")
            return 0

        logger.info(f"Found {len(files)} files to analyze")

        # Process files in parallel
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        config = AnalysisConfig(
            analysis_type=AnalysisType.COMPREHENSIVE, confidence_threshold=0.7, output_format="json"
        )

        results = await reviewer.batch_analyze(files, config, args.parallel)

        # Generate summary report
        summary = {
            "total_files": len(files),
            "analyzed": len(results),
            "average_score": sum(r.overall_score for r in results) / len(results) if results else 0,
            "results": [r.model_dump() for r in results],
        }

        summary_path = output_dir / "batch_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Batch analysis complete. Summary saved to: {summary_path}")
        print("\n📊 Batch Analysis Summary")
        print(f"Files processed: {len(results)}/{len(files)}")
        print(f"Average score: {summary['average_score']:.2f}")
        print(f"Summary: {summary_path}")

        return 0

    except Exception as e:
        logger.error(f"Batch review failed: {e}")
        return 1


async def train_command(args) -> int:
    """Execute train command."""
    try:
        trainer = ModelTrainer()

        data_dir = Path(args.data)
        model_dir = Path(args.model)
        model_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Training models on data from: {data_dir}")

        # Train models
        metrics = await trainer.train(
            data_dir=data_dir, model_dir=model_dir, epochs=args.epochs, validation_split=args.validation_split
        )

        logger.info(f"Training complete. Models saved to: {model_dir}")
        print("\n🤖 Training Results")
        print(f"Final Loss: {metrics['final_loss']:.4f}")
        print(f"Final Accuracy: {metrics['final_accuracy']:.4f}")
        print(f"Best Model: {metrics['best_model_path']}")

        return 0

    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1


async def validate_command(args) -> int:
    """Execute validate command."""
    try:
        trainer = ModelTrainer()

        model_dir = Path(args.model)
        test_dir = Path(args.test_data)

        logger.info(f"Validating model: {model_dir}")

        # Validate model
        metrics = await trainer.validate(model_dir, test_dir)

        print("\n✅ Model Validation Results")
        print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
        print(f"Test Loss: {metrics['test_loss']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1 Score: {metrics['f1_score']:.4f}")

        return 0

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


async def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command
    if args.command == "analyze":
        return await analyze_command(args)
    if args.command == "batch-review":
        return await batch_review_command(args)
    if args.command == "train":
        return await train_command(args)
    if args.command == "validate":
        return await validate_command(args)
    logger.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
