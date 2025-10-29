#!/usr/bin/env python3

"""
Skills MCP Server - provides access to specialized skills for AI coding agents.

This server enables AI coding agents (like Cursor) to discover and invoke
specialized skills from the skills directory, following the skills pattern
pioneered by Claude Code.
"""
# /// script
# dependencies = ["fastmcp"]
# ///

import os
import re
import urllib.request
import json
from pathlib import Path
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP(
    name="cursor-skills",
    instructions="A skills server that provides access to specialised, reusable capabilities through list_skills and invoke_skill tools."
)

# Get project root (parent of mcp directory)
project_root = Path(__file__).parent.parent

def _discover_skills(base_dir: Path, prefix: str = "") -> list:
    """Recursively discover skills in directory tree.
    
    Args:
        base_dir: Directory to search for skills
        prefix: Prefix for nested skill names (e.g., "document-skills/")
    
    Returns:
        List of tuples (skill_name, skill_path)
    """
    skills = []
    
    if not base_dir.exists():
        return skills
    
    for item in sorted(base_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('.'):
            continue
            
        skill_md = item / "SKILL.md"
        skill_name = f"{prefix}{item.name}" if prefix else item.name
        
        # If this directory has a SKILL.md, it's a skill
        if skill_md.exists():
            skills.append((skill_name, item))
        else:
            # Otherwise, recursively search subdirectories
            nested_skills = _discover_skills(item, f"{skill_name}/")
            skills.extend(nested_skills)
    
    return skills


def _extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content with optional YAML frontmatter
        
    Returns:
        Dictionary of frontmatter fields
    """
    if not content.startswith('---'):
        return {}
    
    # Find the closing ---
    lines = content.split('\n')
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break
    
    if end_index == -1:
        return {}
    
    # Parse the frontmatter (simple key: value parser)
    frontmatter = {}
    for line in lines[1:end_index]:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value
    
    return frontmatter


def _list_skills_impl() -> str:
    """Internal implementation for listing skills."""
    skills_dir = project_root / "skills"
    
    if not skills_dir.exists():
        return "No skills directory found. Create a 'skills' directory to add skills."
    
    discovered_skills = _discover_skills(skills_dir)
    
    if not discovered_skills:
        return "No skills found in the skills directory."
    
    skill_tags = []
    for skill_name, skill_path in discovered_skills:
        skill_md = skill_path / "SKILL.md"
        try:
            content = skill_md.read_text(encoding='utf-8')
            # Extract description from YAML frontmatter
            frontmatter = _extract_frontmatter(content)
            description = frontmatter.get('description', 'No description available')
            skill_tags.append(f"<skill name='{skill_name}'>{description}</skill>")
        except Exception as e:
            skill_tags.append(f"<skill name='{skill_name}'>Error reading skill: {e}</skill>")
    
    return "\n".join(skill_tags)


def _invoke_skill_impl(skill_name: str) -> str:
    """Internal implementation for invoking a skill."""
    skills_dir = project_root / "skills"
    
    # Handle nested skill paths (e.g., "document-skills/pdf")
    skill_path = skills_dir / skill_name
    
    if not skill_path.exists():
        # Get list of all available skills including nested ones
        discovered_skills = _discover_skills(skills_dir)
        available = [name for name, _ in discovered_skills]
        return f"Skill '{skill_name}' not found. Available skills: {', '.join(available)}"
    
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return f"Skill '{skill_name}' found but SKILL.md is missing."
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        return f"# {skill_name} Skill\n\n{content}"
    except Exception as e:
        return f"Error reading skill '{skill_name}': {e}"


def _parse_github_url(url: str) -> dict:
    """Parse a GitHub URL to extract components.
    
    Args:
        url: GitHub URL (repo or subdirectory)
        
    Returns:
        Dictionary with owner, repo, branch, and path
    """
    # Handle both https and git URLs
    # Examples:
    # https://github.com/user/repo
    # https://github.com/user/repo/tree/main/path/to/dir
    # https://github.com/user/repo/tree/branch-name/path
    
    pattern = r'github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+)/(.+))?'
    match = re.search(pattern, url)
    
    if not match:
        return None
    
    owner, repo, branch, path = match.groups()
    
    # Remove .git suffix if present
    if repo.endswith('.git'):
        repo = repo[:-4]
    
    return {
        'owner': owner,
        'repo': repo,
        'branch': branch or 'main',
        'path': path or ''
    }


def _download_github_directory(owner: str, repo: str, path: str, branch: str, dest: Path) -> tuple[bool, str]:
    """Download a directory from GitHub using the API.
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within repository
        branch: Branch name
        dest: Destination directory
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # GitHub API endpoint for directory contents
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        
        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with urllib.request.urlopen(req) as response:
            contents = json.loads(response.read().decode())
        
        if not isinstance(contents, list):
            return False, "Path does not point to a directory"
        
        # Create destination directory
        dest.mkdir(parents=True, exist_ok=True)
        
        # Download all files
        for item in contents:
            item_name = item['name']
            item_path = item['path']
            item_type = item['type']
            
            if item_type == 'file':
                # Download file
                download_url = item['download_url']
                file_dest = dest / item_name
                
                with urllib.request.urlopen(download_url) as response:
                    file_dest.write_bytes(response.read())
                    
            elif item_type == 'dir':
                # Recursively download subdirectory
                subdir_dest = dest / item_name
                success, msg = _download_github_directory(owner, repo, item_path, branch, subdir_dest)
                if not success:
                    return False, msg
        
        return True, "Successfully downloaded"
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, f"Repository or path not found (404). Check the URL and branch name."
        return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Error downloading: {str(e)}"


def _is_skill_directory(path: Path) -> bool:
    """Check if a directory contains a SKILL.md file.
    
    Args:
        path: Path to check
        
    Returns:
        True if directory contains SKILL.md
    """
    return (path / "SKILL.md").exists()


def _contains_multiple_skills(path: Path) -> list[str]:
    """Check if a directory contains multiple skill subdirectories.
    
    Args:
        path: Path to check
        
    Returns:
        List of skill subdirectory names, empty if none found
    """
    skills = []
    
    if not path.exists() or not path.is_dir():
        return skills
    
    for item in path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            if _is_skill_directory(item):
                skills.append(item.name)
    
    return skills


def _import_skill_impl(github_url: str) -> str:
    """Internal implementation for importing a skill from GitHub.
    
    Args:
        github_url: GitHub URL to a skill directory or repository
        
    Returns:
        Status message
    """
    # Parse GitHub URL
    parsed = _parse_github_url(github_url)
    if not parsed:
        return f"Invalid GitHub URL format. Expected format: https://github.com/owner/repo or https://github.com/owner/repo/tree/branch/path"
    
    owner = parsed['owner']
    repo = parsed['repo']
    branch = parsed['branch']
    path = parsed['path']
    
    # Determine skill name from the last part of the path or repo name
    if path:
        dir_name = path.split('/')[-1]
    else:
        dir_name = repo
    
    # Download to temporary location first to check if it contains multiple skills
    skills_dir = project_root / "skills"
    temp_path = skills_dir / f"_temp_{dir_name}"
    
    # Download the directory
    success, message = _download_github_directory(owner, repo, path, branch, temp_path)
    
    if not success:
        # Clean up partial download
        if temp_path.exists():
            import shutil
            shutil.rmtree(temp_path)
        return f"Failed to import skill: {message}"
    
    # Check if this is a single skill or a directory containing multiple skills
    is_single_skill = _is_skill_directory(temp_path)
    contained_skills = _contains_multiple_skills(temp_path)
    
    if is_single_skill:
        # Single skill - move to final location
        final_path = skills_dir / dir_name
        
        if final_path.exists():
            import shutil
            shutil.rmtree(temp_path)
            return f"Skill '{dir_name}' already exists at {final_path}. Remove it first if you want to re-import."
        
        temp_path.rename(final_path)
        return f"Successfully imported skill '{dir_name}' to {final_path}"
    
    elif contained_skills:
        # Multiple skills - import each one
        imported = []
        skipped = []
        failed = []
        
        for skill_name in contained_skills:
            source = temp_path / skill_name
            dest = skills_dir / skill_name
            
            if dest.exists():
                skipped.append(skill_name)
                continue
            
            try:
                import shutil
                shutil.move(str(source), str(dest))
                imported.append(skill_name)
            except Exception as e:
                failed.append(f"{skill_name} ({str(e)})")
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_path)
        
        # Build result message
        result_parts = []
        if imported:
            result_parts.append(f"Successfully imported {len(imported)} skill(s): {', '.join(imported)}")
        if skipped:
            result_parts.append(f"Skipped {len(skipped)} existing skill(s): {', '.join(skipped)}")
        if failed:
            result_parts.append(f"Failed to import {len(failed)} skill(s): {', '.join(failed)}")
        
        return "\n".join(result_parts) if result_parts else "No skills were imported."
    
    else:
        # Not a skill and doesn't contain skills
        import shutil
        shutil.rmtree(temp_path)
        return f"Downloaded directory does not contain SKILL.md and does not contain any skill subdirectories. This may not be a valid skill or skills directory. Directory has been removed."


