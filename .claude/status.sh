#!/bin/bash
# Claude Code Status Command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/status_enhancer.py" "$@"