# Lucia Auth Skill

Minimal, secure authentication for Next.js App Router using Oslo (crypto/cookies), Arctic (OAuth), and Drizzle ORM + SQLite. No Auth.js/NextAuth bloat. Follows post-Lucia deprecation patterns from lucia-auth.com.

## When to Use

- Adding authentication to a Next.js project
- Implementing OAuth (Google, Apple, Instagram)
- Managing user sessions (sign-in, sign-out, session validation)
- When the user asks about auth, login, or session management
- Projects using Drizzle + SQLite stack

## Core Principles

- **Minimal deps**: `oslo`, `arctic`, `drizzle-orm`, `better-sqlite3` (or `@libsql/client` for Railway/Turso)
- **Own your schema**: Simple `users`, `sessions`, `accounts` tables in Drizzle/SQLite
- **Sessions**: Cookie-based (opaque token), stored as hash in DB for revocation. Raw token in cookie, SHA-256 hash in database.
- **OAuth**: Use Arctic providers with PKCE. Handle state/code_verifier in secure httpOnly cookies.
- **Routes**: Route handlers for OAuth callbacks (`/api/auth/[provider]/callback`)
- **Security**: Always HttpOnly, Secure (prod), SameSite=Lax, Path=/, short-lived state/verifier cookies (10min)
- **TypeScript strict**: Infer types from Drizzle schema

## Dependencies

```bash
npm install oslo arctic drizzle-orm better-sqlite3 nanoid
npm install -D @types/better-sqlite3
```

## Database Schema

Create `src/db/schema.ts`:

```ts
import { sqliteTable, text, integer, uniqueIndex } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: text('id').primaryKey(), // nanoid or ulid
  name: text('name'),
  email: text('email').notNull(),
  picture: text('picture'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),
});

export const sessions = sqliteTable('sessions', {
  id: text('id').primaryKey(), // SHA-256 hash of session token
  userId: text('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),
});

export const accounts = sqliteTable('accounts', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
  provider: text('provider').notNull(), // 'google', 'apple', 'instagram'
  providerAccountId: text('provider_account_id').notNull(),
  accessToken: text('access_token'),
  refreshToken: text('refresh_token'),
  expiresAt: integer('expires_at', { mode: 'timestamp' }),
}, (t) => ({
  providerUnique: uniqueIndex('accounts_provider_unique').on(t.provider, t.providerAccountId),
}));

// Type exports
export type User = typeof users.$inferSelect;
export type Session = typeof sessions.$inferSelect;
```

## Auth Library

Create `src/lib/auth.ts`:

```ts
import { sha256 } from "oslo/crypto";
import { encodeBase64url, encodeHexLowerCase } from "oslo/encoding";
import { cookies } from "next/headers";
import { db } from "@/db";
import { sessions, users } from "@/db/schema";
import { eq } from "drizzle-orm";

// Constants
const SESSION_COOKIE_NAME = "session";
const SESSION_DURATION_MS = 30 * 24 * 60 * 60 * 1000; // 30 days
const REFRESH_THRESHOLD_MS = 15 * 24 * 60 * 60 * 1000; // 15 days

const isProduction = process.env.NODE_ENV === "production";

// --- Token Generation & Hashing ---

export function generateSessionToken(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return encodeBase64url(bytes);
}

export async function hashToken(token: string): Promise<string> {
  return encodeHexLowerCase(await sha256(new TextEncoder().encode(token)));
}

// --- Session Management ---

export async function createSession(userId: string): Promise<{ token: string; expiresAt: Date }> {
  const token = generateSessionToken();
  const sessionId = await hashToken(token);
  const expiresAt = new Date(Date.now() + SESSION_DURATION_MS);

  await db.insert(sessions).values({
    id: sessionId,
    userId,
    expiresAt,
  });

  return { token, expiresAt };
}

export async function validateSession(token: string): Promise<{
  session: (typeof sessions.$inferSelect & { user: typeof users.$inferSelect }) | null;
  fresh: boolean;
}> {
  const sessionId = await hashToken(token);

  const result = await db
    .select()
    .from(sessions)
    .innerJoin(users, eq(sessions.userId, users.id))
    .where(eq(sessions.id, sessionId))
    .get();

  if (!result) {
    return { session: null, fresh: false };
  }

  const { sessions: session, users: user } = result;

  // Expired - delete and return null
  if (session.expiresAt < new Date()) {
    await db.delete(sessions).where(eq(sessions.id, sessionId));
    return { session: null, fresh: false };
  }

  // Check if we should extend (sliding window)
  const shouldRefresh = session.expiresAt.getTime() - Date.now() < REFRESH_THRESHOLD_MS;

  if (shouldRefresh) {
    const newExpiry = new Date(Date.now() + SESSION_DURATION_MS);
    await db.update(sessions).set({ expiresAt: newExpiry }).where(eq(sessions.id, sessionId));
    return { session: { ...session, expiresAt: newExpiry, user }, fresh: true };
  }

  return { session: { ...session, user }, fresh: false };
}

export async function invalidateSession(token: string): Promise<void> {
  const sessionId = await hashToken(token);
  await db.delete(sessions).where(eq(sessions.id, sessionId));
}

export async function invalidateAllUserSessions(userId: string): Promise<void> {
  await db.delete(sessions).where(eq(sessions.userId, userId));
}

// --- Cookie Management ---

export function setSessionCookie(token: string, expiresAt: Date): void {
  cookies().set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: isProduction,
    expires: expiresAt,
    path: "/",
  });
}

export function deleteSessionCookie(): void {
  cookies().set(SESSION_COOKIE_NAME, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: isProduction,
    maxAge: 0,
    path: "/",
  });
}

export function getSessionCookie(): string | undefined {
  return cookies().get(SESSION_COOKIE_NAME)?.value;
}

// --- Auth Helper for Server Components/Actions ---

export async function getAuth(): Promise<{
  user: typeof users.$inferSelect | null;
  session: typeof sessions.$inferSelect | null;
}> {
  const token = getSessionCookie();
  if (!token) {
    return { user: null, session: null };
  }

  const { session, fresh } = await validateSession(token);

  if (!session) {
    deleteSessionCookie();
    return { user: null, session: null };
  }

  // Refresh cookie if session was extended
  if (fresh) {
    setSessionCookie(token, session.expiresAt);
  }

  return { user: session.user, session };
}
```

