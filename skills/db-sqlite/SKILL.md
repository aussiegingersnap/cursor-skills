---
name: db-sqlite
description: SQLite database management with better-sqlite3, versioned migrations, and Railway deployment. This skill should be used when creating database schemas, writing migrations, managing SQLite on Railway volumes, or troubleshooting database issues.
---

# SQLite Database Skill

Comprehensive patterns for SQLite database management in Node.js/TypeScript projects using `better-sqlite3`, including a versioned migration system and Railway deployment workflows.

## When to Use This Skill

- Setting up SQLite in a new project
- Writing database migrations
- Adding tables or columns to existing schemas
- Deploying SQLite to Railway with persistent volumes
- Backing up or restoring production databases
- Troubleshooting database issues

## Core Concepts

### SQLite vs Network Databases

SQLite is appropriate when:
- Single server/container deployment
- Read-heavy workloads (or moderate writes)
- Simplicity is valued over horizontal scaling
- Local-first or embedded scenarios

Consider PostgreSQL when:
- Multiple servers need database access
- Remote database inspection is required
- High write concurrency is expected
- Team needs direct database access for debugging

### Railway Deployment Constraints

SQLite on Railway requires understanding these constraints:

1. **Volume mounting** - Database file must live on a Railway volume (not container filesystem)
2. **No remote access** - Cannot connect database GUI tools directly to production
3. **Single container** - Only one instance can write to the database
4. **`railway run` limitations** - One-off commands don't have volume access; use Litestream restore instead

### Critical: Railway Volume Path vs Container Path

**This is the #1 cause of data loss on Railway SQLite deployments.**

Railway volumes mount at a specific path (e.g., `/data`). But your app runs in `/app/` by default. If your code writes to `./data/study-bible.db`, it creates the file at `/app/data/study-bible.db` — **which is NOT on the volume** and gets destroyed on every deploy.

**Solution**: Set `DB_PATH=/data` in Railway environment variables.

```
# Wrong (data lost on each deploy):
/app/data/study-bible.db  ← Container filesystem, not persistent

# Correct (data persists):
/data/study-bible.db      ← Railway volume, persistent + backed up
```

**Verify your setup**:
```bash
railway variables | grep DB_PATH
# Should show: DB_PATH=/data

railway variables | grep RAILWAY_VOLUME_MOUNT_PATH
# Should show: RAILWAY_VOLUME_MOUNT_PATH=/data
```

## Database Setup Pattern

### Package Installation

```bash
npm install better-sqlite3
npm install -D @types/better-sqlite3
```

### Directory Structure

```
src/lib/db/
├── index.ts      # Connection, migrations, types
├── schema.sql    # Base schema (for fresh installs)
└── queries.ts    # Typed query functions
```

### Environment Configuration

```bash
# .env.local (development) — NOT NEEDED
# DB_PATH defaults to ./data (process.cwd()/data)
# Only set if you want a custom location

# Railway (production) — REQUIRED
# Must match the volume mount path exactly
railway variables --set DB_PATH=/data
```

**The app code should default correctly:**
```typescript
const DB_DIR = process.env.DB_PATH || path.join(process.cwd(), 'data')
const DB_FILE = path.join(DB_DIR, 'study-bible.db')
```

| Environment | DB_PATH | Actual Path | Persistent? |
|------------|---------|-------------|-------------|
| Local dev | (unset) | `./data/study-bible.db` | ✅ Yes |
| Railway | `/data` | `/data/study-bible.db` | ✅ Yes (volume) |
| Railway | (unset) | `/app/data/study-bible.db` | ❌ **NO** — lost on deploy |

### Connection Singleton

See `references/boilerplate.md` for the complete database initialization pattern with:
- Singleton connection management
- WAL mode for performance
- Schema initialization
- Automatic migration running

## Migration System

The migration system provides versioned, tracked schema changes that run automatically on application startup.

### Migration Structure

```typescript
interface Migration {
  version: number    // Incrementing integer
  name: string       // Descriptive snake_case name
  up: (db: Database.Database) => void
}
```

### Writing Migrations

See `references/migrations.md` for complete patterns including:
- Adding columns safely
- Creating new tables
- Adding indexes
- Complex multi-step migrations

### Key Rules

1. **Never modify existing migrations** - They may have already run in production
2. **Always increment version** - Each migration gets the next integer
3. **Use IF NOT EXISTS** - Makes migrations idempotent
4. **Check columns before adding** - SQLite doesn't support `IF NOT EXISTS` for columns
5. **Update schema.sql too** - Keep base schema in sync for fresh installs

### Adding a New Migration

1. Open `src/lib/db/index.ts`
2. Add new entry to `MIGRATIONS` array:

```typescript
{
  version: 5, // Next version number
  name: 'add_feature_x_table',
  up: (db) => {
    db.exec(`
      CREATE TABLE IF NOT EXISTS feature_x (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        data TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );
      CREATE INDEX IF NOT EXISTS idx_feature_x_user ON feature_x(user_id);
    `)
  }
}
```

3. Update `schema.sql` with the same table definition
4. Add TypeScript interface to `index.ts`
5. Deploy - migration runs automatically on startup

## Railway Operations

### Environment Variables

Required Railway configuration:
```
DB_PATH=/data
RAILWAY_VOLUME_MOUNT_PATH=/data
```

### Shell Access

