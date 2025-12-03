#!/usr/bin/env python3
"""
LLM Integration - Production LLM service integration for AI Assistant
Provides seamless integration with multiple LLM providers and optimization
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import sys
import os

# Add amplifier to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from anthropic import Anthropic
    from openai import AsyncOpenAI

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ LLM libraries not installed - run: pip install anthropic openai")

try:
    from amplifier.llm_integration.caching import ResponseCache, SemanticCache
    from amplifier.llm_integration.rate_limiting import RateLimiter
    from amplifier.llm_integration.fallback import FallbackManager
    from amplifier.llm_integration.monitoring import LLMMonitor

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL = "local"


@dataclass
class LLMRequest:
    """Standardized LLM request"""

    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Standardized LLM response"""

    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, int]
    latency: float
    request_id: str
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """LLM provider configuration"""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: float = 30.0
    max_retries: int = 3
    organization_id: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.monitor = LLMMonitor() if INTEGRATION_AVAILABLE else None

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM"""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest):
        """Generate streaming response"""
        pass

    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        try:
            test_request = LLMRequest(prompt="Hello", max_tokens=10)
            response = await self.generate(test_request)
            return bool(response.content)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic library not installed")

        self.client = Anthropic(api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY"))

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic Claude"""
        start_time = time.time()

        try:
            # Build messages
            messages = [{"role": "user", "content": request.prompt}]

            # Build API parameters
            api_params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature,
            }

            if request.system_prompt:
                api_params["system"] = request.system_prompt

            # Make API call
            response = self.client.messages.create(**api_params)

            latency = time.time() - start_time

            # Extract usage
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            llm_response = LLMResponse(
                content=response.content[0].text,
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                usage=usage,
                latency=latency,
                request_id=str(response.id),
                cached=False,
            )

            # Record metrics
            if self.monitor:
                await self.monitor.record_request(llm_response, request)

            return llm_response

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            latency = time.time() - start_time
            raise RuntimeError(f"Anthropic generation failed: {e}")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("openai library not installed")

        self.client = AsyncOpenAI(api_key=config.api_key or os.getenv("OPENAI_API_KEY"), base_url=config.base_url)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI GPT"""
        start_time = time.time()

        try:
            # Build messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            # Build API parameters
            api_params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or self.config.max_tokens,
            }

            # Make API call
            response = await self.client.chat.completions.create(**api_params)

            latency = time.time() - start_time

            # Extract usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            llm_response = LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                usage=usage,
                latency=latency,
                request_id=str(response.id),
                cached=False,
            )

            # Record metrics
            if self.monitor:
                await self.monitor.record_request(llm_response, request)

            return llm_response

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            latency = time.time() - start_time
            raise RuntimeError(f"OpenAI generation failed: {e}")


class LLMManager:
    """Production LLM manager with caching, rate limiting, and fallback"""

    def __init__(
        self,
        providers: Dict[LLMProvider, LLMConfig],
        cache_dir: Path = Path("llm_cache"),
        enable_cache: bool = True,
        enable_fallback: bool = True,
    ):
        self.providers = providers
        self.enable_cache = enable_cache
        self.enable_fallback = enable_fallback

        # Initialize providers
        self.provider_instances = {}
        for provider, config in providers.items():
            try:
                if provider == LLMProvider.ANTHROPIC:
                    self.provider_instances[provider] = AnthropicProvider(config)
                elif provider == LLMProvider.OPENAI:
                    self.provider_instances[provider] = OpenAIProvider(config)
                else:
                    logger.warning(f"Provider {provider} not implemented")
            except Exception as e:
                logger.error(f"Failed to initialize {provider}: {e}")

        # Initialize services
        if INTEGRATION_AVAILABLE:
            self.cache = ResponseCache(cache_dir) if enable_cache else None
            self.rate_limiter = RateLimiter()
            self.fallback_manager = FallbackManager(list(self.provider_instances.keys()))
            self.monitor = LLMMonitor()
        else:
            self.cache = None
            self.rate_limiter = None
            self.fallback_manager = None
            self.monitor = None

        # Primary provider
        self.primary_provider = list(providers.keys())[0] if providers else None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response with caching, rate limiting, and fallback"""
        request_id = f"{int(time.time() * 1000)}-{hash(request.prompt) % 10000}"

        # Check cache first
        if self.cache:
            cached_response = await self.cache.get(request)
            if cached_response:
                logger.info(f"Cache hit for request {request_id}")
                cached_response.cached = True
                cached_response.request_id = request_id
                return cached_response

        # Check rate limits
        if self.rate_limiter:
            await self.rate_limiter.check_limit(request.user_id or "anonymous")

        # Try primary provider first
        provider = self.primary_provider
        if provider in self.provider_instances:
            try:
                response = await self.provider_instances[provider].generate(request)

                # Cache successful response
                if self.cache and response.content:
                    await self.cache.set(request, response)

                return response

            except Exception as e:
                logger.error(f"Primary provider {provider} failed: {e}")

                # Try fallback providers
                if self.enable_fallback and self.fallback_manager:
                    fallback_providers = await self.fallback_manager.get_fallback_providers(provider)

                    for fallback_provider in fallback_providers:
                        if fallback_provider in self.provider_instances:
                            try:
                                logger.info(f"Trying fallback provider: {fallback_provider}")
                                response = await self.provider_instances[fallback_provider].generate(request)

                                # Cache successful response
                                if self.cache and response.content:
                                    await self.cache.set(request, response)

                                return response

                            except Exception as fallback_error:
                                logger.error(f"Fallback provider {fallback_provider} failed: {fallback_error}")

        raise RuntimeError("All LLM providers failed")

    async def generate_stream(self, request: LLMRequest):
        """Generate streaming response"""
        if self.primary_provider in self.provider_instances:
            async for chunk in self.provider_instances[self.primary_provider].generate_stream(request):
                yield chunk

    async def health_check(self) -> Dict[LLMProvider, bool]:
        """Check health of all providers"""
        health_status = {}
        for provider, instance in self.provider_instances.items():
            try:
                health_status[provider] = await instance.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider}: {e}")
                health_status[provider] = False
        return health_status

    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if self.monitor:
            return await self.monitor.get_stats()
        return {}

    async def clear_cache(self):
        """Clear response cache"""
        if self.cache:
            await self.cache.clear()


