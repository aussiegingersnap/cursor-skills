#!/usr/bin/env python3
"""
List 1Password vaults and items.

Usage:
    python3 op_list.py --vaults
    python3 op_list.py --items --vault "Vault Name"
    python3 op_list.py --items --vault "Vault Name" --category login

Options:
    --vaults              List all accessible vaults
    --items               List items (requires --vault)
    --vault <name>        Vault name or ID
    --category <type>     Filter by category (login, password, etc.)
    --tags <tags>         Filter by tags (comma-separated)
    --json                Output as JSON (default)
    --table               Output as formatted table
"""

import subprocess
import sys
import json
import argparse


def run_op_command(args: list[str]) -> tuple[bool, str, str]:
    """Run an op command and return success, stdout, stderr."""
    try:
        result = subprocess.run(
            ["op"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return False, "", "1Password CLI not found. Install with: brew install --cask 1password-cli"
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def list_vaults() -> tuple[bool, list[dict], str]:
    """List all accessible vaults."""
    success, output, error = run_op_command(["vault", "list", "--format", "json"])
    
    if not success:
        return False, [], error
    
    try:
        vaults = json.loads(output) if output else []
        return True, vaults, ""
    except json.JSONDecodeError as e:
        return False, [], f"Failed to parse response: {e}"


def list_items(vault: str, category: str = None, tags: str = None) -> tuple[bool, list[dict], str]:
    """List items in a vault."""
    args = ["item", "list", "--vault", vault, "--format", "json"]
    
    if category:
        args.extend(["--categories", category])
    
    if tags:
        args.extend(["--tags", tags])
    
    success, output, error = run_op_command(args)
    
    if not success:
        return False, [], error
    
    try:
        items = json.loads(output) if output else []
        return True, items, ""
    except json.JSONDecodeError as e:
        return False, [], f"Failed to parse response: {e}"


def format_table(data: list[dict], columns: list[str]) -> str:
    """Format data as a simple table."""
    if not data:
        return "No items found."
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            val = str(row.get(col, ""))
            widths[col] = max(widths[col], len(val))
    
    # Build table
    lines = []
    
    # Header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # Rows
    for row in data:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        lines.append(line)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="List 1Password vaults and items")
    parser.add_argument("--vaults", action="store_true", help="List all vaults")
    parser.add_argument("--items", action="store_true", help="List items in a vault")
    parser.add_argument("--vault", type=str, help="Vault name or ID")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--tags", type=str, help="Filter by tags (comma-separated)")
    parser.add_argument("--json", action="store_true", default=True, help="Output as JSON (default)")
    parser.add_argument("--table", action="store_true", help="Output as table")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.vaults and not args.items:
        parser.error("Specify --vaults or --items")
    
    if args.items and not args.vault:
        parser.error("--items requires --vault")
    
    # List vaults
    if args.vaults:
        success, vaults, error = list_vaults()
        
        if not success:
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(1)
        
        if args.table:
            print(format_table(vaults, ["name", "id"]))
        else:
            print(json.dumps(vaults, indent=2))
        
        sys.exit(0)
    
    # List items
    if args.items:
        success, items, error = list_items(args.vault, args.category, args.tags)
        
        if not success:
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(1)
        
        if args.table:
            print(format_table(items, ["title", "category", "id"]))
        else:
            # Simplify output to essential fields
            simplified = [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": item.get("category"),
                    "vault": item.get("vault", {}).get("name"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at")
                }
                for item in items
            ]
            print(json.dumps(simplified, indent=2))
        
        sys.exit(0)


if __name__ == "__main__":
    main()
