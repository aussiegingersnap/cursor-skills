# SQLite Migration Patterns

Common migration patterns for SQLite with better-sqlite3.

## Basic Patterns

### Add a Column

```typescript
{
  version: 1,
  name: 'add_phone_to_users',
  up: (db) => {
    // Simple add (will fail if column exists)
    db.exec('ALTER TABLE users ADD COLUMN phone TEXT')
  }
}
```

### Add a Column Safely (Idempotent)

```typescript
{
  version: 2,
  name: 'add_verified_at_to_users',
  up: (db) => {
    const cols = db.prepare("PRAGMA table_info(users)").all() as { name: string }[]
    if (!cols.some(c => c.name === 'verified_at')) {
      db.exec('ALTER TABLE users ADD COLUMN verified_at TEXT')
    }
  }
}
```

### Add Column with Default Value

```typescript
{
  version: 3,
  name: 'add_role_to_users',
  up: (db) => {
    const cols = db.prepare("PRAGMA table_info(users)").all() as { name: string }[]
    if (!cols.some(c => c.name === 'role')) {
      db.exec("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'")
      // Optionally set default for existing rows
      db.exec("UPDATE users SET role = 'member' WHERE role IS NULL")
    }
  }
}
```

### Create a New Table

```typescript
{
  version: 4,
  name: 'create_posts_table',
  up: (db) => {
    db.exec(`
      CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        published_at TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
      );
      
      CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id);
      CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published_at);
    `)
  }
}
```

### Add an Index

```typescript
{
  version: 5,
  name: 'add_email_index',
  up: (db) => {
    db.exec('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
  }
}
```

### Add Multiple Columns

```typescript
{
  version: 6,
  name: 'add_session_tracking_columns',
  up: (db) => {
    const cols = db.prepare("PRAGMA table_info(sessions)").all() as { name: string }[]
    const colNames = cols.map(c => c.name)
    
    if (!colNames.includes('expires_at')) {
      db.exec("ALTER TABLE sessions ADD COLUMN expires_at TEXT DEFAULT (datetime('now', '+30 days'))")
      db.exec("UPDATE sessions SET expires_at = datetime('now', '+30 days') WHERE expires_at IS NULL")
    }
    if (!colNames.includes('last_seen_at')) {
      db.exec("ALTER TABLE sessions ADD COLUMN last_seen_at TEXT DEFAULT (datetime('now'))")
    }
    if (!colNames.includes('request_count')) {
      db.exec('ALTER TABLE sessions ADD COLUMN request_count INTEGER DEFAULT 0')
    }
  }
}
```

## Advanced Patterns

### Create Table with Constraints

```typescript
{
  version: 7,
  name: 'create_audit_log',
  up: (db) => {
    db.exec(`
      CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
        action TEXT NOT NULL CHECK (action IN ('create', 'update', 'delete')),
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        old_value TEXT, -- JSON
        new_value TEXT, -- JSON
        ip_address TEXT,
        user_agent TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );
      
      CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
      CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
      CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
    `)
  }
}
```

### Rename Column (SQLite Workaround)

SQLite doesn't support `ALTER TABLE RENAME COLUMN` before version 3.25. Use table recreation:

```typescript
{
  version: 8,
  name: 'rename_display_name_to_name',
  up: (db) => {
    // Check if old column exists
    const cols = db.prepare("PRAGMA table_info(users)").all() as { name: string }[]
    if (!cols.some(c => c.name === 'display_name')) return
    if (cols.some(c => c.name === 'name')) return
    
    // SQLite 3.25+ supports direct rename
    db.exec('ALTER TABLE users RENAME COLUMN display_name TO name')
  }
}
```

### Add Foreign Key to Existing Table

SQLite doesn't support `ALTER TABLE ADD CONSTRAINT`. Create a new table:

```typescript
{
  version: 9,
  name: 'add_category_fk_to_posts',
  up: (db) => {
    // Create categories table first
    db.exec(`
      CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      )
    `)
    
    // Add column (FK constraints only enforced if PRAGMA foreign_keys = ON)
    const cols = db.prepare("PRAGMA table_info(posts)").all() as { name: string }[]
    if (!cols.some(c => c.name === 'category_id')) {
      db.exec('ALTER TABLE posts ADD COLUMN category_id TEXT REFERENCES categories(id) ON DELETE SET NULL')
      db.exec('CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category_id)')
    }
  }
}
```

### Data Migration

```typescript
{
  version: 10,
  name: 'split_name_into_first_last',
  up: (db) => {
    const cols = db.prepare("PRAGMA table_info(users)").all() as { name: string }[]
    const colNames = cols.map(c => c.name)
    
    // Add new columns
    if (!colNames.includes('first_name')) {
      db.exec('ALTER TABLE users ADD COLUMN first_name TEXT')
    }
    if (!colNames.includes('last_name')) {
      db.exec('ALTER TABLE users ADD COLUMN last_name TEXT')
    }
    
    // Migrate data (split on first space)
    const users = db.prepare('SELECT id, display_name FROM users WHERE display_name IS NOT NULL').all() as { id: string, display_name: string }[]
    
    const update = db.prepare('UPDATE users SET first_name = ?, last_name = ? WHERE id = ?')
    
    for (const user of users) {
      const parts = user.display_name.split(' ')
      const firstName = parts[0] || null
      const lastName = parts.slice(1).join(' ') || null
      update.run(firstName, lastName, user.id)
    }
  }
}
```

### Conditional Migration Based on Data

```typescript
{
  version: 11,
  name: 'migrate_legacy_plan_values',
  up: (db) => {
    // Convert old plan values to new format
    db.exec(`
      UPDATE users SET plan = 'free' WHERE plan = 'basic';
      UPDATE users SET plan = 'pro' WHERE plan IN ('premium', 'enterprise');
    `)
  }
}
```

## Testing Migrations

### Check Current Schema

```sql
-- List all tables
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Show table schema
PRAGMA table_info(users);

-- Show indexes
PRAGMA index_list(users);

-- Show migration history
SELECT * FROM _migrations ORDER BY version;
```

### Reset Local Database

```bash
# Delete local database to test fresh install
rm -rf data/*.db data/*.db-shm data/*.db-wal

# Restart app - schema + all migrations run fresh
npm run dev
```

## Common Gotchas

### 1. SQLite Column Constraints

SQLite ignores most column constraints in `ALTER TABLE ADD COLUMN`:
- `NOT NULL` only works with a default value
- `CHECK` constraints are ignored
- `UNIQUE` constraints require an index

### 2. Datetime Defaults

Use SQLite's datetime function:
```sql
created_at TEXT NOT NULL DEFAULT (datetime('now'))
-- NOT: created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP (different format)
```

### 3. Boolean Values

SQLite uses INTEGER for booleans:
```sql
is_active INTEGER NOT NULL DEFAULT 1  -- 1 = true, 0 = false
```

### 4. JSON Storage

Store as TEXT, parse in application:
```sql
metadata TEXT  -- Store JSON.stringify() result
```

### 5. Array Storage

Options:
1. Separate junction table (normalized)
2. JSON array in TEXT column
3. Comma-separated values (simple but limited)
