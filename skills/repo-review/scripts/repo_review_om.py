#!/usr/bin/env python3
"""
Omarchy Repository Contribution Analyzer

Analyzes git repos counting meaningful lines of code contributions by author
with hackerman-themed terminal output and weekly visualization.

Usage:
    python repo_review_om.py                    # Scan local repos in ~/Code
    python repo_review_om.py --all              # Fetch & analyze all WTD-UP org repos
    python repo_review_om.py --repo URL         # Analyze a single repo from GitHub URL
    python repo_review_om.py --no-docs          # Exclude .md, .txt, etc from analysis
    python repo_review_om.py --since 2025-01-01
    python repo_review_om.py --chart            # Generate weekly dot plot
    python repo_review_om.py --output out.csv

Examples:
    python repo_review_om.py --repo https://github.com/newmanuaiprojects/newman_rcd
    python repo_review_om.py --repo git@github.com:org/repo.git --since 2025-06-01
"""

import argparse
import csv
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# HACKERMAN OMARCHY THEME COLORS (from btop current.theme)
# ═══════════════════════════════════════════════════════════════════════════════

class C:
    """Hackerman Omarchy color palette - exact btop theme colors."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # From theme - main colors
    # main_bg="#0B0C16", main_fg="#ddf7ff", title="#86a7df"
    # hi_fg="#7cf8f7", inactive_fg="#6a6e95"
    # box outlines="#4fe88f", div_line="#6a6e95"
    
    # Primary - hi_fg (bright cyan-teal)
    CYAN = "\033[38;2;124;248;247m"      # #7cf8f7 - highlights, headers
    # Title blue
    BLUE = "\033[38;2;134;167;223m"      # #86a7df - titles, accents
    # Teal/aqua from gradients
    TEAL = "\033[38;2;80;247;212m"       # #50f7d4 - secondary accent
    
    # Box outline green
    GREEN = "\033[38;2;79;232;143m"      # #4fe88f - boxes, positive values
    # For deletions - use a warm red that contrasts well
    RED = "\033[38;2;255;107;107m"       # Soft red for deletions
    # Numbers/values - bright cyan
    YELLOW = "\033[38;2;124;248;247m"    # #7cf8f7 - use cyan for numbers too
    # Authors - title blue
    MAGENTA = "\033[38;2;134;167;223m"   # #86a7df - author names
    # Main foreground
    WHITE = "\033[38;2;221;247;255m"     # #ddf7ff - primary text
    # Inactive/dim
    GRAY = "\033[38;2;106;110;149m"      # #6a6e95 - dim text, separators
    
    # Box drawing - green from theme
    BOX = "\033[38;2;79;232;143m"        # #4fe88f - box borders


class Box:
    """Unicode box-drawing characters."""
    H = "─"      # Horizontal
    V = "│"      # Vertical
    TL = "┌"     # Top-left
    TR = "┐"     # Top-right
    BL = "└"     # Bottom-left
    BR = "┘"     # Bottom-right
    LT = "├"     # Left-tee
    RT = "┤"     # Right-tee
    TT = "┬"     # Top-tee
    BT = "┴"     # Bottom-tee
    X = "┼"      # Cross


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

CODE_DIR = Path("/home/ags/Code")
DEFAULT_SINCE = "2025-01-01"
ORG_NAME = "WTD-UP"

# Global flag for excluding docs (set by --no-docs)
EXCLUDE_DOCS = False
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}

EXCLUDE_AUTHORS = [
    "gpt-engineer-app[bot]", "dependabot[bot]", "renovate[bot]",
    "github-actions[bot]", "cursor agent", "copilot",
]

EXCLUDE_PATTERNS = [
    "node_modules/*", "vendor/*", "venv/*", ".venv/*",
    "dist/*", "build/*", "coverage/*", ".next/*", "out/*",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.lock", "Gemfile.lock", "poetry.lock", "*.lock",
    "*.generated.*", "*.d.ts", "types.ts",
    "logs/*", "*.log", "temp/*", "tmp/*",
    "*.min.js", "*.min.css",
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.ico",
    "*.woff", "*.woff2", "*.ttf", "*.eot", "*.mp4", "*.mp3",
    "*.wav", "*.pdf", "*.zip", "*.tar", "*.gz",
    ".cursor/*", ".vscode/*", ".idea/*", "*.tfstate", "*.tfstate.*",
    ".bmad/*", "bmad/*", "*.excalidraw",
    "*.map", ".git/*", ".DS_Store", "Thumbs.db",
]

# Chart colors - hackerman omarchy palette
AUTHOR_COLORS = [
    "#4fe88f",  # Green (box outline)
    "#7cf8f7",  # Bright cyan (hi_fg)
    "#50f7d4",  # Teal (download)
    "#86a7df",  # Blue (title)
    "#829dd4",  # Mid blue (cpu_mid)
    "#ddf7ff",  # White (main_fg)
    "#6a6e95",  # Gray (inactive)
    "#4fe88f",  # Green repeat
    "#7cf8f7",  # Cyan repeat
    "#50f7d4",  # Teal repeat
]

# File type to work category mapping
FILE_CATEGORIES = {
    # Frontend
    ".tsx": "frontend", ".jsx": "frontend", ".vue": "frontend", ".svelte": "frontend",
    ".css": "frontend", ".scss": "frontend", ".sass": "frontend", ".less": "frontend",
    ".html": "frontend", ".htm": "frontend",
    # Backend
    ".py": "backend", ".go": "backend", ".rs": "backend", ".java": "backend",
    ".rb": "backend", ".php": "backend", ".cs": "backend", ".cpp": "backend",
    ".c": "backend", ".h": "backend",
    # JavaScript/TypeScript (context-dependent, default to fullstack)
    ".ts": "fullstack", ".js": "fullstack", ".mjs": "fullstack", ".cjs": "fullstack",
    # Database/Data
    ".sql": "database", ".prisma": "database", ".graphql": "database", ".gql": "database",
    # Config/DevOps
    ".yml": "config", ".yaml": "config", ".toml": "config", ".ini": "config",
    ".json": "config", ".env": "config", ".conf": "config",
    ".tf": "infra", ".tfvars": "infra", ".hcl": "infra",
    ".dockerfile": "infra", ".dockerignore": "infra",
    # Documentation (can be excluded with --no-docs)
    ".md": "docs", ".mdx": "docs", ".rst": "docs", ".txt": "docs",
    # Shell/Scripts
    ".sh": "scripts", ".bash": "scripts", ".zsh": "scripts", ".fish": "scripts",
    ".ps1": "scripts", ".bat": "scripts", ".cmd": "scripts",
    # Testing
    ".test.ts": "testing", ".test.js": "testing", ".spec.ts": "testing", ".spec.js": "testing",
    ".test.tsx": "testing", ".test.jsx": "testing",
}

CATEGORY_LABELS = {
    "frontend": ("Frontend", C.CYAN),
    "backend": ("Backend", C.GREEN),
    "fullstack": ("JS/TS", C.TEAL),
    "database": ("Database", C.MAGENTA),
    "config": ("Config", C.GRAY),
    "infra": ("Infra", C.BLUE),
    "docs": ("Docs", C.WHITE),
    "scripts": ("Scripts", C.YELLOW),
    "testing": ("Testing", C.RED),
    "other": ("Other", C.GRAY),
}


def get_file_category(filepath: str) -> str:
    """Determine work category from file extension."""
    basename = os.path.basename(filepath).lower()
    
    # Check for test files first (special patterns)
    if ".test." in basename or ".spec." in basename or "_test." in basename:
        return "testing"
    if basename == "dockerfile" or basename.startswith("dockerfile."):
        return "infra"
    
    # Get extension
    _, ext = os.path.splitext(filepath.lower())
    return FILE_CATEGORIES.get(ext, "other")


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_term_width() -> int:
    """Get terminal width, default to 100."""
    return shutil.get_terminal_size((100, 24)).columns


def fmt_num(n: int, width: int = 10) -> str:
    """Format number with thousands separator, right-aligned."""
    return f"{n:>{width},}"


def progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a mini progress bar."""
    if total == 0:
        return f"{C.GRAY}{'░' * width}{C.RESET}"
    pct = min(current / total, 1.0)
    filled = int(width * pct)
    return f"{C.TEAL}{'█' * filled}{C.GRAY}{'░' * (width - filled)}{C.RESET}"


