#!/usr/bin/env python3
"""
MCP App Project Initializer

Scaffolds a new MCP App project with server, UI, and configuration files.

Usage:
    python init_mcp_app.py <project-name> [--path <output-directory>]
    
Examples:
    python init_mcp_app.py my-dashboard
    python init_mcp_app.py color-picker --path ./projects
"""

import argparse
import os
import sys
from pathlib import Path

# ============================================
# Template Files
# ============================================

PACKAGE_JSON = """{
  "name": "{name}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "INPUT=mcp-app.html vite build",
    "serve": "npx tsx server.ts",
    "dev": "npm run build && npm run serve",
    "start": "npm run dev"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^0.1.0",
    "@modelcontextprotocol/sdk": "^1.12.0",
    "cors": "^2.8.5",
    "express": "^4.21.0"
  },
  "devDependencies": {
    "@types/cors": "^2.8.17",
    "@types/express": "^5.0.0",
    "@types/node": "^22.0.0",
    "tsx": "^4.19.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0",
    "vite-plugin-singlefile": "^2.0.0"
  }
}
"""

TSCONFIG_JSON = """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["*.ts", "src/**/*.ts"]
}
"""

VITE_CONFIG = """import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: process.env.INPUT,
    },
  },
});
"""

SERVER_TS = '''/**
 * {title} - MCP App Server
 */

console.log("Starting {title} server...");

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import {{
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
}} from "@modelcontextprotocol/ext-apps/server";
import cors from "cors";
import express from "express";
import fs from "node:fs/promises";
import path from "node:path";

const server = new McpServer({{
  name: "{title}",
  version: "1.0.0",
}});

const resourceUri = "ui://{tool_name}/app.html";

// ============================================
// Register Tool with UI
// ============================================

registerAppTool(
  server,
  "{tool_name}",
  {{
    title: "{title}",
    description: "TODO: Describe what this tool does and when to use it",
    inputSchema: {{
      type: "object",
      properties: {{
        query: {{
          type: "string",
          description: "The input query",
        }},
      }},
    }},
    _meta: {{
      ui: {{ resourceUri }},
    }},
  }},
  async (args) => {{
    const query = (args as {{ query?: string }}).query || "default";
    
    return {{
      content: [
        {{
          type: "text",
          text: JSON.stringify({{
            query,
            timestamp: new Date().toISOString(),
            message: `Received: ${{query}}`,
          }}),
        }},
      ],
    }};
  }}
);

// ============================================
// Register UI Resource
// ============================================

registerAppResource(
  server,
  resourceUri,
  resourceUri,
  {{ mimeType: RESOURCE_MIME_TYPE }},
  async () => {{
    const html = await fs.readFile(
      path.join(import.meta.dirname, "dist", "mcp-app.html"),
      "utf-8"
    );
    return {{
      contents: [{{ uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html }}],
    }};
  }}
);

// ============================================
// HTTP Server
// ============================================

const expressApp = express();
expressApp.use(cors());
expressApp.use(express.json());

expressApp.post("/mcp", async (req, res) => {{
  const transport = new StreamableHTTPServerTransport({{
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  }});
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
}});

expressApp.get("/health", (req, res) => {{
  res.json({{ status: "ok" }});
}});

const PORT = process.env.PORT || 3001;
expressApp.listen(PORT, () => {{
  console.log(`Server listening on http://localhost:${{PORT}}/mcp`);
}});
'''

