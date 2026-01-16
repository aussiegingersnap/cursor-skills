# Email Copy & Templates Guide

Best practices for writing effective transactional emails.

## Subject Line Guidelines

### Length
- **Optimal**: 40-60 characters
- **Mobile cutoff**: ~35 characters
- Front-load important words

### Patterns by Email Type

| Type | Pattern | Example |
|------|---------|---------|
| Verification | Action + context | "Verify your email for AppName" |
| Password reset | Action + urgency | "Reset your password" |
| Welcome | Greeting + next step | "Welcome! Here's how to get started" |
| Receipt | Order + identifier | "Your receipt for Order #1234" |
| Notification | What happened | "New comment on your post" |

### What to Avoid

- ALL CAPS (looks spammy)
- Excessive punctuation (!!!)
- Misleading content
- Generic subjects ("Hello" or "Update")
- Emojis (use sparingly, test deliverability)

## Preheader Text

The preview text shown after the subject line in email clients.

### Best Practices
- 40-130 characters
- Complements subject line
- Provides additional context
- Don't repeat the subject

### Implementation

```html
<!-- Hidden preheader -->
<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
  Your preheader text here - this appears in email previews
</div>
```

## Email Structure

### Transactional Email Template

```
1. Logo (optional, small)
2. Greeting (personalized if possible)
3. Main message (1-2 sentences)
4. Primary CTA button
5. Supporting details
6. Fallback link (plain text URL)
7. Footer (company info, unsubscribe if needed)
```

### Example: Verification Email

```html
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
  <!-- Preheader -->
  <div style="display:none;">Click to verify your email and get started</div>
  
  <div style="max-width: 560px; margin: 0 auto; padding: 40px 20px;">
    <!-- Logo -->
    <img src="logo.png" alt="AppName" style="height: 32px; margin-bottom: 24px;">
    
    <!-- Greeting -->
    <h1 style="font-size: 24px; font-weight: 600; margin: 0 0 16px;">
      Verify your email
    </h1>
    
    <!-- Main message -->
    <p style="margin: 0 0 24px; color: #555;">
      Thanks for signing up! Please verify your email address to get started.
    </p>
    
    <!-- Primary CTA -->
    <a href="{{verify_url}}" style="
      display: inline-block;
      background: #000;
      color: #fff;
      padding: 12px 24px;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 500;
    ">Verify Email Address</a>
    
    <!-- Fallback -->
    <p style="margin: 24px 0 0; font-size: 14px; color: #666;">
      Or copy and paste this link:<br>
      <a href="{{verify_url}}" style="color: #666; word-break: break-all;">
        {{verify_url}}
      </a>
    </p>
    
    <!-- Expiry notice -->
    <p style="margin: 24px 0 0; font-size: 14px; color: #999;">
      This link expires in 24 hours.
    </p>
    
    <!-- Footer -->
    <hr style="margin: 32px 0; border: none; border-top: 1px solid #eee;">
    <p style="font-size: 12px; color: #999; margin: 0;">
      If you didn't create an account, you can ignore this email.
    </p>
  </div>
</body>
```

## CTA Buttons

### Button Styles

```css
/* Primary CTA */
.btn-primary {
  display: inline-block;
  background: #000;
  color: #fff;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
}

/* Secondary CTA */
.btn-secondary {
  display: inline-block;
  background: transparent;
  color: #000;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 6px;
  border: 1px solid #ddd;
}
```

### Button Text Patterns

| Type | Good | Avoid |
|------|------|-------|
| Verification | "Verify Email" | "Click Here" |
| Password reset | "Reset Password" | "Continue" |
| Login | "Sign In" | "Go" |
| Action | "View Order" | "See More" |

### Accessibility

- Use descriptive text (not "Click here")
- Ensure sufficient color contrast
- Make buttons large enough for mobile (44px+ height)

## Plain Text Fallback

Always include a plain text version:

```text
Verify your email
==================

Thanks for signing up! Please verify your email address to get started.

Verify Email: {{verify_url}}

This link expires in 24 hours.

If you didn't create an account, you can ignore this email.

---
AppName | https://yourapp.com
```

## Legal Requirements

### CAN-SPAM (US)

Required for commercial emails:
- Clear "From" name and address
- Accurate subject line
- Physical postal address
- Unsubscribe mechanism

**Transactional emails are exempt** from most requirements, but:
- Still need accurate "From" address
- Cannot be primarily promotional

### GDPR (EU)

- Consent before marketing emails
- Easy unsubscribe
- Data processing disclosure
- Right to be forgotten

### Transactional vs Marketing

| Transactional (Exempt) | Marketing (Requires Consent) |
|------------------------|------------------------------|
| Password reset | Newsletter |
| Order confirmation | Product announcements |
| Account verification | Promotional offers |
| Security alerts | Re-engagement campaigns |
| Usage notifications | Abandoned cart |

## Footer Templates

### Minimal (Transactional)

```html
<p style="font-size: 12px; color: #999;">
  This is an automated message from AppName.<br>
  123 Main St, City, State 12345
</p>
```

### With Unsubscribe (Marketing)

```html
<p style="font-size: 12px; color: #999;">
  You received this email because you signed up for AppName.<br>
  <a href="{{unsubscribe_url}}" style="color: #999;">Unsubscribe</a> | 
  <a href="{{preferences_url}}" style="color: #999;">Email Preferences</a><br>
  123 Main St, City, State 12345
</p>
```

## Testing

### Before Sending

1. Send test to yourself
2. Check all links work
3. View on mobile and desktop
4. Test in Gmail, Outlook, Apple Mail
5. Verify plain text version
6. Run through mail-tester.com

### Checklist

- [ ] Subject line under 60 chars
- [ ] Preheader text set
- [ ] All links working
- [ ] CTA button visible
- [ ] Fallback URL included
- [ ] Plain text version included
- [ ] Footer with required info
- [ ] Renders on mobile
- [ ] Passes spam tests
