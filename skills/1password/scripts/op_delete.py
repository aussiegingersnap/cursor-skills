#!/usr/bin/env python3
"""
Delete items from 1Password.

Usage:
    python3 op_delete.py --vault "Vault" --item "Item Name"
    python3 op_delete.py --id "item-id"
    python3 op_delete.py --vault "Vault" --item "Item Name" --force

Options:
    --vault <name>        Vault name or ID
    --item <name>         Item name or title
    --id <id>             Item ID (alternative to --vault/--item)
    --archive             Archive instead of delete (can be restored)
    --force               Permanently delete without confirmation prompt
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
        return False, "", "1Password CLI not found"
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def get_item_info(vault: str = None, item: str = None, item_id: str = None) -> tuple[bool, dict, str]:
    """Get item info before deletion for confirmation."""
    args = ["item", "get", "--format", "json"]
    
    if item_id:
        args.append(item_id)
    elif vault and item:
        args.extend([item, "--vault", vault])
    else:
        return False, {}, "Specify either --id or --vault and --item"
    
    success, output, error = run_op_command(args)
    
    if not success:
        return False, {}, error
    
    try:
        item_data = json.loads(output) if output else {}
        return True, item_data, ""
    except json.JSONDecodeError:
        return False, {}, "Failed to parse item data"


def delete_item(
    vault: str = None,
    item: str = None,
    item_id: str = None,
    archive: bool = False
) -> tuple[bool, str]:
    """Delete or archive an item."""
    args = ["item", "delete"]
    
    if item_id:
        args.append(item_id)
    elif vault and item:
        args.extend([item, "--vault", vault])
    else:
        return False, "Specify either --id or --vault and --item"
    
    if archive:
        args.append("--archive")
    
    success, output, error = run_op_command(args)
    
    if not success:
        return False, error
    
    return True, "Item deleted successfully" if not archive else "Item archived successfully"


def main():
    parser = argparse.ArgumentParser(description="Delete 1Password items")
    parser.add_argument("--vault", type=str, help="Vault name or ID")
    parser.add_argument("--item", type=str, help="Item name or title")
    parser.add_argument("--id", type=str, dest="item_id", help="Item ID")
    parser.add_argument("--archive", action="store_true", help="Archive instead of delete")
    parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    args = parser.parse_args()
    
    # Validate
    if not args.item_id and not (args.vault and args.item):
        parser.error("Specify --id or --vault and --item")
    
    # Get item info first
    success, item_info, error = get_item_info(
        vault=args.vault,
        item=args.item,
        item_id=args.item_id
    )
    
    if not success:
        print(json.dumps({"error": f"Item not found: {error}"}), file=sys.stderr)
        sys.exit(1)
    
    item_title = item_info.get("title", "Unknown")
    item_vault = item_info.get("vault", {}).get("name", "Unknown")
    item_id = item_info.get("id", "")
    
    # Confirm deletion (unless --force)
    if not args.force:
        action = "archive" if args.archive else "delete"
        print(json.dumps({
            "warning": f"About to {action} item",
            "item": {
                "id": item_id,
                "title": item_title,
                "vault": item_vault
            },
            "hint": f"Run with --force to confirm {action}"
        }, indent=2))
        sys.exit(0)
    
    # Perform deletion
    success, message = delete_item(
        vault=args.vault,
        item=args.item,
        item_id=args.item_id,
        archive=args.archive
    )
    
    if not success:
        print(json.dumps({"error": message}), file=sys.stderr)
        sys.exit(1)
    
    result = {
        "success": True,
        "action": "archived" if args.archive else "deleted",
        "item": {
            "id": item_id,
            "title": item_title,
            "vault": item_vault
        }
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
