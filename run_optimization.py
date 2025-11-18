#!/usr/bin/env python3
"""
Run Claude Code optimization cycle and analyze results.
"""

from claude_code_optimization import claude_optimizer
from claude_code_optimization import get_claude_performance
from claude_code_optimization import run_claude_optimization


def main():
    print("🚀 Running Claude Code Optimization Cycle")
    print("=" * 50)

    # Get current performance summary
    print("📊 Current Performance Summary:")
    summary = get_claude_performance()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 50)

    # Run optimization cycle
    try:
        print("🔄 Running optimization cycle...")
        metrics = run_claude_optimization()

        print("✅ Optimization cycle completed!")
        print("\n📈 Training Metrics:")
        print(f"  Iteration: {metrics.iteration}")
        print(f"  Reward Score: {metrics.reward_score:.3f}")
        print(f"  Accuracy: {metrics.accuracy:.3f}")
        print(f"  Efficiency: {metrics.efficiency:.3f}")
        print(f"  Clarity: {metrics.clarity:.3f}")
        print(f"  Safety: {metrics.safety:.3f}")
        print(f"  Timestamp: {metrics.timestamp}")

        # Generate improvement suggestions
        print("\n💡 Improvement Suggestions:")
        suggestions = claude_optimizer.generate_improvement_suggestions()
        for suggestion in suggestions:
            print(f"  {suggestion}")

        # Analyze performance trends
        print("\n📊 Performance Analysis:")
        if len(claude_optimizer.metrics_history) > 1:
            current = claude_optimizer.metrics_history[-1]
            previous = claude_optimizer.metrics_history[-2]

            print(f"  Reward Change: {current.reward_score - previous.reward_score:+.3f}")
            print(f"  Accuracy Change: {current.accuracy - previous.accuracy:+.3f}")
            print(f"  Efficiency Change: {current.efficiency - previous.efficiency:+.3f}")
            print(f"  Clarity Change: {current.clarity - previous.clarity:+.3f}")
            print(f"  Safety Change: {current.safety - previous.safety:+.3f}")

            # Overall trend
            total_change = current.reward_score - previous.reward_score
            if total_change > 0.01:
                print(f"  📈 Overall Trend: Improving (+{total_change:.3f})")
            elif total_change < -0.01:
                print(f"  📉 Overall Trend: Declining ({total_change:.3f})")
            else:
                print(f"  ➡️  Overall Trend: Stable ({total_change:.3f})")

        # Show top performing tools
        print("\n🛠️  Top Performing Tools:")
        tools = summary.get("top_performing_tools", {})
        for tool, count in list(tools.items())[:5]:
            print(f"  {tool}: {count} uses")

        # Show common errors (if any)
        errors = summary.get("common_errors", {})
        if errors:
            print("\n⚠️  Common Errors:")
            for error, count in errors.items():
                print(f"  {error}: {count} occurrences")
        else:
            print("\n✅ No common errors detected")

        print(f"\n🎯 Total Interactions Analyzed: {summary.get('total_interactions', 0)}")
        print(f"📊 Recent Interactions: {summary.get('recent_interactions', 0)}")

    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 Optimization cycle completed successfully!")

    return True


if __name__ == "__main__":
    main()