# ═══════════════════════════════════════════════════════════════════════════════
# GIT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def run_cmd(cmd: list[str], cwd: str = None) -> tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def discover_local_repos(base_dir: Path) -> list[dict]:
    repos = []
    if not base_dir.exists():
        return repos
    for item in base_dir.iterdir():
        if item.is_dir() and (item / ".git").exists():
            repos.append({"name": item.name, "path": item})
    return sorted(repos, key=lambda x: x["name"].lower())


def fetch_org_repos(base_dir: Path) -> list[dict]:
    """Fetch all repos from WTD-UP GitHub org, clone missing ones."""
    import json
    
    print(f"{C.CYAN}Fetching repos from {ORG_NAME} organization...{C.RESET}")
    
    cmd = ["gh", "repo", "list", ORG_NAME, "--limit", "100", "--json", "name,sshUrl,url"]
    rc, stdout, stderr = run_cmd(cmd)
    
    if rc != 0:
        print(f"{C.RED}Error fetching repos: {stderr}{C.RESET}")
        print(f"{C.GRAY}Make sure 'gh' CLI is installed and authenticated{C.RESET}")
        sys.exit(1)
    
    org_repos = json.loads(stdout)
    print(f"{C.GREEN}Found {len(org_repos)} repos in {ORG_NAME}{C.RESET}")
    
    repos = []
    skipped = []
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for repo_info in org_repos:
        repo_name = repo_info["name"]
        repo_path = base_dir / repo_name
        
        if repo_path.exists() and (repo_path / ".git").exists():
            # Fetch latest
            print(f"  {C.GRAY}├─{C.RESET} {C.WHITE}{repo_name}{C.RESET} {C.GRAY}(fetch){C.RESET}")
            run_cmd(["git", "fetch", "--all"], cwd=str(repo_path))
            repos.append({"name": repo_name, "path": repo_path})
        else:
            # Try HTTPS first (works with gh auth), then SSH
            https_url = f"https://github.com/{ORG_NAME}/{repo_name}.git"
            ssh_url = repo_info.get("sshUrl", "")
            
            print(f"  {C.TEAL}├─{C.RESET} {C.WHITE}{repo_name}{C.RESET} {C.TEAL}(clone){C.RESET}", end="", flush=True)
            
            # Try HTTPS first
            rc, _, stderr = run_cmd(["git", "clone", "--quiet", https_url, str(repo_path)])
            
            if rc != 0 and ssh_url:
                # Fallback to SSH
                rc, _, stderr = run_cmd(["git", "clone", "--quiet", ssh_url, str(repo_path)])
            
            if rc != 0:
                print(f" {C.RED}✗ skipped{C.RESET}")
                skipped.append(repo_name)
                continue
            
            print(f" {C.GREEN}✓{C.RESET}")
            repos.append({"name": repo_name, "path": repo_path})
    
    if skipped:
        print(f"\n{C.GRAY}Skipped {len(skipped)} repos (no access): {', '.join(skipped[:5])}{C.RESET}")
    
    return sorted(repos, key=lambda x: x["name"].lower())


