#!/usr/bin/env python3
"""
Simple GitHub MCP Server using GitHub CLI
Provides basic GitHub repository operations via MCP
"""

import json
import subprocess
import sys
from typing import Any


def run_github_command(args: list[str]) -> dict[str, Any]:
    """Run a GitHub CLI command and return the result"""
    try:
        cmd = ["gh"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {"success": True, "data": data}
            except json.JSONDecodeError:
                return {"success": True, "data": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_list_repos(args: dict[str, Any]) -> dict[str, Any]:
    """List repositories"""
    limit = args.get("limit", 10)
    result = run_github_command(
        ["repo", "list", "--limit", str(limit), "--json", "name,description,language,updatedAt"]
    )
    return result


def handle_repo_info(args: dict[str, Any]) -> dict[str, Any]:
    """Get repository information"""
    repo = args.get("repo")
    if not repo:
        return {"success": False, "error": "Repository name required"}

    result = run_github_command(
        ["repo", "view", repo, "--json", "name,description,language,stargazerCount,forkCount,createdAt,updatedAt"]
    )
    return result


def handle_create_issue(args: dict[str, Any]) -> dict[str, Any]:
    """Create an issue"""
    repo = args.get("repo")
    title = args.get("title")
    body = args.get("body", "")

    if not repo or not title:
        return {"success": False, "error": "Repository and title required"}

    cmd_args = ["issue", "create", "--repo", repo, "--title", title]
    if body:
        cmd_args.extend(["--body", body])

    result = run_github_command(cmd_args)
    return result


def handle_list_issues(args: dict[str, Any]) -> dict[str, Any]:
    """List issues"""
    repo = args.get("repo")
    limit = args.get("limit", 10)

    if not repo:
        return {"success": False, "error": "Repository name required"}

    result = run_github_command(
        ["issue", "list", "--repo", repo, "--limit", str(limit), "--json", "number,title,state,createdAt"]
    )
    return result


def main():
    """Main MCP server loop"""
    tools = [
        {
            "name": "list_repos",
            "description": "List GitHub repositories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of repositories to return",
                        "default": 10,
                    }
                },
            },
        },
        {
            "name": "get_repo_info",
            "description": "Get detailed information about a repository",
            "inputSchema": {
                "type": "object",
                "properties": {"repo": {"type": "string", "description": "Repository name (format: owner/repo)"}},
                "required": ["repo"],
            },
        },
        {
            "name": "create_issue",
            "description": "Create a new GitHub issue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository name (format: owner/repo)"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body/description"},
                },
                "required": ["repo", "title"],
            },
        },
        {
            "name": "list_issues",
            "description": "List issues in a repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository name (format: owner/repo)"},
                    "limit": {"type": "integer", "description": "Maximum number of issues to return", "default": 10},
                },
                "required": ["repo"],
            },
        },
    ]

    # Handle MCP protocol
    for line in sys.stdin:
        try:
            message = json.loads(line)

            if message.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "github-mcp", "version": "1.0.0"},
                    },
                }
                print(json.dumps(response))
                sys.stdout.flush()

            elif message.get("method") == "tools/list":
                response = {"jsonrpc": "2.0", "id": message.get("id"), "result": {"tools": tools}}
                print(json.dumps(response))
                sys.stdout.flush()

            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = {"success": False, "error": "Unknown tool"}

                if tool_name == "list_repos":
                    result = handle_list_repos(arguments)
                elif tool_name == "get_repo_info":
                    result = handle_repo_info(arguments)
                elif tool_name == "create_issue":
                    result = handle_create_issue(arguments)
                elif tool_name == "list_issues":
                    result = handle_list_issues(arguments)

                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
                }
                print(json.dumps(response))
                sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": message.get("id") if "message" in locals() else None,
                "error": {"code": -1, "message": str(e)},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
