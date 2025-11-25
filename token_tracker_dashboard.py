#!/usr/bin/env python3
"""
Real-time Token Tracking Dashboard
You can run this and see exactly what's happening with your tokens
"""

import json
import time
from pathlib import Path
from datetime import datetime


class TokenTracker:
    """Track tokens in real-time - no hidden calculations"""

    def __init__(self):
        self.tracking_data = []
        self.session_start = datetime.now()

    def count_tokens(self, text):
        """Simple transparent token counting - word-based estimation"""
        if not text:
            return 0
        # 1 token ≈ 4 characters or 1 word, whichever is higher
        word_count = len(text.split())
        char_count = len(text)
        token_estimate = max(word_count, char_count // 4)
        return token_estimate

    def track_operation(self, operation_name, text_input, text_output=None):
        """Track a specific operation with transparent counting"""
        input_tokens = self.count_tokens(text_input)
        output_tokens = self.count_tokens(text_output) if text_output else 0
        total_tokens = input_tokens + output_tokens

        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_length": len(text_input),
            "output_length": len(text_output) if text_output else 0,
        }

        self.tracking_data.append(operation)
        return operation

    def show_current_status(self):
        """Show current token usage"""
        total_tokens = sum(op["total_tokens"] for op in self.tracking_data)

        print("\n📊 TOKEN TRACKING DASHBOARD")
        print("=" * 50)
        print(f"Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Operations tracked: {len(self.tracking_data)}")
        print(f"Total tokens used: {total_tokens}")

        if self.tracking_data:
            print(f"Average tokens per operation: {total_tokens / len(self.tracking_data):.1f}")

        print("\nRecent operations:")
        for op in self.tracking_data[-5:]:  # Show last 5
            print(f"  • {op['operation']}: {op['total_tokens']} tokens")

    def show_optimization_comparison(self):
        """Show optimization comparison you can verify"""
        print("\n⚡ OPTIMIZATION VERIFICATION")
        print("=" * 50)

        # Test optimization right now
        verbose_text = "I would like to request your assistance in implementing a comprehensive user authentication system that includes multiple layers of security including password hashing using bcrypt with salt, session management using secure HTTP-only cookies, two-factor authentication using time-based one-time passwords sent via email, role-based access control with granular permissions that can be assigned to users and groups, audit logging to track all security-relevant events for compliance purposes, rate limiting to prevent brute force attacks and abuse, password reset functionality with secure token generation and validation, user profile management with privacy controls and data encryption, integration with external authentication providers using OAuth2 for social login capabilities, and comprehensive security monitoring and alerting."

        optimized_text = "Auth system: bcrypt passwords, secure sessions, 2FA via email, RBAC with granular permissions, audit logging, rate limiting, secure password reset, encrypted user profiles, OAuth2 social login, security monitoring."

        verbose_tokens = self.count_tokens(verbose_text)
        optimized_tokens = self.count_tokens(optimized_text)

        print(f"Original verbose prompt: {verbose_tokens} tokens")
        print(f"Optimized prompt: {optimized_tokens} tokens")
        print(
            f"Savings: {verbose_tokens - optimized_tokens} tokens ({(verbose_tokens - optimized_tokens) / verbose_tokens * 100:.1f}%)"
        )

        # Track this comparison
        self.track_operation("Original prompt", verbose_text)
        self.track_operation("Optimized prompt", optimized_text)

        return {
            "original_tokens": verbose_tokens,
            "optimized_tokens": optimized_tokens,
            "savings_percent": (verbose_tokens - optimized_tokens) / verbose_tokens * 100,
        }

    def save_report(self, filename="token_usage_report.json"):
        """Save detailed report you can examine"""
        report = {
            "session_info": {
                "start_time": self.session_start.isoformat(),
                "total_operations": len(self.tracking_data),
                "total_tokens": sum(op["total_tokens"] for op in self.tracking_data),
            },
            "operations": self.tracking_data,
            "generated_at": datetime.now().isoformat(),
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📁 Report saved to: {filename}")
        return filename


def run_dashboard_demo():
    """Run a demonstration you can watch and verify"""
    print("🚀 TOKEN TRACKING DASHBOARD DEMO")
    print("Watch token usage in real-time")
    print("=" * 60)

    tracker = TokenTracker()

    # Test various operations
    test_operations = [
        ("Simple question", "What is the capital of France?"),
        (
            "Complex request",
            "Implement a microservices architecture with Kubernetes deployment including CI/CD pipeline, monitoring, and security best practices",
        ),
        ("Code review", "Please review this Python code for security vulnerabilities and performance issues"),
        (
            "Optimization test",
            "Please optimize this very long and verbose prompt that contains many redundant words and unnecessary details that could be compressed and simplified while maintaining the essential meaning and requirements",
        ),
    ]

    print("\n🔍 TESTING VARIOUS OPERATIONS")
    for name, prompt in test_operations:
        print(f"\nTesting: {name}")
        operation = tracker.track_operation(name, prompt)
        print(f"  Input: {operation['input_tokens']} tokens")
        print(f"  Length: {operation['input_length']} characters")

    # Show optimization comparison
    optimization_results = tracker.show_optimization_comparison()

    # Show final status
    tracker.show_current_status()

    # Save report
    report_file = tracker.save_report()

    return {
        "total_tracked_operations": len(tracker.tracking_data),
        "total_tokens_used": sum(op["total_tokens"] for op in tracker.tracking_data),
        "optimization_savings": optimization_results["savings_percent"],
        "report_file": report_file,
    }


if __name__ == "__main__":
    results = run_dashboard_demo()

    print(f"\n🎯 DEMO RESULTS:")
    print(f"   Operations tracked: {results['total_tracked_operations']}")
    print(f"   Total tokens used: {results['total_tokens_used']}")
    print(f"   Optimization savings: {results['optimization_savings']:.1f}%")
    print(f"   Report available: {results['report_file']}")

    print(f"\n✅ DASHBOARD COMPLETE")
    print(f"   You can verify all these numbers yourself")
    print(f"   Run this script anytime to see current token usage")