def parse_repo_url(url: str) -> tuple[str, str, str]:
    """
    Parse a GitHub URL into (owner, repo_name, clone_url).
    Supports:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - git@github.com:owner/repo.git
    """
    # SSH format: git@github.com:owner/repo.git
    ssh_match = re.match(r'^git@github\.com:([^/]+)/(.+?)(?:\.git)?$', url)
    if ssh_match:
        owner, repo = ssh_match.groups()
        return owner, repo, url if url.endswith('.git') else f"{url}.git"
    
    # HTTPS format: https://github.com/owner/repo[.git]
    https_match = re.match(r'^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$', url)
    if https_match:
        owner, repo = https_match.groups()
        clone_url = f"https://github.com/{owner}/{repo}.git"
        return owner, repo, clone_url
    
    raise ValueError(f"Could not parse GitHub URL: {url}")


def clone_single_repo(url: str, temp_dir: Path) -> dict:
    """Clone a single repo from URL into temp directory and return repo info."""
    owner, repo_name, clone_url = parse_repo_url(url)
    
    display_name = f"{owner}/{repo_name}"
    repo_path = temp_dir / repo_name
    
    print(f"{C.CYAN}Cloning {display_name}...{C.RESET}")
    
    # Clone the repo
    rc, _, stderr = run_cmd(["git", "clone", "--quiet", clone_url, str(repo_path)])
    
    if rc != 0:
        print(f"{C.RED}Failed to clone {display_name}: {stderr}{C.RESET}")
        sys.exit(1)
    
    print(f"{C.GREEN}✓ Cloned {display_name}{C.RESET}")
    
    return {"name": display_name, "path": repo_path}


def should_exclude_file(filepath: str) -> bool:
    basename = os.path.basename(filepath)
    filepath_lower = filepath.lower()
    
    # Check --no-docs flag
    if EXCLUDE_DOCS:
        _, ext = os.path.splitext(filepath_lower)
        if ext in DOC_EXTENSIONS:
            return True
    
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(filepath, pattern):
            return True
        if fnmatch.fnmatch(filepath, f"*/{pattern}"):
            return True
        if fnmatch.fnmatch(basename, pattern):
            return True
        if "/" in pattern:
            dir_pattern = pattern.rstrip("/*").rstrip("*")
            if dir_pattern and dir_pattern in filepath_lower:
                return True
    return False


def should_exclude_author(author: str) -> bool:
    author_lower = author.lower()
    return any(ex.lower() in author_lower for ex in EXCLUDE_AUTHORS)


def get_git_log(repo_path: Path, since: str, until: str = None) -> str:
    cmd = ["git", "log", "--numstat", "--format=COMMIT|%H|%an|%ad", "--date=short", f"--since={since}", "--all"]
    if until:
        cmd.append(f"--until={until}")
    rc, stdout, _ = run_cmd(cmd, cwd=str(repo_path))
    return stdout if rc == 0 else ""


