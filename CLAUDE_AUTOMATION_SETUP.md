# Claude Code Action Setup Guide for Microsoft Amplifier

This guide walks you through setting up GitHub Actions automation with Claude Code Action for the Microsoft Amplifier project.

## 🚀 Overview

Microsoft Amplifier now includes comprehensive GitHub Actions automation powered by Claude Code Action. This setup provides:

- **Intelligent Mode Detection** - Automatically determines optimal Claude execution mode
- **Multi-Method Authentication** - Support for GitHub Apps, personal tokens, and OIDC
- **Code Review Automation** - Automated code reviews with contextual awareness
- **Issue Automation** - Intelligent issue handling and triage
- **Development Workflow** - Comprehensive CI/CD with testing and validation
- **Security Scanning** - Automated security analysis and vulnerability detection
- **Performance Monitoring** - Performance analysis and optimization recommendations

## 📋 Prerequisites

### Required Secrets

Configure these secrets in your GitHub repository settings:

#### For GitHub App Authentication (Recommended)
```
CLAUDE_APP_ID=your_github_app_id
CLAUDE_APP_PRIVATE_KEY=your_github_app_private_key
```

#### For Anthropic API Access
```
ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### Optional Cloud Provider Secrets

**AWS Bedrock:**
```
AWS_ROLE_ARN=arn:aws:iam::account:role/YourRole
AWS_REGION=us-west-2
```

**Google Vertex AI:**
```
GCP_WORKLOAD_IDENTITY_PROVIDER=projects/PROJECT_ID/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
GCP_SERVICE_ACCOUNT=your-service-account@PROJECT.iam.gserviceaccount.com
```

### Required Permissions

Your GitHub Actions need these permissions:

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  packages: write
  id-token: write  # Required for OIDC
```

## 🔧 Setup Instructions

### 1. Create GitHub App (Recommended)

1. Go to your GitHub repository Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Configure the app:
   ```
   App name: Microsoft Amplifier Claude Assistant
   Homepage URL: https://github.com/your-org/microsoft-amplifier
   Webhook URL: https://github.com/github-apps/webhook
   Webhook secret: your_webhook_secret
   ```
4. Set permissions:
   ```
   Contents: Read & Write
   Pull requests: Read & Write
   Issues: Read & Write
   Metadata: Read
   ```
5. Set "Where can this be installed" to "Only on this account"
6. Generate and download private key
7. Install the app on your repository
8. Note the App ID and save the private key as repository secrets

### 2. Configure Repository Secrets

Go to your repository Settings → Secrets and variables → Actions and add:

```bash
# Required
CLAUDE_APP_ID=your_app_id_here
CLAUDE_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
[Your private key content]
-----END RSA PRIVATE KEY-----
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key-here

# Optional for cloud providers
AWS_ROLE_ARN=arn:aws:iam::account:role/YourRole
AWS_REGION=us-west-2
GCP_WORKLOAD_IDENTITY_PROVIDER=projects/PROJECT/locations/global/workloadIdentityPools/POOL/providers/PROVIDER
GCP_SERVICE_ACCOUNT=service@PROJECT.iam.gserviceaccount.com
```

### 3. Enable Workflows

The workflows are automatically enabled when you push to the main branch. No additional setup needed.

## 🎯 Available Workflows

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch
- Comments with `/claude-*` commands

**Features:**
- Intelligent mode detection based on context
- Multi-environment testing (Ubuntu, macOS)
- Code quality checks with `make check`
- Comprehensive test suite
- Claude Code integration for intelligent assistance
- Security scanning
- Performance monitoring
- Automated releases

**Usage:**
```bash
# Trigger manually
gh workflow run ci-cd.yml --field claude_mode=review --field trigger_comment="Please review recent changes"

# Trigger with comment
/claude-review
/claude-fix
/claude-test
/claude-docs
```

### 2. Code Review Automation (`code-review.yml`)

**Triggers:**
- Pull request creation and updates
- Comments with `/review-*` commands
- Manual workflow dispatch

