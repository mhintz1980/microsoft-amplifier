#!/usr/bin/env python3
"""
CreaTech API Server for bolt.diy Integration

This API server provides endpoints for bolt.diy to access CreaTech Assistant
capabilities including creative-technical synthesis, UI prototyping, and
multi-agent orchestration.
"""

import logging
from datetime import datetime
from typing import Any

import uvicorn
from creative_workflow_orchestrator import CreativeWorkflowOrchestrator
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import CreaTech components
from main_assistant import CreaTechAssistant
from pydantic import BaseModel
from pydantic import Field
from ui_rapid_prototyper import UIRapidPrototyper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CreaTech API Server",
    description="Creative-Technical Synthesis API for bolt.diy integration",
    version="1.0.0",
)

# Add CORS middleware for bolt.diy integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # bolt.diy default ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global CreaTech instance
crean_assistant: CreaTechAssistant | None = None
ui_prototyper: UIRapidPrototyper | None = None
workflow_orchestrator: CreativeWorkflowOrchestrator | None = None


# Request/Response Models
class CreativeRequest(BaseModel):
    prompt: str = Field(..., description="The creative-technical prompt")
    context: str | None = Field(None, description="Additional context for the request")
    requirements: list[str] | None = Field(None, description="Specific requirements")
    constraints: dict[str, Any] | None = Field(None, description="Technical constraints")


class UIPrototypeRequest(BaseModel):
    description: str = Field(..., description="UI/UX description")
    style_preferences: dict[str, str] | None = Field(None, description="Style preferences")
    interaction_patterns: list[str] | None = Field(None, description="Interaction patterns")


class WorkflowRequest(BaseModel):
    task: str = Field(..., description="Main task description")
    agents: list[str] | None = Field(None, description="Specific agents to involve")
    phases: list[dict[str, Any]] | None = Field(None, description="Workflow phases")


class CreativeResponse(BaseModel):
    success: bool
    result: dict[str, Any] | None
    confidence: float
    metadata: dict[str, Any]


# Initialize CreaTech components
async def initialize_crean_components():
    """Initialize CreaTech Assistant components"""
    global crean_assistant, ui_prototyper, workflow_orchestrator

    try:
        crean_assistant = CreaTechAssistant()
        ui_prototyper = UIRapidPrototyper()
        workflow_orchestrator = CreativeWorkflowOrchestrator()

        logger.info("✅ CreaTech components initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize CreaTech components: {e}")
        return False


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for bolt.diy to verify API availability"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "crean_assistant": crean_assistant is not None,
            "ui_prototyper": ui_prototyper is not None,
            "workflow_orchestrator": workflow_orchestrator is not None,
        },
    }


# Models endpoint (for bolt.diy provider integration)
@app.get("/models")
async def get_available_models():
    """Return available CreaTech models/capabilities"""
    return {
        "models": [
            {
                "id": "crean-creative-technical",
                "name": "CreaTech Creative-Technical Synthesis",
                "description": "Combines creative design with technical implementation",
                "maxTokens": 8192,
                "capabilities": ["creative_synthesis", "technical_validation", "ui_prototyping"],
            },
            {
                "id": "crean-ui-prototyper",
                "name": "CreaTech UI Prototyper",
                "description": "Rapid UI/UX prototyping with aesthetic optimization",
                "maxTokens": 4096,
                "capabilities": ["ui_design", "interaction_design", "aesthetic_enhancement"],
            },
            {
                "id": "crean-workflow-orchestrator",
                "name": "CreaTech Workflow Orchestrator",
                "description": "Multi-agent creative-technical workflow coordination",
                "maxTokens": 16384,
                "capabilities": ["agent_coordination", "workflow_orchestration", "cross_domain_synthesis"],
            },
        ]
    }


