#!/usr/bin/env python3
"""
Docker Model Runner CLI

Command-line interface for managing local LLM models with Docker.
Provides simple commands for model management and server operation.

Usage:
    python -m amplifier.cli.model_runner start [model_name]
    python -m amplifier.cli.model_runner stop [model_name]
    python -m amplifier.cli.model_runner list
    python -m amplifier.cli.model_runner pull [model_name]
    python -m amplifier.cli.model_runner serve [port]
    python -m amplifier.cli.model_runner chat [model_name]
"""
