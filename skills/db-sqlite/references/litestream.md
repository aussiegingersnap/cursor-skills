# Litestream Backup for SQLite on Railway

Continuous SQLite replication to S3-compatible storage. Zero-config automatic backups with ~10 second recovery point objective.

## Why Litestream

| Problem | Litestream Solution |
|---------|---------------------|
| Volume data loss on container crash | Continuous streaming to bucket |
| Manual backup scripts | Automatic, real-time replication |
| Point-in-time recovery | WAL-based granular restore |
| External S3 providers | Railway Buckets (same network) |

## Quick Setup (Railway + Bucket)

### 1. Create Railway Bucket

```bash
# Via Railway CLI
railway add --service bucket

# Or via Dashboard:
# Project → Add → Bucket → Name: "{project}-backups"
```

Railway auto-injects these env vars to your service:
- `BUCKET_NAME`
- `BUCKET_ENDPOINT` 
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### 2. Add Litestream Config

Create `litestream.yml` in project root:

```yaml
# litestream.yml
dbs:
  - path: /data/study-bible.db
    replicas:
      - type: s3
        bucket: ${BUCKET_NAME}
        path: litestream/study-bible
        endpoint: ${BUCKET_ENDPOINT}
        access-key-id: ${AWS_ACCESS_KEY_ID}
        secret-access-key: ${AWS_SECRET_ACCESS_KEY}
        region: ${AWS_REGION}
        sync-interval: 10s
```

### 3. Update nixpacks.toml

```toml
# nixpacks.toml
[phases.setup]
nixPkgs = ["nodejs_22", "npm"]

[phases.install]
cmds = [
  "npm ci",
  "wget -qO- https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-amd64.tar.gz | tar xz",
  "mv litestream /usr/local/bin/"
]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "/usr/local/bin/litestream replicate -config litestream.yml -exec 'npm run start'"
```

### 4. Update railway.toml

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "/usr/local/bin/litestream replicate -config litestream.yml -exec 'npm run start'"
healthcheckPath = "/api/version"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### 5. Add Restore Script

Create `scripts/restore-db.sh`:

```bash
#!/bin/bash
# Restore database from Litestream backup before starting app
# Used when volume is empty (new deploy or wipe)

DB_PATH="${DB_PATH:-/data}/study-bible.db"

if [ -f "$DB_PATH" ]; then
  echo "[Litestream] Database exists, skipping restore"
else
  echo "[Litestream] No database found, attempting restore..."
  litestream restore -config litestream.yml "$DB_PATH" || true
  
  if [ -f "$DB_PATH" ]; then
    echo "[Litestream] Restore successful"
  else
    echo "[Litestream] No backup found, starting fresh"
  fi
fi
```

Update `railway.toml`:

```toml
[deploy]
startCommand = "chmod +x scripts/restore-db.sh && ./scripts/restore-db.sh && /usr/local/bin/litestream replicate -config litestream.yml -exec 'npm run start'"
```

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Your Next.js   │     │   Litestream     │     │ Railway Bucket  │
│      App        │────▶│    Process       │────▶│   (S3-compat)   │
│                 │     │                  │     │                 │
│ SQLite writes   │     │ Monitors WAL     │     │ Stores WAL      │
│ to /data/app.db │     │ Streams changes  │     │ segments        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

1. **App writes to SQLite** - Normal database operations
2. **Litestream monitors WAL** - Watches for new write-ahead log entries
3. **Streams to bucket** - Uploads WAL segments every `sync-interval` (default 10s)
4. **On restart** - Restore script rebuilds DB from bucket if missing

## Recovery Scenarios

### Scenario: Container Restart

1. Container stops (deploy, crash, etc.)
2. New container starts
3. Restore script runs, finds no DB on volume
4. Litestream restores from bucket
5. App starts with recovered data

**Data loss**: Up to 10 seconds (sync-interval)

### Scenario: Volume Wipe

Same as container restart - Litestream backup in bucket is unaffected.

### Scenario: Bucket Corruption

You lose your backup source. Database on volume is still primary source.

**Mitigation**: Enable bucket versioning in Railway.

## Manual Operations

### Check Backup Status

```bash
railway shell

# View Litestream status
litestream generations -config litestream.yml /data/study-bible.db

# List WAL segments in bucket
litestream wal -config litestream.yml /data/study-bible.db
```

### Force Restore