## OAuth Utilities

Create `src/lib/oauth.ts`:

```ts
import { Google, Apple, generateState, generateCodeVerifier } from "arctic";
import { cookies } from "next/headers";

// Initialize providers
export const google = new Google(
  process.env.GOOGLE_CLIENT_ID!,
  process.env.GOOGLE_CLIENT_SECRET!,
  process.env.GOOGLE_REDIRECT_URI!
);

export const apple = new Apple(
  process.env.APPLE_CLIENT_ID!,
  process.env.APPLE_TEAM_ID!,
  process.env.APPLE_KEY_ID!,
  process.env.APPLE_PRIVATE_KEY!,
  process.env.APPLE_REDIRECT_URI!
);

// Cookie names
const STATE_COOKIE = "oauth_state";
const VERIFIER_COOKIE = "oauth_code_verifier";
const COOKIE_MAX_AGE = 60 * 10; // 10 minutes

const isProduction = process.env.NODE_ENV === "production";

// --- State & Verifier Cookies ---

export function setOAuthCookies(state: string, codeVerifier?: string): void {
  const options = {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: isProduction,
    maxAge: COOKIE_MAX_AGE,
    path: "/",
  };

  cookies().set(STATE_COOKIE, state, options);
  if (codeVerifier) {
    cookies().set(VERIFIER_COOKIE, codeVerifier, options);
  }
}

export function getOAuthCookies(): { state: string | undefined; codeVerifier: string | undefined } {
  return {
    state: cookies().get(STATE_COOKIE)?.value,
    codeVerifier: cookies().get(VERIFIER_COOKIE)?.value,
  };
}

export function clearOAuthCookies(): void {
  const options = {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: isProduction,
    maxAge: 0,
    path: "/",
  };
  cookies().set(STATE_COOKIE, "", options);
  cookies().set(VERIFIER_COOKIE, "", options);
}

// --- URL Generators ---

export async function createGoogleAuthURL(): Promise<URL> {
  const state = generateState();
  const codeVerifier = generateCodeVerifier();
  const url = await google.createAuthorizationURL(state, codeVerifier, {
    scopes: ["openid", "email", "profile"],
  });
  setOAuthCookies(state, codeVerifier);
  return url;
}

export async function createAppleAuthURL(): Promise<URL> {
  const state = generateState();
  const url = await apple.createAuthorizationURL(state, {
    scopes: ["name", "email"],
  });
  setOAuthCookies(state);
  return url;
}
```

## OAuth Route Handlers

### Google Login Initiation

Create `src/app/api/auth/google/route.ts`:

```ts
import { redirect } from "next/navigation";
import { createGoogleAuthURL } from "@/lib/oauth";

export async function GET(): Promise<Response> {
  const url = await createGoogleAuthURL();
  return redirect(url.toString());
}
```

