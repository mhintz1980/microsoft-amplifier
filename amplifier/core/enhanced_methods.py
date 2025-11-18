"""
Enhanced Method Replacements
Automatically substitutes standard methods with enhanced versions
"""

import asyncio
import functools
from collections.abc import Callable


def enhanced_method(original_method: Callable) -> Callable:
    """Decorator to replace standard method with enhanced version"""

    @functools.wraps(original_method)
    def wrapper(*args, **kwargs):
        # Use enhanced SDK if available
        client = _get_enhanced_client()
        if client and hasattr(client, "execute_streaming_response"):
            return client.execute_streaming_response(*args, **kwargs)
        return original_method(*args, **kwargs)

    return wrapper


def _get_enhanced_client():
    """Get or create enhanced client instance"""
    try:
        from amplifier.sdk_enhancements.anthropic_integration import get_enhanced_anthropic_client

        if not hasattr(_get_enhanced_client, "_instance"):
            # Create instance synchronously
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            _get_enhanced_client._instance = loop.run_until_complete(get_enhanced_anthropic_client())

        return _get_enhanced_client._instance
    except:
        return None


# Auto-replace common methods
try:
    from anthropic import Anthropic

    Anthropic.messages.create = enhanced_method(Anthropic.messages.create)
    Anthropic.messages.stream = enhanced_method(Anthropic.messages.stream)
    print("✅ Enhanced method replacements active")
except ImportError:
    pass
