# SQLite Database Boilerplate

Complete setup pattern for SQLite with better-sqlite3 in TypeScript projects.

## Database Client (`src/lib/db/index.ts`)

```typescript
/**
 * SQLite Database Client
 * Local-first storage using better-sqlite3
 */

import Database from 'better-sqlite3'
import path from 'path'
import fs from 'fs'

// Database file location
const DB_DIR = process.env.DB_PATH || path.join(process.cwd(), 'data')
const DB_FILE = path.join(DB_DIR, 'app.db')

// Singleton instance
let db: Database.Database | null = null

/**
 * Get or create the database connection
 */
export function getDb(): Database.Database {
  if (db) return db

  console.log(`[DB] Initializing database at: ${DB_FILE}`)
  
  // Ensure data directory exists
  if (!fs.existsSync(DB_DIR)) {
    console.log(`[DB] Creating data directory: ${DB_DIR}`)
    fs.mkdirSync(DB_DIR, { recursive: true })
  }

  // Create database connection
  db = new Database(DB_FILE)
  
  // Enable WAL mode for better performance
  db.pragma('journal_mode = WAL')
  
  // Initialize schema and run migrations
  initSchema(db)
  runMigrations(db)

  console.log('[DB] Database initialization complete')
  return db
}

/**
 * Close the database connection
 */
export function closeDb(): void {
  if (db) {
    db.close()
    db = null
  }
}

// ============================================
// Migration System
// ============================================

interface Migration {
  version: number
  name: string
  up: (db: Database.Database) => void
}

/**
 * All migrations in order. Add new migrations to the end.
 * Each migration runs once and is tracked in _migrations table.
 */
const MIGRATIONS: Migration[] = [
  // Add migrations here as the schema evolves
  // {
  //   version: 1,
  //   name: 'add_feature_column',
  //   up: (db) => {
  //     db.exec('ALTER TABLE users ADD COLUMN feature TEXT')
  //   }
  // },
]

/**
 * Run versioned migrations. Each migration runs exactly once.
 * Safe to call multiple times - already-run migrations are skipped.
 */
function runMigrations(database: Database.Database): void {
  console.log('[DB] Checking migrations...')
  
  try {
    // Create migrations tracking table
    database.exec(`
      CREATE TABLE IF NOT EXISTS _migrations (
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TEXT NOT NULL DEFAULT (datetime('now'))
      )
    `)
    
    // Get already-applied migrations
    const applied = database.prepare('SELECT version FROM _migrations').all() as { version: number }[]
    const appliedVersions = new Set(applied.map(m => m.version))
    
    // Run pending migrations
    const pending = MIGRATIONS.filter(m => !appliedVersions.has(m.version))
    
    if (pending.length === 0) {
      console.log('[DB] No pending migrations')
      return
    }
    
    console.log(`[DB] Running ${pending.length} migration(s)...`)
    
    for (const migration of pending.sort((a, b) => a.version - b.version)) {
      console.log(`[DB] Running migration ${migration.version}: ${migration.name}`)
      
      // Run in transaction for safety
      database.exec('BEGIN TRANSACTION')
      try {
        migration.up(database)
        database.prepare('INSERT INTO _migrations (version, name) VALUES (?, ?)').run(migration.version, migration.name)
        database.exec('COMMIT')
        console.log(`[DB] ✓ Migration ${migration.version} complete`)
      } catch (err) {
        database.exec('ROLLBACK')
        throw err
      }
    }
    
    console.log('[DB] All migrations complete')
  } catch (error) {
    console.error('[DB] Migration error:', error)
    throw error
  }
}

/**
 * Initialize database schema
 */
function initSchema(database: Database.Database): void {
  // Option 1: Load from schema.sql file (development)
  const schemaPath = path.join(__dirname, 'schema.sql')
  
  if (fs.existsSync(schemaPath)) {
    console.log('[DB] Loading schema from file:', schemaPath)
    const schema = fs.readFileSync(schemaPath, 'utf-8')
    database.exec(schema)
  } else {
    // Option 2: Inline schema (production - __dirname may not work)
    console.log('[DB] Using inline schema (production mode)')
    database.exec(`
      -- Add your base schema here
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        display_name TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      );
    `)
  }
}

// ============================================
// Types
// ============================================

export interface DbUser {
  id: string
  email: string | null
  display_name: string | null
  created_at: string
}

// Add more interfaces as tables are created
```

## Base Schema (`src/lib/db/schema.sql`)

```sql
-- Application SQLite Schema
-- This file defines the base schema for fresh installs
-- Migrations handle incremental changes

-- ============================================
-- Users
-- ============================================

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  display_name TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

## Query Functions (`src/lib/db/queries.ts`)

```typescript
import { getDb, DbUser } from './index'

/**
 * Get user by ID
 */
export function getUserById(id: string): DbUser | undefined {
  const db = getDb()
  return db.prepare('SELECT * FROM users WHERE id = ?').get(id) as DbUser | undefined
}

/**
 * Get user by email
 */
export function getUserByEmail(email: string): DbUser | undefined {
  const db = getDb()
  return db.prepare('SELECT * FROM users WHERE email = ?').get(email) as DbUser | undefined
}

/**
 * Create a new user
 */
export function createUser(user: Omit<DbUser, 'created_at'>): DbUser {
  const db = getDb()
  
  db.prepare(`
    INSERT INTO users (id, email, display_name)
    VALUES (?, ?, ?)
  `).run(user.id, user.email, user.display_name)
  
  return db.prepare('SELECT * FROM users WHERE id = ?').get(user.id) as DbUser
}

/**
 * Update user
 */
export function updateUser(id: string, updates: Partial<Omit<DbUser, 'id' | 'created_at'>>): boolean {
  const db = getDb()
  
  const fields: string[] = []
  const values: unknown[] = []
  
  if (updates.email !== undefined) {
    fields.push('email = ?')
    values.push(updates.email)
  }
  if (updates.display_name !== undefined) {
    fields.push('display_name = ?')
    values.push(updates.display_name)
  }
  
  if (fields.length === 0) return false
  
  values.push(id)
  const result = db.prepare(`UPDATE users SET ${fields.join(', ')} WHERE id = ?`).run(...values)
  
  return result.changes > 0
}

/**
 * Delete user
 */
export function deleteUser(id: string): boolean {
  const db = getDb()
  const result = db.prepare('DELETE FROM users WHERE id = ?').run(id)
  return result.changes > 0
}
```

## .gitignore Additions

```gitignore
# SQLite
*.db
*.db-shm
*.db-wal
data/
```

## Package.json Dependencies

```json
{
  "dependencies": {
    "better-sqlite3": "^12.6.0"
  },
  "devDependencies": {
    "@types/better-sqlite3": "^7.6.13"
  }
}
```
