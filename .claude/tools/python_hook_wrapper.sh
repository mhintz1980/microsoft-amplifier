#!/bin/bash
# Universal Python Hook Wrapper for Claude Code
# Ensures hooks execute in the correct Python environment with comprehensive error handling

set -euo pipefail

# Configuration
SCRIPT_NAME="$(basename "$0")"
LOG_FILE=".claude/logs/hook_execution.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure log directory exists
mkdir -p "$(dirname "$PROJECT_ROOT/$LOG_FILE")"

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] [$SCRIPT_NAME] $message" | tee -a "$PROJECT_ROOT/$LOG_FILE"
}

# Error handling
error_exit() {
    log_message "ERROR" "$1"
    echo "❌ Hook execution failed: $1" >&2
    exit 1
}

# Python environment detection
find_python() {
    # Try virtual environment first
    if [[ -f "$PROJECT_ROOT/.venv/bin/python" ]]; then
        echo "$PROJECT_ROOT/.venv/bin/python"
        return 0
    fi

    # Try alternative venv location
    if [[ -f "$PROJECT_ROOT/venv/bin/python" ]]; then
        echo "$PROJECT_ROOT/venv/bin/python"
        return 0
    fi

    # Try system python3
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
        return 0
    fi

    # Try system python
    if command -v python >/dev/null 2>&1; then
        echo "python"
        return 0
    fi

    error_exit "Python interpreter not found"
}

# Set environment variables
setup_environment() {
    export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

    # Add virtual environment to PATH if available
    if [[ -f "$PROJECT_ROOT/.venv/bin/python" ]]; then
        export PATH="$PROJECT_ROOT/.venv/bin:$PATH"
    fi
}

# Main execution
main() {
    log_message "INFO" "Starting hook execution"

    # Validate arguments
    if [[ $# -lt 1 ]]; then
        error_exit "Usage: $0 <python_script> [args...]"
    fi

    local python_script="$1"
    shift
    local script_args=("$@")

    # Validate script exists
    if [[ ! -f "$SCRIPT_DIR/$python_script" ]]; then
        error_exit "Python script not found: $SCRIPT_DIR/$python_script"
    fi

    # Find Python interpreter
    local python_cmd
    python_cmd=$(find_python)
    log_message "INFO" "Using Python: $python_cmd"

    # Set up environment
    setup_environment
    log_message "INFO" "Environment: CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR"

    # Execute the Python script
    log_message "INFO" "Executing: $python_cmd $SCRIPT_DIR/$python_script ${script_args[*]}"

    if "$python_cmd" "$SCRIPT_DIR/$python_script" "${script_args[@]}"; then
        log_message "INFO" "Hook execution completed successfully"
        exit 0
    else
        local exit_code=$?
        log_message "ERROR" "Python script failed with exit code: $exit_code"
        # For Stop hooks, don't exit with error to avoid blocking Claude Code
        if [[ "$python_script" == *"hook_stop"* ]]; then
            log_message "INFO" "Stop hook failed but exiting successfully to avoid blocking"
            exit 0
        else
            error_exit "Python script execution failed (exit code: $exit_code)"
        fi
    fi
}

# Execute main function
main "$@"