def parse_git_log(log_output: str) -> dict:
    stats = defaultdict(lambda: {
        "commits": set(), "inserts": 0, "deletes": 0,
        "weekly": defaultdict(lambda: {"inserts": 0, "deletes": 0, "commits": set()}),
        "by_ext": defaultdict(lambda: {"inserts": 0, "deletes": 0}),
        "by_category": defaultdict(lambda: {"inserts": 0, "deletes": 0}),
    })
    current_author = None
    current_commit = None
    current_date = None

    for line in log_output.strip().split("\n"):
        if not line:
            continue
        if line.startswith("COMMIT|"):
            parts = line.split("|")
            if len(parts) >= 4:
                current_commit = parts[1]
                author_name = parts[2].strip()
                if should_exclude_author(author_name):
                    current_author = None
                    continue
                current_author = author_name
                try:
                    current_date = datetime.strptime(parts[3], "%Y-%m-%d")
                except ValueError:
                    current_date = None
            continue
        parts = line.split("\t")
        if len(parts) == 3 and current_author:
            insertions, deletions, filepath = parts
            if insertions == "-" or deletions == "-":
                continue
            if should_exclude_file(filepath):
                continue
            try:
                ins, dels = int(insertions), int(deletions)
                stats[current_author]["commits"].add(current_commit)
                stats[current_author]["inserts"] += ins
                stats[current_author]["deletes"] += dels
                
                # Track by file extension
                _, ext = os.path.splitext(filepath.lower())
                if ext:
                    stats[current_author]["by_ext"][ext]["inserts"] += ins
                    stats[current_author]["by_ext"][ext]["deletes"] += dels
                
                # Track by work category
                category = get_file_category(filepath)
                stats[current_author]["by_category"][category]["inserts"] += ins
                stats[current_author]["by_category"][category]["deletes"] += dels
                
                if current_date:
                    week_start = current_date - timedelta(days=current_date.weekday())
                    stats[current_author]["weekly"][week_start]["inserts"] += ins
                    stats[current_author]["weekly"][week_start]["deletes"] += dels
                    stats[current_author]["weekly"][week_start]["commits"].add(current_commit)
            except ValueError:
                continue
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_repos(repos: list[dict], since: str, until: str = None) -> tuple[list[dict], dict, dict, dict]:
    all_data = []
    weekly_stats = defaultdict(lambda: defaultdict(lambda: {"inserts": 0, "deletes": 0, "commits": set()}))
    ext_stats = defaultdict(lambda: defaultdict(lambda: {"inserts": 0, "deletes": 0}))
    category_stats = defaultdict(lambda: defaultdict(lambda: {"inserts": 0, "deletes": 0}))
    total = len(repos)

    for i, repo in enumerate(repos, 1):
        repo_name = repo["name"]
        bar = progress_bar(i, total, 15)
        print(f"  {C.GRAY}{Box.V}{C.RESET} {bar} {C.CYAN}{repo_name:<30}{C.RESET}", end="\r")

        log_output = get_git_log(repo["path"], since, until)
        if not log_output:
            continue

        stats = parse_git_log(log_output)
        for author, data in stats.items():
            if data["inserts"] > 0 or data["deletes"] > 0:
                all_data.append({
                    "author": author, "repo": repo_name,
                    "commits": len(data["commits"]),
                    "inserts": data["inserts"], "deletes": data["deletes"],
                    "net": data["inserts"] - data["deletes"]
                })
                for week, week_data in data["weekly"].items():
                    weekly_stats[author][week]["inserts"] += week_data["inserts"]
                    weekly_stats[author][week]["deletes"] += week_data["deletes"]
                    weekly_stats[author][week]["commits"].update(week_data["commits"])
                
                # Aggregate extension stats
                for ext, ext_data in data["by_ext"].items():
                    ext_stats[author][ext]["inserts"] += ext_data["inserts"]
                    ext_stats[author][ext]["deletes"] += ext_data["deletes"]
                
                # Aggregate category stats
                for cat, cat_data in data["by_category"].items():
                    category_stats[author][cat]["inserts"] += cat_data["inserts"]
                    category_stats[author][cat]["deletes"] += cat_data["deletes"]

    print(" " * 60)  # Clear progress line
    return all_data, weekly_stats, ext_stats, category_stats


# ═══════════════════════════════════════════════════════════════════════════════
# OMARCHY-STYLED OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def print_header(title: str, width: int = None):
    """Print a styled section header."""
    w = width or get_term_width()
    inner = w - 4
    print(f"\n{C.BOX}{Box.TL}{Box.H * inner}{Box.TR}{C.RESET}")
    print(f"{C.BOX}{Box.V}{C.RESET} {C.CYAN}{C.BOLD}{title:<{inner-1}}{C.RESET}{C.BOX}{Box.V}{C.RESET}")
    print(f"{C.BOX}{Box.BL}{Box.H * inner}{Box.BR}{C.RESET}")


