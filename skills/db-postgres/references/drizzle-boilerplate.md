# Drizzle PostgreSQL Boilerplate

Complete copy-paste setup for a new project.

## 1. Install Dependencies

```bash
npm install drizzle-orm postgres
npm install -D drizzle-kit tsx @types/node
```

## 2. Environment Variables

Add to `.env.local`:

```bash
DATABASE_URL=postgres://postgres:postgres@localhost:5432/myapp
```

## 3. Drizzle Config

Create `drizzle.config.ts`:

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/db/schema.ts',
  out: './drizzle/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
```

## 4. Database Connection

Create `src/lib/db/index.ts`:

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is required');
}

// Disable prefetch for serverless environments
const queryClient = postgres(connectionString, {
  prepare: false,
});

export const db = drizzle(queryClient, { schema });

// Re-export schema for convenience
export * from './schema';
```

## 5. Schema File

Create `src/lib/db/schema.ts`:

```typescript
import { pgTable, text, timestamp, uuid, varchar, boolean, integer, index, uniqueIndex, pgEnum } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// Define tables here using singular names
// Example:
// export const user = pgTable('user', { ... });

// Define relations here
// Example:
// export const userRelations = relations(user, ({ many }) => ({ ... }));

// Export types
// Example:
// export type User = typeof user.$inferSelect;
// export type NewUser = typeof user.$inferInsert;
```

## 6. Migration Runner

Create `src/lib/db/migrate.ts`:

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import postgres from 'postgres';

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is required');
}

const migrationClient = postgres(connectionString, { max: 1 });
const db = drizzle(migrationClient);

async function runMigrations() {
  console.log('⏳ Running migrations...');
  
  const start = Date.now();
  
  await migrate(db, {
    migrationsFolder: './drizzle/migrations',
  });
  
  const end = Date.now();
  
  console.log(`✅ Migrations complete in ${end - start}ms`);
  
  await migrationClient.end();
  process.exit(0);
}

runMigrations().catch((err) => {
  console.error('❌ Migration failed:', err);
  process.exit(1);
});
```

## 7. Package.json Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "db:generate": "drizzle-kit generate",
    "db:migrate": "tsx src/lib/db/migrate.ts",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio",
    "db:drop": "drizzle-kit drop"
  }
}
```

## 8. TypeScript Config

Ensure `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## 9. Gitignore

Add to `.gitignore`:

```
# Don't ignore migrations - they're part of the codebase
# drizzle/migrations/

# Do ignore local database files if using SQLite for testing
*.db
*.sqlite
```

## Usage

```bash
# Start local PostgreSQL (see docker-local skill)
docker compose up -d postgres

# Generate initial migration
npm run db:generate

# Run migrations
npm run db:migrate

# Open Drizzle Studio for visual database management
npm run db:studio
```
