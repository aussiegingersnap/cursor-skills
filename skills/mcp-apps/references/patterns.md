# MCP App UI Patterns

Common patterns and examples for building MCP App interfaces.

## Form Pattern

Interactive form with validation and submission.

### Server Tool

```typescript
registerAppTool(server, "config-form", {
  title: "Configuration Form",
  description: "Configure settings with an interactive form",
  inputSchema: {
    type: "object",
    properties: {
      defaults: { type: "object" }
    }
  },
  _meta: { ui: { resourceUri: "ui://config-form/app.html" } }
}, async (args) => {
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        fields: [
          { name: "name", label: "Name", type: "text", required: true },
          { name: "email", label: "Email", type: "email", required: true },
          { name: "role", label: "Role", type: "select", options: ["admin", "user", "guest"] },
          { name: "notifications", label: "Enable Notifications", type: "checkbox" }
        ],
        defaults: args.defaults || {}
      })
    }]
  };
});

registerAppTool(server, "submit-config", {
  title: "Submit Configuration",
  description: "Process form submission",
  inputSchema: {
    type: "object",
    properties: {
      formData: { type: "object" }
    }
  }
}, async (args) => {
  const data = args.formData;
  // Validate and process
  return {
    content: [{ type: "text", text: JSON.stringify({ success: true, data }) }]
  };
});
```

### UI Implementation

```typescript
interface FormField {
  name: string;
  label: string;
  type: "text" | "email" | "select" | "checkbox";
  required?: boolean;
  options?: string[];
}

app.ontoolresult = (result) => {
  const data = JSON.parse(result.content[0].text);
  renderForm(data.fields, data.defaults);
};

function renderForm(fields: FormField[], defaults: Record<string, unknown>) {
  const form = document.createElement("form");
  
  fields.forEach(field => {
    const wrapper = document.createElement("div");
    wrapper.className = "field";
    
    const label = document.createElement("label");
    label.textContent = field.label;
    label.htmlFor = field.name;
    wrapper.appendChild(label);
    
    let input: HTMLElement;
    
    if (field.type === "select" && field.options) {
      const select = document.createElement("select");
      select.name = field.name;
      select.id = field.name;
      field.options.forEach(opt => {
        const option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        select.appendChild(option);
      });
      input = select;
    } else if (field.type === "checkbox") {
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.name = field.name;
      checkbox.id = field.name;
      checkbox.checked = !!defaults[field.name];
      input = checkbox;
    } else {
      const textInput = document.createElement("input");
      textInput.type = field.type;
      textInput.name = field.name;
      textInput.id = field.name;
      textInput.required = !!field.required;
      textInput.value = String(defaults[field.name] || "");
      input = textInput;
    }
    
    wrapper.appendChild(input);
    form.appendChild(wrapper);
  });
  
  const submit = document.createElement("button");
  submit.type = "submit";
  submit.textContent = "Save";
  form.appendChild(submit);
  
  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    const result = await app.callServerTool({
      name: "submit-config",
      arguments: { formData: data }
    });
    
    const response = JSON.parse(result.content[0].text);
    if (response.success) {
      await app.updateModelContext({
        content: [{ type: "text", text: "Configuration saved successfully" }]
      });
    }
  };
  
  document.getElementById("app")!.appendChild(form);
}
```

## Dashboard Pattern

Real-time metrics dashboard with auto-refresh.

### Server Tool

```typescript
registerAppTool(server, "dashboard", {
  title: "System Dashboard",
  description: "Real-time system metrics dashboard",
  inputSchema: { type: "object" },
  _meta: { ui: { resourceUri: "ui://dashboard/app.html" } }
}, async () => {
  return {
    content: [{ type: "text", text: JSON.stringify(getMetrics()) }]
  };
});

registerAppTool(server, "get-metrics", {
  title: "Get Current Metrics",
  inputSchema: { type: "object" }
}, async () => {
  return {
    content: [{ type: "text", text: JSON.stringify(getMetrics()) }]
  };
});

function getMetrics() {
  return {
    cpu: Math.random() * 100,
    memory: Math.random() * 100,
    requests: Math.floor(Math.random() * 1000),
    errors: Math.floor(Math.random() * 10),
    timestamp: new Date().toISOString()
  };
}
```

### UI Implementation

