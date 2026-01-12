#!/usr/bin/env python3
"""
Read/retrieve secrets from 1Password.

Usage:
    python3 op_read.py --vault "Vault" --item "Item Name"
    python3 op_read.py --vault "Vault" --item "Item Name" --field password
    python3 op_read.py --id "item-id"
    python3 op_read.py --reference "op://Vault/Item/field"

Options:
    --vault <name>        Vault name or ID
    --item <name>         Item name or title
    --id <id>             Item ID (alternative to --vault/--item)
    --reference <ref>     Secret reference URI (op://vault/item/field)
    --field <name>        Get specific field value only
    --reveal              Include secret values in output (CAUTION: exposes secrets)
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


def read_by_reference(reference: str) -> tuple[bool, str, str]:
    """Read a secret by reference URI."""
    success, output, error = run_op_command(["read", reference])
    return success, output, error


def get_item(vault: str = None, item: str = None, item_id: str = None) -> tuple[bool, dict, str]:
    """Get full item details."""
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
    except json.JSONDecodeError as e:
        return False, {}, f"Failed to parse response: {e}"


def get_field_value(vault: str = None, item: str = None, item_id: str = None, field: str = None) -> tuple[bool, str, str]:
    """Get a specific field value."""
    args = ["item", "get"]
    
    if item_id:
        args.append(item_id)
    elif vault and item:
        args.extend([item, "--vault", vault])
    else:
        return False, "", "Specify either --id or --vault and --item"
    
    if field:
        args.extend(["--fields", field])
    
    success, output, error = run_op_command(args)
    return success, output, error


def redact_secrets(item: dict) -> dict:
    """Redact secret values from item for safe output."""
    redacted = item.copy()
    
    if "fields" in redacted:
        redacted_fields = []
        for field in redacted["fields"]:
            field_copy = field.copy()
            field_type = field.get("type", "")
            
            # Redact concealed/password fields
            if field_type == "CONCEALED" or field.get("purpose") == "PASSWORD":
                if "value" in field_copy:
                    field_copy["value"] = "••••••••"
                    field_copy["redacted"] = True
            
            redacted_fields.append(field_copy)
        
        redacted["fields"] = redacted_fields
    
    return redacted


def main():
    parser = argparse.ArgumentParser(description="Read secrets from 1Password")
    parser.add_argument("--vault", type=str, help="Vault name or ID")
    parser.add_argument("--item", type=str, help="Item name or title")
    parser.add_argument("--id", type=str, dest="item_id", help="Item ID")
    parser.add_argument("--reference", type=str, help="Secret reference (op://vault/item/field)")
    parser.add_argument("--field", type=str, help="Get specific field only")
    parser.add_argument("--reveal", action="store_true", help="Include secret values (CAUTION)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.reference, args.item_id, (args.vault and args.item)]):
        parser.error("Specify --reference, --id, or --vault and --item")
    
    # Read by reference
    if args.reference:
        success, value, error = read_by_reference(args.reference)
        
        if not success:
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(1)
        
        if args.reveal:
            print(json.dumps({"reference": args.reference, "value": value}, indent=2))
        else:
            print(json.dumps({
                "reference": args.reference, 
                "value": "••••••••",
                "hint": "Use --reveal to show actual value"
            }, indent=2))
        
        sys.exit(0)
    
    # Get specific field
    if args.field:
        success, value, error = get_field_value(
            vault=args.vault,
            item=args.item,
            item_id=args.item_id,
            field=args.field
        )
        
        if not success:
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(1)
        
        if args.reveal:
            print(json.dumps({"field": args.field, "value": value}, indent=2))
        else:
            print(json.dumps({
                "field": args.field,
                "value": "••••••••",
                "hint": "Use --reveal to show actual value"
            }, indent=2))
        
        sys.exit(0)
    
    # Get full item
    success, item, error = get_item(
        vault=args.vault,
        item=args.item,
        item_id=args.item_id
    )
    
    if not success:
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(1)
    
    # Output item
    if args.reveal:
        print(json.dumps(item, indent=2))
    else:
        redacted = redact_secrets(item)
        print(json.dumps(redacted, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
