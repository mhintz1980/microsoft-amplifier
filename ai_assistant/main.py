#!/usr/bin/env python3
"""
AI Assistant Main Application - Production-ready AI Assistant for Component Library Management
Integrates all components into a cohesive, production-ready system
"""

import asyncio
import json
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
from datetime import datetime

# Add amplifier to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn

    WEB_FRAMEWORK_AVAILABLE = True
except ImportError:
    WEB_FRAMEWORK_AVAILABLE = False

# Import our components
from component_library_assistant import ComponentLibraryAssistant, Component, ConversationContext
from nlp_pipeline import EnhancedNLUEngine, NLUResult
from conversation_flows import ConversationFlowEngine, FlowContext
from llm_integration import create_llm_manager, LLMRequest, LLMProvider
from monitoring_dashboard import MetricsCollector, MonitoringDashboard

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration"""

    app_name: str = "Component Library Assistant"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # LLM Configuration
    llm_provider: str = "anthropic"
    llm_cache_dir: str = "llm_cache"
    llm_max_tokens: int = 4000
    llm_temperature: float = 0.7

    # Component Library Configuration
    component_storage_dir: str = "components"
    max_components_per_user: int = 1000
    enable_web_scraping: bool = True

    # Monitoring Configuration
    enable_monitoring: bool = True
    monitoring_port: int = 8080
    metrics_collection_interval: int = 30

    # Security Configuration
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_cors: bool = True


# Pydantic models for API
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation identifier")
    intent: Optional[str] = Field(None, description="Detected intent")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities")
    suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up actions")


class ComponentInfo(BaseModel):
    name: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    url_source: Optional[str] = None
    html_code: Optional[str] = None
    css_code: Optional[str] = None
    js_code: Optional[str] = None


class ComponentLibraryManager:
    """Production component library manager"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.storage_dir = Path(config.component_storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize AI components
        self.nlu_engine = EnhancedNLUEngine()
        self.flow_engine = ConversationFlowEngine()
        self.assistant = ComponentLibraryAssistant(nlu_engine=self.nlu_engine, flow_engine=self.flow_engine)

        # Initialize LLM manager
        try:
            self.llm_manager = create_llm_manager(
                cache_dir=config.llm_cache_dir, primary_provider=LLMProvider(config.llm_provider)
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM manager: {e}")
            self.llm_manager = None

        # Storage
        self.components: Dict[str, List[Component]] = {}
        self.conversations: Dict[str, ConversationContext] = {}

        # Metrics
        self.metrics = MetricsCollector()

    async def initialize(self):
        """Initialize the manager"""
        logger.info("Initializing Component Library Manager")

        # Load existing components
        await self.load_components()

        # Initialize LLM manager health check
        if self.llm_manager:
            try:
                health = await self.llm_manager.health_check()
                logger.info(f"LLM Manager health: {health}")
            except Exception as e:
                logger.error(f"LLM Manager health check failed: {e}")

        logger.info("Component Library Manager initialized successfully")

    async def load_components(self):
        """Load existing components from storage"""
        try:
            for user_file in self.storage_dir.glob("*.json"):
                user_id = user_file.stem
                with open(user_file, "r", encoding="utf-8") as f:
                    user_components = json.load(f)
                    self.components[user_id] = [Component(**comp_data) for comp_data in user_components]
            logger.info(f"Loaded components for {len(self.components)} users")
        except Exception as e:
            logger.error(f"Failed to load components: {e}")

    async def save_components(self, user_id: str):
        """Save components to storage"""
        try:
            user_file = self.storage_dir / f"{user_id}.json"
            user_components = self.components.get(user_id, [])
            with open(user_file, "w", encoding="utf-8") as f:
                json.dump([comp.__dict__ for comp in user_components], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save components for user {user_id}: {e}")

    async def process_message(
        self, message: str, user_id: str, conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate response"""
        start_time = datetime.now()

        try:
            # Get or create conversation context
            if conversation_id is None:
                conversation_id = f"{user_id}_{int(start_time.timestamp())}"

            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = ConversationContext(
                    user_id=user_id, conversation_id=conversation_id
                )

            context = self.conversations[conversation_id]

            # Process with assistant
            response = await self.assistant.process_message(message, context)

            # Update conversation
            self.conversations[conversation_id] = context

            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.add_custom_metric("message_processing_time", processing_time)

            return {
                "response": response.response,
                "conversation_id": conversation_id,
                "intent": response.intent.value if response.intent else None,
                "entities": response.entities,
                "suggestions": response.suggestions,
                "processing_time": processing_time,
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again.",
                "conversation_id": conversation_id or f"{user_id}_error",
                "error": str(e),
            }

    async def add_component(self, user_id: str, component_info: ComponentInfo) -> Dict[str, Any]:
        """Add a new component to the library"""
        try:
            # Validate user limit
            user_components = self.components.get(user_id, [])
            if len(user_components) >= self.config.max_components_per_user:
                raise HTTPException(status_code=400, detail="Component limit reached")

            # Create component
            component = Component(
                name=component_info.name,
                category=component_info.category or "Uncategorized",
                tags=component_info.tags or [],
                url_source=component_info.url_source,
                html_code=component_info.html_code,
                css_code=component_info.css_code,
                js_code=component_info.js_code,
                date_saved=datetime.now(),
            )

            # Add to user's collection
            if user_id not in self.components:
                self.components[user_id] = []
            self.components[user_id].append(component)

            # Save to storage
            await self.save_components(user_id)

            # Record metrics
            self.metrics.add_custom_metric("components_added", 1, {"user_id": user_id})

            return {
                "component_id": component.id,
                "message": f"Component '{component.name}' added successfully to your library",
                "component": component.__dict__,
            }

        except Exception as e:
            logger.error(f"Error adding component: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_components(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get components for a user"""
        try:
            user_components = self.components.get(user_id, [])

            if category:
                user_components = [c for c in user_components if c.category == category]

            return [comp.__dict__ for comp in user_components]

        except Exception as e:
            logger.error(f"Error getting components: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def search_components(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search components using semantic search"""
        try:
            user_components = self.components.get(user_id, [])

            # Simple text search for now (can be enhanced with semantic search)
            query_lower = query.lower()
            results = []

            for component in user_components:
                score = 0
                if query_lower in component.name.lower():
                    score += 10
                if query_lower in component.category.lower():
                    score += 5
                if any(query_lower in tag.lower() for tag in component.tags):
                    score += 3

                if score > 0:
                    results.append({"component": component.__dict__, "score": score})

            # Sort by score descending
            results.sort(key=lambda x: x["score"], reverse=True)

            return [r["component"] for r in results]

        except Exception as e:
            logger.error(f"Error searching components: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Global application instance
app_manager: Optional[ComponentLibraryManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global app_manager

    # Startup
    logger.info("Starting Component Library Assistant")
    app_manager = ComponentLibraryManager(AppConfig())
    await app_manager.initialize()

    # Initialize monitoring
    monitoring_task = None
    if app_manager.config.enable_monitoring and WEB_FRAMEWORK_AVAILABLE:
        monitoring_task = asyncio.create_task(
            app_manager.metrics.start_collection(app_manager.config.metrics_collection_interval)
        )

    yield

    # Shutdown
    logger.info("Shutting down Component Library Assistant")
    if monitoring_task:
        monitoring_task.cancel()

    # Save all components
    for user_id in app_manager.components.keys():
        await app_manager.save_components(user_id)


def create_app(config: AppConfig) -> FastAPI:
    """Create FastAPI application"""
    if not WEB_FRAMEWORK_AVAILABLE:
        raise ImportError("Web framework dependencies not installed")

    app = FastAPI(
        title=config.app_name,
        version=config.version,
        description="AI-powered component library management assistant",
        lifespan=lifespan,
    )

    # Middleware
    if config.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # API Routes
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with basic UI"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Component Library Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
        .chat-messages { height: 400px; overflow-y: auto; padding: 20px; background: #f9f9f9; }
        .chat-input { display: flex; padding: 20px; background: #fff; border-top: 1px solid #ddd; }
        .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .chat-input button { padding: 10px 20px; margin-left: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .message { margin-bottom: 20px; }
        .user { text-align: right; }
        .assistant { text-align: left; }
        .message-bubble { display: inline-block; padding: 10px 15px; border-radius: 18px; max-width: 70%; }
        .user .message-bubble { background: #007bff; color: white; }
        .assistant .message-bubble { background: #e9ecef; color: #333; }
    </style>
</head>
<body>
    <h1>🤖 Component Library Assistant</h1>
    <div class="chat-container">
        <div class="chat-messages" id="messages"></div>
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Ask me about saving or finding components..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let conversationId = null;

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;

            const messagesDiv = document.getElementById('messages');

            // Add user message
            messagesDiv.innerHTML += `<div class="message user"><div class="message-bubble">${message}</div></div>`;
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        user_id: 'demo_user',
                        conversation_id: conversationId
                    })
                });

                const data = await response.json();
                conversationId = data.conversation_id;

                // Add assistant response
                messagesDiv.innerHTML += `<div class="message assistant"><div class="message-bubble">${data.response}</div></div>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

            } catch (error) {
                messagesDiv.innerHTML += `<div class="message assistant"><div class="message-bubble">Error: ${error.message}</div></div>`;
            }
        }

        // Allow Enter key to send message
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
        """

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Chat with the AI assistant"""
        if not app_manager:
            raise HTTPException(status_code=500, detail="Application not initialized")

        result = await app_manager.process_message(
            message=request.message, user_id=request.user_id or "anonymous", conversation_id=request.conversation_id
        )

        return ChatResponse(**result)

    @app.post("/components", response_model=Dict[str, Any])
    async def add_component(user_id: str, component: ComponentInfo):
        """Add a new component"""
        if not app_manager:
            raise HTTPException(status_code=500, detail="Application not initialized")

        return await app_manager.add_component(user_id, component)

    @app.get("/components/{user_id}", response_model=List[Dict[str, Any]])
    async def get_components(user_id: str, category: Optional[str] = None):
        """Get components for a user"""
        if not app_manager:
            raise HTTPException(status_code=500, detail="Application not initialized")

        return await app_manager.get_components(user_id, category)

    @app.get("/components/{user_id}/search", response_model=List[Dict[str, Any]])
    async def search_components(user_id: str, q: str):
        """Search components"""
        if not app_manager:
            raise HTTPException(status_code=500, detail="Application not initialized")

        return await app_manager.search_components(user_id, q)

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        if not app_manager:
            return {"status": "initializing", "timestamp": datetime.now().isoformat()}

        # Check LLM manager health
        llm_healthy = True
        if app_manager.llm_manager:
            try:
                llm_health = await app_manager.llm_manager.health_check()
                llm_healthy = any(llm_health.values())
            except:
                llm_healthy = False

        return {
            "status": "healthy" if llm_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "llm_healthy": llm_healthy,
            "total_components": sum(len(comps) for comps in app_manager.components.values()),
            "active_conversations": len(app_manager.conversations),
        }

    @app.get("/stats")
    async def get_stats():
        """Get application statistics"""
        if not app_manager:
            raise HTTPException(status_code=500, detail="Application not initialized")

        return {
            "total_users": len(app_manager.components),
            "total_components": sum(len(comps) for comps in app_manager.components.values()),
            "active_conversations": len(app_manager.conversations),
            "categories": list(
                set(comp.category for user_comps in app_manager.components.values() for comp in user_comps)
            ),
            "timestamp": datetime.now().isoformat(),
        }

    return app


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Component Library Assistant")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    parser.add_argument("--llm-provider", default="anthropic", help="LLM provider")
    parser.add_argument("--no-monitoring", action="store_true", help="Disable monitoring dashboard")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )

    # Create configuration
    config = AppConfig(
        debug=args.debug,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        llm_provider=args.llm_provider,
        enable_monitoring=not args.no_monitoring,
    )

    # Check dependencies
    if not WEB_FRAMEWORK_AVAILABLE:
        print("❌ Web framework dependencies not installed")
        print("   Run: pip install fastapi uvicorn pydantic")
        return 1

    print(f"🚀 Starting {config.app_name} v{config.version}")
    print(f"   🌐 API: http://{config.host}:{config.port}")
    print(f"   📊 Monitoring: http://localhost:{config.monitoring_port}")
    print(f"   🤖 LLM Provider: {config.llm_provider}")
    print(f"   📁 Components: {config.component_storage_dir}")
    print()

    try:
        # Create FastAPI app
        app = create_app(config)

        # Start monitoring dashboard if enabled
        monitoring_task = None
        if config.enable_monitoring:

            async def run_monitoring():
                dashboard = MonitoringDashboard(MetricsCollector(), config.monitoring_port)
                await dashboard.start_server()

            monitoring_task = asyncio.create_task(run_monitoring())

        # Run the main application
        config = uvicorn.Config(
            app, host=config.host, port=config.port, log_level=config.log_level.lower(), access_log=True
        )

        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Component Library Assistant")

    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
