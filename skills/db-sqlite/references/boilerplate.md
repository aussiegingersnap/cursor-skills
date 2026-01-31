# SQLite + Prisma Boilerplate

Complete setup pattern for SQLite with Prisma in TypeScript projects.

## Prisma Schema (`prisma/schema.prisma`)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

// ============================================
// Example: User model
// ============================================

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts Post[]
}

enum Role {
  ADMIN
  USER
}

// ============================================
// Example: Post model with relation
// ============================================

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String   @default("")
  published Boolean  @default(false)
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  author User @relation(fields: [authorId], references: [id], onDelete: Cascade)

  @@index([authorId])
  @@index([published, createdAt])
}
```

## Prisma Client Singleton (`src/lib/db/index.ts`)

```typescript
import { PrismaClient } from '@prisma/client'

// Prevent multiple instances during hot reload in development
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' 
    ? ['query', 'error', 'warn'] 
    : ['error'],
})

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

// Named export for convenience
export const db = prisma

export default prisma
```

## Environment Files

### Development (`.env.local`)

```bash
# SQLite database in prisma folder (gitignored)
DATABASE_URL="file:./dev.db"
```

### Production (Railway)

```bash
# SQLite database on Railway volume
DATABASE_URL="file:/data/app.db"
```

### Example (`.env.example`)

```bash
# Database
# Development: file:./dev.db
# Production (Railway): file:/data/app.db
DATABASE_URL="file:./dev.db"
```

## Package.json Scripts

```json
{
  "scripts": {
    "db:generate": "prisma generate",
    "db:migrate": "prisma migrate dev",
    "db:migrate:prod": "prisma migrate deploy",
    "db:push": "prisma db push",
    "db:studio": "prisma studio",
    "db:reset": "prisma migrate reset",
    "db:seed": "tsx prisma/seed.ts",
    "postinstall": "prisma generate"
  }
}
```

## Seed File (`prisma/seed.ts`)

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding database...')

  // Create admin user
  const admin = await prisma.user.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: {
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'ADMIN',
    },
  })

  console.log('Created admin:', admin.email)

  // Create sample posts
  await prisma.post.createMany({
    data: [
      { title: 'First Post', content: 'Hello world!', authorId: admin.id, published: true },
      { title: 'Draft Post', content: 'Work in progress...', authorId: admin.id },
    ],
    skipDuplicates: true,
  })

  console.log('Seeding complete!')
}

main()
  .catch((e) => {
    console.error('Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
```

Add to `package.json`:

```json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

## .gitignore Additions

```gitignore
# Prisma
prisma/dev.db
prisma/dev.db-journal
*.db
*.db-journal

# Data folder (Railway volume mount)
data/
```

## Package Dependencies

```json
{
  "dependencies": {
    "@prisma/client": "^6.0.0"
  },
  "devDependencies": {
    "prisma": "^6.0.0",
    "tsx": "^4.0.0"
  }
}
```

## Query Examples (`src/lib/db/queries.ts`)

```typescript
import { prisma } from './index'
import type { User, Post, Prisma } from '@prisma/client'

// ============================================
// User queries
// ============================================

export async function getUserById(id: string): Promise<User | null> {
  return prisma.user.findUnique({
    where: { id },
  })
}

export async function getUserByEmail(email: string): Promise<User | null> {
  return prisma.user.findUnique({
    where: { email },
  })
}

export async function createUser(data: Prisma.UserCreateInput): Promise<User> {
  return prisma.user.create({ data })
}

export async function updateUser(
  id: string, 
  data: Prisma.UserUpdateInput
): Promise<User> {
  return prisma.user.update({
    where: { id },
    data,
  })
}

export async function deleteUser(id: string): Promise<void> {
  await prisma.user.delete({ where: { id } })
}

// ============================================
// Post queries
// ============================================

export async function getPublishedPosts(options?: {
  take?: number
  skip?: number
}): Promise<Post[]> {
  return prisma.post.findMany({
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    take: options?.take ?? 10,
    skip: options?.skip ?? 0,
  })
}

export async function getPostsByAuthor(authorId: string): Promise<Post[]> {
  return prisma.post.findMany({
    where: { authorId },
    orderBy: { createdAt: 'desc' },
  })
}

export async function getPostWithAuthor(id: string) {
  return prisma.post.findUnique({
    where: { id },
    include: { author: true },
  })
}

export async function createPost(
  data: Prisma.PostCreateInput
): Promise<Post> {
  return prisma.post.create({ data })
}

export async function publishPost(id: string): Promise<Post> {
  return prisma.post.update({
    where: { id },
    data: { published: true },
  })
}

// ============================================
// Transactions
// ============================================

export async function createUserWithPost(
  userData: Prisma.UserCreateInput,
  postTitle: string
) {
  return prisma.$transaction(async (tx) => {
    const user = await tx.user.create({ data: userData })
    
    const post = await tx.post.create({
      data: {
        title: postTitle,
        authorId: user.id,
      },
    })
    
    return { user, post }
  })
}
```

## Type Exports

Prisma auto-generates types. Import them from `@prisma/client`:

```typescript
import type { User, Post, Role, Prisma } from '@prisma/client'

// Use generated types
function formatUser(user: User): string {
  return `${user.name} (${user.email})`
}

// Use input types for create/update
function validateUserInput(data: Prisma.UserCreateInput): boolean {
  return data.email.includes('@')
}

// Use with relations
type UserWithPosts = Prisma.UserGetPayload<{
  include: { posts: true }
}>
```

## Next.js API Route Example

```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

export async function GET() {
  const users = await prisma.user.findMany({
    select: {
      id: true,
      email: true,
      name: true,
      role: true,
    },
  })
  
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  
  const user = await prisma.user.create({
    data: {
      email: body.email,
      name: body.name,
    },
  })
  
  return NextResponse.json(user, { status: 201 })
}
```

## Railway Startup Script

For production deployments, run migrations before starting the app:

```json
{
  "scripts": {
    "start": "npm run db:migrate:prod && next start"
  }
}
```

Or in `railway.toml`:

```toml
[deploy]
startCommand = "npx prisma migrate deploy && npm run start"
```
