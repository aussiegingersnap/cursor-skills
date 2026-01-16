---
name: email-resend
description: Email delivery using Resend. Use this skill when implementing transactional emails (verification, password reset, notifications), configuring email infrastructure, or following email best practices for deliverability and spam prevention.
---

# Email Resend Skill

This skill provides workflows, best practices, and code patterns for sending transactional emails using [Resend](https://resend.com).

## Overview

Resend is a modern email API designed for developers. It provides:
- Simple REST API and SDKs
- React Email integration for beautiful templates
- Built-in analytics and deliverability monitoring
- MCP server for AI-assisted email workflows

## Prerequisites

### 1. Resend Account Setup

1. Sign up at [resend.com](https://resend.com)
2. Generate an API key in the dashboard
3. Add to your environment:

```bash
# .env.local
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL="App Name <noreply@yourdomain.com>"
```

### 2. Domain Verification

Before sending from your domain, you must verify it:

1. Go to Resend Dashboard → Domains → Add Domain
2. Add these DNS records at your provider:

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| TXT | `@` or domain | `v=spf1 include:_spf.resend.com ~all` | SPF |
| CNAME | `resend._domainkey` | Provided by Resend | DKIM |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com` | DMARC |

3. Wait for verification (usually 5-60 minutes)

### 3. MCP Server Setup (Optional - for Cursor AI)

To use Resend directly from Cursor's AI:

1. Clone and build the MCP server:
```bash
cd ~/Desktop/Code
git clone https://github.com/resend/mcp-send-email.git mcp-send-email
cd mcp-send-email && npm install && npm run build
```

2. Add to your `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "resend": {
      "type": "command",
      "command": "node /Users/YOUR_USERNAME/Desktop/Code/mcp-send-email/build/index.js --key=re_xxxxx --sender=noreply@yourdomain.com"
    }
  }
}
```

Replace `YOUR_USERNAME` and API key with your values.

## Code Patterns

### Basic Resend Client (TypeScript)

```typescript
// lib/email/index.ts
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'App <noreply@example.com>'
const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'

export interface SendEmailOptions {
  to: string
  subject: string
  html: string
  text?: string
  replyTo?: string
}

export async function sendEmail(options: SendEmailOptions) {
  const { data, error } = await resend.emails.send({
    from: FROM_EMAIL,
    to: options.to,
    subject: options.subject,
    html: options.html,
    text: options.text,
    replyTo: options.replyTo,
  })

  if (error) {
    console.error('[Email] Failed to send:', error)
    throw new Error(`Failed to send email: ${error.message}`)
  }

  return data
}
```

### Verification Email

```typescript
export async function sendVerificationEmail(email: string, token: string) {
  const verifyUrl = `${APP_URL}/verify-email?token=${token}`
  
  return sendEmail({
    to: email,
    subject: 'Verify your email address',
    html: `
      <h2>Welcome!</h2>
      <p>Please verify your email address by clicking the button below:</p>
      <a href="${verifyUrl}" style="
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        margin: 16px 0;
      ">Verify Email</a>
      <p>Or copy this link: ${verifyUrl}</p>
      <p>This link expires in 24 hours.</p>
      <p style="color: #666; font-size: 12px;">
        If you didn't create an account, you can ignore this email.
      </p>
    `,
    text: `Verify your email: ${verifyUrl}`,
  })
}
```

### Password Reset Email

```typescript
export async function sendPasswordResetEmail(email: string, token: string) {
  const resetUrl = `${APP_URL}/reset-password?token=${token}`
  
  return sendEmail({
    to: email,
    subject: 'Reset your password',
    html: `
      <h2>Password Reset Request</h2>
      <p>We received a request to reset your password. Click below to choose a new one:</p>
      <a href="${resetUrl}" style="
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        margin: 16px 0;
      ">Reset Password</a>
      <p>Or copy this link: ${resetUrl}</p>
      <p>This link expires in 1 hour.</p>
      <p style="color: #666; font-size: 12px;">
        If you didn't request this, you can safely ignore this email.
      </p>
    `,
    text: `Reset your password: ${resetUrl}`,
  })
}
```

### Welcome Email (after verification)

```typescript
export async function sendWelcomeEmail(email: string, name?: string) {
  return sendEmail({
    to: email,
    subject: 'Welcome to App Name!',
    html: `
      <h2>Welcome${name ? `, ${name}` : ''}!</h2>
      <p>Your email has been verified and your account is ready.</p>
      <p>Here are some things you can do:</p>
      <ul>
        <li>Complete your profile</li>
        <li>Explore features</li>
        <li>Check out the documentation</li>
      </ul>
      <a href="${APP_URL}" style="
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        margin: 16px 0;
      ">Get Started</a>
    `,
    text: `Welcome! Your account is ready. Get started at ${APP_URL}`,
  })
}
```

## Token Generation Pattern

Use secure, URL-safe tokens for verification and reset links:

```typescript
// lib/auth/tokens.ts
import { sha256 } from 'oslo/crypto'
import { encodeBase64url, encodeHex } from 'oslo/encoding'

// Token valid for 24 hours
const VERIFICATION_TOKEN_EXPIRY = 24 * 60 * 60 * 1000
// Reset token valid for 1 hour
const RESET_TOKEN_EXPIRY = 60 * 60 * 1000

/**
 * Generate a cryptographically secure token
 */
export function generateToken(): string {
  const bytes = new Uint8Array(32)
  crypto.getRandomValues(bytes)
  return encodeBase64url(bytes)
}

/**
 * Hash a token for database storage
 * Never store raw tokens - always hash them
 */
export async function hashToken(token: string): Promise<string> {
  return encodeHex(await sha256(new TextEncoder().encode(token)))
}
```

## Rate Limiting

Prevent email abuse with rate limiting:

```typescript
// Per-email rate limits
const EMAIL_RATE_LIMITS = {
  verification: { max: 3, window: 60 * 60 * 1000 },    // 3 per hour
  passwordReset: { max: 3, window: 60 * 60 * 1000 },   // 3 per hour
  general: { max: 10, window: 24 * 60 * 60 * 1000 },   // 10 per day
}
```

## Resend API Limits

| Plan | Emails/day | Emails/month | Rate limit |
|------|------------|--------------|------------|
| Free | 100 | 3,000 | 2/second |
| Pro | 5,000+ | Based on plan | 10/second |

## Best Practices

### Subject Lines
- Keep under 60 characters
- Be specific and action-oriented
- Avoid spam triggers (see references/deliverability.md)

### Email Copy
- Front-load important information
- Use clear CTAs
- Always include plain text fallback
- Keep emails focused on one purpose

### Transactional vs Marketing
- **Transactional**: Triggered by user action (verification, reset, receipts)
- **Marketing**: Promotional content (newsletters, announcements)
- Keep them separate - different sending reputations

### Error Handling
- Log all email failures
- Have fallback mechanisms (show token in UI for dev)
- Don't block user actions on email failures

## References

- [Deliverability Guide](references/deliverability.md) - DNS, spam prevention, reputation
- [Email Templates](references/templates.md) - Copy best practices, compliance
- [React Email Patterns](references/react-email.md) - Component-based email templates

## Dependencies

Install the Resend SDK:

```bash
npm install resend
```

For React Email templates (optional):

```bash
npm install @react-email/components react-email
```