```bash
railway shell

# Stop the app first (or it will conflict)
pkill -f "npm run start"

# Restore to specific point (optional timestamp)
litestream restore -config litestream.yml /data/study-bible.db

# Or restore to specific generation
litestream restore -config litestream.yml -generation <gen-id> /data/study-bible.db
```

### Manual Snapshot

```bash
railway shell

# Force immediate sync
litestream snapshots -config litestream.yml /data/study-bible.db
```

### Download Backup Locally

```bash
# From local machine
railway run litestream restore -config litestream.yml -o ./backup.db /data/study-bible.db
```

## Configuration Options

### litestream.yml Reference

```yaml
dbs:
  - path: /data/study-bible.db
    replicas:
      - type: s3
        bucket: ${BUCKET_NAME}
        path: litestream/study-bible  # Prefix in bucket
        endpoint: ${BUCKET_ENDPOINT}
        access-key-id: ${AWS_ACCESS_KEY_ID}
        secret-access-key: ${AWS_SECRET_ACCESS_KEY}
        region: ${AWS_REGION}
        
        # Sync interval (how often to upload WAL)
        sync-interval: 10s
        
        # Snapshot interval (full DB backup)
        snapshot-interval: 1h
        
        # Retention (how long to keep old generations)
        retention: 168h  # 7 days
        
        # Retention check interval
        retention-check-interval: 1h
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BUCKET_NAME` | Railway bucket name | `study-bible-backups` |
| `BUCKET_ENDPOINT` | S3 endpoint URL | `https://xxx.r2.cloudflarestorage.com` |
| `AWS_ACCESS_KEY_ID` | Bucket access key | Auto-injected |
| `AWS_SECRET_ACCESS_KEY` | Bucket secret | Auto-injected |
| `AWS_REGION` | Bucket region | `auto` |

## Cost Analysis

### Railway Buckets Pricing

- Storage: $0.015/GB/month
- Egress: Free (within Railway network)
- Requests: Free

### Example Costs

| Database Size | Monthly Backup Cost |
|---------------|---------------------|
| 10 MB | $0.00015 |
| 100 MB | $0.0015 |
| 1 GB | $0.015 |
| 10 GB | $0.15 |

With 7-day retention, multiply by ~1.5x for WAL history.

## Troubleshooting

### Litestream Not Starting

```bash
# Check if litestream binary exists
railway shell
which litestream
litestream version
```

If missing, nixpacks install failed. Check build logs.

### Restore Fails: "no matching backups"

No backup exists yet. This is expected on first deploy.

```bash
# Check if backup exists
litestream generations -config litestream.yml /data/study-bible.db
```

### Database Locked During Restore

Stop the app before restoring:

```bash
railway shell
pkill -f "npm run start"
litestream restore -config litestream.yml /data/study-bible.db
# Redeploy to restart app
```

### Environment Variables Not Found

Ensure bucket is linked to your service in Railway dashboard:
- Project → Bucket → Settings → Link to service

### WAL Mode Not Enabled

Litestream requires WAL mode. Verify in your app:

```typescript
db.pragma('journal_mode = WAL')
```

Check current mode:
```bash
railway shell
sqlite3 /data/study-bible.db "PRAGMA journal_mode;"
# Should output: wal
```

## Alternative: External S3

If not using Railway Buckets, any S3-compatible storage works:

### Cloudflare R2

```yaml
replicas:
  - type: s3
    bucket: my-bucket
    path: litestream
    endpoint: https://<account-id>.r2.cloudflarestorage.com
    access-key-id: ${R2_ACCESS_KEY}
    secret-access-key: ${R2_SECRET_KEY}
    region: auto
```

### AWS S3

```yaml
replicas:
  - type: s3
    bucket: my-bucket
    path: litestream
    region: us-east-1
    access-key-id: ${AWS_ACCESS_KEY_ID}
    secret-access-key: ${AWS_SECRET_ACCESS_KEY}
```

### Backblaze B2

```yaml
replicas:
  - type: s3
    bucket: my-bucket
    path: litestream
    endpoint: https://s3.us-west-002.backblazeb2.com
    access-key-id: ${B2_KEY_ID}
    secret-access-key: ${B2_APPLICATION_KEY}
    region: us-west-002
```

## Checklist

- [ ] Railway Bucket created and linked to service
- [ ] `litestream.yml` in project root
- [ ] `nixpacks.toml` installs litestream binary
- [ ] `railway.toml` starts litestream wrapper
- [ ] `scripts/restore-db.sh` handles empty volume
- [ ] WAL mode enabled in app code
- [ ] Test restore on staging before production
