#!/usr/bin/env python3
"""
Execute commands with 1Password secrets injected.

Usage:
    python3 op_run.py --env-file .env.tpl -- npm start
    python3 op_run.py --secret "API_KEY=op://Vault/Item/password" -- ./script.sh
    python3 op_run.py --secret "DB_HOST=op://Dev/DB/host" --secret "DB_PASS=op://Dev/DB/password" -- python app.py

Options:
    --env-file <file>         Path to .env template file with secret references
    --secret <KEY=ref>        Inline secret reference (can be repeated)
    --no-masking              Disable automatic secret masking in output
    --                        Separator before the command to run

Environment File Format (.env.tpl):
    DATABASE_URL=op://Development/Database/url
    API_KEY=op://Development/OpenAI/password
    SECRET_KEY=op://Development/App/secret
"""

import subprocess
import sys
import os
import json
import argparse
import tempfile


def run_with_secrets(
    command: list[str],
    env_file: str = None,
    secrets: list[str] = None,
    no_masking: bool = False
) -> tuple[int, str, str]:
    """Run a command with secrets injected from 1Password."""
    
    args = ["op", "run"]
    
    # Add env file if provided
    if env_file:
        args.extend(["--env-file", env_file])
    
    # Add no-masking flag if requested
    if no_masking:
        args.append("--no-masking")
    
    # Handle inline secrets by creating a temporary env file
    temp_env_file = None
    if secrets and not env_file:
        try:
            temp_env_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.env',
                delete=False
            )
            for secret in secrets:
                temp_env_file.write(f"{secret}\n")
            temp_env_file.close()
            args.extend(["--env-file", temp_env_file.name])
        except Exception as e:
            return 1, "", f"Failed to create temp env file: {e}"
    
    # Add command separator and command
    args.append("--")
    args.extend(command)
    
    try:
        result = subprocess.run(
            args,
            capture_output=False,  # Let output flow through to terminal
            text=True
        )
        return result.returncode, "", ""
    except FileNotFoundError:
        return 1, "", "1Password CLI not found"
    except Exception as e:
        return 1, "", str(e)
    finally:
        # Clean up temp file
        if temp_env_file and os.path.exists(temp_env_file.name):
            os.unlink(temp_env_file.name)


def validate_secret_reference(ref: str) -> bool:
    """Validate a secret reference format."""
    if not ref.startswith("op://"):
        return False
    parts = ref[5:].split("/")  # Remove "op://" prefix
    return len(parts) >= 2  # At least vault/item


def main():
    # Custom argument parsing to handle -- separator
    parser = argparse.ArgumentParser(
        description="Run commands with 1Password secrets injected",
        usage="%(prog)s [options] -- <command>"
    )
    parser.add_argument("--env-file", type=str, help="Path to .env template file")
    parser.add_argument("--secret", type=str, action="append", dest="secrets", 
                        help="Inline secret reference (KEY=op://vault/item/field)")
    parser.add_argument("--no-masking", action="store_true", help="Disable secret masking")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run")
    
    args = parser.parse_args()
    
    # Extract command (everything after --)
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    
    if not command:
        parser.error("No command specified. Use: op_run.py [options] -- <command>")
    
    # Validate inputs
    if not args.env_file and not args.secrets:
        parser.error("Specify --env-file or --secret")
    
    # Validate env file exists
    if args.env_file and not os.path.exists(args.env_file):
        print(json.dumps({"error": f"Env file not found: {args.env_file}"}), file=sys.stderr)
        sys.exit(1)
    
    # Validate secret references
    if args.secrets:
        for secret in args.secrets:
            if "=" not in secret:
                print(json.dumps({"error": f"Invalid secret format: {secret}. Use KEY=op://vault/item/field"}), file=sys.stderr)
                sys.exit(1)
            
            key, ref = secret.split("=", 1)
            if not validate_secret_reference(ref):
                print(json.dumps({"error": f"Invalid secret reference: {ref}. Use op://vault/item/field"}), file=sys.stderr)
                sys.exit(1)
    
    # Run command with secrets
    exit_code, stdout, stderr = run_with_secrets(
        command=command,
        env_file=args.env_file,
        secrets=args.secrets,
        no_masking=args.no_masking
    )
    
    if stderr:
        print(json.dumps({"error": stderr}), file=sys.stderr)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