**Features:**
- Intelligent review type detection
- Comprehensive code analysis
- Security-focused reviews
- Performance analysis
- Architecture review
- Quick review mode
- Automatic labeling and follow-up

**Usage:**
```bash
# Review commands
/review-comprehensive
/review-security
/review-performance
/review-architecture
/review-quick
/review path/to/file.py
```

### 3. Issue Automation (`issue-automation.yml`)

**Triggers:**
- Issue creation and updates
- Issue comments
- Daily schedule for maintenance
- Manual workflow dispatch

**Features:**
- Automatic issue triage
- Intelligent classification
- Priority assessment
- Duplicate detection
- Progress tracking
- Backlog grooming
- Milestone management

**Usage:**
```bash
# Issue commands
/claude-help
/claude-diagnose
/claude-suggest
/claude-status
```

### 4. Development Workflow (`development-workflow.yml`)

**Triggers:**
- Push to any branch
- Pull requests
- Manual workflow dispatch
- Nightly schedule

**Features:**
- Configurable workflow types (quick, integration, security, performance)
- Parallel testing matrix
- Integration testing
- Security scanning with Claude
- Performance analysis
- Build and packaging
- Comprehensive reporting

**Usage:**
```bash
# Trigger specific workflow type
gh workflow run development-workflow.yml --field workflow_type=security
gh workflow run development-workflow.yml --field workflow_type=performance
```

### 5. Authentication Setup (`authentication.yml`)

**Triggers:**
- Workflow call from other workflows
- Manual workflow dispatch

**Features:**
- Multi-method authentication support
- GitHub App authentication
- OIDC for AWS and GCP
- Personal token support
- Service account authentication
- Connection testing and validation

## 🤖 Claude Commands

### In Pull Requests
```bash
/claude              # General assistance
/claude-review       # Comprehensive review
/claude-fix         # Fix identified issues
/claude-test        # Help with testing
/claude-docs        # Documentation assistance
/claude-diagnose    # Technical diagnosis
/claude-suggest     # Improvement suggestions
```

### In Issues
```bash
/claude-help        # Get help with Microsoft Amplifier
/claude-status      # Check issue status
/claude-progress    # Progress update
```

### Review-Specific Commands
```bash
/review-comprehensive    # Full review
/review-security        # Security-focused review
/review-performance     # Performance analysis
/review-architecture    # Architecture review
/review-quick          # Quick review
/review path/to/file   # Review specific files
```

## 📊 Configuration Options

### Claude Mode Detection

The system automatically detects the optimal mode based on:

- **Trigger Context** - PR, issue, manual trigger
- **File Changes** - Types of files modified
- **Command Usage** - Specific commands used
- **User Input** - Manual mode selection

**Available Modes:**
- `auto` - Automatic detection (default)
- `review` - Code review focused
- `fix` - Bug fixing and problem resolution
- `test` - Testing and validation
- `docs` - Documentation and guides

### Authentication Methods

**GitHub App (Recommended):**
- Most secure and flexible
- Fine-grained permissions
- Rate limit benefits
- Audit logging

**Personal Token:**
- Simple setup
- Limited permissions
- Lower rate limits

**OIDC (Cloud Providers):**
- AWS Bedrock integration
- Google Vertex AI integration
- No secret management required
- Enhanced security

### Workflow Configuration

**Workflow Types:**
- `quick` - Fast feedback, basic tests
- `integration` - Full integration testing
- `security` - Security-focused analysis
- `performance` - Performance optimization
- `full` - Comprehensive analysis

**Caching Strategy:**
- UV package manager caching
- Python virtual environment caching
- Node.js npm caching
- GitHub Actions cache optimization

## 🔍 Monitoring and Reporting

### Artifacts and Reports

Each workflow generates downloadable artifacts:

- **Test Results:** Coverage reports, test logs
- **Security Reports:** Vulnerability scans, dependency analysis
- **Performance Reports:** Benchmarks, optimization suggestions
- **Build Artifacts:** Package files, documentation

### Status Badges

Add these badges to your README:

