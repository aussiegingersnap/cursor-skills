# MCP Apps Boilerplate

Complete project setup for building MCP Apps with interactive UI.

## Project Structure

```
my-mcp-app/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── server.ts           # MCP server with tool + resource
├── mcp-app.html        # UI entry point
└── src/
    └── mcp-app.ts      # UI logic with App class
```

## package.json

```json
{
  "name": "my-mcp-app",
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
```

## tsconfig.json

```json
{
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
```

## vite.config.ts

```typescript
import { defineConfig } from "vite";
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
```

## server.ts

```typescript
/**
 * MCP App Server
 * Registers a tool with UI and serves the bundled HTML resource
 */

console.log("Starting MCP App server...");

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import cors from "cors";
import express from "express";
import fs from "node:fs/promises";
import path from "node:path";

// Create MCP server
const server = new McpServer({
  name: "My MCP App Server",
  version: "1.0.0",
});

// UI resource URI (ui:// scheme indicates MCP App)
const resourceUri = "ui://my-tool/app.html";

// ============================================
// Register Tool with UI
// ============================================

registerAppTool(
  server,
  "my-tool",
  {
    title: "My Tool",
    description: "An interactive tool with UI. Use this when the user wants to...",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "The query to process",
        },
      },
    },
    _meta: {
      ui: { resourceUri },
    },
  },
  async (args) => {
    // Process the tool call
    const query = (args as { query?: string }).query || "default";
    
    // Return data that will be sent to the UI
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            query,
            timestamp: new Date().toISOString(),
            message: `Processed query: ${query}`,
          }),
        },
      ],
    };
  }
);

// ============================================
// Register UI Resource
// ============================================

registerAppResource(
  server,
  resourceUri,
  resourceUri,
  { mimeType: RESOURCE_MIME_TYPE },
  async () => {
    // Read the bundled HTML file
    const html = await fs.readFile(
      path.join(import.meta.dirname, "dist", "mcp-app.html"),
      "utf-8"
    );
    return {
      contents: [
        {
          uri: resourceUri,
          mimeType: RESOURCE_MIME_TYPE,
          text: html,
        },
      ],
    };
  }
);

// ============================================
// HTTP Server
// ============================================

const expressApp = express();
expressApp.use(cors());
expressApp.use(express.json());

// MCP endpoint
expressApp.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

// Health check
expressApp.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// Start server
const PORT = process.env.PORT || 3001;
expressApp.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}/mcp`);
});
```

## mcp-app.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My MCP App</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 1rem;
      background: #fafafa;
      color: #1a1a1a;
    }
    
    .container {
      max-width: 600px;
      margin: 0 auto;
    }
    
    h1 {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1rem;
    }
    
    .card {
      background: white;
      border: 1px solid #e5e5e5;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    
    .label {
      font-size: 0.75rem;
      font-weight: 500;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }
    
    .value {
      font-size: 1rem;
      color: #1a1a1a;
    }
    
    button {
      background: #0066cc;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s;
    }
    
    button:hover {
      background: #0052a3;
    }
    
    button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    
    .status {
      font-size: 0.875rem;
      color: #666;
      margin-top: 1rem;
    }
    
    .error {
      color: #cc0000;
    }
    
    @media (prefers-color-scheme: dark) {
      body {
        background: #1a1a1a;
        color: #fafafa;
      }
      
      .card {
        background: #2a2a2a;
        border-color: #3a3a3a;
      }
      
      .label {
        color: #999;
      }
      
      .value {
        color: #fafafa;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>My MCP App</h1>
    
    <div class="card">
      <div class="label">Result</div>
      <div class="value" id="result">Waiting for data...</div>
    </div>
    
    <button id="refresh-btn">Refresh Data</button>
    
    <div class="status" id="status"></div>
  </div>
  
  <script type="module" src="/src/mcp-app.ts"></script>
</body>
</html>
```

## src/mcp-app.ts

```typescript
/**
 * MCP App UI Logic
 * Communicates with the MCP server via the App class
 */

import { App } from "@modelcontextprotocol/ext-apps";

// DOM elements
const resultEl = document.getElementById("result")!;
const refreshBtn = document.getElementById("refresh-btn")! as HTMLButtonElement;
const statusEl = document.getElementById("status")!;

// Initialize app
const app = new App({
  name: "My MCP App",
  version: "1.0.0",
});

// ============================================
// Connect to Host
// ============================================

app.connect();
app.log("info", "MCP App initialized");

// ============================================
// Handle Tool Results
// ============================================

interface ToolData {
  query: string;
  timestamp: string;
  message: string;
}

app.ontoolresult = (result) => {
  try {
    const textContent = result.content?.find((c) => c.type === "text");
    if (textContent && "text" in textContent) {
      const data: ToolData = JSON.parse(textContent.text);
      renderResult(data);
      statusEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
      statusEl.classList.remove("error");
    }
  } catch (error) {
    console.error("Failed to parse result:", error);
    resultEl.textContent = "Error parsing result";
    statusEl.textContent = "Parse error";
    statusEl.classList.add("error");
  }
};

// ============================================
// Render Functions
// ============================================

function renderResult(data: ToolData) {
  resultEl.innerHTML = `
    <div><strong>Query:</strong> ${escapeHtml(data.query)}</div>
    <div><strong>Message:</strong> ${escapeHtml(data.message)}</div>
    <div><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</div>
  `;
}

function escapeHtml(text: string): string {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ============================================
// User Interactions
// ============================================

refreshBtn.addEventListener("click", async () => {
  refreshBtn.disabled = true;
  statusEl.textContent = "Refreshing...";
  
  try {
    const result = await app.callServerTool({
      name: "my-tool",
      arguments: { query: "refresh-" + Date.now() },
    });
    
    const textContent = result.content?.find((c) => c.type === "text");
    if (textContent && "text" in textContent) {
      const data: ToolData = JSON.parse(textContent.text);
      renderResult(data);
      statusEl.textContent = `Refreshed at ${new Date().toLocaleTimeString()}`;
      statusEl.classList.remove("error");
      
      // Notify model about the refresh
      await app.updateModelContext({
        content: [{ type: "text", text: `User refreshed data: ${data.message}` }],
      });
    }
  } catch (error) {
    console.error("Refresh failed:", error);
    statusEl.textContent = "Refresh failed";
    statusEl.classList.add("error");
  } finally {
    refreshBtn.disabled = false;
  }
});
```

## .gitignore

```gitignore
node_modules/
dist/
*.log
.env
.env.local
```

## Running the App

```bash
# Install dependencies
npm install

# Build UI and start server
npm run dev
```

## Testing Locally

1. Start the server:
   ```bash
   npm run dev
   ```

2. Expose via cloudflared:
   ```bash
   npx cloudflared tunnel --url http://localhost:3001
   ```

3. Add to Claude as custom connector using the cloudflared URL.

4. Ask Claude to use your tool.