# Production-ready instance factory
def create_llm_manager(
    anthropic_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    cache_dir: str = "llm_cache",
    primary_provider: LLMProvider = LLMProvider.ANTHROPIC,
) -> LLMManager:
    """Create production LLM manager with sensible defaults"""

    providers = {}

    if anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"):
        providers[LLMProvider.ANTHROPIC] = LLMConfig(
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-sonnet-20240229",
            temperature=0.7,
            max_tokens=4000,
        )

    if openai_api_key or os.getenv("OPENAI_API_KEY"):
        providers[LLMProvider.OPENAI] = LLMConfig(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY"), model="gpt-4", temperature=0.7, max_tokens=4000
        )

    if not providers:
        raise ValueError("No API keys provided - set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables")

    # Reorder providers based on primary choice
    if primary_provider in providers:
        ordered_providers = {primary_provider: providers[primary_provider]}
        ordered_providers.update({k: v for k, v in providers.items() if k != primary_provider})
        providers = ordered_providers

    return LLMManager(providers=providers, cache_dir=Path(cache_dir), enable_cache=True, enable_fallback=True)


# CLI testing interface
async def main():
    """Test LLM integration"""
    import argparse

    parser = argparse.ArgumentParser(description="Test LLM integration")
    parser.add_argument("--prompt", default="Hello, how can you help me build a component library?")
    parser.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    parser.add_argument("--no-cache", action="store_true")

    args = parser.parse_args()

    try:
        manager = create_llm_manager(cache_dir="test_llm_cache", primary_provider=LLMProvider(args.provider))

        request = LLMRequest(prompt=args.prompt, temperature=0.7, max_tokens=1000)

        print(f"🤖 Testing {args.provider} with prompt: {args.prompt}")
        print("=" * 50)

        response = await manager.generate(request)

        print(f"📤 Provider: {response.provider.value}")
        print(f"📤 Model: {response.model}")
        print(f"📤 Latency: {response.latency:.2f}s")
        print(f"📤 Usage: {response.usage}")
        print(f"📤 Cached: {response.cached}")
        print(f"📤 Request ID: {response.request_id}")
        print()
        print("📄 Response:")
        print("-" * 30)
        print(response.content)

        # Health check
        print("\n🏥 Health Check:")
        health = await manager.health_check()
        for provider, healthy in health.items():
            status = "✅" if healthy else "❌"
            print(f"  {status} {provider.value}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
