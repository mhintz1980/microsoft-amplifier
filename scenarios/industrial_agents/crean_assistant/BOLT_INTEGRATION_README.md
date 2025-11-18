# CreaTech + bolt.diy Integration

## Overview

This integration connects the CreaTech Assistant (creative-technical synthesis AI) with bolt.diy (AI-powered full-stack web development) to create a unique development environment that combines technical precision with creative excellence.

## Architecture

```
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐  ┌──────────────────┐
│  bolt.diy UI     │  │  CreaTech API     │  │  Agent Lightning   │  │  Amplifier        │
│  (Browser)       │◄─┤  (Port 8000)     │◄─┤  Training          │◄─┤  Agent Ecosystem  │
└─────────────────┘  └──────────────────┘  └─────────────────────┘  └──────────────────┘
         │                       │                        │                    │
         ▼                       ▼                        ▼                    ▼
   Multi-LLM Platform    Creative-Technical    Continuous Learning   20+ Specialized
   with CreaTech as      Synthesis Engine      & Improvement         Agents
   a Provider
```

## Features

### CreaTech Models Available in bolt.diy

1. **CreaTech Creative-Technical Synthesis** (`crean-creative-technical`)
   - Combines creative design with technical implementation
   - Max tokens: 8192
   - Use for: Innovative solutions that require both creativity and technical precision

2. **CreaTech UI Prototyper** (`crean-ui-prototyper`)
   - Rapid UI/UX prototyping with aesthetic optimization
   - Max tokens: 4096
   - Use for: Beautiful, functional interface design with creative enhancement

3. **CreaTech Workflow Orchestrator** (`crean-workflow-orchestrator`)
   - Multi-agent creative-technical workflow coordination
   - Max tokens: 16384
   - Use for: Complex projects requiring coordination across multiple specialized agents

## Setup Instructions

### Prerequisites

1. **Amplifier Project**: ✅ Already set up with CreaTech Assistant
2. **bolt.diy**: ✅ Already cloned and running locally
3. **Python Dependencies**: FastAPI, Uvicorn, Pydantic

### Step 1: Start CreaTech API Server

```bash
cd /home/markimus/projects/microsoft-amplifier/scenarios/industrial_agents/crean_assistant
./start_crean_api.sh
```

The API server will start on `http://localhost:8001`

### Step 2: Configure bolt.diy

1. Open bolt.diy in your browser (usually `http://localhost:5173`)
2. Go to Settings → Providers
3. Find "CreaTech" in the provider list
4. Configure the following settings:
   - **API Key**: `crean-api-key-local` (or any value for local development)
   - **Base URL**: `http://localhost:8001` (should be pre-filled)
5. Enable the CreaTech provider

### Step 3: Test the Integration

1. In bolt.diy, select "CreaTech Creative-Technical Synthesis" as your model
2. Try a prompt like:
   ```
   Create a React component for a pump scheduling dashboard that is both technically robust and visually beautiful
   ```
3. You should receive a response that combines:
   - Technical implementation details
   - Creative design concepts
   - Synthesized solution approach
   - Implementation notes

## API Endpoints

### Health Check
```
GET http://localhost:8001/health
```
Returns the health status of CreaTech components

### Models
```
GET http://localhost:8001/models
```
Returns available CreaTech models and their capabilities

### Chat Completions (OpenAI-Compatible)
```
POST http://localhost:8001/v1/chat/completions
```
OpenAI-compatible endpoint for bolt.diy integration

## Usage Examples

### Creative-Technical Synthesis
```
Design an electric vehicle charging station interface that balances technical functionality with sustainable design aesthetics
```

### UI Prototyping
```
Create a beautiful data visualization dashboard for factory operations with real-time metrics and intuitive controls
```

### Workflow Orchestration
```
Coordinate a multi-agent project to develop a smart home energy management system with hardware integration and mobile app
```

## Troubleshooting

### CreaTech Not Showing in bolt.diy

1. **Check API Server**: Ensure `http://localhost:8001/health` is accessible
2. **Refresh Providers**: In bolt.diy settings, refresh the provider list
3. **Check Configuration**: Verify API key and base URL are set correctly
4. **Check Logs**: Look for CreaTech registration logs in bolt.diy console

### API Connection Issues

1. **Port Conflict**: Ensure port 8001 is not in use
2. **CORS Issues**: The API server includes CORS middleware for bolt.diy
3. **Dependencies**: Run `pip install fastapi uvicorn pydantic` in the CreaTech directory

### Performance Issues

1. **Response Time**: CreaTech responses may take 10-30 seconds due to complex synthesis
2. **Token Limits**: Large requests may be truncated; consider breaking into smaller prompts
3. **Resource Usage**: Monitor CPU/memory usage during complex workflows

## Development

### Adding New CreaTech Capabilities

1. **Update API Server**: Add new endpoints in `api_server.py`
2. **Update Provider**: Add new models in `crean.ts`
3. **Update Workflow**: Enhance synthesis logic in CreaTech components
4. **Test Integration**: Verify compatibility with bolt.diy

### Custom Workflows

The integration supports custom workflows through the workflow orchestrator. You can:

1. Define specific agent coordination patterns
2. Add domain-specific synthesis logic
3. Implement custom creative-technical algorithms
4. Create specialized templates for different use cases

## Next Steps

1. **Enhanced Integration**: Add WebSocket support for real-time collaboration
2. **Custom Prompts**: Create bolt.diy prompt templates optimized for CreaTech
3. **Performance Optimization**: Implement caching and response streaming
4. **Advanced Workflows**: Develop specialized creative-technical workflows for specific domains

## Support

For issues or questions:

1. **API Issues**: Check CreaTech API server logs
2. **bolt.diy Issues**: Check browser console and bolt.diy logs
3. **Integration Issues**: Verify both systems are running and configured correctly

---

**Result**: The world's first AI-powered development environment that combines creative design excellence with technical implementation precision, all within the familiar bolt.diy interface! 🚀✨