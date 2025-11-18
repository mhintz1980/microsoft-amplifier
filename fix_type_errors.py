#!/usr/bin/env python3
"""
Type Error Batch Fix Utility

A command-line utility for fixing type errors in batches using the MCP skill.
This provides an easy way to run the type error fixing skill on the current project.

Usage:
    python fix_type_errors.py                    # Fix all type errors
    python fix_type_errors.py --dry-run          # Show what would be fixed
    python fix_type_errors.py --limit 50         # Fix only first 50 errors
    python fix_type_errors.py --file path.py     # Fix errors in specific file
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Add the amplifier module to the path
sys.path.insert(0, str(Path(__file__).parent / "amplifier"))

from amplifier.mcp.code_execution import get_mcp_executor


def extract_type_errors(limit=None, file_filter=None):
    """Extract type errors from the project."""
    print("Extracting type errors...")

    try:
        cmd = ["uv", "run", "pyright", "--outputjson"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0 and result.returncode != 1:  # 1 means errors found
            print(f"Pyright failed: {result.stderr}")
            return []

        # Parse JSON output
        try:
            pyright_data = json.loads(result.stdout)
            errors = []

            for file_info in pyright_data.get("files", []):
                file_path = file_info.get("filePath", "")

                # Apply file filter if specified
                if file_filter and file_filter not in file_path:
                    continue

                for error in file_info.get("errors", []):
                    error_str = f"{file_path}:{error.get('line', 0)}:{error.get('column', 0)} - error: {error.get('message', '')}"
                    errors.append(error_str)

            # Apply limit if specified
            if limit:
                errors = errors[:limit]

            print(f"Extracted {len(errors)} type errors")
            return errors

        except json.JSONDecodeError as e:
            print(f"Failed to parse pyright output: {e}")
            return []

    except Exception as e:
        print(f"Error running pyright: {e}")
        return []


async def fix_type_errors(errors, dry_run=False):
    """Fix type errors using the MCP skill."""
    if not errors:
        print("No type errors to fix!")
        return None

    print(f"Processing {len(errors)} type errors...")

    # Prepare input data for the skill
    input_data = {
        "errors": errors,
        "config": {"dry_run": dry_run, "parallel_processing": True, "max_files_per_batch": 10},
    }

    # Get MCP executor
    executor = get_mcp_executor()

    # Execute the skill
    print("Executing fix_type_errors_batch skill...")
    try:
        result = await executor.execute_skill("fix_type_errors_batch", input_data)

        if result.status.value == "completed":
            print("✅ Skill executed successfully!")

            # Parse results
            try:
                skill_result = json.loads(result.stdout)
                summary = skill_result.get("summary", {})

                print("\n=== Fix Summary ===")
                print(f"Total errors: {summary.get('total_errors', 0)}")
                print(f"Files processed: {summary.get('files_processed', 0)}")
                print(f"Files fixed: {summary.get('files_fixed', 0)}")
                print(f"Fixes applied: {summary.get('fixes_applied', 0)}")
                print(f"Success rate: {summary.get('success_rate', 0):.1%}")

                # Show error categories
                error_categories = summary.get("error_categories", {})
                if error_categories:
                    print("\n=== Error Categories ===")
                    for category, count in error_categories.items():
                        if count > 0:
                            print(f"  {category}: {count}")

                # Show successful fixes
                successful_fixes = skill_result.get("successful_fixes", [])
                if successful_fixes:
                    print("\n=== Fixed Files ===")
                    for fix in successful_fixes:
                        file_name = Path(fix.get("file", "Unknown")).name
                        fixes_applied = fix.get("fixes_applied", [])
                        if fixes_applied:
                            print(f"  {file_name}: {len(fixes_applied)} fixes")
                            if len(fixes_applied) <= 3:
                                print(f"    {', '.join(fixes_applied)}")

                # Show failed fixes
                failed_fixes = skill_result.get("failed_fixes", [])
                if failed_fixes:
                    print("\n=== Failed Fixes ===")
                    for fix in failed_fixes:
                        if "file" in fix:
                            print(f"  {fix['file']}: {fix.get('error', 'Unknown error')}")
                        else:
                            print(f"  {fix.get('error', 'Unknown error')}")

                return skill_result

            except json.JSONDecodeError as e:
                print(f"Failed to parse skill result: {e}")
                print(f"Raw output: {result.stdout[:500]}...")
                return None

        else:
            print("❌ Skill execution failed!")
            print(f"Status: {result.status.value}")
            print(f"Error: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Error executing skill: {e}")
        return None


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Fix type errors in batches using MCP skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fix_type_errors.py                    # Fix all type errors
  python fix_type_errors.py --dry-run          # Show what would be fixed
  python fix_type_errors.py --limit 50         # Fix only first 50 errors
  python fix_type_errors.py --file path.py     # Fix errors in specific file
        """,
    )

    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--limit", type=int, help="Limit number of errors to process")
    parser.add_argument("--file", type=str, help="Fix errors only in specific file")
    parser.add_argument("--extract-only", action="store_true", help="Only extract and show errors, don't fix them")

    args = parser.parse_args()

    print("=== Type Error Batch Fix Utility ===\n")

    # Extract type errors
    errors = extract_type_errors(limit=args.limit, file_filter=args.file)

    if not errors:
        print("No type errors found!")
        return

    if args.extract_only:
        print(f"\n=== Found {len(errors)} Type Errors ===")
        for i, error in enumerate(errors, 1):
            print(f"{i:3d}. {error}")
        return

    # Show sample of errors
    print("\n=== Sample Errors ===")
    for i, error in enumerate(errors[:5], 1):
        print(f"{i}. {error}")

    if len(errors) > 5:
        print(f"... and {len(errors) - 5} more errors")

    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print("No changes will be made.")
    else:
        print("\n=== FIX MODE ===")
        print("Changes will be applied to source files.")
        response = input("Continue? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            return

    # Fix the errors
    result = await fix_type_errors(errors, dry_run=args.dry_run)

    if result and not args.dry_run:
        print("\n=== Verification ===")
        print("Running type check again to verify fixes...")
        remaining_errors = extract_type_errors()
        fixes_successful = len(errors) - len(remaining_errors)
        print(f"Fixed: {fixes_successful} errors")
        print(f"Remaining: {len(remaining_errors)} errors")

        if remaining_errors > 0:
            print(f"\nRun again to fix remaining errors, or use --limit {len(remaining_errors)} to process them.")


if __name__ == "__main__":
    asyncio.run(main())
