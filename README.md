# Cursor Skills Starter

A starter template for leveraging the skills pattern in Cursor, as pioneered by Claude Code.

## Overview

This repository transforms Cursor into a **general-purpose AI agent** through the combination of two key components:

### 1. **Role-Based Rules System** (`.cursor/rules/main_rule.mdc`)

The rules file defines two distinct operational roles that the AI agent can assume:

- **Orchestrator** (Default): The key innovation - delegates tasks to specialised skills via MCP tools rather than solving everything directly. This includes using the `skill-creator` skill to build new capabilities when needed.
- **Pair Programmer**: Standard Cursor behavior - directly writes code, modifies files, and makes changes to the repository without skill delegation. Used for repository maintenance and troubleshooting.

The agent automatically determines which role to adopt based on your request. By defaulting to Orchestrator mode, the system ensures that specialised skills are leveraged when available, rather than relying solely on general coding knowledge.

### 2. **Skills MCP Server** (`mcp/skills_mcp.py`)

The MCP (Model Context Protocol) server provides the infrastructure for the agent to:

- **Discover** available skills via `list_skills`
- **Invoke** specialised skills via `invoke_skill` to access domain-specific expertise
- **Find** community skills via `find_skill` to browse the skills directory
- **Import** new skills from a github repo url via `import_skill`

When you ask Cursor to perform a task, the Orchestrator role checks for relevant skills first, then delegates to that skill's specialised knowledge rather than attempting the task with general knowledge alone.

**The Result**: A flexible, extensible agent system where you can continuously add new skills, and the agent knows when and how to use them effectively.

## What are Skills?

Skills are a simple yet powerful pattern for giving AI coding agents specialised capabilities. A skill is a Markdown file telling the model how to do something, optionally accompanied by extra documents and pre-written scripts that the model can run to help it accomplish the tasks described by the skill.

### Anatomy of a Skill

Each skill is self-contained in its own directory with:

- **`SKILL.md`** (required): The core instructions telling the agent how to perform specific tasks. This is just Markdown with a bit of YAML frontmatter metadata.
- **`scripts/`** (optional): Pre-written scripts (Python, bash, etc.) that the model can execute to accomplish tasks more reliably or efficiently
- **Additional resources** (optional): Supporting files like reference documentation, examples, templates, or data files that `SKILL.md` points to

The beauty of this design is its **simplicity and token efficiency**. The agent initially only reads the short metadata from each skill (a few dozen tokens). The full `SKILL.md` and associated resources are only loaded when the user requests a task that the skill can help solve.

**Note:** You can organise skills in subdirectories for better organization. For example:

```
skills/
├── document-skills/
│   ├── docx/
│   │   └── SKILL.md
│   ├── pdf/
│   │   └── SKILL.md
│   └── xlsx/
│       └── SKILL.md
├── artifacts-builder/     # Or at the root level
│   └── SKILL.md
├── skill-creator/
│   └── SKILL.md
```

The MCP server automatically discovers skills in nested directories and lists them with their full path (e.g., `document-skills/pdf`, `creative/algorithmic-art`).


### Why Skills Work

Skills leverage the fact that modern coding agents have access to a filesystem and can execute commands. This simple dependency unlocks enormous capability - any task you can accomplish by typing commands into a computer can be encoded as a skill and automated by the agent.

As Simon Willison observed: "The core simplicity of the skills design is why I'm so excited about it... They feel a lot closer to the spirit of LLMs—throw in some text and let the model figure it out."

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Open the `.cursor` dir and rename `mcp_example.json` to `mcp.json`. Then update the MCP server path `"path/to/cursor-skills/mcp/skills_mcp.py"` to the correct path for your repo. 
2. Open Cursor Settings > Tools and MCP and make sure the "cursor-skills" mcp server is showing as on (with 4 tools).

That's it! No separate dependency installation needed - `uv run` handles everything automatically.

### Import Skills from GitHub

The fastest way to get started is to import skills directly from GitHub. Simply paste a GitHub URL and the skills will be automatically downloaded and installed:

**Import a single skill:**
```
Please import https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills/creating-financial-models
```

**Import multiple skills at once:**
```
Please import https://github.com/anthropics/skills
```

This works with any GitHub repository containing skills - whether it's a single skill directory or a collection of skills. The import tool will:
- ✅ Automatically detect single skills vs. directories containing multiple skills
- ✅ Download all necessary files including scripts and resources
- ✅ Validate each skill has a proper SKILL.md file
- ✅ Skip skills that are already installed
- ✅ Support nested directory structures

