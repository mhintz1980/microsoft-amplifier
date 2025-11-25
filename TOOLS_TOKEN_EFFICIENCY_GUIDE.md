# 🔧 TOOLS TOKEN EFFICIENCY GUIDE

**ALWAYS CHECK THIS BEFORE ANY TOOL EXECUTION**

## 🎯 The Token Efficiency First Rule

**Before launching ANY agent or tool, ask:**
1. **Can I do this with native tools instead?** (GitHub CLI, curl, make, etc.)
2. **Is there a cheaper workflow available?** (Our efficient workflows)
3. **Do I really need an LLM agent for this?** (Often not!)
4. **What's the token cost vs. alternative?** (Calculate before proceeding)

## 📋 TOKEN EFFICIENCY CHECKLIST

### **Phase 1: Quick Check (5 seconds)**
```python
from amplifier.token_efficiency import check_token_efficiency_first

is_efficient, recommendation = check_token_efficiency_first("Research repository", "github_research")
if not is_efficient:
    print(f"⚠️ {recommendation}")
    # Use recommended alternative instead
```

### **Phase 2: Workflow Selection (30 seconds)**
```python
from amplifier.token_efficiency import efficient_github_analysis, efficient_dependency_analysis

# Instead of expensive agent:
# ❌ integration-specialist (25k tokens, 5 minutes)
# ✅ Native GitHub CLI (2k tokens, 30 seconds)
result = efficient_github_analysis("https://github.com/owner/repo")

# Instead of expensive agent:
# ❌ zen-architect (15k tokens, 3 minutes)
# ✅ Dependency analysis (1k tokens, 1 minute)
result = efficient_dependency_analysis("./")
```

## 🚀 EFFICIENT WORKFLODS vs EXPENSIVE AGENTS

| Task | Expensive Agent | Efficient Workflow | Token Savings | Time Savings |
|------|----------------|-------------------|-------------|-------------|
| **GitHub Research** | integration-specialist (25k tokens) | GitHub CLI (2k tokens) | **12x** | **10x** |
| **Dependency Analysis** | zen-architect (15k tokens) | Native tools (1k tokens) | **15x** | **3x** |
| **Code Quality Check** | bug-hunter (10k tokens) | make check (500 tokens) | **20x** | **2x** |
| **Security Scan** | security-guardian (25k tokens) | safety/grep (2k tokens) | **12x** | **5x** |
| **Performance Analysis** | performance-optimizer (20k tokens) | cProfile (1k tokens) | **20x** | **2x** |

## 🔧 COMMON EFFICIENCY PATTERNS

### **GitHub Repository Research**
```python
# ❌ INEFFICIENT: 25k tokens
Task(description="Research Claude-Flow repository").execute(subagent="integration-specialist")

# ✅ EFFICIENT: 2k tokens
from amplifier.token_efficiency import efficient_github_analysis
result = efficient_github_analysis("https://github.com/ruvnet/claude-flow")
```

### **Architecture Planning**
```python
# ❌ INEFFICIENT: 20k tokens
Task(description="Design system architecture").execute(subagent="zen-architect")

# ✅ EFFICIENT: 3k tokens
from amplifier.token_efficiency import TokenEfficiencyManager
manager = TokenEfficiencyManager()
best_option = manager.analyze_task_efficiency("Design system architecture", "planning")
# Use template-based approach instead
```

### **Code Implementation**
```python
# ❌ INEFFICIENT: 30k tokens
Task(description="Build API integration").execute(subagent="modular-builder")

# ✅ EFFICIENT: 5k tokens
from amplifier.token_efficiency import efficient_code_check
# Check existing implementations first, only generate what's needed
```

## 🎯 DECISION MATRIX

### **Use Native Tools When:**
- ✅ Task is routine (git operations, file analysis)
- ✅ Well-established CLI tools exist
- ✅ Data is structured and accessible
- ✅ Repetitive task with patterns

### **Use Efficient Workflows When:**
- ✅ Task needs analysis but not creative design
- ✅ Multiple steps with clear patterns
- ✅ Can be automated with scripts
- ✅ Results are predictable and measurable

### **Use Agents ONLY When:**
- ✅ Task requires genuine creativity or complex reasoning
- ✅ Multiple conflicting requirements need synthesis
- ✅ Domain expertise beyond standard patterns
- ✅ Task has high strategic importance
- ✅ Cost-benefit justifies token expenditure

## 💰 TOKEN CALCULATOR

### **Before Using Agent:**
```python
# Calculate estimated token cost
estimated_tokens = agent_task.estimate_tokens()
alternative_tokens = efficient_workflow.estimate_tokens()

if estimated_tokens > alternative_tokens * 10:
    print(f"⚠️ EXPENSIVE AGENT: {estimated_tokens:,} tokens vs {alternative_tokens:,} tokens")
    print("Consider efficient alternative")
```

### **Track Token Usage:**
```python
from amplifier.token_efficiency import efficiency_orchestrator

report = efficiency_orchestrator.get_efficiency_report()
print(f"💰 Tokens saved: {report['token_savings']:,}")
print(f"⚡ Tasks processed: {report['tasks_processed']}")
print(f"📈 Efficiency score: {report['efficiency_score']}%")
```

## 🔧 INTEGRATION WITH EXISTING TOOLS

### **Make Commands**
```bash
# Add efficiency check to Makefile
check-efficiency:
	@echo "🔧 Checking token efficiency before check..."
	@python -c "from amplifier.token_efficiency import check_token_efficiency_first; check_token_efficiency_first('Run code quality checks')"
	@$(MAKE) check
```

### **GitHub Actions**
```yaml
# Add efficiency check to workflows
- name: Token Efficiency Check
  run: |
    python -c "from amplifier.token_efficiency import check_token_efficiency_first; check_efficiency_first('GitHub Actions validation')"
    echo "✅ Token-efficient approach validated"
```

### **Development Workflow**
```python
# Wrap expensive operations with efficiency check
def expensive_operation(task_description):
    from amplifier.token_efficiency import check_token_efficiency_first

    is_efficient, recommendation = check_token_efficiency_first(task_description)
    if not is_efficient:
        print(f"⚠️ {recommendation}")
        return None

    # Proceed with expensive operation
    return perform_expensive_operation()
```

## 📊 SUCCESS METRICS

### **Target Efficiency Goals:**
- **Token Reduction**: 80-90% reduction vs. agent-only approach
- **Time Savings**: 5-10x faster execution for common tasks
- **Quality Maintenance**: Same or better results with native tools
- **Cost Optimization**: 10-20x cost reduction for routine operations

### **Monitoring:**
```python
# Track efficiency over time
efficiency_score = efficiency_orchestrator.get_efficiency_report()
if efficiency_score['efficiency_score'] < 80:
    print("⚠️ Token efficiency dropping - review workflows")
```

## 🎯 IMMEDIATE ACTIONS

### **1. Always Check First**
```python
from amplifier.token_efficiency import check_token_efficiency_first
check_efficiency_first("Your task description here")
```

### **2. Use Efficient Workflows**
```python
from amplifier.token_efficiency import efficient_github_analysis, efficient_dependency_analysis
# Replace expensive agent calls
```

### **3. Track Token Savings**
```python
from amplifier.token_efficiency import efficiency_orchestrator
print(efficiency_orchestrator.get_efficiency_report())
```

---

**REMEMBER**: Every token saved is a token we can use for genuine creative work that actually needs LLM assistance!

**PRINCIPLE**: Use native tools for patterns, agents for creativity. 🎯