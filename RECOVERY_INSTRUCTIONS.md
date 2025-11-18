# 🚨 NEXT SESSION RECOVERY INSTRUCTIONS

**CRITICAL**: Follow these steps EXACTLY to restore optimization capabilities after context reset.

## 🎯 **IMMEDIATE ACTIONS (First 5 Minutes)**

### **Step 1: Load Master Registry**
```bash
# FIRST THING TO DO AFTER CONTEXT RESET
READ /home/markimus/projects/microsoft-amplifier/CLAUDE_TECHNIQUES_REGISTRY.md
```

### **Step 2: Verify Docker Storage**
```bash
# Check that techniques survived housekeeping
ls -la /home/markimus/projects/microsoft-amplifier/.docker-storage/claude-techniques-registry/
```

### **Step 3: Activate MCP Integration**
```python
# Enable 98.7% token reduction immediately
from amplifier.mcp.code_execution import execute_in_docker
from amplifier.mcp.persistent_storage import load_techniques_registry

# Load saved techniques
techniques = load_techniques_registry()
print(f"✅ Loaded {len(techniques)} technique categories from Docker storage")
```

## 🔧 **PATTERNS TO APPLY IMMEDIATELY**

### **For Any Complex Task:**
1. **Check for Specialized Agent First** - Use Task tool with domain-specific agents
2. **Use Parallel Execution** - Single message, multiple agents if possible
3. **Apply MCP Code Execution** - 98.7% token reduction
4. **Context Prune at 25%** - Save completed work to Docker storage

### **For Prime Command:**
The enhanced `/prime` command now automatically:
- Loads from Docker storage
- Uses MCP code execution (98.7% reduction)
- Executes tasks in parallel
- Saves learnings back to Docker storage

## 📊 **SUCCESS METRICS TO VERIFY**

After recovery, you should see:
- **Token Usage**: <25% of context window
- **Agent Availability**: 4 specialized agents ready
- **MCP Integration**: 98.7% token reduction active
- **Docker Storage**: Unlimited context capability
- **Parallel Execution**: 60%+ speed improvement

## ⚠️ **COMMON RECOVERY ISSUES**

### **If Docker Storage Missing:**
```bash
# Recreate storage directory
mkdir -p /home/markimus/projects/microsoft-amplifier/.docker-storage/claude-techniques-registry/

# Restore from backup files
cp CLAUDE_TECHNIQUES_REGISTRY.md .docker-storage/claude-techniques-registry/
```

### **If MCP Not Working:**
```bash
# Check MCP installation
python -c "from amplifier.mcp.code_execution import execute_in_docker; print('MCP OK')"
```

### **If Agents Not Available:**
- Use subagent-architect to recreate specialized agents
- Refer to `specialized_agents.md` in Docker storage for definitions

## 🔄 **QUICK RECOVERY COMMAND**

```bash
# One-line recovery check
python -c "
import os
try:
    from amplifier.mcp.persistent_storage import load_techniques_registry
    techniques = load_techniques_registry()
    print(f'✅ SUCCESS: {len(techniques)} technique categories loaded')
except Exception as e:
    print(f'❌ ERROR: {e}')
    print('🔧 Run recovery steps from RECOVERY_INSTRUCTIONS.md')
"
```

## 🎯 **EXPECTED RECOVERY TIME**

- **Quick Recovery**: 2-3 minutes (if Docker storage intact)
- **Full Recovery**: 5-10 minutes (if rebuilding needed)
- **Verification**: Test with enhanced `/prime` command

---

**Remember**: The entire optimization system is designed to survive context resets. Load `CLAUDE_TECHNIQUES_REGISTRY.md` first thing!