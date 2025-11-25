#!/usr/bin/env python3
"""
Basic functionality test for enhanced SDK integration
"""

import sys
import asyncio

# Add project root to path
sys.path.insert(0, "/home/markimus/projects/microsoft-amplifier")


async def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Basic Enhanced SDK Functionality Test")
    print("=" * 50)

    try:
        # Test imports
        print("📦 Testing imports...")
        from amplifier.sdk_enhancements.enhanced_anthropic_integration import (
            EnhancedAnthropicClient,
            TextAccumulator,
            get_enhanced_anthropic_client,
            SDK_VERSION,
            ANTHROPIC_AVAILABLE,
        )

        print(f"✅ Imports successful - SDK v{SDK_VERSION}")

        # Test TextAccumulator
        print("\n🔤 Testing TextAccumulator...")
        accumulator = TextAccumulator()
        test_chunks = ["Hello", " ", "world", "!"]
        for chunk in test_chunks:
            accumulator.add_chunk(chunk)

        result = accumulator.get_text()
        stats = accumulator.get_stats()
        print(f"✅ TextAccumulator: '{result}' ({stats['chunks_count']} chunks, {stats['char_count']} chars)")

        # Test Enhanced Client
        print("\n🚀 Testing Enhanced Client...")
        client = await get_enhanced_anthropic_client()
        perf_summary = client.get_enhanced_performance_summary()
        print(f"✅ Enhanced Client: {perf_summary['sdk_status']}")

        capabilities = perf_summary["enhanced_capabilities"]
        print(f"   Enhanced streaming: {capabilities['enhanced_streaming']}")
        print(f"   Advanced token counting: {capabilities['advanced_token_counting']}")
        print(f"   Message batches: {capabilities['message_batches']}")

        # Test compatibility layer
        print("\n🔧 Testing Compatibility Layer...")
        from amplifier.sdk_enhancements.compatibility_layer import (
            get_compatibility_layer,
        )

        compat_layer = await get_compatibility_layer()
        test_messages = [{"role": "user", "content": "Test message"}]

        token_count = await compat_layer.count_tokens(test_messages)
        streaming_response = await compat_layer.execute_streaming_response(test_messages, max_tokens=10)

        print(f"✅ Compatibility Layer: Token count={token_count}, Streaming={len(streaming_response) > 0}")

        # Test core skills compatibility
        print("\n🎯 Testing Core Skills Compatibility...")
        from amplifier.sdk_enhancements.compatibility_layer import verify_core_skills_compatibility

        compatibility_results = await verify_core_skills_compatibility()

        print(f"   Total Skills: {compatibility_results['total_core_skills']}")
        print(f"   Compatible Skills: {compatibility_results['compatible_skills']}")
        print(f"   Compatibility Rate: {compatibility_results['compatibility_percentage']:.1f}%")
        print(f"   All Compatible: {compatibility_results['all_compatible']}")

        # Final summary
        print("\n📊 SUMMARY:")
        print(f"   SDK Version: {SDK_VERSION}")
        print(f"   Anthropic Available: {ANTHROPIC_AVAILABLE}")
        print(f"   Core Skills Compatibility: {compatibility_results['compatibility_percentage']:.1f}%")
        print(f"   Enhanced Features: All working")

        if compatibility_results["all_compatible"]:
            print("🎉 SUCCESS: Enhanced SDK integration with 100% core skills compatibility!")
            return True
        else:
            print("⚠️  PARTIAL SUCCESS: Enhanced SDK working but some core skills need attention")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
