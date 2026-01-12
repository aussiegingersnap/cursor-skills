#!/usr/bin/env python3
"""
Create new items/secrets in 1Password.

Usage:
    python3 op_create.py --vault "Vault" --title "Item Title" --category password --password "secret"
    python3 op_create.py --vault "Vault" --title "Login" --category login --username "user" --password "pass" --url "https://example.com"
    python3 op_create.py --vault "Vault" --title "Custom" --category password --field "key=value" --field "other=data"

Options:
    --vault <name>        Vault name or ID (required)
    --title <title>       Item title (required)
    --category <type>     Item category: login, password, secure-note, api-credential, database, ssh-key (required)
    --username <user>     Username (for login category)
    --password <pass>     Password or secret value
    --url <url>           URL (for login category)
    --field <key=value>   Custom field (can be repeated)
    --generate            Generate a random password instead of specifying one
    --tags <tags>         Comma-separated tags
    --notes <text>        Notes to add to the item
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


def create_item(
    vault: str,
    title: str,
    category: str,
    username: str = None,
    password: str = None,
    url: str = None,
    fields: list[str] = None,
    generate_password: bool = False,
    tags: str = None,
    notes: str = None
) -> tuple[bool, dict, str]:
    """Create a new item in 1Password."""
    
    args = [
        "item", "create",
        "--category", category,
        "--title", title,
        "--vault", vault,
        "--format", "json"
    ]
    
    # Add generate password flag
    if generate_password:
        args.append("--generate-password")
    
    # Add tags
    if tags:
        args.extend(["--tags", tags])
    
    # Build field assignments
    field_assignments = []
    
    if username:
        field_assignments.append(f"username={username}")
    
    if password and not generate_password:
        field_assignments.append(f"password={password}")
    
    if url:
        field_assignments.append(f"url={url}")
    
    if notes:
        field_assignments.append(f"notesPlain={notes}")
    
    # Add custom fields
    if fields:
        for field in fields:
            # Handle field type syntax: fieldname[type]=value
            if "[" not in field and "=" in field:
                # Add [text] type for plain fields
                key, value = field.split("=", 1)
                field_assignments.append(f"{key}[text]={value}")
            else:
                field_assignments.append(field)
    
    # Append field assignments to args
    args.extend(field_assignments)
    
    success, output, error = run_op_command(args)
    
    if not success:
        return False, {}, error
    
    try:
        item = json.loads(output) if output else {}
        return True, item, ""
    except json.JSONDecodeError as e:
        return False, {}, f"Failed to parse response: {e}"


def main():
    parser = argparse.ArgumentParser(description="Create new 1Password items")
    parser.add_argument("--vault", type=str, required=True, help="Vault name or ID")
    parser.add_argument("--title", type=str, required=True, help="Item title")
    parser.add_argument("--category", type=str, required=True, 
                        choices=["login", "password", "secure-note", "api-credential", "database", "ssh-key"],
                        help="Item category")
    parser.add_argument("--username", type=str, help="Username")
    parser.add_argument("--password", type=str, help="Password or secret")
    parser.add_argument("--url", type=str, help="URL")
    parser.add_argument("--field", type=str, action="append", dest="fields", help="Custom field (key=value)")
    parser.add_argument("--generate", action="store_true", help="Generate random password")
    parser.add_argument("--tags", type=str, help="Comma-separated tags")
    parser.add_argument("--notes", type=str, help="Notes")
    
    args = parser.parse_args()
    
    # Validate
    if not args.password and not args.generate and args.category in ["login", "password"]:
        parser.error("Specify --password or --generate for login/password items")
    
    success, item, error = create_item(
        vault=args.vault,
        title=args.title,
        category=args.category,
        username=args.username,
        password=args.password,
        url=args.url,
        fields=args.fields,
        generate_password=args.generate,
        tags=args.tags,
        notes=args.notes
    )
    
    if not success:
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(1)
    
    # Output created item (without exposing secrets)
    result = {
        "success": True,
        "id": item.get("id"),
        "title": item.get("title"),
        "category": item.get("category"),
        "vault": item.get("vault", {}).get("name"),
        "created_at": item.get("created_at"),
        "reference": f"op://{args.vault}/{args.title}/password"
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
