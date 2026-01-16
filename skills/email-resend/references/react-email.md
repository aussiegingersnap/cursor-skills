# React Email Patterns

Component-based email templates using [React Email](https://react.email).

## Setup

```bash
npm install @react-email/components react-email
```

## Project Structure

```
src/
├── emails/
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Footer.tsx
│   │   └── Layout.tsx
│   ├── verification.tsx
│   ├── password-reset.tsx
│   └── welcome.tsx
└── lib/
    └── email/
        └── index.ts
```

## Base Layout Component

```tsx
// src/emails/components/Layout.tsx
import {
  Body,
  Container,
  Head,
  Html,
  Preview,
  Section,
  Text,
} from '@react-email/components'

interface LayoutProps {
  preview: string
  children: React.ReactNode
}

export function Layout({ preview, children }: LayoutProps) {
  return (
    <Html>
      <Head />
      <Preview>{preview}</Preview>
      <Body style={body}>
        <Container style={container}>
          {children}
        </Container>
      </Body>
    </Html>
  )
}

const body = {
  backgroundColor: '#f6f9fc',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
}

const container = {
  backgroundColor: '#ffffff',
  margin: '40px auto',
  padding: '40px',
  borderRadius: '8px',
  maxWidth: '560px',
}
```

## Button Component

```tsx
// src/emails/components/Button.tsx
import { Button as EmailButton } from '@react-email/components'

interface ButtonProps {
  href: string
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

export function Button({ href, children, variant = 'primary' }: ButtonProps) {
  const style = variant === 'primary' ? primaryStyle : secondaryStyle
  
  return (
    <EmailButton href={href} style={style}>
      {children}
    </EmailButton>
  )
}

const primaryStyle = {
  backgroundColor: '#000',
  color: '#fff',
  padding: '12px 24px',
  borderRadius: '6px',
  textDecoration: 'none',
  fontWeight: '500',
  display: 'inline-block',
}

const secondaryStyle = {
  backgroundColor: 'transparent',
  color: '#000',
  padding: '12px 24px',
  borderRadius: '6px',
  textDecoration: 'none',
  border: '1px solid #ddd',
  display: 'inline-block',
}
```

## Footer Component

```tsx
// src/emails/components/Footer.tsx
import { Hr, Text, Link } from '@react-email/components'

interface FooterProps {
  companyName: string
  address: string
  unsubscribeUrl?: string
}

export function Footer({ companyName, address, unsubscribeUrl }: FooterProps) {
  return (
    <>
      <Hr style={hr} />
      <Text style={footer}>
        {unsubscribeUrl && (
          <>
            <Link href={unsubscribeUrl} style={link}>Unsubscribe</Link>
            {' | '}
          </>
        )}
        {companyName}<br />
        {address}
      </Text>
    </>
  )
}

const hr = {
  borderColor: '#e6ebf1',
  margin: '32px 0',
}

const footer = {
  color: '#8898aa',
  fontSize: '12px',
  lineHeight: '16px',
}

const link = {
  color: '#8898aa',
}
```

## Verification Email

```tsx
// src/emails/verification.tsx
import { Heading, Text, Link } from '@react-email/components'
import { Layout } from './components/Layout'
import { Button } from './components/Button'
import { Footer } from './components/Footer'

interface VerificationEmailProps {
  verifyUrl: string
  expiresIn?: string
}

export function VerificationEmail({ 
  verifyUrl, 
  expiresIn = '24 hours' 
}: VerificationEmailProps) {
  return (
    <Layout preview="Verify your email address to get started">
      <Heading style={heading}>Verify your email</Heading>
      
      <Text style={paragraph}>
        Thanks for signing up! Please verify your email address to get started.
      </Text>
      
      <Button href={verifyUrl}>Verify Email Address</Button>
      
      <Text style={fallback}>
        Or copy and paste this link:{' '}
        <Link href={verifyUrl} style={link}>{verifyUrl}</Link>
      </Text>
      
      <Text style={expiry}>
        This link expires in {expiresIn}.
      </Text>
      
      <Footer 
        companyName="AppName" 
        address="123 Main St, City, State 12345" 
      />
      
      <Text style={disclaimer}>
        If you didn't create an account, you can ignore this email.
      </Text>
    </Layout>
  )
}

const heading = {
  fontSize: '24px',
  fontWeight: '600',
  color: '#1a1a1a',
  margin: '0 0 16px',
}

const paragraph = {
  fontSize: '16px',
  lineHeight: '24px',
  color: '#555',
  margin: '0 0 24px',
}

const fallback = {
  fontSize: '14px',
  color: '#666',
  margin: '24px 0 0',
}

const link = {
  color: '#666',
  wordBreak: 'break-all' as const,
}

const expiry = {
  fontSize: '14px',
  color: '#999',
  margin: '16px 0 0',
}

const disclaimer = {
  fontSize: '12px',
  color: '#999',
  margin: '16px 0 0',
}

export default VerificationEmail
```

## Password Reset Email

```tsx
// src/emails/password-reset.tsx
import { Heading, Text, Link } from '@react-email/components'
import { Layout } from './components/Layout'
import { Button } from './components/Button'
import { Footer } from './components/Footer'

interface PasswordResetEmailProps {
  resetUrl: string
  expiresIn?: string
}

export function PasswordResetEmail({ 
  resetUrl, 
  expiresIn = '1 hour' 
}: PasswordResetEmailProps) {
  return (
    <Layout preview="Reset your password">
      <Heading style={heading}>Reset your password</Heading>
      
      <Text style={paragraph}>
        We received a request to reset your password. Click below to choose a new one.
      </Text>
      
      <Button href={resetUrl}>Reset Password</Button>
      
      <Text style={fallback}>
        Or copy and paste this link:{' '}
        <Link href={resetUrl} style={link}>{resetUrl}</Link>
      </Text>
      
      <Text style={expiry}>
        This link expires in {expiresIn}.
      </Text>
      
      <Footer 
        companyName="AppName" 
        address="123 Main St, City, State 12345" 
      />
      
      <Text style={disclaimer}>
        If you didn't request this, you can safely ignore this email.
      </Text>
    </Layout>
  )
}

// ... same styles as VerificationEmail

export default PasswordResetEmail
```

## Welcome Email

```tsx
// src/emails/welcome.tsx
import { Heading, Text, Section } from '@react-email/components'
import { Layout } from './components/Layout'
import { Button } from './components/Button'
import { Footer } from './components/Footer'

interface WelcomeEmailProps {
  name?: string
  appUrl: string
}

export function WelcomeEmail({ name, appUrl }: WelcomeEmailProps) {
  const greeting = name ? `Welcome, ${name}!` : 'Welcome!'
  
  return (
    <Layout preview="Your account is ready - here's how to get started">
      <Heading style={heading}>{greeting}</Heading>
      
      <Text style={paragraph}>
        Your email has been verified and your account is ready to go.
      </Text>
      
      <Section style={features}>
        <Text style={featureTitle}>Here's what you can do:</Text>
        <Text style={featureItem}>✓ Complete your profile</Text>
        <Text style={featureItem}>✓ Explore features</Text>
        <Text style={featureItem}>✓ Connect with others</Text>
      </Section>
      
      <Button href={appUrl}>Get Started</Button>
      
      <Footer 
        companyName="AppName" 
        address="123 Main St, City, State 12345" 
      />
    </Layout>
  )
}

const heading = {
  fontSize: '24px',
  fontWeight: '600',
  color: '#1a1a1a',
  margin: '0 0 16px',
}

const paragraph = {
  fontSize: '16px',
  lineHeight: '24px',
  color: '#555',
  margin: '0 0 24px',
}

const features = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '20px',
  margin: '0 0 24px',
}

const featureTitle = {
  fontSize: '14px',
  fontWeight: '600',
  color: '#333',
  margin: '0 0 12px',
}

const featureItem = {
  fontSize: '14px',
  color: '#555',
  margin: '4px 0',
}

export default WelcomeEmail
```

## Rendering Emails

```tsx
// src/lib/email/index.ts
import { render } from '@react-email/render'
import { Resend } from 'resend'
import { VerificationEmail } from '@/emails/verification'
import { PasswordResetEmail } from '@/emails/password-reset'
import { WelcomeEmail } from '@/emails/welcome'

const resend = new Resend(process.env.RESEND_API_KEY)
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL!
const APP_URL = process.env.NEXT_PUBLIC_APP_URL!

export async function sendVerificationEmail(email: string, token: string) {
  const verifyUrl = `${APP_URL}/verify-email?token=${token}`
  
  const html = await render(VerificationEmail({ verifyUrl }))
  const text = await render(VerificationEmail({ verifyUrl }), { plainText: true })
  
  return resend.emails.send({
    from: FROM_EMAIL,
    to: email,
    subject: 'Verify your email address',
    html,
    text,
  })
}

export async function sendPasswordResetEmail(email: string, token: string) {
  const resetUrl = `${APP_URL}/reset-password?token=${token}`
  
  const html = await render(PasswordResetEmail({ resetUrl }))
  const text = await render(PasswordResetEmail({ resetUrl }), { plainText: true })
  
  return resend.emails.send({
    from: FROM_EMAIL,
    to: email,
    subject: 'Reset your password',
    html,
    text,
  })
}

export async function sendWelcomeEmail(email: string, name?: string) {
  const html = await render(WelcomeEmail({ name, appUrl: APP_URL }))
  const text = await render(WelcomeEmail({ name, appUrl: APP_URL }), { plainText: true })
  
  return resend.emails.send({
    from: FROM_EMAIL,
    to: email,
    subject: 'Welcome to AppName!',
    html,
    text,
  })
}
```

## Development Preview

Add a script to preview emails locally:

```json
// package.json
{
  "scripts": {
    "email:dev": "email dev --dir src/emails --port 3001"
  }
}
```

Run `npm run email:dev` to open the React Email preview interface.

## Testing Emails

```tsx
// src/emails/__tests__/verification.test.tsx
import { render } from '@react-email/render'
import { VerificationEmail } from '../verification'

describe('VerificationEmail', () => {
  it('renders with verify URL', async () => {
    const html = await render(
      VerificationEmail({ verifyUrl: 'https://app.com/verify?token=abc123' })
    )
    
    expect(html).toContain('Verify your email')
    expect(html).toContain('abc123')
  })
  
  it('includes plain text fallback', async () => {
    const text = await render(
      VerificationEmail({ verifyUrl: 'https://app.com/verify?token=abc123' }),
      { plainText: true }
    )
    
    expect(text).toContain('Verify your email')
    expect(text).toContain('abc123')
  })
})
```
