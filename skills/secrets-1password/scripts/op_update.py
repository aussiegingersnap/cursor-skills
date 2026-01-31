#!/usr/bin/env python3
"""
Update existing secrets in 1Password.

Usage:
    python3 op_update.py --vault "Vault" --item "Item Name" --password "newpassword"
    python3 op_update.py --vault "Vault" --item "Item Name" --field "key=newvalue"
    python3 op_update.py --id "item-id" --username "newuser"

Options:
    --vault <name>        Vault name or ID
    --item <name>         Item name or title
    --id <id>             Item ID (alternative to --vault/--item)
    --username <user>     Update username
    --password <pass>     Update password
    --url <url>           Update URL
    --field <key=value>   Update or add custom field (can be repeated)
    --generate            Generate new random password
    --title <title>       Update item title
    --tags <tags>         Update tags (comma-separated)
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


def update_item(
    vault: str = None,
    item: str = None,
    item_id: str = None,
    username: str = None,
    password: str = None,
    url: str = None,
    fields: list[str] = None,
    generate_password: bool = False,
    title: str = None,
    tags: str = None
) -> tuple[bool, dict, str]:
    """Update an existing item in 1Password."""
    
    args = ["item", "edit", "--format", "json"]
    
    # Identify item
    if item_id:
        args.append(item_id)
    elif vault and item:
        args.extend([item, "--vault", vault])
    else:
        return False, {}, "Specify either --id or --vault and --item"
    
    # Generate password flag
    if generate_password:
        args.append("--generate-password")
    
    # Update title
    if title:
        args.extend(["--title", title])
    
    # Update tags
    if tags:
        args.extend(["--tags", tags])
    
    # Build field updates
    field_updates = []
    
    if username:
        field_updates.append(f"username={username}")
    
    if password and not generate_password:
        field_updates.append(f"password={password}")
    
    if url:
        field_updates.append(f"url={url}")
    
    # Add custom fields
    if fields:
        for field in fields:
            if "[" not in field and "=" in field:
                key, value = field.split("=", 1)
                field_updates.append(f"{key}[text]={value}")
            else:
                field_updates.append(field)
    
    # Must have something to update
    if not field_updates and not generate_password and not title and not tags:
        return False, {}, "No updates specified"
    
    args.extend(field_updates)
    
    success, output, error = run_op_command(args)
    
    if not success:
        return False, {}, error
    
    try:
        item_data = json.loads(output) if output else {}
        return True, item_data, ""
    except json.JSONDecodeError as e:
        return False, {}, f"Failed to parse response: {e}"


def main():
    parser = argparse.ArgumentParser(description="Update 1Password items")
    parser.add_argument("--vault", type=str, help="Vault name or ID")
    parser.add_argument("--item", type=str, help="Item name or title")
    parser.add_argument("--id", type=str, dest="item_id", help="Item ID")
    parser.add_argument("--username", type=str, help="Update username")
    parser.add_argument("--password", type=str, help="Update password")
    parser.add_argument("--url", type=str, help="Update URL")
    parser.add_argument("--field", type=str, action="append", dest="fields", help="Update field (key=value)")
    parser.add_argument("--generate", action="store_true", help="Generate new password")
    parser.add_argument("--title", type=str, help="Update item title")
    parser.add_argument("--tags", type=str, help="Update tags (comma-separated)")
    
    args = parser.parse_args()
    
    # Validate
    if not args.item_id and not (args.vault and args.item):
        parser.error("Specify --id or --vault and --item")
    
    success, item, error = update_item(
        vault=args.vault,
        item=args.item,
        item_id=args.item_id,
        username=args.username,
        password=args.password,
        url=args.url,
        fields=args.fields,
        generate_password=args.generate,
        title=args.title,
        tags=args.tags
    )
    
    if not success:
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(1)
    
    # Output updated item info (without secrets)
    result = {
        "success": True,
        "id": item.get("id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "vault": item.get("vault", {}).get("name"),
        "updated_at": item.get("updated_at")
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
