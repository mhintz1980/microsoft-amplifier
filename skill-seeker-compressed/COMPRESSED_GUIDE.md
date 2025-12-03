# Skill Seeker Compressed Guide

This folder contains the essential components of the Skill Seeker project, focused on the **enhanced function** for creating high-quality AI skills from documentation.

## 📂 Contents

- **`cli/`**: Core command-line tools for scraping, enhancing, and packaging skills.
  - `doc_scraper.py`: The main scraping tool.
  - `enhance_skill.py`: AI enhancement script (requires API key).
  - `enhance_skill_local.py`: Local AI enhancement script (uses Claude Code Max).
- **`mcp/`**: Model Context Protocol server for integrating with Claude Code.
- **`configs/`**: Preset configurations for popular frameworks (React, Vue, Godot, etc.).
- **`docs/`**: Detailed documentation and guides.
- **Key Markdowns**:
  - `README.md`: Main overview.
  - `BULLETPROOF_QUICKSTART.md`: Step-by-step guide for beginners.
  - `ARCHITECTURE.md`: Technical details of the modular design.

## 🚀 How to Use the Enhanced Function

The "enhanced function" refers to the ability to use AI to analyze scraped documentation and generate a comprehensive `SKILL.md` file with real code examples and key concepts.

### Option 1: Local Enhancement (Recommended)

This method uses your existing Claude Code session (Claude Code Max) and does **not** require an API key.

1.  **Scrape and Enhance**:

    ```bash
    python3 cli/doc_scraper.py --config configs/react.json --enhance-local
    ```

    This will scrape the React docs and then automatically open a new terminal window to run the enhancement process using Claude Code.

2.  **Enhance Existing Output**:
    If you have already scraped data:
    ```bash
    python3 cli/enhance_skill_local.py output/react/
    ```

### Option 2: API-Based Enhancement

This method requires an Anthropic API key.

1.  **Set API Key**:

    ```bash
    export ANTHROPIC_API_KEY=sk-ant-...
    ```

2.  **Scrape and Enhance**:
    ```bash
    python3 cli/doc_scraper.py --config configs/react.json --enhance
    ```

## 📦 Packaging

After enhancement, package your skill for upload to Claude.ai:

```bash
python3 cli/package_skill.py output/react/
```

This creates a `.zip` file in the `output/` directory.

## 🛠️ Setup

1.  **Install Dependencies**:

    ```bash
    pip install requests beautifulsoup4
    # For MCP support:
    pip install -r mcp/requirements.txt
    ```

2.  **MCP Setup (Optional)**:
    Run `./setup_mcp.sh` to configure the MCP server for use with Claude Code.