You can import from:
- [Anthropic's official skills repository](https://github.com/anthropics/skills)
- [Claude Cookbooks custom skills](https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills)
- Any GitHub repo with skills in SKILL.md format

## Using Skills in Cursor

Once the MCP server is running, you can ask Cursor to do something for you that involves a skill and you should see it call these MCP tools:

### `list_skills`
Lists all available skills in your local `skills/` directory with their descriptions.

### `invoke_skill`
Invokes a specific skill to access its complete documentation and specialised instructions.

Example:
```
invoke_skill("pdf")
```

### `find_skill`
Browses the community skills directory to discover available skills from the broader ecosystem. Returns a curated list of skills with descriptions and GitHub URLs that can be imported.

Example:
```
What skills are available in the community directory?
```

### `import_skill`
Imports skills directly from GitHub repositories. Supports both single skills and directories containing multiple skills.

Examples:
```
import_skill("https://github.com/anthropics/skills/tree/main/algorithmic-art")
import_skill("https://github.com/anthropics/skills")
```

## Creating Your Own Skills


### Automatically

Simply ask Cursor to create a given skill and you should see it use the `skill-creator` skill to create that new skill for you. You can always tweak and improve it from there.

### Manually

1. Create a new directory in `skills/` with your skill name (e.g., `skills/my-skill/`)

2. Add a `SKILL.md` file with your skill documentation:
   - Start with a clear description (first line becomes the skill's summary)
   - Include detailed instructions, examples, and best practices
   - Add any relevant code snippets or techniques

3. Optionally add a `scripts/` directory for any helper scripts

4. Add a `LICENSE.txt` file if you want to specify licensing

## Example Skills

This repo can work with any skills from Anthropic's official skills repositories or custom skills in the same format. Use the `import_skill` tool to quickly add skills from GitHub.

**Popular skill collections to import:**

- [**Anthropic's Skills Repository**](https://github.com/anthropics/skills) - Official collection including:
  - **artifacts-builder**: Build complex HTML artifacts with React and shadcn/ui
  - **document-skills**: Comprehensive DOCX, PDF, PPTX, and XLSX manipulation
  - **skill-creator**: Tools for creating and packaging new skills
  - **algorithmic-art**: Create generative art with p5.js
  - **mcp-builder**: Guide for creating MCP servers
  - And many more...

- [**Claude Cookbooks Custom Skills**](https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills) - Additional examples:
  - **creating-financial-models**: DCF analysis and financial modeling
  - **analyzing-financial-statements**: Calculate financial ratios and metrics
  - **applying-brand-guidelines**: Apply corporate branding to documents

Import them with a simple command:
```
Please import https://github.com/anthropics/skills
```

## Project Structure

```
cursor-skills/
├── mcp/
│   └── skills_mcp.py          # MCP server (with inline dependencies)
├── skills/
│   ├── document-skills/       # Skills can be organised in subdirectories
│   │   ├── docx/
│   │   │   └── SKILL.md
│   │   ├── pdf/
│   │   │   └── SKILL.md
│   │   ├── pptx/
│   │   │   └── SKILL.md
│   │   └── xlsx/
│   │       └── SKILL.md
│   ├── artifacts-builder/     # Or at the root level
│   │   └── SKILL.md
│   ├── skill-creator/
│   │   └── SKILL.md
│   └── etc...
├── .cursor/
│   ├── rules/
│   │   └── main_rule.mdc      # Main Cursor rules file
│   └── mcp.json               # Cursor MCP configuration
└── README.md
```

## How It Works

The MCP (Model Context Protocol) server provides four tools that Cursor can use:

1. **list_skills**: Scans the `skills/` directory and returns available skills with descriptions
2. **invoke_skill**: Reads the `SKILL.md` file for a specific skill and returns its contents
3. **find_skill**: Fetches the community skills directory to help discover new skills to import
4. **import_skill**: Downloads skills from GitHub repositories and installs them locally

When you invoke a skill, the AI agent receives the complete skill documentation and can use that specialised knowledge to help you with your task. It then agentically follows the instructions described in that SKILL.md file including running scripts, refering to other md files, etc.

## Troubleshooting

### MCP Server Not Starting

Check the Cursor logs (View → Output → MCP) for errors. Common issues:

- Python version: Ensure Python 3.10+
- uv not installed: Install from https://github.com/astral-sh/uv
- Path issues: Verify paths in `.cursor/mcp.json` are correct

### Skills Not Found

- Ensure your skill directory has a `SKILL.md` file
- Check that the directory name doesn't start with `.` or `_`
- Verify the `skills/` directory exists at the project root


### Bonus

If you want to make skills available in all of the repos you work on with Cursor, you can install the MCP server at the global Cursor level rather than the repo level. You'll also need to copy and paste the contents of '/.cursor/rules/main_rule.mdc` into your Cursor "User Rules" in Cursor Settings>Rules and Memories

## License

This repository is licensed under the [MIT License](LICENSE).

**Third-party skills** imported from external sources (like Anthropic's skills repository) retain their original licenses. See individual skill directories for specific LICENSE files.

Skills created in this repository (design-system, youtube, repo-review) are MIT licensed.