### Google Callback

Create `src/app/api/auth/google/callback/route.ts`:

```ts
import { OAuth2RequestError } from "arctic";
import { google, getOAuthCookies, clearOAuthCookies } from "@/lib/oauth";
import { createSession, setSessionCookie } from "@/lib/auth";
import { db } from "@/db";
import { users, accounts } from "@/db/schema";
import { eq, and } from "drizzle-orm";
import { nanoid } from "nanoid";
import { redirect } from "next/navigation";

interface GoogleUser {
  sub: string;
  name: string;
  email: string;
  picture: string;
}

export async function GET(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");

  const { state: storedState, codeVerifier } = getOAuthCookies();

  // Validate state
  if (!code || !state || !storedState || state !== storedState || !codeVerifier) {
    clearOAuthCookies();
    return redirect("/login?error=invalid_state");
  }

  try {
    // Exchange code for tokens
    const tokens = await google.validateAuthorizationCode(code, codeVerifier);

    // Fetch user info
    const response = await fetch("https://openidconnect.googleapis.com/v1/userinfo", {
      headers: { Authorization: `Bearer ${tokens.accessToken}` },
    });
    const googleUser: GoogleUser = await response.json();

    clearOAuthCookies();

    // Check for existing account
    const existingAccount = await db
      .select()
      .from(accounts)
      .where(and(eq(accounts.provider, "google"), eq(accounts.providerAccountId, googleUser.sub)))
      .get();

    let userId: string;

    if (existingAccount) {
      // Update tokens
      await db
        .update(accounts)
        .set({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken ?? existingAccount.refreshToken,
          expiresAt: tokens.accessTokenExpiresAt,
        })
        .where(eq(accounts.id, existingAccount.id));

      userId = existingAccount.userId;
    } else {
      // Check if user exists by email
      const existingUser = await db
        .select()
        .from(users)
        .where(eq(users.email, googleUser.email))
        .get();

      if (existingUser) {
        userId = existingUser.id;
      } else {
        // Create new user
        userId = nanoid();
        await db.insert(users).values({
          id: userId,
          name: googleUser.name,
          email: googleUser.email,
          picture: googleUser.picture,
        });
      }

      // Link account
      await db.insert(accounts).values({
        id: nanoid(),
        userId,
        provider: "google",
        providerAccountId: googleUser.sub,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        expiresAt: tokens.accessTokenExpiresAt,
      });
    }

    // Create session
    const { token, expiresAt } = await createSession(userId);
    setSessionCookie(token, expiresAt);

    return redirect("/");
  } catch (e) {
    clearOAuthCookies();

    if (e instanceof OAuth2RequestError) {
      console.error("OAuth error:", e.message);
      return redirect("/login?error=oauth_error");
    }

    throw e;
  }
}
```

### Apple Callback

Create `src/app/api/auth/apple/callback/route.ts`:

```ts
import { OAuth2RequestError } from "arctic";
import { apple, getOAuthCookies, clearOAuthCookies } from "@/lib/oauth";
import { createSession, setSessionCookie } from "@/lib/auth";
import { db } from "@/db";
import { users, accounts } from "@/db/schema";
import { eq, and } from "drizzle-orm";
import { nanoid } from "nanoid";
import { redirect } from "next/navigation";
import { decodeIdToken } from "arctic";

interface AppleIdToken {
  sub: string;
  email: string;
}

// Apple sends POST request with form data
export async function POST(request: Request): Promise<Response> {
  const formData = await request.formData();
  const code = formData.get("code") as string;
  const state = formData.get("state") as string;

  // Apple sends user info only on first auth
  const userDataString = formData.get("user") as string | null;
  let userName: string | null = null;
  if (userDataString) {
    try {
      const userData = JSON.parse(userDataString);
      userName = `${userData.name?.firstName || ""} ${userData.name?.lastName || ""}`.trim() || null;
    } catch {
      // Ignore parse errors
    }
  }

  const { state: storedState } = getOAuthCookies();

  if (!code || !state || !storedState || state !== storedState) {
    clearOAuthCookies();
    return redirect("/login?error=invalid_state");
  }

  try {
    const tokens = await apple.validateAuthorizationCode(code);
    const idToken = decodeIdToken(tokens.idToken) as AppleIdToken;

    clearOAuthCookies();

    const existingAccount = await db
      .select()
      .from(accounts)
      .where(and(eq(accounts.provider, "apple"), eq(accounts.providerAccountId, idToken.sub)))
      .get();

    let userId: string;

    if (existingAccount) {
      await db
        .update(accounts)
        .set({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken ?? existingAccount.refreshToken,
        })
        .where(eq(accounts.id, existingAccount.id));

      userId = existingAccount.userId;
    } else {
      const existingUser = await db
        .select()
        .from(users)
        .where(eq(users.email, idToken.email))
        .get();

      if (existingUser) {
        userId = existingUser.id;
      } else {
        userId = nanoid();
        await db.insert(users).values({
          id: userId,
          name: userName,
          email: idToken.email,
          picture: null,
        });
      }

      await db.insert(accounts).values({
        id: nanoid(),
        userId,
        provider: "apple",
        providerAccountId: idToken.sub,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      });
    }

    const { token, expiresAt } = await createSession(userId);
    setSessionCookie(token, expiresAt);

    return redirect("/");
  } catch (e) {
    clearOAuthCookies();

    if (e instanceof OAuth2RequestError) {
      console.error("OAuth error:", e.message);
      return redirect("/login?error=oauth_error");
    }

    throw e;
  }
}
```

