# AI Career Copilot - Setup Guide

## 🎯 Quick Start

The AI Career Copilot is now fully set up and ready to use! This guide will walk you through getting started with the application.

## 📋 Prerequisites You Need

### Required API Keys
1. **Claude API Key** - Get from [Anthropic Console](https://console.anthropic.com/)
   - Required for resume parsing, career coaching, and skill analysis

### Environment Setup
- ✅ Python 3.11+ (already configured)
- ✅ Node.js 18+ (already configured)
- ✅ All dependencies installed

## 🚀 Getting Started

### 1. Configure Environment Variables

Copy the example configuration file and add your API key:

```bash
# Copy the example configuration
cp .env.example .env

# Edit the .env file and add your Claude API key
nano .env  # or use your favorite editor
```

**Add these required values to your `.env` file:**

```env
# Required: Your Claude API Key
ANTHROPIC_API_KEY=your_claude_api_key_here

# Required: JWT Secret Key (generate a secure random string)
CAREER_COPILOT_SECRET_KEY=your_jwt_secret_key_here_at_least_32_characters_long
```

### 2. Start the Backend Server

```bash
# Start the Career Copilot API server
uv run python -m amplifier.career_copilot
```

**You should see output like:**
```
Starting AI Career Copilot server on 0.0.0.0:8000
Environment: development
API Documentation: http://0.0.0.0:8000/docs
Starting Career Copilot v1.0.0 in development mode
Career Copilot started successfully
INFO:     Started server process [xxx]
INFO:     Application startup complete.
```

### 3. Start the Frontend (Optional)

Open a new terminal and start the React frontend:

```bash
# Navigate to frontend directory
cd amplifier/career_copilot/frontend

# Start the development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

## 📚 Documentation & Resources

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **API Examples**: See `amplifier/career_copilot/README.md`

### Core Documentation Files

1. **📖 Main README**: `amplifier/career_copilot/README.md` (545 lines)
   - Complete installation guide
   - API usage examples
   - Architecture overview
   - Development workflow

2. **⚙️ Configuration**: See `.env.example` for all available settings

3. **🧪 Testing**: `amplifier/career_copilot/tests/`
   - Model validation tests
   - API endpoint tests
   - Service integration tests

## 🎯 Available Features

### 📄 Resume Processing
- Upload resumes in PDF, DOCX, TXT, JSON, or Markdown format
- AI-powered structured extraction using Claude
- Automatic parsing of work experience, education, skills, and contact info

### 🤖 AI Career Coaching
- Interactive chat with AI career coach
- Personalized career advice and guidance
- Skill gap analysis and recommendations
- Interview preparation and salary negotiation tips

### 🎯 Job Matching
- AI-generated job descriptions tailored to your profile
- Relevance scoring and matching analysis
- Application strategy recommendations

### 📝 Document Generation
- Tailored resumes for specific job applications
- Personalized cover letters
- Career summaries and achievement highlights

## 🔌 API Endpoints

### Core Endpoints
- `POST /api/v1/resume/parse` - Parse resume text
- `POST /api/v1/profile/enrich` - AI coaching chat
- `POST /api/v1/skills/analyze` - Skill gap analysis
- `GET /api/v1/jobs/match` - Job matching
- `POST /api/v1/resumes/generate` - Generate tailored resume
- `POST /api/v1/cover-letters/generate` - Generate cover letter

### Management Endpoints
- `GET /` - Health check
- `GET /api/v1/profile` - Get master profile
- `PUT /api/v1/profile` - Update profile
- `GET /debug/config` - Debug configuration (dev only)

## 🛠️ Development Commands

### Backend Commands
```bash
# Start development server
uv run python -m amplifier.career_copilot

# Run tests
uv run pytest amplifier/career_copilot/tests/

# Type checking
uv run pyright amplifier/career_copilot/

# Linting
uv run ruff check amplifier/career_copilot/
```

### Frontend Commands
```bash
cd amplifier/career_copilot/frontend

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Type checking
npm run type-check
```

## 🔍 Troubleshooting

### Common Issues

**1. Claude API Key Not Found**
- Ensure `ANTHROPIC_API_KEY` is set in your `.env` file
- Verify your API key is valid and active

**2. Port Already in Use**
- Change `CAREER_COPILOT_PORT` in `.env` to another port (e.g., 8001)
- Or kill the process using the port: `lsof -ti:8000 | xargs kill`

**3. Dependencies Issues**
- Run `uv sync` to refresh Python dependencies
- Run `npm install` in frontend directory

**4. Import Errors**
- Ensure you're in the project root directory
- Run `source .venv/bin/activate` if your virtual environment isn't active

### Getting Help

1. **Check the logs** - Both backend and frontend provide detailed logging
2. **API Documentation** - Visit http://localhost:8000/docs for interactive API testing
3. **Configuration** - Review `.env.example` for all available options
4. **README** - See `amplifier/career_copilot/README.md` for detailed documentation

## 🎉 Ready to Use!

Your AI Career Copilot is now fully operational! You can:

1. **Visit the API**: http://localhost:8000/docs
2. **Start parsing resumes**: Upload your resume via the API
3. **Chat with the AI coach**: Get personalized career advice
4. **Generate tailored documents**: Create custom resumes and cover letters

The system is production-ready and integrates seamlessly with the Microsoft Amplifier ecosystem. Happy career development! 🚀