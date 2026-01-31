# Prisma Migration Patterns for SQLite

Common migration patterns using Prisma with SQLite.

## Migration Workflow

### Development

```bash
# 1. Edit prisma/schema.prisma

# 2. Create migration (interactive)
npx prisma migrate dev --name add_posts_table

# 3. Migration is applied automatically
# Prisma client is regenerated
```

### Quick Iteration (No Migration)

For rapid prototyping, skip migrations and sync directly:

```bash
# Sync schema without creating migration file
npx prisma db push
```

**Warning**: `db push` can cause data loss. Use only in development.

### Production

```bash
# Apply pending migrations (non-interactive)
npx prisma migrate deploy
```

## Common Migration Patterns

### Add a New Model

```prisma
// Before: no Post model

// After: add Post model
model Post {
  id        String   @id @default(cuid())
  title     String
  content   String   @default("")
  published Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

```bash
npx prisma migrate dev --name create_posts_table
```

### Add a Column

```prisma
// Before
model User {
  id    String @id @default(cuid())
  email String @unique
}

// After: add name column
model User {
  id    String  @id @default(cuid())
  email String  @unique
  name  String? // Optional to avoid breaking existing rows
}
```

```bash
npx prisma migrate dev --name add_user_name
```

### Add Required Column with Default

```prisma
// Before
model User {
  id    String @id @default(cuid())
  email String @unique
}

// After: add required role with default
model User {
  id    String @id @default(cuid())
  email String @unique
  role  Role   @default(USER)
}

enum Role {
  ADMIN
  USER
}
```

```bash
npx prisma migrate dev --name add_user_role
```

### Add Relation (One-to-Many)

```prisma
// Before: standalone models
model User {
  id    String @id @default(cuid())
  email String @unique
}

model Post {
  id    String @id @default(cuid())
  title String
}

// After: add relation
model User {
  id    String @id @default(cuid())
  email String @unique
  posts Post[]
}

model Post {
  id       String @id @default(cuid())
  title    String
  authorId String
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)
}
```

```bash
npx prisma migrate dev --name add_post_author_relation
```

### Add Index

```prisma
// Before
model Post {
  id        String   @id @default(cuid())
  authorId  String
  published Boolean  @default(false)
  createdAt DateTime @default(now())
}

// After: add indexes
model Post {
  id        String   @id @default(cuid())
  authorId  String
  published Boolean  @default(false)
  createdAt DateTime @default(now())

  @@index([authorId])
  @@index([published, createdAt])
}
```

```bash
npx prisma migrate dev --name add_post_indexes
```

### Add Unique Constraint

```prisma
// Before
model BookCollaborator {
  id     String @id @default(cuid())
  bookId String
  userId String
}

// After: add unique constraint
model BookCollaborator {
  id     String @id @default(cuid())
  bookId String
  userId String

  @@unique([bookId, userId])
}
```

```bash
npx prisma migrate dev --name add_collaborator_unique_constraint
```

### Rename Column

Prisma detects renames if you use `@map`:

```prisma
// Before
model User {
  id          String @id @default(cuid())
  displayName String
}

// After: rename to 'name' but keep old column name in DB
model User {
  id   String @id @default(cuid())
  name String @map("displayName")
}
```

For true rename without `@map`, Prisma treats it as drop + create. Use a multi-step migration:

```bash
# Step 1: Add new column
npx prisma migrate dev --name add_name_column

# Step 2: Migrate data manually in SQL
# Edit the migration file to add: UPDATE User SET name = displayName;

# Step 3: Drop old column
npx prisma migrate dev --name drop_display_name
```

### Delete Column

```prisma
// Before
model User {
  id       String  @id @default(cuid())
  email    String  @unique
  oldField String?
}