## Sign Out Action

Create `src/app/actions/auth.ts`:

```ts
"use server";

import { redirect } from "next/navigation";
import { getSessionCookie, invalidateSession, deleteSessionCookie } from "@/lib/auth";

export async function signOut(): Promise<void> {
  const token = getSessionCookie();

  if (token) {
    await invalidateSession(token);
  }

  deleteSessionCookie();
  redirect("/login");
}
```

## Proxy (Next.js 16+) / Middleware (Next.js 16 and earlier)

> **Next.js 16 Breaking Change**: `middleware.ts` has been replaced by `proxy.ts`.
> The proxy runs on the Node.js runtime (not Edge) and the export is `proxy` not `middleware`.

### Next.js 16+ (proxy.ts)

Create `src/proxy.ts` for protected routes:

```ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/settings", "/profile"];
const authRoutes = ["/login", "/signup"];

export function proxy(request: NextRequest): NextResponse {
  const sessionCookie = request.cookies.get("session");
  const { pathname } = request.nextUrl;

  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Redirect unauthenticated users from protected routes
  if (isProtectedRoute && !sessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users from auth routes
  if (isAuthRoute && sessionCookie) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

### Next.js 16 and earlier (middleware.ts)

Create `src/middleware.ts` for protected routes:

```ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/settings", "/profile"];
const authRoutes = ["/login", "/signup"];

export function middleware(request: NextRequest): NextResponse {
  const sessionCookie = request.cookies.get("session");
  const { pathname } = request.nextUrl;

  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Redirect unauthenticated users from protected routes
  if (isProtectedRoute && !sessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users from auth routes
  if (isAuthRoute && sessionCookie) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

### Proxy/Middleware Best Practices

- **Use for fast, early interception**: redirects, header manipulation, basic auth checks
- **Don't use for**: DB queries, heavy validation, email sending - these belong in API routes/server components
- **Security note**: Always validate auth in your API routes too - don't rely solely on proxy

## Environment Variables

Add to `.env.local`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/google/callback

# Apple OAuth (optional)
APPLE_CLIENT_ID=your_client_id
APPLE_TEAM_ID=your_team_id
APPLE_KEY_ID=your_key_id
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
APPLE_REDIRECT_URI=http://localhost:3000/api/auth/apple/callback
```

## Security Checklist

- [x] Session tokens: 32 bytes of entropy, base64url encoded
- [x] Store SHA-256 hash in DB, raw token in cookie
- [x] HttpOnly cookies (no JS access)
- [x] Secure flag in production
- [x] SameSite=Lax (CSRF protection for GET)
- [x] Path=/ (accessible from all routes)
- [x] Expires set (not session cookie)
- [x] OAuth state validation (CSRF)
- [x] PKCE for Google (code_verifier)
- [x] Short-lived OAuth cookies (10 min)
- [x] Sliding session expiration
- [x] Cascade delete sessions on user delete

## Usage Examples

### In Server Components

```tsx
import { getAuth } from "@/lib/auth";

export default async function Dashboard() {
  const { user } = await getAuth();

  if (!user) {
    redirect("/login");
  }

  return <div>Welcome, {user.name}</div>;
}
```

### Sign Out Button

```tsx
"use client";

import { signOut } from "@/app/actions/auth";

export function SignOutButton() {
  return (
    <form action={signOut}>
      <button type="submit">Sign Out</button>
    </form>
  );
}
```

### Login Page

```tsx
export default function LoginPage() {
  return (
    <div>
      <h1>Sign In</h1>
      <a href="/api/auth/google">Continue with Google</a>
      <a href="/api/auth/apple">Continue with Apple</a>
    </div>
  );
}
```