MCP_APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 1rem;
      background: #fafafa;
      color: #1a1a1a;
    }}
    
    .container {{
      max-width: 600px;
      margin: 0 auto;
    }}
    
    h1 {{
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1rem;
    }}
    
    .card {{
      background: white;
      border: 1px solid #e5e5e5;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }}
    
    .label {{
      font-size: 0.75rem;
      font-weight: 500;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }}
    
    .value {{
      font-size: 1rem;
      color: #1a1a1a;
    }}
    
    button {{
      background: #0066cc;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s;
    }}
    
    button:hover {{
      background: #0052a3;
    }}
    
    button:disabled {{
      background: #ccc;
      cursor: not-allowed;
    }}
    
    .status {{
      font-size: 0.875rem;
      color: #666;
      margin-top: 1rem;
    }}
    
    .error {{
      color: #cc0000;
    }}
    
    @media (prefers-color-scheme: dark) {{
      body {{
        background: #1a1a1a;
        color: #fafafa;
      }}
      
      .card {{
        background: #2a2a2a;
        border-color: #3a3a3a;
      }}
      
      .label {{
        color: #999;
      }}
      
      .value {{
        color: #fafafa;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{title}</h1>
    
    <div class="card">
      <div class="label">Result</div>
      <div class="value" id="result">Waiting for data...</div>
    </div>
    
    <button id="refresh-btn">Refresh</button>
    
    <div class="status" id="status"></div>
  </div>
  
  <script type="module" src="/src/mcp-app.ts"></script>
</body>
</html>
"""

MCP_APP_TS = '''/**
 * {title} - UI Logic
 */

import {{ App }} from "@modelcontextprotocol/ext-apps";

const resultEl = document.getElementById("result")!;
const refreshBtn = document.getElementById("refresh-btn")! as HTMLButtonElement;
const statusEl = document.getElementById("status")!;

const app = new App({{
  name: "{title}",
  version: "1.0.0",
}});

// Connect to host
app.connect();
app.log("info", "{title} initialized");

// ============================================
// Handle Tool Results
// ============================================

interface ToolData {{
  query: string;
  timestamp: string;
  message: string;
}}

app.ontoolresult = (result) => {{
  try {{
    const textContent = result.content?.find((c) => c.type === "text");
    if (textContent && "text" in textContent) {{
      const data: ToolData = JSON.parse(textContent.text);
      renderResult(data);
      statusEl.textContent = `Updated: ${{new Date().toLocaleTimeString()}}`;
      statusEl.classList.remove("error");
    }}
  }} catch (error) {{
    console.error("Failed to parse result:", error);
    resultEl.textContent = "Error parsing result";
    statusEl.classList.add("error");
  }}
}};

// ============================================
// Render
// ============================================

function renderResult(data: ToolData) {{
  resultEl.innerHTML = `
    <div><strong>Query:</strong> ${{escapeHtml(data.query)}}</div>
    <div><strong>Message:</strong> ${{escapeHtml(data.message)}}</div>
    <div><strong>Time:</strong> ${{new Date(data.timestamp).toLocaleString()}}</div>
  `;
}}

function escapeHtml(text: string): string {{
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}}

// ============================================
// User Interactions
// ============================================

refreshBtn.addEventListener("click", async () => {{
  refreshBtn.disabled = true;
  statusEl.textContent = "Refreshing...";
  
  try {{
    const result = await app.callServerTool({{
      name: "{tool_name}",
      arguments: {{ query: "refresh-" + Date.now() }},
    }});
    
    const textContent = result.content?.find((c) => c.type === "text");
    if (textContent && "text" in textContent) {{
      const data: ToolData = JSON.parse(textContent.text);
      renderResult(data);
      statusEl.textContent = `Refreshed: ${{new Date().toLocaleTimeString()}}`;
      
      await app.updateModelContext({{
        content: [{{ type: "text", text: `User refreshed: ${{data.message}}` }}],
      }});
    }}
  }} catch (error) {{
    console.error("Refresh failed:", error);
    statusEl.textContent = "Refresh failed";
    statusEl.classList.add("error");
  }} finally {{
    refreshBtn.disabled = false;
  }}
}});
'''

GITIGNORE = """node_modules/
dist/
*.log
.env
.env.local
"""

README = """# {title}

An MCP App that renders interactive UI inside Claude, ChatGPT, and VSCode.

## Quick Start

```bash
# Install dependencies
npm install

# Build and start
npm run dev
```

## Testing

1. Start the server:
   ```bash
   npm run dev
   ```

2. Expose via cloudflared:
   ```bash
   npx cloudflared tunnel --url http://localhost:3001
   ```

3. Add to Claude as custom connector using the cloudflared URL.

4. Ask Claude to use {tool_name}.

## Project Structure

```
{name}/
├── server.ts        # MCP server with tool + resource
├── mcp-app.html     # UI entry point
├── src/
│   └── mcp-app.ts   # UI logic
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Customization

1. Edit `server.ts` to modify tool logic and input schema
2. Edit `mcp-app.html` and `src/mcp-app.ts` for UI changes
3. Run `npm run dev` to rebuild and test
"""


def to_title_case(name: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in name.split("-"))


def to_tool_name(name: str) -> str:
    """Convert to valid tool name (lowercase with hyphens)."""
    return name.lower().replace(" ", "-").replace("_", "-")


def create_project(project_name: str, output_dir: Path) -> None:
    """Create a new MCP App project."""
    project_dir = output_dir / project_name
    
    if project_dir.exists():
        print(f"Error: Directory already exists: {project_dir}")
        sys.exit(1)
    
    # Create directories
    project_dir.mkdir(parents=True)
    (project_dir / "src").mkdir()
    
    # Template variables
    title = to_title_case(project_name)
    tool_name = to_tool_name(project_name)
    
    # Write files
    files = {
        "package.json": PACKAGE_JSON.format(name=project_name),
        "tsconfig.json": TSCONFIG_JSON,
        "vite.config.ts": VITE_CONFIG,
        "server.ts": SERVER_TS.format(title=title, tool_name=tool_name),
        "mcp-app.html": MCP_APP_HTML.format(title=title),
        "src/mcp-app.ts": MCP_APP_TS.format(title=title, tool_name=tool_name),
        ".gitignore": GITIGNORE,
        "README.md": README.format(title=title, name=project_name, tool_name=tool_name),
    }
    
    for filename, content in files.items():
        filepath = project_dir / filename
        filepath.write_text(content)
        print(f"  Created: {filename}")
    
    print(f"\n✓ MCP App project created: {project_dir}")
    print(f"\nNext steps:")
    print(f"  cd {project_dir}")
    print(f"  npm install")
    print(f"  npm run dev")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new MCP App project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_mcp_app.py my-dashboard
  python init_mcp_app.py color-picker --path ./projects
        """
    )
    parser.add_argument(
        "project_name",
        help="Name of the project (kebab-case recommended)"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.path).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    print(f"Creating MCP App: {args.project_name}")
    create_project(args.project_name, output_dir)


if __name__ == "__main__":
    main()
