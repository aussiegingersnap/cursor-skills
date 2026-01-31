# Email Deliverability Guide

Best practices for ensuring your emails reach the inbox, not spam.

## DNS Configuration

### SPF (Sender Policy Framework)

SPF tells receiving servers which IPs are authorized to send email for your domain.

```
Type: TXT
Name: @ (or your domain)
Value: v=spf1 include:_spf.resend.com ~all
```

**Notes:**
- `~all` = soft fail (recommended for starting out)
- `-all` = hard fail (stricter, use after testing)
- Only ONE SPF record per domain

### DKIM (DomainKeys Identified Mail)

DKIM cryptographically signs your emails to prove authenticity.

```
Type: CNAME
Name: resend._domainkey
Value: (provided by Resend dashboard)
```

### DMARC (Domain-based Message Authentication)

DMARC tells receivers what to do when SPF/DKIM fail.

**Starting (monitoring only):**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
```

**Production (after monitoring):**
```
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

**Strict (fully verified):**
```
Value: v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com
```

### Verification Checklist

- [ ] SPF record added
- [ ] DKIM CNAME added
- [ ] DMARC record added
- [ ] Resend dashboard shows "Verified"
- [ ] Test email lands in inbox (not spam)

## Spam Prevention

### Words/Phrases to Avoid

These words trigger spam filters when overused:

**High Risk:**
- FREE, FREE!, 100% FREE
- ACT NOW, URGENT, LIMITED TIME
- WINNER, CONGRATULATIONS
- $$$ or multiple dollar signs
- ALL CAPS SENTENCES

**Medium Risk:**
- Click here, Click below
- Buy now, Order now
- Guarantee, No obligation
- Risk-free, No cost
- Amazing, Incredible

**Low Risk (but be careful):**
- Offer, Deal, Discount
- Save, Money
- New, Introducing

### Formatting Rules

| Rule | Recommendation |
|------|----------------|
| Image-to-text ratio | Keep under 40% images |
| Links | Limit to 3-5 per email |
| Attachments | Avoid or use trusted file types |
| HTML | Keep clean, no excessive CSS |
| Text version | Always include plain text |

### Authentication Alignment

Ensure your "From" domain matches:
- SPF authenticated domain
- DKIM signing domain

**Good:**
```
From: noreply@yourapp.com
SPF: yourapp.com
DKIM: yourapp.com
```

**Bad:**
```
From: noreply@yourapp.com
Actual sender: mail.resend.com (misaligned)
```

## Domain Warm-up

New domains need gradual volume increases to build reputation.

### Week 1-2: Low Volume
- Send 10-50 emails/day
- Only to engaged users
- Monitor bounce rates

### Week 3-4: Ramp Up
- Increase to 100-500/day
- Continue monitoring metrics
- Address any issues

### Month 2+: Normal Volume
- Gradually reach target volume
- Maintain consistent sending patterns
- Avoid sudden spikes

### Warm-up Signals

**Good signs:**
- Bounce rate < 2%
- Spam complaints < 0.1%
- Good open rates (20%+)

**Warning signs:**
- High bounce rate
- Spam complaints
- Emails going to spam folder

## Bounce Handling

### Bounce Types

| Type | Meaning | Action |
|------|---------|--------|
| Hard bounce | Invalid email | Remove immediately |
| Soft bounce | Temporary issue | Retry 2-3 times, then remove |
| Spam complaint | User marked as spam | Remove and investigate |

### Implementation

```typescript
// Handle Resend webhooks for bounces
export async function handleEmailEvent(event: ResendEvent) {
  switch (event.type) {
    case 'email.bounced':
      await markEmailInvalid(event.data.to)
      break
    case 'email.complained':
      await markEmailUnsubscribed(event.data.to)
      await logSpamComplaint(event)
      break
  }
}
```

## List Hygiene

### Regular Cleanup
- Remove bounced emails immediately
- Remove unsubscribes within 10 days (legal requirement)
- Remove inactive users after 6-12 months

### Engagement Tracking
- Track opens and clicks
- Segment by engagement level
- Re-engage or remove cold subscribers

## Monitoring

### Key Metrics

| Metric | Target | Warning |
|--------|--------|---------|
| Delivery rate | > 98% | < 95% |
| Bounce rate | < 2% | > 5% |
| Spam rate | < 0.1% | > 0.3% |
| Open rate | > 20% | < 10% |

### Tools

- **Resend Dashboard**: Built-in analytics
- **Google Postmaster Tools**: Gmail-specific reputation
- **MXToolbox**: DNS and blacklist checking
- **Mail Tester**: Spam score testing

## Troubleshooting

### Emails Going to Spam

1. Check DNS records are correct
2. Verify domain in Resend dashboard
3. Test with mail-tester.com
4. Review email content for spam triggers
5. Check sender reputation

### Low Open Rates

1. Check subject lines
2. Verify emails aren't in spam
3. Send at optimal times
4. Segment your audience
5. A/B test content

### High Bounce Rates

1. Verify email addresses at signup
2. Use double opt-in
3. Clean your list regularly
4. Check for typos in email collection
