# Advanced Migration Patterns

Patterns for complex schema changes in Drizzle ORM.

## Adding Columns

### With Default Value (Safe)

```typescript
// schema.ts
export const user = pgTable('user', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull(),
  // New column with default - safe to add
  isActive: boolean('is_active').notNull().default(true),
});
```

```bash
npm run db:generate
npm run db:migrate
```

### Without Default (Requires Data Migration)

If adding a NOT NULL column without a default to a table with existing data:

1. Add as nullable first
2. Backfill data
3. Alter to NOT NULL

```sql
-- Generated migration (edit manually if needed)
ALTER TABLE "user" ADD COLUMN "new_field" text;

-- Backfill (add manually)
UPDATE "user" SET "new_field" = 'default_value' WHERE "new_field" IS NULL;

-- Make NOT NULL (add manually)
ALTER TABLE "user" ALTER COLUMN "new_field" SET NOT NULL;
```

## Renaming Columns

Drizzle doesn't auto-detect renames. Generate migration, then edit:

```sql
-- Change from DROP + ADD to RENAME
ALTER TABLE "user" RENAME COLUMN "old_name" TO "new_name";
```

## Renaming Tables

Same approach - edit the generated migration:

```sql
ALTER TABLE "old_table" RENAME TO "new_table";
```

## Adding Indexes

```typescript
export const user = pgTable('user', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull(),
  organizationId: uuid('organization_id'),
}, (table) => ({
  emailIdx: uniqueIndex('user_email_idx').on(table.email),
  orgIdx: index('user_organization_idx').on(table.organizationId),
}));
```

For large tables, use `CONCURRENTLY`:

```sql
-- Edit generated migration
CREATE INDEX CONCURRENTLY "user_organization_idx" ON "user" ("organization_id");
```

## Dropping Columns

1. Remove from schema
2. Generate migration
3. Review - data will be lost

```bash
npm run db:generate
# Review the DROP COLUMN statement
npm run db:migrate
```

## Changing Column Types

### Safe Changes

- `varchar(100)` → `varchar(255)` (expanding)
- `integer` → `bigint` (expanding)
- `text` → `varchar(n)` where n > max data length

### Unsafe Changes (Require Care)

- `varchar(255)` → `varchar(100)` (data truncation risk)
- `text` → `integer` (conversion required)

For unsafe changes:

```sql
-- Add new column
ALTER TABLE "user" ADD COLUMN "age_new" integer;

-- Migrate data
UPDATE "user" SET "age_new" = CAST("age" AS integer);

-- Drop old column
ALTER TABLE "user" DROP COLUMN "age";

-- Rename new column
ALTER TABLE "user" RENAME COLUMN "age_new" TO "age";
```

## Adding Enums

```typescript
import { pgEnum } from 'drizzle-orm/pg-core';

export const statusEnum = pgEnum('status', ['pending', 'active', 'archived']);

export const project = pgTable('project', {
  id: uuid('id').primaryKey().defaultRandom(),
  status: statusEnum('status').notNull().default('pending'),
});
```

### Adding Values to Existing Enums

Edit the generated migration:

```sql
ALTER TYPE "status" ADD VALUE 'completed';
```

Note: Cannot remove enum values in PostgreSQL without dropping and recreating.

## Junction Tables

For many-to-many relationships:

```typescript
export const userToProject = pgTable('user_to_project', {
  userId: uuid('user_id').notNull().references(() => user.id, { onDelete: 'cascade' }),
  projectId: uuid('project_id').notNull().references(() => project.id, { onDelete: 'cascade' }),
  role: varchar('role', { length: 50 }).notNull().default('member'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  pk: primaryKey({ columns: [table.userId, table.projectId] }),
}));
```

## Rolling Back Migrations

Drizzle doesn't have built-in rollback. Options:

1. **Restore from backup** (recommended for production)
2. **Write a reverse migration manually**
3. **Use `db:drop`** to remove specific migrations (dev only)

```bash
# Remove last migration file (dev only)
npm run db:drop
```

## Production Migration Checklist

- [ ] Test migration on a copy of production data
- [ ] Backup database before applying
- [ ] Check for long-running queries that might block
- [ ] Use `CONCURRENTLY` for index creation on large tables
- [ ] Have a rollback plan
- [ ] Run during low-traffic period
- [ ] Monitor for locks and performance