def print_repo_table(data: list[dict]):
    """Print detailed repo contribution table in omarchy style."""
    if not data:
        print(f"\n{C.YELLOW}No contribution data found.{C.RESET}")
        return

    # Filter to only rows with actual activity
    data = [d for d in data if d["inserts"] > 0 or d["deletes"] > 0]
    if not data:
        print(f"\n{C.YELLOW}No contribution data found in this date range.{C.RESET}")
        return

    data = sorted(data, key=lambda x: x["net"], reverse=True)
    
    # Calculate column widths
    aw = max(20, max(len(d["author"]) for d in data) + 2)
    rw = max(25, max(len(d["repo"]) for d in data) + 2)
    
    print_header("repo contributions")
    
    # Header row
    print(f"{C.BOX}{Box.TL}{Box.H * aw}{Box.TT}{Box.H * rw}{Box.TT}{Box.H * 10}{Box.TT}{Box.H * 12}{Box.TT}{Box.H * 12}{Box.TT}{Box.H * 12}{Box.TR}{C.RESET}")
    print(f"{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Author':<{aw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Repository':<{rw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Commits':>10}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.GREEN}{'Inserts':>12}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.RED}{'Deletes':>12}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.BLUE}{'Net':>12}{C.RESET}{C.BOX}{Box.V}{C.RESET}")
    print(f"{C.BOX}{Box.LT}{Box.H * aw}{Box.X}{Box.H * rw}{Box.X}{Box.H * 10}{Box.X}{Box.H * 12}{Box.X}{Box.H * 12}{Box.X}{Box.H * 12}{Box.RT}{C.RESET}")

    for row in data[:20]:  # Top 20
        print(f"{C.BOX}{Box.V}{C.RESET}{C.MAGENTA}{row['author']:<{aw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.WHITE}{row['repo']:<{rw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.WHITE}{row['commits']:>10,}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.GREEN}{row['inserts']:>12,}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.RED}{row['deletes']:>12,}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.BLUE}{row['net']:>12,}{C.RESET}{C.BOX}{Box.V}{C.RESET}")

    print(f"{C.BOX}{Box.BL}{Box.H * aw}{Box.BT}{Box.H * rw}{Box.BT}{Box.H * 10}{Box.BT}{Box.H * 12}{Box.BT}{Box.H * 12}{Box.BT}{Box.H * 12}{Box.BR}{C.RESET}")


def print_author_summary(data: list[dict]):
    """Print author summary with visual bars."""
    if not data:
        return

    author_totals = defaultdict(lambda: {"commits": 0, "inserts": 0, "deletes": 0, "net": 0, "repos": set()})
    for row in data:
        author_totals[row["author"]]["commits"] += row["commits"]
        author_totals[row["author"]]["inserts"] += row["inserts"]
        author_totals[row["author"]]["deletes"] += row["deletes"]
        author_totals[row["author"]]["net"] += row["net"]
        author_totals[row["author"]]["repos"].add(row["repo"])

    # Filter out authors with no activity
    author_totals = {k: v for k, v in author_totals.items() 
                     if v["inserts"] > 0 or v["deletes"] > 0}
    
    if not author_totals:
        return

    sorted_authors = sorted(author_totals.items(), key=lambda x: x[1]["net"], reverse=True)
    max_net = max(abs(a[1]["net"]) for a in sorted_authors) if sorted_authors else 1

    print_header("author summary")
    
    aw = max(20, max(len(a[0]) for a in sorted_authors) + 2)
    
    print(f"{C.BOX}{Box.TL}{Box.H * aw}{Box.TT}{Box.H * 6}{Box.TT}{Box.H * 10}{Box.TT}{Box.H * 22}{Box.TT}{Box.H * 12}{Box.TR}{C.RESET}")
    print(f"{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Author':<{aw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Repos':>6}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Commits':>10}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.CYAN}{'Contribution':^22}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.BLUE}{'Net LoC':>12}{C.RESET}{C.BOX}{Box.V}{C.RESET}")
    print(f"{C.BOX}{Box.LT}{Box.H * aw}{Box.X}{Box.H * 6}{Box.X}{Box.H * 10}{Box.X}{Box.H * 22}{Box.X}{Box.H * 12}{Box.RT}{C.RESET}")

    for author, totals in sorted_authors:
        # Create visual bar with gradient
        bar_width = 20
        if totals["net"] >= 0:
            fill = int((totals["net"] / max_net) * bar_width) if max_net > 0 else 0
            bar = gradient_bar(fill / bar_width * 100, bar_width, "cyan")
        else:
            fill = int((abs(totals["net"]) / max_net) * bar_width) if max_net > 0 else 0
            bar = f"{C.GRAY}{'░' * (bar_width - fill)}{C.RED}{'█' * fill}{C.RESET}"
        
        print(f"{C.BOX}{Box.V}{C.RESET}{C.MAGENTA}{author:<{aw}}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.WHITE}{len(totals['repos']):>6}{C.RESET}{C.BOX}{Box.V}{C.RESET}{C.WHITE}{totals['commits']:>10,}{C.RESET}{C.BOX}{Box.V}{C.RESET} {bar} {C.BOX}{Box.V}{C.RESET}{C.BLUE}{totals['net']:>12,}{C.RESET}{C.BOX}{Box.V}{C.RESET}")

    print(f"{C.BOX}{Box.BL}{Box.H * aw}{Box.BT}{Box.H * 6}{Box.BT}{Box.H * 10}{Box.BT}{Box.H * 22}{Box.BT}{Box.H * 12}{Box.BR}{C.RESET}")

    # Totals
    total_commits = sum(d["commits"] for d in data)
    total_inserts = sum(d["inserts"] for d in data)
    total_deletes = sum(d["deletes"] for d in data)
    total_net = sum(d["net"] for d in data)

    print(f"\n{C.GRAY}{'─' * 60}{C.RESET}")
    print(f"  {C.CYAN}Total:{C.RESET} {C.WHITE}{total_commits:,}{C.RESET} commits  {C.GREEN}+{total_inserts:,}{C.RESET}  {C.RED}-{total_deletes:,}{C.RESET}  {C.BLUE}= {total_net:,} net{C.RESET}")
    print(f"{C.GRAY}{'─' * 60}{C.RESET}")