```markdown
![CI/CD](https://github.com/your-org/microsoft-amplifier/workflows/Microsoft%20Amplifier%20CI%2FCD/badge.svg)
![Code Review](https://github.com/your-org/microsoft-amplifier/workflows/%F0%9F%A4%96%20Code%20Review%20Automation/badge.svg)
![Issue Automation](https://github.com/your-org/microsoft-amplifier/workflows/%F0%9E%AF%8E%20Issue%20Automation/badge.svg)
![Development Workflow](https://github.com/your-org/microsoft-amplifier/workflows/%F0%9F%9A%80%20Development%20Workflow/badge.svg)
```

### Progress Tracking

- **Pull Request Status:** Real-time progress updates
- **Issue Triage:** Automatic labeling and categorization
- **Workflow Results:** Comprehensive completion reports
- **Claude Responses:** Detailed analysis and recommendations

## 🛠️ Customization

### Adding New Commands

To add new Claude commands, modify the workflow files:

```yaml
# In detect-mode job
case "$COMMENT" in
  *"/claude-custom"*)
    MODE="custom"
    TRIGGER_PHRASE="/claude-custom"
    ;;
esac
```

### Custom Prompts

Modify prompt templates in workflow files:

```yaml
# Add to prompt creation
case "$MODE" in
  "custom")
    PROMPT="$PROMPT

    **Custom Analysis:**
    - Your custom instructions here
    - Specific criteria to evaluate
    - Output format requirements"
    ;;
esac
```

### Environment-Specific Configuration

Create environment-specific settings:

```yaml
# Environment variables
env:
  PRODUCTION_MODE: "${{ github.ref == 'refs/heads/main' }}"
  DEVELOPMENT_MODE: "${{ github.ref == 'refs/heads/develop' }}"
```

## 🔧 Troubleshooting

### Common Issues

**Authentication Failures:**
- Check GitHub App permissions
- Verify secret configuration
- Ensure OIDC setup is correct

**Workflow Failures:**
- Review workflow logs
- Check permissions
- Validate secret configuration

**Claude Code Issues:**
- Verify API key configuration
- Check model availability
- Review prompt syntax

### Debug Commands

```bash
# Test GitHub App authentication
gh api app

# Check workflow permissions
gh api repos/:owner/:repo/actions/permissions

# Test Claude API connection
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "messages": [{"role": "user", "content": "test"}], "max_tokens": 10}'
```

### Support Resources

- **Claude Code Documentation:** https://docs.anthropic.com/claude-code
- **GitHub Actions Documentation:** https://docs.github.com/en/actions
- **Microsoft Amplifier Repository:** https://github.com/your-org/microsoft-amplifier

## 📚 Best Practices

### Workflow Optimization

1. **Use Caching:** Enable all available caches
2. **Parallel Execution:** Run jobs in parallel when possible
3. **Fail Fast:** Configure appropriate fail-fast settings
4. **Resource Management:** Set appropriate resource limits

### Security Best Practices

1. **Use GitHub Apps:** Prefer over personal tokens
2. **OIDC Authentication:** Use for cloud provider access
3. **Secrets Management:** Never commit secrets to repository
4. **Least Privilege:** Grant minimum necessary permissions

### Claude Code Best Practices

1. **Specific Prompts:** Provide clear, specific instructions
2. **Context Awareness:** Include relevant project context
3. **Mode Selection:** Use appropriate modes for tasks
4. **Follow-up Actions:** Act on Claude's recommendations

## 🎯 Next Steps

1. **Complete Setup:** Follow all setup instructions
2. **Test Workflows:** Trigger a test workflow
3. **Monitor Results:** Review first workflow executions
4. **Customize:** Adjust configuration for your needs
5. **Optimize:** Fine-tune based on usage patterns

---

**Need Help?**
- Create an issue using the "Claude Code Assistance" template
- Use `/claude-help` in any issue or PR
- Review the troubleshooting section above

*This setup provides production-ready automation for Microsoft Amplifier with intelligent Claude Code integration.*