```typescript
interface Metrics {
  cpu: number;
  memory: number;
  requests: number;
  errors: number;
  timestamp: string;
}

let pollInterval: number | undefined;

app.ontoolresult = (result) => {
  const metrics = JSON.parse(result.content[0].text);
  renderDashboard(metrics);
  startPolling();
};

function renderDashboard(metrics: Metrics) {
  const container = document.getElementById("dashboard")!;
  container.innerHTML = `
    <div class="metric">
      <div class="metric-label">CPU Usage</div>
      <div class="metric-value">${metrics.cpu.toFixed(1)}%</div>
      <div class="metric-bar">
        <div class="metric-fill" style="width: ${metrics.cpu}%"></div>
      </div>
    </div>
    <div class="metric">
      <div class="metric-label">Memory Usage</div>
      <div class="metric-value">${metrics.memory.toFixed(1)}%</div>
      <div class="metric-bar">
        <div class="metric-fill" style="width: ${metrics.memory}%"></div>
      </div>
    </div>
    <div class="metric">
      <div class="metric-label">Requests/min</div>
      <div class="metric-value">${metrics.requests}</div>
    </div>
    <div class="metric ${metrics.errors > 5 ? 'error' : ''}">
      <div class="metric-label">Errors</div>
      <div class="metric-value">${metrics.errors}</div>
    </div>
    <div class="timestamp">Last updated: ${new Date(metrics.timestamp).toLocaleTimeString()}</div>
  `;
}

function startPolling() {
  if (pollInterval) return;
  
  pollInterval = setInterval(async () => {
    try {
      const result = await app.callServerTool({
        name: "get-metrics",
        arguments: {}
      });
      const metrics = JSON.parse(result.content[0].text);
      renderDashboard(metrics);
    } catch (error) {
      console.error("Poll failed:", error);
    }
  }, 5000);
}

// Clean up on unload
window.addEventListener("beforeunload", () => {
  if (pollInterval) {
    clearInterval(pollInterval);
  }
});
```

## List Selection Pattern

Selectable list with actions.

### Server Tool

```typescript
registerAppTool(server, "item-list", {
  title: "Item List",
  description: "Browse and select items",
  inputSchema: { type: "object" },
  _meta: { ui: { resourceUri: "ui://item-list/app.html" } }
}, async () => {
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        items: [
          { id: "1", name: "Item One", status: "active" },
          { id: "2", name: "Item Two", status: "pending" },
          { id: "3", name: "Item Three", status: "completed" }
        ]
      })
    }]
  };
});

registerAppTool(server, "select-item", {
  title: "Select Item",
  inputSchema: {
    type: "object",
    properties: { itemId: { type: "string" } }
  }
}, async (args) => {
  const item = findItem(args.itemId);
  return {
    content: [{ type: "text", text: JSON.stringify(item) }]
  };
});
```

### UI Implementation

```typescript
interface Item {
  id: string;
  name: string;
  status: "active" | "pending" | "completed";
}

let selectedId: string | null = null;

app.ontoolresult = (result) => {
  const data = JSON.parse(result.content[0].text);
  renderList(data.items);
};

function renderList(items: Item[]) {
  const list = document.getElementById("list")!;
  list.innerHTML = "";
  
  items.forEach(item => {
    const row = document.createElement("div");
    row.className = `list-item ${item.id === selectedId ? "selected" : ""}`;
    row.innerHTML = `
      <span class="item-name">${item.name}</span>
      <span class="item-status status-${item.status}">${item.status}</span>
    `;
    
    row.onclick = () => selectItem(item);
    list.appendChild(row);
  });
}

async function selectItem(item: Item) {
  selectedId = item.id;
  
  // Update UI immediately
  document.querySelectorAll(".list-item").forEach(el => {
    el.classList.remove("selected");
  });
  event?.currentTarget?.classList.add("selected");
  
  // Call server for details
  const result = await app.callServerTool({
    name: "select-item",
    arguments: { itemId: item.id }
  });
  
  const details = JSON.parse(result.content[0].text);
  renderDetails(details);
  
  // Update model context
  await app.updateModelContext({
    content: [{ type: "text", text: `User selected: ${item.name}` }]
  });
}
```

## Wizard/Stepper Pattern

Multi-step workflow with navigation.

### Server Tools

```typescript
const STEPS = ["setup", "configure", "review", "complete"];

registerAppTool(server, "wizard-start", {
  title: "Start Wizard",
  inputSchema: { type: "object" },
  _meta: { ui: { resourceUri: "ui://wizard/app.html" } }
}, async () => {
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        step: 0,
        totalSteps: STEPS.length,
        stepName: STEPS[0],
        data: {}
      })
    }]
  };
});

registerAppTool(server, "wizard-next", {
  title: "Next Step",
  inputSchema: {
    type: "object",
    properties: {
      currentStep: { type: "number" },
      stepData: { type: "object" }
    }
  }
}, async (args) => {
  const nextStep = args.currentStep + 1;
  // Validate and process current step data
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        step: nextStep,
        totalSteps: STEPS.length,
        stepName: STEPS[nextStep],
        data: args.stepData
      })
    }]
  };
});
```