# Creative synthesis endpoint
@app.post("/v1/chat/completions")
async def creative_synthesis(request: dict[str, Any]):
    """Main chat completion endpoint compatible with OpenAI format"""
    try:
        # Extract messages from request
        messages = request.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the last message as the prompt
        last_message = messages[-1]
        prompt = last_message.get("content", "")

        # Determine model/capability
        model = request.get("model", "crean-creative-technical")

        # Process based on model type
        if model == "crean-creative-technical":
            result = await handle_creative_synthesis(prompt)
        elif model == "crean-ui-prototyper":
            result = await handle_ui_prototyping(prompt)
        elif model == "crean-workflow-orchestrator":
            result = await handle_workflow_orchestration(prompt)
        else:
            # Default to creative synthesis
            result = await handle_creative_synthesis(prompt)

        # Return OpenAI-compatible response
        return {
            "id": f"crean-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": result.get("content", "")},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(result.get("content", "").split()),
                "total_tokens": len(prompt.split()) + len(result.get("content", "").split()),
            },
        }

    except Exception as e:
        logger.error(f"Error in creative synthesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_creative_synthesis(prompt: str) -> dict[str, Any]:
    """Handle creative-technical synthesis request"""
    if not crean_assistant:
        raise HTTPException(status_code=503, detail="CreaTech Assistant not initialized")

    try:
        # Analyze requirement
        analysis = await crean_assistant.analyze_requirement(prompt)

        # Generate creative concepts
        concepts = await crean_assistant.generate_creative_concepts(analysis)

        # Synthesize solution
        synthesis = await crean_assistant.synthesize_solution(prompt)

        content = f"""
# Creative-Technical Synthesis

## Analysis
{analysis.get("domain_analysis", "Analysis complete")}

## Creative Concepts
{chr(10).join([f"- {concept}" for concept in concepts.get("concepts", [])])}

## Synthesized Solution
{synthesis.get("synthesized_solution", "Solution synthesized")}

## Implementation Notes
{synthesis.get("implementation_notes", "Ready for implementation")}
"""

        return {
            "content": content,
            "confidence": 0.85,
            "metadata": {"analysis": analysis, "concepts": concepts, "synthesis": synthesis},
        }

    except Exception as e:
        logger.error(f"Error in creative synthesis: {e}")
        return {"content": f"Error: {str(e)}", "confidence": 0.0, "metadata": {}}


async def handle_ui_prototyping(prompt: str) -> dict[str, Any]:
    """Handle UI prototyping request"""
    if not ui_prototyper:
        raise HTTPException(status_code=503, detail="UI Prototyper not initialized")

    try:
        # Generate UI prototype
        result = await ui_prototyper.generate_ui_prototype(prompt)

        content = f"""
# UI Prototype Design

## Design Overview
{result.get("design_overview", "Design generated")}

## Components
{chr(10).join([f"- {component}" for component in result.get("components", [])])}

## Styling
{result.get("styling", "Styling applied")}

## Interaction Patterns
{result.get("interaction_patterns", "Interactions defined")}
"""

        return {"content": content, "confidence": 0.90, "metadata": result}

    except Exception as e:
        logger.error(f"Error in UI prototyping: {e}")
        return {"content": f"Error: {str(e)}", "confidence": 0.0, "metadata": {}}


async def handle_workflow_orchestration(prompt: str) -> dict[str, Any]:
    """Handle workflow orchestration request"""
    if not workflow_orchestrator:
        raise HTTPException(status_code=503, detail="Workflow Orchestrator not initialized")

    try:
        # Plan and execute workflow
        result = await workflow_orchestrator.coordinate_workflow(prompt)

        content = f"""
# Workflow Orchestration

## Workflow Plan
{result.get("workflow_plan", "Workflow planned")}

## Agent Coordination
{chr(10).join([f"- {agent}: {status}" for agent, status in result.get("agent_status", {}).items()])}

## Execution Results
{result.get("execution_results", "Workflow executed")}

## Deliverables
{chr(10).join([f"- {deliverable}" for deliverable in result.get("deliverables", [])])}
"""

        return {"content": content, "confidence": 0.80, "metadata": result}

    except Exception as e:
        logger.error(f"Error in workflow orchestration: {e}")
        return {"content": f"Error: {str(e)}", "confidence": 0.0, "metadata": {}}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize CreaTech components on startup"""
    success = await initialize_crean_components()
    if not success:
        logger.warning("⚠️ CreaTech components failed to initialize - some features may be unavailable")


# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,  # CreaTech API port
        reload=True,
        log_level="info",
    )
