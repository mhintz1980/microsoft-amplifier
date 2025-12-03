#!/usr/bin/env python3
"""
Prompt Optimizer - Automatically optimize your prompts
Usage: python optimize_prompt.py "Your prompt here"
"""

import sys
import json
import re
from typing import Dict, List


class PromptOptimizer:
    def __init__(self):
        self.optimization_patterns = {
            # Remove redundant phrases
            "redundant_phrases": [
                (r"You are a (.+?) with deep knowledge of", r"ROLE: \1"),
                (r"with deep knowledge of", r"DOMAIN:"),
                (r"You provide comprehensive, practical guidance on", r"FOCUS:"),
                (r"You are an expert in", r"ROLE: Expert"),
                (r"You are a (.+?) specialist", r"ROLE: \1 specialist"),
            ],
            # Add structured thinking
            "thinking_patterns": [
                "THINKING PROCESS:\n1. Analyze requirements\n2. Identify patterns\n3. Design solution\n4. Validate approach",
                "ANALYSIS FRAMEWORK:\n1. Context assessment\n2. Technical evaluation\n3. Solution design\n4. Implementation planning",
                "REASONING APPROACH:\n1. Problem decomposition\n2. Solution exploration\n3. Risk assessment\n4. Recommendation",
            ],
            # Add constitutional AI
            "constitutional_principles": [
                "ACCURACY: Verify claims, flag uncertainties",
                "SAFETY: Check for harmful content, bias, ethics",
                "QUALITY: Ensure clarity, consistency, completeness",
                "UTILITY: Provide actionable, practical guidance",
            ],
        }

    def optimize_prompt(self, prompt: str) -> Dict:
        """Optimize a single prompt"""
        original_tokens = len(prompt.split())

        # Step 1: Extract role and domain
        role_match = re.search(r"You are (?:a )?([^,\.]+)(?: expert| specialist)?", prompt)
        domain_match = re.search(r"knowledge of ([^,\.\n]+)", prompt)
        focus_match = re.search(r"guidance on ([^,\.\n]+)", prompt)

        # Step 2: Apply optimizations
        optimized = prompt

        # Remove redundant phrases
        for old, new in self.optimization_patterns["redundant_phrases"]:
            optimized = re.sub(old, new, optimized)

        # Extract role and create structured prompt
        if role_match:
            role = role_match.group(1).strip()
            # Build optimized structured prompt
            optimized = f"=== {role.upper().replace(' ', ' ')} EXPERT ===\n\nROLE: {role}\n"

            # Add domain if found
            if domain_match:
                domain = domain_match.group(1).strip()
                optimized += f"DOMAIN: {domain}\n"

            # Add focus if found
            if focus_match:
                focus = focus_match.group(1).strip()
                optimized += f"FOCUS: {focus}\n"

            # Add structured thinking
            optimized += f"\n{self.optimization_patterns['thinking_patterns'][1]}"

            # Add constitutional principles
            constitutional = "\n\nCONSTITUTIONAL PRINCIPLES:\n" + "\n".join(
                f"- {p}" for p in self.optimization_patterns["constitutional_principles"]
            )
            optimized += constitutional

            # Add output format
            optimized += "\n\nOUTPUT: Clear, actionable response with examples"

        # Add structured thinking if not present
        if "THINKING" not in optimized and "PROCESS" not in optimized:
            thinking = self.optimization_patterns["thinking_patterns"][0]
            optimized += f"\n\n{thinking}"

        # Add constitutional principles
        if "CONSTITUTIONAL" not in optimized:
            constitutional = "\n\nCONSTITUTIONAL PRINCIPLES:\n" + "\n".join(
                f"- {p}" for p in self.optimization_patterns["constitutional_principles"]
            )
            optimized += constitutional

        # Add output format if not specified
        if "OUTPUT" not in optimized:
            optimized += "\n\nOUTPUT: Clear, actionable response with examples"

        # Calculate improvements
        optimized_tokens = len(optimized.split())
        token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

        return {
            "original_prompt": prompt,
            "optimized_prompt": optimized,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction_percent": round(token_reduction, 1),
            "improvements": self._get_improvements(prompt, optimized),
        }

    def _get_improvements(self, original: str, optimized: str) -> List[str]:
        """Identify specific improvements made"""
        improvements = []

        if "ROLE:" in optimized and "ROLE:" not in original:
            improvements.append("Added structured role definition")

        if any(word in optimized for word in ["THINKING", "PROCESS", "FRAMEWORK"]):
            improvements.append("Added structured reasoning approach")

        if "CONSTITUTIONAL" in optimized:
            improvements.append("Added safety and quality principles")

        if "OUTPUT:" in optimized:
            improvements.append("Specified output format requirements")

        return improvements


def main():
    if len(sys.argv) != 2:
        print('Usage: python optimize_prompt.py "Your prompt here"')
        print('Example: python optimize_prompt.py "You are a Python expert with deep knowledge of..."')
        sys.exit(1)

    prompt = sys.argv[1]
    optimizer = PromptOptimizer()
    result = optimizer.optimize_prompt(prompt)

    print("🚀 PROMPT OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"📊 Token Reduction: {result['token_reduction_percent']}%")
    print(f"📝 Original Tokens: {result['original_tokens']}")
    print(f"⚡ Optimized Tokens: {result['optimized_tokens']}")
    print(f"💰 Cost Savings: ~{result['token_reduction_percent']}%")

    print("\n🎯 IMPROVEMENTS MADE:")
    for improvement in result["improvements"]:
        print(f"   ✅ {improvement}")

    print("\n📄 OPTIMIZED PROMPT:")
    print("-" * 30)
    print(result["optimized_prompt"])


if __name__ == "__main__":
    main()