@mcp.tool()
def list_skills() -> str:
    """List all available skills in the skills directory.
    
    Returns:
        str: Formatted list of available skills with descriptions in <skill> tags
    """
    return _list_skills_impl()


@mcp.tool()
def invoke_skill(skill_name: str) -> str:
    """Invoke a skill to access its specialized instructions and capabilities.

    Args:
        skill_name: The name of the skill to invoke (e.g., "pdf", "artifacts-builder")
        
    Returns:
        str: Complete skill documentation with specialized instructions
    """
    return _invoke_skill_impl(skill_name)


@mcp.tool()
def import_skill(github_url: str) -> str:
    """Import a skill from a GitHub repository URL.
    Supports both single skills and directories containing multiple skills.
    
    Args:
        github_url: GitHub URL to a skill directory or repository.
    
    Returns:
        str: Success message with imported skill name and location, or error details
    """
    return _import_skill_impl(github_url)


@mcp.tool()
def find_skill() -> str:
    """Find available skills from the community skill directory.
    
    Returns:
        str: Content of the skills directory README with descriptions and URLs
    """
    try:
        # URL to the raw README.md file
        url = "https://raw.githubusercontent.com/chrisboden/find-skills/main/README.md"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
        
        return content
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "Error: Skills directory README not found (404)."
        return f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return f"Error fetching skills directory: {str(e)}"


if __name__ == "__main__":
    mcp.run()