```bash
# Open interactive shell in Railway container
cd /path/to/project/web
railway shell

# Inside container:
sqlite3 /data/study-bible.db
.tables
.schema users
SELECT * FROM users LIMIT 5;
.quit
```

### Download Production Database

**⚠️ `railway run cp` does NOT work** — one-off commands don't have volume access.

Use Litestream to restore from the backup bucket:

```bash
# 1. Install Litestream locally (macOS)
curl -sLO https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-darwin-amd64.zip
unzip litestream-v0.3.13-darwin-amd64.zip
mkdir -p ~/bin && mv litestream ~/bin/
export PATH="$HOME/bin:$PATH"

# 2. Create restore config with Railway Bucket credentials
cat > /tmp/litestream-restore.yml << 'EOF'
dbs:
  - path: ./study-bible-prod.db
    replicas:
      - type: s3
        bucket: YOUR_BUCKET_NAME
        path: replica
        endpoint: https://storage.railway.app
        access-key-id: YOUR_ACCESS_KEY_ID
        secret-access-key: YOUR_SECRET_ACCESS_KEY
        region: iad
        force-path-style: true
EOF

# 3. Restore from backup
cd /path/to/project/web
litestream restore -config /tmp/litestream-restore.yml -o ./study-bible-prod.db ./study-bible-prod.db

# 4. Verify and use
sqlite3 ./study-bible-prod.db ".tables"
```

**Get bucket credentials from Railway:**
```bash
railway variables | grep AWS
# AWS_S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ENDPOINT_URL
```

### Restore Database (DANGEROUS)

```bash
# Upload local database to production
# ⚠️ This overwrites all production data
railway run cp ./local-database.db /data/study-bible.db
```

### Check Migration Status

```bash
railway shell
sqlite3 /data/study-bible.db "SELECT * FROM _migrations ORDER BY version;"
```

## Schema Conventions

### Primary Keys

Use TEXT UUIDs for user-facing entities, INTEGER for internal-only:

```sql
-- User-facing: TEXT PRIMARY KEY
CREATE TABLE users (
  id TEXT PRIMARY KEY,  -- nanoid or UUID
  ...
);

-- Internal singleton: INTEGER with CHECK
CREATE TABLE reading_progress (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  ...
);
```

### Timestamps

Always use ISO 8601 TEXT format:

```sql
created_at TEXT NOT NULL DEFAULT (datetime('now')),
updated_at TEXT NOT NULL DEFAULT (datetime('now'))
```

### Foreign Keys

Enable cascading deletes for dependent data:

```sql
user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE
```

### Indexes

Create indexes for:
- Foreign keys used in JOINs
- Columns used in WHERE clauses
- Columns used in ORDER BY

```sql
CREATE INDEX IF NOT EXISTS idx_notes_session ON notes(session_id);
CREATE INDEX IF NOT EXISTS idx_notes_passage ON notes(book, chapter);
```

### CHECK Constraints

Use for enums and validation:

```sql
plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro')),
role TEXT NOT NULL CHECK (role IN ('user', 'assistant'))
```

## Common PRAGMA Commands

```sql
-- Check current journal mode
PRAGMA journal_mode;

-- Get table info
PRAGMA table_info(users);

-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- Check foreign keys are enabled
PRAGMA foreign_keys;

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';
```

## Continuous Backup with Litestream

Litestream provides real-time SQLite replication to S3-compatible storage. Combined with Railway Buckets, this gives you continuous backups without external providers.

**See `references/litestream.md` for complete setup guide.**

### Quick Overview

1. Litestream monitors SQLite WAL changes
2. Streams changes to Railway Bucket every ~10 seconds
3. On container restart, restores from bucket if local DB is missing
4. ~10 second recovery point objective (RPO)

### Minimal Setup

```bash
# 1. Create Railway Bucket
railway add --service bucket

# 2. Add litestream.yml to project root
# 3. Update nixpacks.toml to install litestream
# 4. Update railway.toml start command
# 5. Add restore script for empty volumes
```

### Cost

Railway Buckets: $0.015/GB/month with free egress.

| DB Size | Monthly Cost |
|---------|--------------|
| 100 MB | ~$0.002 |
| 1 GB | ~$0.02 |
| 10 GB | ~$0.15 |

## Troubleshooting

### "database is locked"

SQLite allows only one writer at a time. Solutions:
1. Ensure WAL mode is enabled: `db.pragma('journal_mode = WAL')`
2. Keep transactions short
3. Use connection pooling sparingly (usually singleton is fine)

### Migration Failed Mid-Way

Migrations run in transactions, so partial failures rollback. To fix:
1. Check `_migrations` table for applied versions
2. Fix the failing migration code
3. Redeploy

### Column Already Exists

Always check before adding columns:

```typescript
const cols = db.prepare("PRAGMA table_info(users)").all() as { name: string }[]
if (!cols.some(c => c.name === 'new_column')) {
  db.exec('ALTER TABLE users ADD COLUMN new_column TEXT')
}
```

### Production Database Corrupted

1. Stop the Railway service
2. Download the corrupted database for analysis
3. Restore from backup
4. Investigate what caused corruption

## References

- `references/boilerplate.md` - Complete database setup code
- `references/migrations.md` - Migration patterns and examples
- `references/litestream.md` - Continuous backup setup with Railway Buckets
- [Railway Storage Buckets](https://docs.railway.com/guides/storage-buckets) - S3-compatible buckets on Railway
- [Litestream Docs](https://litestream.io/) - SQLite replication tool