// After: remove oldField
model User {
  id    String @id @default(cuid())
  email String @unique
}
```

```bash
npx prisma migrate dev --name remove_old_field
```

**Warning**: This permanently deletes data in that column.

### Add Enum

```prisma
// Add enum and use it
enum Status {
  DRAFT
  PUBLISHED
  ARCHIVED
}

model Post {
  id     String @id @default(cuid())
  title  String
  status Status @default(DRAFT)
}
```

```bash
npx prisma migrate dev --name add_post_status_enum
```

### Modify Enum

SQLite doesn't support ALTER TYPE, so Prisma recreates the column:

```prisma
// Before
enum Status {
  DRAFT
  PUBLISHED
}

// After: add ARCHIVED
enum Status {
  DRAFT
  PUBLISHED
  ARCHIVED
}
```

```bash
npx prisma migrate dev --name add_archived_status
```

## Data Migrations

For complex data transformations, edit the generated SQL migration:

```bash
# 1. Generate migration
npx prisma migrate dev --name split_name_field --create-only

# 2. Edit the migration file in prisma/migrations/
# Add custom SQL for data transformation

# 3. Apply the migration
npx prisma migrate dev
```

Example migration with data transformation:

```sql
-- prisma/migrations/20240101000000_split_name_field/migration.sql

-- Add new columns
ALTER TABLE "User" ADD COLUMN "firstName" TEXT;
ALTER TABLE "User" ADD COLUMN "lastName" TEXT;

-- Migrate data
UPDATE "User" SET 
  "firstName" = substr("name", 1, instr("name" || ' ', ' ') - 1),
  "lastName" = substr("name", instr("name" || ' ', ' ') + 1)
WHERE "name" IS NOT NULL;

-- Drop old column (optional, do in separate migration for safety)
-- ALTER TABLE "User" DROP COLUMN "name";
```

## SQLite-Specific Considerations

### No ALTER COLUMN Support

SQLite doesn't support modifying column types. Prisma works around this by:
1. Creating a new table with the correct schema
2. Copying data
3. Dropping the old table
4. Renaming the new table

This is automatic but can be slow for large tables.

### Foreign Key Constraints

Enable foreign key enforcement in your Prisma schema:

```prisma
datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}
```

Prisma enables foreign keys automatically.

### Boolean Storage

SQLite stores booleans as integers (0/1). Prisma handles this transparently.

### DateTime Storage

SQLite stores datetimes as TEXT in ISO 8601 format. Prisma handles conversion.

## Migration Commands Reference

```bash
# Create and apply migration
npx prisma migrate dev --name <name>

# Create migration without applying
npx prisma migrate dev --name <name> --create-only

# Apply pending migrations (production)
npx prisma migrate deploy

# Check migration status
npx prisma migrate status

# Reset database (drops all data!)
npx prisma migrate reset

# Mark migration as applied (dangerous)
npx prisma migrate resolve --applied <migration_name>

# Mark migration as rolled back
npx prisma migrate resolve --rolled-back <migration_name>

# Generate Prisma Client without migrating
npx prisma generate

# Sync schema without migration (dev only)
npx prisma db push
```

## Troubleshooting

### "Migration failed to apply cleanly"

The migration SQL has an error. Check:
1. View the SQL in `prisma/migrations/<name>/migration.sql`
2. Look for SQLite-incompatible syntax
3. Fix and re-run

### "Drift detected"

The database schema doesn't match migration history:

```bash
# See what's different
npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-schema-datasource prisma/schema.prisma

# Reset to clean state (dev only)
npx prisma migrate reset
```

### "Migration already applied"

The migration was partially applied. Either:

```bash
# Mark as applied and continue
npx prisma migrate resolve --applied <migration_name>

# Or reset (dev only)
npx prisma migrate reset
```

### "Cannot drop table"

SQLite requires foreign key checks to be disabled. Prisma handles this, but if you're editing SQL manually:

```sql
PRAGMA foreign_keys=OFF;
-- your DROP TABLE
PRAGMA foreign_keys=ON;
```