def gradient_bar(pct: float, width: int = 20, style: str = "cyan") -> str:
    """Create a gradient progress bar like btop disk usage."""
    filled = int(width * min(pct / 100, 1.0))
    empty = width - filled
    
    # Gradient colors based on style
    if style == "cyan":
        # Cyan → Teal gradient
        start = "\033[38;2;124;248;247m"  # #7cf8f7
        mid = "\033[38;2;80;247;212m"     # #50f7d4
        end = "\033[38;2;79;232;143m"     # #4fe88f
    elif style == "green":
        # Green gradient
        start = "\033[38;2;79;232;143m"   # #4fe88f
        mid = "\033[38;2;80;247;212m"     # #50f7d4
        end = "\033[38;2;124;248;247m"    # #7cf8f7
    else:
        start = mid = end = C.CYAN
    
    # Build gradient bar
    if filled == 0:
        bar = ""
    elif filled <= width // 3:
        bar = f"{start}{'█' * filled}"
    elif filled <= 2 * width // 3:
        third = width // 3
        bar = f"{start}{'█' * third}{mid}{'█' * (filled - third)}"
    else:
        third = width // 3
        bar = f"{start}{'█' * third}{mid}{'█' * third}{end}{'█' * (filled - 2*third)}"
    
    empty_bar = f"{C.GRAY}{'░' * empty}{C.RESET}"
    return f"{bar}{C.RESET}{empty_bar}"


def print_file_type_breakdown(ext_stats: dict, category_stats: dict):
    """Print per-author file type breakdown with gradient bars like btop."""
    if not ext_stats:
        return
    
    print_header("work breakdown by author")
    
    # Sort authors by total net lines, filter out zero contributors
    author_totals = {}
    for author in ext_stats:
        total_net = sum(d["inserts"] - d["deletes"] for d in ext_stats[author].values())
        total_activity = sum(d["inserts"] + d["deletes"] for d in ext_stats[author].values())
        if total_activity > 0:  # Only include authors with actual contributions
            author_totals[author] = total_net
    
    if not author_totals:
        print(f"\n{C.GRAY}No contributions in this date range.{C.RESET}")
        return
    
    sorted_authors = sorted(author_totals.items(), key=lambda x: x[1], reverse=True)
    
    for author, total_net in sorted_authors:
        exts = ext_stats[author]
        cats = category_stats.get(author, {})
        
        # Get sorted data
        sorted_exts = sorted(exts.items(), key=lambda x: x[1]["inserts"] - x[1]["deletes"], reverse=True)
        sorted_cats = sorted(cats.items(), key=lambda x: x[1]["inserts"] - x[1]["deletes"], reverse=True)
        
        # Calculate totals for percentages
        ext_total = sum(abs(d["inserts"] - d["deletes"]) for d in exts.values())
        cat_total = sum(abs(d["inserts"] - d["deletes"]) for d in cats.values())
        
        # Determine primary work type
        primary_label = "Mixed"
        if sorted_cats:
            primary_cat = sorted_cats[0][0]
            primary_label, _ = CATEGORY_LABELS.get(primary_cat, ("Other", C.GRAY))
        
        # Fixed width box (80 chars inner content)
        W = 68  # Inner content width
        
        # Author header
        author_display = author[:30]
        loc_str = f"{total_net:>+,} LoC"
        header_content = f" {author_display:<30} {C.GRAY}│{C.RESET} {C.CYAN}{primary_label:<10}{C.RESET} {C.GRAY}│{C.RESET} {C.BLUE}{loc_str:>16}{C.RESET} "
        
        print(f"\n{C.BOX}┌{'─' * W}┐{C.RESET}")
        print(f"{C.BOX}│{C.RESET}{C.MAGENTA}{C.BOLD}{author_display:<30}{C.RESET} {C.GRAY}│{C.RESET} {C.CYAN}{primary_label:<10}{C.RESET} {C.GRAY}│{C.RESET} {C.BLUE}{loc_str:>16}{C.RESET} {C.BOX}│{C.RESET}")
        print(f"{C.BOX}├{'─' * W}┤{C.RESET}")
        
        # File types section
        section_label = "file types"
        pad = W - len(section_label) - 1
        print(f"{C.BOX}│{C.RESET}{C.CYAN}{section_label}{C.RESET}{' ' * pad}{C.BOX}│{C.RESET}")
        
        for ext, data in sorted_exts[:6]:
            net = data["inserts"] - data["deletes"]
            if net == 0:
                continue
            pct = abs(net) / ext_total * 100 if ext_total > 0 else 0
            bar = gradient_bar(pct, width=20, style="cyan")
            net_color = C.GREEN if net >= 0 else C.RED
            # Build line: "  .ext     [bar] XX.X%  +XXX,XXX"
            line = f"  {ext:<6} {bar} {pct:>5.1f}%  {net_color}{net:>+10,}{C.RESET}"
            # Calculate visible length (without ANSI codes)
            visible_len = 2 + 6 + 1 + 20 + 1 + 6 + 2 + 10  # = 48
            pad = W - visible_len
            print(f"{C.BOX}│{C.RESET}  {C.WHITE}{ext:<6}{C.RESET} {bar} {C.GRAY}{pct:>5.1f}%{C.RESET}  {net_color}{net:>+10,}{C.RESET}{' ' * pad}{C.BOX}│{C.RESET}")
        
        # Blank line
        print(f"{C.BOX}│{C.RESET}{' ' * W}{C.BOX}│{C.RESET}")
        
        # Work categories section
        section_label = "work type"
        pad = W - len(section_label) - 1
        print(f"{C.BOX}│{C.RESET}{C.CYAN}{section_label}{C.RESET}{' ' * pad}{C.BOX}│{C.RESET}")
        
        for cat, data in sorted_cats[:4]:
            net = data["inserts"] - data["deletes"]
            if net == 0:
                continue
            label, _ = CATEGORY_LABELS.get(cat, ("Other", C.GRAY))
            pct = abs(net) / cat_total * 100 if cat_total > 0 else 0
            bar = gradient_bar(pct, width=20, style="green")
            net_color = C.GREEN if net >= 0 else C.RED
            visible_len = 2 + 8 + 1 + 20 + 1 + 6 + 2 + 10  # = 50
            pad = W - visible_len
            print(f"{C.BOX}│{C.RESET}  {C.TEAL}{label:<8}{C.RESET} {bar} {C.GRAY}{pct:>5.1f}%{C.RESET}  {net_color}{net:>+10,}{C.RESET}{' ' * pad}{C.BOX}│{C.RESET}")
        
        # Focus line
        print(f"{C.BOX}│{C.RESET}{' ' * W}{C.BOX}│{C.RESET}")
        work_desc = get_work_description(sorted_cats)
        focus_line = f"Focus: {work_desc}"[:W-1]
        pad = W - len(focus_line) - 1
        print(f"{C.BOX}│{C.RESET}{C.GRAY}Focus:{C.RESET} {C.WHITE}{work_desc[:W-8]:<{W-8}}{C.RESET}{C.BOX}│{C.RESET}")
        print(f"{C.BOX}└{'─' * W}┘{C.RESET}")


