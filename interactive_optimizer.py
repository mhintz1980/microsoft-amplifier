#!/usr/bin/env python3
"""
Interactive Prompt Optimizer
Real-time prompt optimization with immediate feedback
"""

import sys
import json
from optimize_prompt import PromptOptimizer


def interactive_optimize():
    """Run interactive optimization session"""
    optimizer = PromptOptimizer()

    print("🚀 INTERACTIVE PROMPT OPTIMIZER")
    print("=" * 50)
    print("Paste your prompt (or 'quit' to exit):")
    print()

    while True:
        print("📝 Enter your prompt:")
        prompt_lines = []

        # Multi-line input
        while True:
            try:
                line = input()
                if line.strip() == "quit":
                    return
                if line.strip() == "" and prompt_lines:
                    break
                prompt_lines.append(line)
            except EOFError:
                break

        if not prompt_lines:
            continue

        prompt = "\n".join(prompt_lines)

        # Optimize the prompt
        result = optimizer.optimize_prompt(prompt)

        # Display results
        print("\n🎯 OPTIMIZATION RESULTS:")
        print("-" * 30)
        print(f"💰 Token Savings: {result['token_reduction_percent']}%")
        print(f"📊 {result['original_tokens']} → {result['optimized_tokens']} tokens")

        if result["improvements"]:
            print("\n✅ Improvements Made:")
            for improvement in result["improvements"]:
                print(f"   • {improvement}")

        print("\n📄 Optimized Prompt:")
        print("-" * 20)
        print(result["optimized_prompt"])
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    interactive_optimize()
