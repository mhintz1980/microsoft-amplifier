# 🚀 Microsoft Amplifier Pull Request

## 📋 Description

<!--
  Describe your changes in detail.
  What does this PR do?
  What problem does it solve?
-->

## 🔗 Related Issues

<!--
  Link to any related issues or discussions.
  Use format: Closes #123, Fixes #456, Related to #789
-->

## 🧪 Testing

<!--
  Describe how you tested your changes.
  Include commands run and output if relevant.
-->

### Commands Used
```bash
make check
make test
make smoke-test
```

### Test Results
<!--
  Describe test results and any edge cases considered.
-->

## 🏗️ Architecture Impact

<!--
  How does this change affect the overall architecture?
  Does it follow the implementation philosophy?
-->

### Compliance Checklist
- [ ] **Ruthless Simplicity** - Changes are as simple as possible
- [ ] **Implementation Philosophy** - Follows `@ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- [ ] **Modular Design** - Aligns with `@ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- [ ] **Agent-First Development** - Optimized for AI agent usage
- [ ] **Defensive Programming** - Includes proper error handling
- [ ] **POSIX Compliance** - Works across platforms if applicable
- [ ] **7/7 Core Skills** - Integrates with core skills framework

## 📦 Dependencies

<!--
  List any new dependencies added or changed.
  Include version requirements.
-->

### New Dependencies
-

### Updated Dependencies
-

## 🔄 Breaking Changes

<!--
  List any breaking changes and migration steps.
-->

## 📚 Documentation

<!--
  List documentation changes included in this PR.
-->

- [ ] README updated
- [ ] API documentation updated
- [ ] Code comments added/updated
- [ ] User guide updated

## 🔐 Security

<!--
  Describe any security considerations.
  - New dependencies reviewed
  - Input validation added
  - Authentication/authorization changes
-->

### Security Checklist
- [ ] No hardcoded secrets or API keys
- [ ] Input validation implemented
- [ ] Error handling doesn't leak sensitive information
- [ ] Dependencies are up-to-date and secure
- [ ] File operations are safe

## 📈 Performance

<!--
  Describe performance impact and any optimizations.
-->

- [ ] No performance degradation
- [ ] Performance improvements implemented
- [ ] Memory usage optimized
- [ ] Response time improved

## 🔍 Code Review Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Functions and classes are properly documented
- [ ] Error handling is comprehensive
- [ ] Code is modular and reusable

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Edge cases covered
- [ ] Test coverage maintained or improved

### Integration
- [ ] Compatible with existing systems
- [ ] Make commands work correctly
- [ ] Virtual environment safety maintained
- [ ] CI/CD pipeline passes

## 📊 Claude Code Review

<!--
  Claude Code will automatically review this PR and provide feedback.
  You can trigger specific reviews using:
  - /claude-review - Comprehensive review
  - /claude-security - Security-focused review
  - /claude-performance - Performance analysis
-->

### Claude Commands Available
- `/claude-review` - Request comprehensive code review
- `/claude-fix` - Ask Claude to fix identified issues
- `/claude-test` - Request help with testing
- `/claude-docs` - Ask for documentation improvements

## 📸 Screenshots/Demo

<!--
  If applicable, include screenshots or demo links.
  For UI changes, show before/after.
-->

## 📋 Deployment Notes

<!--
  Any special considerations for deployment.
-->

- [ ] Database migrations required
- [ ] Environment variables needed
- [ ] Cache invalidation required
- [ ] Service restart required

## 🏷️ Labels

<!--
  Suggest labels for this PR.
-->

- `feature` / `bug` / `enhancement` / `documentation`
- `security` / `performance` / `testing`
- `breaking-change` (if applicable)
- `claude-reviewed` (after Claude review)

## 👥 Reviewers

<!--
  Tag specific reviewers if needed.
  @username
-->

---

## ✅ Submission Checklist

### Before Submitting
- [ ] I have read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

### After Submitting
- [ ] All CI checks pass
- [ ] Claude Code review completed
- [ ] Required approvals received
- [ ] Documentation updated
- [ ] Tests passing

---

### 🤖 Merge Requirements

This PR can be merged when:

1. ✅ All automated checks pass
2. ✅ Claude Code review completed successfully
3. ✅ At least one human approval received
4. ✅ Documentation updated (if applicable)
5. ✅ Tests passing with adequate coverage

---

*This PR template is optimized for Claude Code integration and follows Microsoft Amplifier development best practices.*