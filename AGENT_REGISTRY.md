# Agent Registry - Progressive Discovery System

**Purpose**: Lightweight agent directory for on-demand loading. Full agent details loaded only when Task tool is called.

**Usage**: Search by capability tags or agent name, then Task tool loads full definition.

## Core Development Agents

- **zen-architect**: Code planning, architecture design, review tasks (345 tokens)
  - Tags: `architecture`, `planning`, `design`, `review`, `code-quality`

- **modular-builder**: Primary implementation agent for all code building (208 tokens)
  - Tags: `implementation`, `code-generation`, `building`, `development`

- **bug-hunter**: Debugging and error resolution specialist (193 tokens)
  - Tags: `debugging`, `errors`, `troubleshooting`, `fixes`

- **test-coverage**: Test analysis and coverage optimization (195 tokens)
  - Tags: `testing`, `coverage`, `quality-assurance`, `test-planning`

## Analysis & Optimization Agents

- **performance-optimizer**: Code and system performance optimization (430 tokens)
  - Tags: `performance`, `optimization`, `speed`, `efficiency`

- **analysis-engine**: Multi-mode analysis (DEEP/SYNTHESIS/TRIAGE) (273 tokens)
  - Tags: `analysis`, `research`, `information-gathering`, `triage`

- **insight-synthesizer**: Revolutionary connections and breakthrough insights (512 tokens)
  - Tags: `insights`, `synthesis`, `connections`, `breakthrough-thinking`

## Integration & System Agents

- **integration-specialist**: External services, APIs, MCP server integration (303 tokens)
  - Tags: `integration`, `apis`, `external-services`, `mcp`, `dependencies`

- **database-architect**: Database design, optimization, migrations (416 tokens)
  - Tags: `database`, `schema`, `sql`, `optimization`, `data-modeling`

- **api-contract-designer**: REST/GraphQL API design and documentation (446 tokens)
  - Tags: `api`, `rest`, `graphql`, `documentation`, `contracts`

## Knowledge & Content Agents

- **content-researcher**: Content analysis and research tasks (333 tokens)
  - Tags: `research`, `content-analysis`, `documentation`, `learning`

- **knowledge-archaeologist**: Knowledge evolution and historical context (496 tokens)
  - Tags: `knowledge-history`, `evolution`, `context-research`, `patterns`

- **concept-extractor**: Knowledge extraction from articles/documents (441 tokens)
  - Tags: `knowledge-extraction`, `content-processing`, `analysis`

## Specialized Development Agents

- **python-development:python-pro**: Python 3.12+ expert (78 tokens)
  - Tags: `python`, `development`, `async`, `performance`

- **python-development:fastapi-pro**: FastAPI async APIs (65 tokens)
  - Tags: `python`, `fastapi`, `async`, `apis`

- **python-development:django-pro**: Django 5.x expert (67 tokens)
  - Tags: `python`, `django`, `web-development`, `orm`

- **javascript-pro**: Modern ES2023+ JavaScript expert (59 tokens)
  - Tags: `javascript`, `es2023`, `nodejs`, `async`

- **typescript-pro**: Advanced TypeScript development (62 tokens)
  - Tags: `typescript`, `type-system`, `build-optimization`

- **nextjs-developer**: Next.js 14+ with App Router (65 tokens)
  - Tags: `nextjs`, `react`, `full-stack`, `ssr`

## Shell & Infrastructure Agents

- **shell-scripting:bash-pro**: Production-grade Bash scripting (44 tokens)
  - Tags: `bash`, `shell-scripting`, `cicd`, `automation`

- **shell-scripting:posix-shell-pro**: POSIX sh portability (53 tokens)
  - Tags: `posix`, `shell-scripting`, `portability`, `unix`

## Application Performance Agents

- **application-performance:frontend-developer**: React, Next.js, responsive design (80 tokens)
  - Tags: `frontend`, `react`, `performance`, `ui`, `responsive`

- **application-performance:performance-engineer**: Core Web Vitals, optimization (115 tokens)
  - Tags: `performance`, `optimization`, `web-vitals`, `monitoring`

- **application-performance:observability-engineer**: Monitoring, logging, tracing (78 tokens)
  - Tags: `observability`, `monitoring`, `logging`, `telemetry`

## Testing & Quality Agents

- **unit-testing:test-automator**: pytest, modern frameworks, TDD (68 tokens)
  - Tags: `testing`, `pytest`, `tdd`, `test-automation`

- **error-diagnostics:error-detective**: Production errors, log analysis (65 tokens)
  - Tags: `debugging`, `error-analysis`, `logs`, `production`

## Specialized Architecture Agents

- **amplifier-cli-architect**: Amplifier CLI tool guidance (448 tokens)
  - Tags: `amplifier`, `cli`, `tools`, `architecture`

- **subagent-architect**: Creates new specialized agents (490 tokens)
  - Tags: `agent-creation`, `specialization`, `tool-development`

- **contract-spec-author**: Contract and implementation specifications (327 tokens)
  - Tags: `specifications`, `contracts`, `documentation`, `formal-specs`

- **pattern-emergence**: Orchestrates diverse perspectives (342 tokens)
  - Tags: `orchestration`, `multi-perspective`, `emergence`, `synthesis`

- **visualization-architect**: Data visualization and interactive graphs (518 tokens)
  - Tags: `visualization`, `data-visuals`, `interactive`, `graphs`

## Security & Safety Agents

- **security-guardian**: Security reviews, vulnerability assessments (465 tokens)
  - Tags: `security`, `vulnerability-assessment`, `code-review`, `auth`

## Knowledge Synthesis Agents

- **graph-builder**: Knowledge graph construction from agent outputs (343 tokens)
  - Tags: `knowledge-graphs`, `synthesis`, `data-structures`

- **ambiguity-guardian**: Preserves tensions and contradictions (463 tokens)
  - Tags: `ambiguity`, `tension-management`, `context-preservation`

## Orchestration Agents

- **prime-orchestrator**: Optimal tool usage for prime commands (249 tokens)
  - Tags: `orchestration`, `prime-commands`, `optimization`, `coordination`

## Post-Execution Agents

- **post-task-cleanup**: Codebase hygiene and cleanup (375 tokens)
  - Tags: `cleanup`, `code-hygiene`, `maintenance`, `post-processing`

## Plugin Agents (External)

- **episodic-memory**: Cross-session conversation search
  - Tags: `memory`, `search`, `conversation-history`

## Usage Pattern

1. **Search registry**: Find agent by capability tags or name
2. **Progressive load**: Task tool loads full agent definition on-demand
3. **Execute**: Full agent capabilities available during task execution
4. **Context efficient**: Only active agents consume context

**Total registry context**: ~800 tokens vs 9,900 tokens (92% reduction)