def get_work_description(sorted_cats: list) -> str:
    """Generate a human-readable work description based on category breakdown."""
    if not sorted_cats:
        return "Mixed contributions"
    
    # Get top 2 categories
    top_cats = [c[0] for c in sorted_cats[:2] if c[1]["inserts"] - c[1]["deletes"] > 0]
    
    descriptions = {
        ("frontend",): "UI/UX development, component building",
        ("backend",): "Server-side logic, API development",
        ("fullstack",): "Full-stack JavaScript/TypeScript development",
        ("database",): "Database schema, queries, migrations",
        ("config",): "Configuration, project setup",
        ("infra",): "Infrastructure, DevOps, deployment",
        ("docs",): "Documentation, technical writing",
        ("scripts",): "Automation, scripting, tooling",
        ("testing",): "Test coverage, quality assurance",
        ("frontend", "fullstack"): "Frontend-focused full-stack development",
        ("backend", "fullstack"): "Backend-focused with JS/TS integration",
        ("backend", "database"): "Backend + database architecture",
        ("frontend", "backend"): "True full-stack development",
        ("infra", "config"): "DevOps and infrastructure",
        ("docs", "config"): "Documentation and project maintenance",
    }
    
    key = tuple(top_cats[:2]) if len(top_cats) >= 2 else tuple(top_cats[:1])
    return descriptions.get(key, descriptions.get(tuple(top_cats[:1]), "Mixed contributions"))


def print_banner(base_dir: Path, since: str, until: str, repo_count: int):
    """Print the omarchy-styled banner."""
    w = get_term_width()
    now = datetime.now().strftime("%H:%M:%S")
    
    print(f"\n{C.BOX}{'═' * w}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  ┌repos┐ ┌review┐{C.RESET}                                      {C.GRAY}{now}{C.RESET}")
    print(f"{C.BOX}{'═' * w}{C.RESET}")
    print(f"  {C.GRAY}Path:{C.RESET}   {C.WHITE}{base_dir}{C.RESET}")
    print(f"  {C.GRAY}Period:{C.RESET} {C.TEAL}{since}{C.RESET} {C.GRAY}→{C.RESET} {C.TEAL}{until or 'now'}{C.RESET}")
    print(f"  {C.GRAY}Repos:{C.RESET}  {C.YELLOW}{repo_count}{C.RESET}")
    print(f"{C.BOX}{'═' * w}{C.RESET}")


def write_csv(data: list[dict], output_path: str):
    if not data:
        return
    data = sorted(data, key=lambda x: (x["author"].lower(), x["repo"].lower()))
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["author", "repo", "commits", "inserts", "deletes", "net"])
        writer.writeheader()
        writer.writerows(data)
    print(f"\n{C.GRAY}CSV written to:{C.RESET} {C.CYAN}{output_path}{C.RESET}")


