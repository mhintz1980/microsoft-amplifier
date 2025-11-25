---
name: Claude Code Assistance
about: Request assistance from Claude Code for development tasks
title: '[Claude] '
labels: ['claude-assistance']
assignees: ''

---

## 🤖 Claude Code Assistance Request

This issue template helps you request assistance from Claude Code, the AI-powered development assistant integrated into Microsoft Amplifier.

### 📋 Request Type

Choose the type of assistance you need:

- [ ] **Code Review** - Review code changes, suggest improvements
- [ ] **Bug Fix** - Help identify and fix bugs or errors
- [ ] **Feature Implementation** - Implement new features or functionality
- [ ] **Testing** - Create or improve tests
- [ ] **Documentation** - Update or create documentation
- [ ] **Performance** - Optimize code performance
- [ ] **Architecture** - Review or improve architecture
- [ ] **Security** - Security review or improvements
- [ ] **General Help** - General development assistance

### 🔍 Problem Description

Please describe what you need help with:

<!--
  Be specific about:
  - What you're trying to accomplish
  - What you've already tried
  - Any error messages you're seeing
  - Expected vs actual behavior
-->

### 📁 Relevant Files

List the files or directories involved:

```text
# Example:
- amplifier/skills/core_technology/nodejs_expert_enhanced.py
- tests/test_nodejs_integration.py
- docs/ARCHITECTURE.md
```

### 🎯 Success Criteria

What does success look like for this request?

- [ ] Code compiles without errors
- [ ] Tests pass successfully
- [ ] Documentation is updated
- [ ] Performance improves
- [ ] Security vulnerability is resolved
- [ ] Other (please specify):

### 🚧 Context

Provide any additional context that would help Claude:

<!--
  Examples:
  - This is part of the 7/7 core skills framework
  - Must follow the implementation philosophy
  - Need to maintain backward compatibility
  - Should work with the virtual environment safety system
-->

### 🔧 Technical Requirements

Any specific technical requirements or constraints:

```yaml
# Example:
python_version: "3.11+"
frameworks: ["pydantic", "fastapi"]
testing: "pytest with 90%+ coverage"
performance: "sub-second response time"
security: "must pass security scan"
```

### 📚 References

Any relevant documentation, issues, or examples:

- [ ] Implementation Philosophy: `@ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- [ ] Modular Design Philosophy: `@ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- [ ] Related Issues: #
- [ ] Documentation Links:

### 🎨 Claude Instructions

For Claude Code - specific instructions or constraints:

<!--
  Examples for Claude:
  - Focus on defensive programming patterns
  - Ensure POSIX compliance
  - Follow ruthless simplicity principle
  - Maintain agent-first development approach
  - Validate with make check/test/build commands
-->

### 📊 Priority

- [ ] Critical (blocking development)
- [ ] High (important for next release)
- [ ] Medium (nice to have)
- [ ] Low (can be deferred)

---

## 🤖 Available Claude Commands

You can trigger Claude assistance using these commands in comments:

### General Commands
- `/claude` - General assistance with the current issue
- `/claude-help` - Get help with Microsoft Amplifier
- `/claude-status` - Check status of the issue

### Specific Commands
- `/claude-review` - Review code changes
- `/claude-fix` - Help fix bugs or errors
- `/claude-test` - Assist with testing
- `/claude-docs` - Help with documentation
- `/claude-diagnose` - Diagnose technical problems
- `/claude-suggest` - Provide suggestions for improvements

### Example Usage
```
@claude-code /claude-review

Please review the recent changes to the nodejs_expert_enhanced.py file and suggest improvements.
```

---

## 📋 Claude Response Template

Claude Code will respond with:

1. **Analysis** - Understanding of the request
2. **Approach** - Planned solution method
3. **Implementation** - Code changes or solutions
4. **Testing** - Verification steps
5. **Documentation** - Updated documentation if needed
6. **Next Steps** - What to do after Claude's response

---

### 🔔 Notifications

- You'll be notified when Claude responds to your request
- Claude will tag you in any comments or PR reviews
- Progress updates will be posted as comments

### ⚡ Tips for Best Results

1. **Be Specific** - Provide detailed descriptions of what you need
2. **Include Context** - Share relevant files, error messages, and background
3. **Set Clear Goals** - Define what success looks like
4. **Use Commands** - Use the `/claude-*` commands for specific requests
5. **Provide Examples** - Show expected behavior or existing patterns

---

*This issue will be processed by Claude Code, the AI-powered development assistant integrated into Microsoft Amplifier.*