#!/usr/bin/env python3
"""
Verify 1Password CLI installation and authentication status.

Usage:
    python3 op_check.py [--json]

Options:
    --json    Output results as JSON
"""

import subprocess
import sys
import json
import shutil


def run_op_command(args: list[str]) -> tuple[bool, str]:
    """Run an op command and return success status and output."""
    try:
        result = subprocess.run(
            ["op"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, "1Password CLI not found"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_cli_installed() -> tuple[bool, str]:
    """Check if 1Password CLI is installed."""
    if shutil.which("op") is None:
        return False, "Not installed"
    
    success, output = run_op_command(["--version"])
    if success:
        return True, output
    return False, "Unable to get version"


def check_authenticated() -> tuple[bool, str, list[dict]]:
    """Check authentication status and return account info."""
    success, output = run_op_command(["account", "list", "--format", "json"])
    
    if not success:
        return False, "Not authenticated", []
    
    try:
        accounts = json.loads(output) if output else []
        if not accounts:
            return False, "No accounts configured", []
        return True, f"{len(accounts)} account(s)", accounts
    except json.JSONDecodeError:
        return False, "Invalid response", []


def check_vaults() -> tuple[bool, int, list[dict]]:
    """Check accessible vaults."""
    success, output = run_op_command(["vault", "list", "--format", "json"])
    
    if not success:
        return False, 0, []
    
    try:
        vaults = json.loads(output) if output else []
        return True, len(vaults), vaults
    except json.JSONDecodeError:
        return False, 0, []


def main():
    output_json = "--json" in sys.argv
    
    results = {
        "cli_installed": False,
        "cli_version": None,
        "authenticated": False,
        "accounts": [],
        "vaults_accessible": False,
        "vault_count": 0,
        "vaults": [],
        "ready": False
    }
    
    # Check CLI installation
    installed, version = check_cli_installed()
    results["cli_installed"] = installed
    results["cli_version"] = version if installed else None
    
    if not installed:
        if output_json:
            print(json.dumps(results, indent=2))
        else:
            print("❌ 1Password CLI not installed")
            print("\nInstall with:")
            print("  brew install --cask 1password-cli  # macOS")
            print("  # or download from https://1password.com/downloads/command-line")
        sys.exit(1)
    
    # Check authentication
    auth_ok, auth_msg, accounts = check_authenticated()
    results["authenticated"] = auth_ok
    results["accounts"] = accounts
    
    if not auth_ok:
        if output_json:
            print(json.dumps(results, indent=2))
        else:
            print(f"✅ 1Password CLI installed: {version}")
            print(f"❌ Authentication: {auth_msg}")
            print("\nAuthenticate with:")
            print("  op account add    # Add account")
            print("  op signin         # Sign in")
            print("\nFor automation, set:")
            print("  export OP_SERVICE_ACCOUNT_TOKEN='your-token'")
        sys.exit(1)
    
    # Check vaults
    vaults_ok, vault_count, vaults = check_vaults()
    results["vaults_accessible"] = vaults_ok
    results["vault_count"] = vault_count
    results["vaults"] = [{"id": v.get("id"), "name": v.get("name")} for v in vaults]
    results["ready"] = True
    
    if output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"✅ 1Password CLI installed: {version}")
        
        account_names = [a.get("email", a.get("url", "unknown")) for a in accounts]
        print(f"✅ Authenticated as: {', '.join(account_names)}")
        
        print(f"✅ Vaults accessible: {vault_count}")
        if vaults:
            for v in vaults[:5]:  # Show first 5
                print(f"   - {v.get('name')}")
            if len(vaults) > 5:
                print(f"   ... and {len(vaults) - 5} more")
        
        print("\n🎉 1Password CLI is ready to use!")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
