# Cursor Skills

A curated collection of skills for Cursor AI. Skills give your AI agent specialized capabilities - from building UIs to managing databases to creating documents.

## Installation

### Option 1: Cursor Settings (Recommended - Cursor 2.4+)

The simplest way to use skills. No server setup required.

1. Open Cursor Settings (`Cmd+Shift+J`)
2. Go to the **Rules** tab
3. Click **Add Rule** → **Remote Rule (GitHub)**
4. Enter: `https://github.com/aussiegingersnap/cursor-skills`
5. Select the skills you want to import

Skills are copied to your `.cursor/skills/` directory and automatically discovered.

### Option 2: Manual Copy

Clone and copy specific skills to your project:

```bash
git clone https://github.com/aussiegingersnap/cursor-skills /tmp/cursor-skills
cp -r /tmp/cursor-skills/skills/ui-design-system .cursor/skills/
```

### Option 3: MCP Server (Advanced)

For global skill access across all projects or legacy Cursor versions.

1. Copy `.cursor/mcp_example.json` to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project)
2. Update the path to your cloned `mcp/skills_mcp.py`
3. Reload Cursor
4. Copy `main_rule.mdc` contents to Cursor Settings → Rules (for global setup)

See [MCP Setup](#mcp-server-setup) below for details.

---

## Comparison: Native vs MCP

| Feature | Native (Cursor 2.4+) | MCP Server |
|---------|---------------------|------------|
| Setup | None - auto-discovered | Python + uv required |
| Scope | Project-specific | Global or project |
| Discovery | Automatic | Via `list_skills` tool |
| Import | Cursor Settings UI | Via `import_skill` tool |
| Best for | Most users | Advanced setups, global skills |

**Recommendation:** Use native skills for most projects. Use MCP only if you need global skills across all projects.

---

## Available Skills

### Core Skills (Recommended for all projects)

| Skill | Description |
|-------|-------------|
| `feature-build` | Complete feature development lifecycle with phases |
| `skill-creator` | Create new skills with guided workflow |
| `documentation` | Project documentation standards |
| `versioning` | Semantic versioning with CHANGELOG |
| `judge` | Quality review for complex changes |

### UI & Frontend (`ui-`, `state-`)

| Skill | Description |
|-------|-------------|
| `ui-design-system` | Linear/Notion-inspired UI patterns with style guide |
| `ui-principles` | Minimal, crafted UI principles |
| `nextjs-16` | Next.js 16 App Router patterns |
| `state-effector` | Effector reactive state management |
| `state-tanstack` | Tanstack Query + Zustand patterns |

### Backend & Data (`db-`, `auth-`, `api-`)

| Skill | Description |
|-------|-------------|
| `db-postgres` | PostgreSQL with Drizzle ORM |
| `db-sqlite` | SQLite with Prisma + Litestream backup |
| `api-rest` | REST API conventions with Zod validation |
| `auth-better-auth` | Better Auth integration |
| `auth-lucia` | Lucia auth patterns |

### MCP & AI Integration

| Skill | Description |
|-------|-------------|
| `mcp-apps` | Build MCP Apps with interactive UI for Claude/ChatGPT/VSCode |

### Infrastructure (`infra-`, `secrets-`)

| Skill | Description |
|-------|-------------|
| `infra-docker` | Local Docker development |
| `infra-railway` | Railway deployment |
| `infra-env` | Environment configuration patterns |
| `secrets-1password` | 1Password CLI for secrets management |

### Tools & Integrations (`tools-`)

| Skill | Description |
|-------|-------------|
| `tools-linear` | Linear issue tracking |
| `tools-youtube` | YouTube downloads and transcripts |
| `tools-repo-review` | GitHub repository analysis |
| `tools-email` | Email with Resend and React Email |
| `tools-artifacts` | Build HTML artifacts with React and shadcn/ui |
| `tools-posthog` | Feature flags with PostHog |

### Document Skills

| Skill | Description |
|-------|-------------|
| `document-skills/docx` | Microsoft Word documents |
| `document-skills/pdf` | PDF generation and manipulation |
| `document-skills/pptx` | PowerPoint presentations |
| `document-skills/xlsx` | Excel spreadsheets |

---

## What are Skills?

Skills are a simple yet powerful pattern for giving AI coding agents specialized capabilities. A skill is a Markdown file telling the model how to do something, optionally accompanied by scripts and reference documents.

### Anatomy of a Skill

```
skills/my-skill/
├── SKILL.md           # Core instructions (required)
├── scripts/           # Helper scripts (optional)
│   └── helper.py
├── references/        # Supporting docs (optional)
│   └── api-docs.md
└── LICENSE.txt        # License (optional)
```

- **`SKILL.md`** (required): Instructions for the agent. YAML frontmatter provides metadata.
- **`scripts/`** (optional): Pre-written scripts the agent can execute
- **`references/`** (optional): Supporting documentation, examples, templates

### Why Skills Work

Skills leverage that modern AI agents can read files and execute commands. Any task you can accomplish by typing commands can be encoded as a skill.

The design is **token-efficient**: the agent only loads full skill content when needed. Skill discovery uses just the frontmatter metadata (a few dozen tokens).

---

## Creating Your Own Skills

### Automatically

Ask Cursor to create a skill:
```
Create a skill for managing AWS S3 buckets
```

The `skill-creator` skill guides the process.

### Manually

1. Create `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Brief description for discovery. Explain when this skill should be used.
---

# My Skill

Detailed instructions for the agent...
```

2. Add optional scripts in `skills/my-skill/scripts/`
3. Add optional reference docs in `skills/my-skill/references/`

---

## MCP Server Setup

For global skill access or legacy Cursor versions.

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone this repo
2. Copy `.cursor/mcp_example.json` to `.cursor/mcp.json`
3. Update the path:

```json
{
  "mcpServers": {
    "cursor-skills": {
      "command": "uv",
      "type": "stdio",
      "args": ["run", "/path/to/cursor-skills/mcp/skills_mcp.py"]
    }
  }
}
```

4. Reload Cursor (`Cmd+Shift+P` → "Developer: Reload Window")
5. Verify in Settings → Tools and MCP: "cursor-skills" shows 4 tools

### Global Setup

To use skills across all projects:

1. Place `mcp.json` in `~/.cursor/` (global config)
2. Copy contents of `.cursor/rules/main_rule.mdc` to Cursor Settings → Rules

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_skills` | List installed skills with descriptions |
| `invoke_skill` | Load a skill's full instructions |
| `find_skill` | Browse community skills directory |
| `import_skill` | Import from GitHub URL |

### Import from GitHub (MCP)

```
Please import https://github.com/anthropics/skills
```

The import tool automatically:
- Detects single skills vs. directories
- Downloads all files including scripts
- Validates SKILL.md exists
- Skips already-installed skills

---

## External Skill Sources

Import skills from other repositories:

- [**Anthropic's Skills Repository**](https://github.com/anthropics/skills) - Official collection
- [**Claude Cookbooks**](https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills) - Additional examples

---

## Project Structure

```
cursor-skills/
├── .cursor/
│   ├── mcp_example.json       # MCP config template
│   └── rules/
│       └── main_rule.mdc      # Orchestrator rules (for MCP)
├── mcp/
│   └── skills_mcp.py          # MCP server
├── skills/                    # Skills collection
│   ├── ui-design-system/      # ui- prefix for frontend
│   ├── db-postgres/           # db- prefix for database
│   ├── infra-railway/         # infra- prefix for infrastructure
│   ├── tools-linear/          # tools- prefix for integrations
│   ├── feature-build/         # No prefix for core workflow
│   └── ...
├── README.md
└── LICENSE
```

---

## Troubleshooting

### Native Skills Not Discovered

- Ensure skill has `SKILL.md` file with valid frontmatter
- Check `.cursor/skills/` directory exists
- Restart Cursor after adding skills

### MCP Server Not Starting

- Check Cursor logs: View → Output → MCP
- Verify Python 3.10+ installed
- Verify uv installed: https://github.com/astral-sh/uv
- Check paths in `.cursor/mcp.json`

### Skills Not Found (MCP)

- Ensure skill directory has `SKILL.md` file
- Directory name must not start with `.` or `_`
- Verify `skills/` directory exists at repo root

---

## License

This repository is licensed under the [MIT License](LICENSE).

**Third-party skills** imported from external sources retain their original licenses. See individual skill directories for LICENSE files.