### UI Implementation

```typescript
interface WizardState {
  step: number;
  totalSteps: number;
  stepName: string;
  data: Record<string, unknown>;
}

let state: WizardState;

app.ontoolresult = (result) => {
  state = JSON.parse(result.content[0].text);
  renderWizard();
};

function renderWizard() {
  const container = document.getElementById("wizard")!;
  
  // Progress bar
  const progress = (state.step / (state.totalSteps - 1)) * 100;
  
  container.innerHTML = `
    <div class="progress-bar">
      <div class="progress-fill" style="width: ${progress}%"></div>
    </div>
    <div class="step-indicators">
      ${Array.from({ length: state.totalSteps }, (_, i) => `
        <div class="step-dot ${i <= state.step ? 'active' : ''}">
          ${i + 1}
        </div>
      `).join('')}
    </div>
    <div class="step-content" id="step-content">
      ${renderStepContent()}
    </div>
    <div class="wizard-actions">
      ${state.step > 0 ? '<button id="prev-btn">Back</button>' : ''}
      ${state.step < state.totalSteps - 1 
        ? '<button id="next-btn">Next</button>' 
        : '<button id="finish-btn">Finish</button>'}
    </div>
  `;
  
  // Attach event handlers
  document.getElementById("next-btn")?.addEventListener("click", nextStep);
  document.getElementById("prev-btn")?.addEventListener("click", prevStep);
  document.getElementById("finish-btn")?.addEventListener("click", finish);
}

function renderStepContent(): string {
  switch (state.stepName) {
    case "setup":
      return `<h2>Setup</h2><input id="name" placeholder="Enter name" />`;
    case "configure":
      return `<h2>Configure</h2><select id="option"><option>Option A</option><option>Option B</option></select>`;
    case "review":
      return `<h2>Review</h2><pre>${JSON.stringify(state.data, null, 2)}</pre>`;
    case "complete":
      return `<h2>Complete!</h2><p>Your configuration has been saved.</p>`;
    default:
      return "";
  }
}

async function nextStep() {
  const stepData = collectStepData();
  const result = await app.callServerTool({
    name: "wizard-next",
    arguments: { currentStep: state.step, stepData }
  });
  state = JSON.parse(result.content[0].text);
  renderWizard();
}

function collectStepData(): Record<string, unknown> {
  const data: Record<string, unknown> = { ...state.data };
  document.querySelectorAll("#step-content input, #step-content select").forEach((el) => {
    const input = el as HTMLInputElement | HTMLSelectElement;
    data[input.id] = input.value;
  });
  return data;
}

async function finish() {
  await app.updateModelContext({
    content: [{ type: "text", text: `Wizard completed with data: ${JSON.stringify(state.data)}` }]
  });
}
```

## Framework Examples

### React

```tsx
import { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";

const app = new App({ name: "React MCP App", version: "1.0.0" });

function MyApp() {
  const [data, setData] = useState<unknown>(null);
  
  useEffect(() => {
    app.connect();
    app.ontoolresult = (result) => {
      setData(JSON.parse(result.content[0].text));
    };
  }, []);
  
  return (
    <div>
      {data ? <DataView data={data} /> : <div>Loading...</div>}
    </div>
  );
}
```

### Vue

```vue
<script setup lang="ts">
import { App } from "@modelcontextprotocol/ext-apps";
import { ref, onMounted } from "vue";

const app = new App({ name: "Vue MCP App", version: "1.0.0" });
const data = ref<unknown>(null);

onMounted(() => {
  app.connect();
  app.ontoolresult = (result) => {
    data.value = JSON.parse(result.content[0].text);
  };
});
</script>

<template>
  <div>
    <DataView v-if="data" :data="data" />
    <div v-else>Loading...</div>
  </div>
</template>
```

### Svelte

```svelte
<script lang="ts">
import { App } from "@modelcontextprotocol/ext-apps";
import { onMount } from "svelte";

const app = new App({ name: "Svelte MCP App", version: "1.0.0" });
let data: unknown = null;

onMount(() => {
  app.connect();
  app.ontoolresult = (result) => {
    data = JSON.parse(result.content[0].text);
  };
});
</script>

{#if data}
  <DataView {data} />
{:else}
  <div>Loading...</div>
{/if}
```
