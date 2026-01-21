# Railway MCP Tools Reference

## Tool Parameters

### check-railway-status
No parameters required.

### list-projects
No parameters required.

### list-services
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |

### list-deployments
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| service | string | No | Service name or ID |
| environment | string | No | Environment name |
| limit | number | No | Max deployments (default: 20, max: 1000) |
| json | boolean | No | Return as structured JSON |

### list-variables
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| service | string | No | Service to show variables for |
| environment | string | No | Environment to show variables for |
| json | boolean | No | Output in JSON format |
| kv | boolean | No | Output in KV format |

### set-variables
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| variables | string[] | Yes | Array of "KEY=value" pairs |
| service | string | No | Service to set variables for |
| environment | string | No | Environment to set variables for |
| skipDeploys | boolean | No | Skip triggering deploys |

### get-logs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| logType | "build" \| "deploy" | Yes | Type of logs to retrieve |
| deploymentId | string | No | Specific deployment ID |
| service | string | No | Service to view logs from |
| environment | string | No | Environment to view logs from |
| lines | number | No | Number of lines (disables streaming) |
| filter | string | No | Filter logs by terms |
| json | boolean | No | Return structured JSON data |

### deploy
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| service | string | No | Service to deploy to |
| environment | string | No | Environment to deploy to |
| ci | boolean | No | Stream build logs only |

### generate-domain
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| service | string | No | Service to generate domain for |

### link-service
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| serviceName | string | No | Service name to link |

### link-environment
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| environmentName | string | Yes | Environment name to link |

### create-environment
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| environmentName | string | Yes | Name for new environment |
| duplicateEnvironment | string | No | Environment to duplicate |
| serviceVariables | object[] | No | Service variables to set |

### create-project-and-link
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| projectName | string | Yes | Name for the new project |

### deploy-template
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspacePath | string | Yes | Path to the workspace |
| searchQuery | string | Yes | Template search query |
| templateIndex | number | No | Index if multiple matches |
| teamId | string | No | Team ID |

## Deployment Statuses

| Status | Description |
|--------|-------------|
| BUILDING | Build in progress |
| DEPLOYING | Deployment in progress |
| SUCCESS | Deployment successful and running |
| FAILED | Build or deployment failed |
| CRASHED | Application crashed after deployment |
| REMOVED | Deployment was removed |
| SLEEPING | Application is sleeping (inactive) |

## Common Build Errors

### Railpack Detection Failure
```
Railpack could not determine how to build the app
```
**Solution:** Set root directory to the app subdirectory (e.g., `web/` for monorepos).

### Missing Start Script
```
Script start.sh not found
```
**Solution:** Ensure package.json has a valid `start` script.

### Dependency Installation Failure
```
npm ci failed
```
**Solution:** Check package-lock.json is committed and dependencies are valid.

### Build Command Failure
```
npm run build failed
```
**Solution:** Check build logs for specific errors, fix code issues.

## Log Filter Syntax

Use `filter` parameter with get-logs:

| Pattern | Description |
|---------|-------------|
| `error` | Search for "error" text |
| `@level:error` | Filter by log level |
| `@level:warn AND rate` | Combine filters |
| `@status:500` | Filter by status code |

## Railway Configuration Files

### railway.toml
```toml
[build]
builder = "nixpacks"
buildCommand = "npm run build"

[deploy]
startCommand = "npm run start"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### railway.json (alternative)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start",
    "healthcheckPath": "/"
  }
}
```

## Supported Builders

| Builder | Description |
|---------|-------------|
| `NIXPACKS` | Auto-detect language and build (default) |
| `RAILPACK` | Railway's optimized builder |
| `DOCKERFILE` | Use custom Dockerfile |

## Health Check Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| healthcheckPath | HTTP path to check | None |
| healthcheckTimeout | Timeout in seconds | 300 |

Health checks ensure your app is running before routing traffic.

## Restart Policies

| Policy | Description |
|--------|-------------|
| `ON_FAILURE` | Restart only on failure |
| `ALWAYS` | Always restart |
| `NEVER` | Never restart |

## Multi-Region Deployment

Configure in service settings or railway.toml:

```toml
[deploy]
multiRegionConfig = { "us-west1" = { numReplicas = 1 }, "eu-west1" = { numReplicas = 1 } }
```

## Reference Links

- [Railway Documentation](https://docs.railway.com)
- [Railway CLI Guide](https://docs.railway.com/guides/cli)
- [Public Networking](https://docs.railway.com/guides/public-networking)
- [Environment Variables](https://docs.railway.com/guides/variables)
- [Fixing Common Errors](https://docs.railway.com/guides/fixing-common-errors)