def create_dot_plot(weekly_stats: dict, output_path: str, since: str):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.lines import Line2D
    except ImportError:
        print(f"\n{C.YELLOW}Note: pip install matplotlib for chart generation{C.RESET}")
        return

    authors = sorted(weekly_stats.keys(), key=lambda a: sum(
        d["inserts"] - d["deletes"] for d in weekly_stats[a].values()
    ), reverse=True)

    top_authors = authors[:12]
    author_colors = {author: AUTHOR_COLORS[i % len(AUTHOR_COLORS)] for i, author in enumerate(top_authors)}

    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor('#0B0C16')  # main_bg from hackerman theme
    ax.set_facecolor('#0B0C16')

    for author in top_authors:
        weeks = sorted(weekly_stats[author].keys())
        if not weeks:
            continue
        dates, sizes = [], []
        for week in weeks:
            data = weekly_stats[author][week]
            net = data["inserts"] - data["deletes"]
            if net > 0:
                dates.append(week)
                sizes.append(max(10, min(500, (net ** 0.5) * 3)))
        if dates:
            ax.scatter(dates, [author] * len(dates), s=sizes, c=author_colors[author], alpha=0.8, edgecolors='#4fe88f', linewidths=0.5)

    # Hackerman theme colors
    hi_fg = '#7cf8f7'      # Bright cyan
    title_color = '#86a7df'  # Title blue
    box_color = '#4fe88f'    # Green
    inactive = '#6a6e95'     # Gray
    main_fg = '#ddf7ff'      # White text

    ax.set_xlabel('Week', fontsize=12, color=hi_fg, labelpad=10)
    ax.set_title(f'Weekly Code Contributions\n{since} → now', fontsize=16, color=title_color, pad=20, fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45, ha='right', color=hi_fg)
    plt.yticks(color=main_fg)
    ax.grid(True, axis='x', alpha=0.2, color=inactive, linestyle='--')
    ax.grid(True, axis='y', alpha=0.1, color=inactive, linestyle='-')
    for spine in ax.spines.values():
        spine.set_color(box_color)
        spine.set_alpha(0.5)

    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=author_colors[a], markersize=10, label=a, linestyle='None') for a in top_authors if a in author_colors]
    legend = ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), framealpha=0.9, facecolor='#0B0C16', edgecolor=box_color)
    for text in legend.get_texts():
        text.set_color(main_fg)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"\n{C.GRAY}Chart saved to:{C.RESET} {C.CYAN}{output_path}{C.RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Omarchy Repo Contribution Analyzer")
    parser.add_argument("--since", default=DEFAULT_SINCE, help=f"Start date (default: {DEFAULT_SINCE})")
    parser.add_argument("--until", default=None, help="End date (default: today)")
    parser.add_argument("--output", "-o", default=None, help="Output CSV file path")
    parser.add_argument("--chart", action="store_true", help="Generate weekly contribution chart")
    parser.add_argument("--dir", default=str(CODE_DIR), help=f"Base directory (default: {CODE_DIR})")
    parser.add_argument("--all", action="store_true", help=f"Fetch all repos from {ORG_NAME} GitHub org")
    parser.add_argument("--repo", default=None, help="Analyze a single repo from GitHub URL (https or ssh)")
    parser.add_argument("--no-docs", action="store_true", help="Exclude documentation files (.md, .txt, etc)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.repo and args.all:
        print(f"{C.RED}Error: --repo and --all are mutually exclusive{C.RESET}")
        sys.exit(1)

    # Disable colors if requested or not a tty
    if args.no_color or not sys.stdout.isatty():
        for attr in dir(C):
            if not attr.startswith('_'):
                setattr(C, attr, '')

    # Set global docs exclusion flag
    global EXCLUDE_DOCS
    EXCLUDE_DOCS = args.no_docs

    base_dir = Path(args.dir)
    temp_dir = None
    
    # Choose repo discovery method
    if args.repo:
        # Single repo mode - clone to temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="repo_review_"))
        try:
            repo_info = clone_single_repo(args.repo, temp_dir)
            repos = [repo_info]
            source = args.repo
        except ValueError as e:
            print(f"{C.RED}{e}{C.RESET}")
            sys.exit(1)
    elif args.all:
        repos = fetch_org_repos(base_dir)
        source = f"{ORG_NAME} org"
    else:
        repos = discover_local_repos(base_dir)
        source = str(base_dir)

    if not repos:
        print(f"{C.RED}No git repositories found{C.RESET}")
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

    display_path = source if args.repo else base_dir
    print_banner(Path(source) if args.repo else base_dir, args.since, args.until, len(repos))

    print(f"\n{C.CYAN}Scanning repositories...{C.RESET}")
    data, weekly_stats, ext_stats, category_stats = analyze_repos(repos, args.since, args.until)

    print_repo_table(data)
    print_author_summary(data)
    print_file_type_breakdown(ext_stats, category_stats)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        csv_path = args.output
    elif args.repo:
        # For single repo, output to current directory
        csv_path = f"om_contributions_{timestamp}.csv"
    else:
        csv_path = str(base_dir / f"om_contributions_{timestamp}.csv")
    write_csv(data, csv_path)

    if args.chart:
        chart_path = csv_path.replace('.csv', '.png')
        create_dot_plot(weekly_stats, chart_path, args.since)
    
    # Cleanup temp directory if we cloned a single repo
    if temp_dir and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
