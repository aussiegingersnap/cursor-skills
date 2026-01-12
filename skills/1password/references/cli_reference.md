# 1Password CLI Reference

Complete command reference for the `op` CLI.

## Authentication Commands

### op account add
Add a new 1Password account.

```bash
op account add [--address <subdomain.1password.com>] [--email <email>]
```

### op signin
Sign in to an account.

```bash
op signin [--account <account>]
```

### op signout
Sign out of an account.

```bash
op signout [--account <account>] [--all] [--forget]
```

### op account list
List all signed-in accounts.

```bash
op account list
```

## Vault Commands

### op vault list
List all vaults.

```bash
op vault list [--format json|human-readable]
```

**Output fields:** `id`, `name`, `type`, `created_at`, `updated_at`

### op vault get
Get details of a vault.

```bash
op vault get <vault> [--format json]
```

### op vault create
Create a new vault.

```bash
op vault create <name> [--description <description>] [--icon <icon>]
```

## Item Commands

### op item list
List items in a vault.

```bash
op item list [--vault <vault>] [--categories <categories>] [--tags <tags>] [--format json]
```

**Category options:** `login`, `password`, `secure-note`, `credit-card`, `identity`, `document`, `database`, `api-credential`, `ssh-key`

### op item get
Get an item.

```bash
op item get <item> [--vault <vault>] [--fields <fields>] [--format json]
```

**Get specific field:**
```bash
op item get "Item Name" --vault "Vault" --fields password
```

**Get multiple fields:**
```bash
op item get "Item Name" --fields "username,password"
```

### op item create
Create a new item.

```bash
op item create --category <category> --title <title> [--vault <vault>] [field=value...]
```

**Examples:**

Login item:
```bash
op item create --category login --title "GitHub" \
  --vault "Development" \
  --url "https://github.com" \
  username=myuser \
  password=mypassword
```

Password item:
```bash
op item create --category password --title "API Key" \
  --vault "Development" \
  password=sk-abc123
```

With custom fields:
```bash
op item create --category password --title "Database" \
  --vault "Development" \
  password=dbpassword \
  "host[text]=db.example.com" \
  "port[text]=5432"
```

**Field type syntax:** `fieldname[type]=value`

| Type | Description |
|------|-------------|
| `text` | Plain text field |
| `concealed` | Hidden/password field |
| `email` | Email address |
| `url` | URL |
| `date` | Date (YYYY-MM-DD) |
| `totp` | One-time password seed |

### op item edit
Edit an existing item.

```bash
op item edit <item> [--vault <vault>] [field=value...]
```

**Update password:**
```bash
op item edit "Item Name" --vault "Vault" password=newpassword
```

**Update custom field:**
```bash
op item edit "Item Name" "host[text]=new-host.example.com"
```

**Add new field:**
```bash
op item edit "Item Name" "newfield[text]=value"
```

### op item delete
Delete an item.

```bash
op item delete <item> [--vault <vault>] [--archive]
```

**Flags:**
- `--archive`: Move to archive instead of permanently deleting

## Secret Injection

### op read
Read a secret by reference.

```bash
op read "op://vault/item/field"
```

**Examples:**
```bash
op read "op://Development/Database/password"
op read "op://Production/AWS/access-key-id"
```

### op run
Run a command with secrets injected.

```bash
op run [--env-file <file>] -- <command>
```

**With env file template:**
```bash
op run --env-file .env.tpl -- npm start
```

**With inline secret:**
```bash
op run -- sh -c 'echo $SECRET'
```
(where SECRET is defined in a .env.tpl file)

### op inject
Inject secrets into a template file.

```bash
op inject --in-file <template> [--out-file <output>]
```

**Template format:**
```
DATABASE_URL=op://Vault/Database/url
API_KEY=op://Vault/API/key
```

## Service Account

### Environment Variable
```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token"
```

### Creating a Service Account
1. Sign in to 1Password.com
2. Go to Settings → Developer → Service Accounts
3. Click "New Service Account"
4. Name the account and select vault access
5. Copy the generated token

### Vault Access Levels
| Permission | Description |
|------------|-------------|
| Read Items | View items in vault |
| Write Items | Create and edit items |
| Manage Vault | Full vault administration |

## Output Formats

### JSON Output
Add `--format json` to any command for JSON output.

```bash
op vault list --format json
op item list --vault "Development" --format json
op item get "Item" --format json
```

### Field Selection
Use `--fields` or JQ for specific data:

```bash
# Get single field value
op item get "Item" --fields password --format json

# With jq
op item get "Item" --format json | jq -r '.fields[] | select(.label=="password") | .value'
```

## Common Patterns

### Export secret to environment
```bash
export API_KEY=$(op read "op://Development/OpenAI/password")
```

### Use in script
```bash
#!/bin/bash
op run --env-file .env.tpl -- ./deploy.sh
```

### Generate password
```bash
op item create --generate-password --category password --title "New Password" --vault "Development"
```

### Bulk operations with jq
```bash
# List all item titles in a vault
op item list --vault "Development" --format json | jq -r '.[].title'

# Get all logins
op item list --vault "Development" --categories login --format json
```

## Error Codes

| Code | Meaning |
|------|---------|
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Not signed in |
| 4 | Item not found |
| 5 | Vault not found |
| 6 | Permission denied |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OP_SERVICE_ACCOUNT_TOKEN` | Service account authentication |
| `OP_ACCOUNT` | Default account shorthand |
| `OP_BIOMETRIC_UNLOCK_ENABLED` | Enable biometric unlock |
| `OP_FORMAT` | Default output format (json/human-readable) |
