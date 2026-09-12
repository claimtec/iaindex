# IAIndex Email System - Quick Start Guide

## 5-Minute Setup

### 1. Choose Email Provider

**Option A: SendGrid (Recommended for high volume)**
```bash
# Sign up: https://sendgrid.com
# Get API key from Settings > API Keys
export SENDGRID_API_KEY="SG.xxxxxxxxxxxxx"
```

**Option B: Resend (Easier setup)**
```bash
# Sign up: https://resend.com
# Get API key from Settings > API Keys
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
```

### 2. Run Database Migrations

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Email preferences
psql $DATABASE_URL < migrations/create_email_preferences.sql

# Drip campaigns
psql $DATABASE_URL < migrations/create_drip_campaigns.sql
```

### 3. Test Email Sending

```bash
cd apps/api

# Test with Python
python3 << EOF
import asyncio
from src.services.email_service import email_service

async def test():
    success = await email_service.send_email(
        to_email="your-email@example.com",
        subject="Test from IAIndex",
        html_content="<h1>It works!</h1>"
    )
    print(f"Email sent: {success}")

asyncio.run(test())
EOF
```

### 4. Start Drip Scheduler (Optional)

```bash
# Run in background
python3 -m src.tasks.drip_scheduler &

# Or use screen/tmux
screen -S drip-scheduler
python3 -m src.tasks.drip_scheduler
# Ctrl+A, D to detach
```

## Common Tasks

### Send a Welcome Email

```python
from src.services.email_service import email_service

await email_service.send_welcome_email(
    user_email="user@example.com",
    user_name="John"
)
```

### Create Drip Campaign

```python
from src.services.drip_campaign import DripCampaignService

service = DripCampaignService(supabase)

await service.create_free_scan_campaign(
    email="user@example.com",
    website_url="example.com",
    visibility_score=75
)
```

### Process Pending Emails

```python
from src.services.drip_campaign import DripCampaignService

service = DripCampaignService(supabase)

stats = await service.process_pending_emails()
print(f"Sent: {stats['sent']}, Failed: {stats['failed']}")
```

### Check Email Analytics

```bash
curl https://api.iaindex.org/v1/webhooks/analytics
```

## Environment Variables

**Minimal Setup:**
```bash
# Email provider (choose one)
SENDGRID_API_KEY="SG.xxx"
# OR
RESEND_API_KEY="re_xxx"

# Database
DATABASE_URL="postgresql://..."
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_KEY="eyJ..."

# URLs
APP_URL="https://app.iaindex.org"
```

**Full Setup:**
```bash
# Email provider
SENDGRID_API_KEY="SG.xxx"
SENDGRID_WEBHOOK_VERIFICATION_KEY="your_key"
RESEND_API_KEY="re_xxx"

# Email settings
FROM_EMAIL="noreply@iaindex.org"
FROM_NAME="IAIndex"

# Database
DATABASE_URL="postgresql://user:pass@host:5432/db"
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_KEY="eyJ..."

# Application
APP_URL="https://app.iaindex.org"
SITE_URL="https://scan.iaindex.org"
```

## API Endpoints

### Email Preferences

```bash
# Get preferences
GET /v1/email-preferences/
Authorization: Bearer {token}

# Update preferences
PUT /v1/email-preferences/
{
  "marketing_emails": false,
  "weekly_reports": true
}

# Unsubscribe
POST /v1/email-preferences/unsubscribe
{
  "token": "base64_token",
  "unsubscribe_all": true
}
```

### Webhooks

```bash
# SendGrid webhook
POST /v1/webhooks/sendgrid

# Resend webhook
POST /v1/webhooks/resend

# Analytics
GET /v1/webhooks/analytics
```

## Drip Campaign Flow

```
Free Scan → Day 0: PDF Report (immediate)
         ↓
         → Day 1: "Did you review?" follow-up
         ↓
         → Day 3: Case study (127% increase)
         ↓
         → Day 7: 20% discount offer
         ↓
         → Day 14: Urgency message
```

## Testing Checklist

- [ ] Email provider configured
- [ ] Test email sent successfully
- [ ] Database migrations run
- [ ] Templates render correctly
- [ ] Drip campaign created
- [ ] Scheduler processing emails
- [ ] Webhooks receiving events
- [ ] Analytics tracking data
- [ ] Unsubscribe working

## Troubleshooting

**Emails not sending?**
```bash
# Check provider
python3 -c "from src.services.email_service import email_service; print(email_service.provider)"

# Check logs
tail -f /var/log/iaindex/api.log | grep email
```

**Drip not working?**
```sql
-- Check pending emails
SELECT * FROM get_pending_drip_emails();

-- Check campaigns
SELECT * FROM drip_campaigns WHERE status = 'active';
```

**Webhooks failing?**
```bash
# Test endpoint
curl https://api.iaindex.org/v1/webhooks/sendgrid

# Check provider config
# SendGrid: Settings > Mail Settings > Event Webhook
# Resend: Settings > Webhooks
```

## Quick Reference

### Email Templates Available

1. `welcome.html` - Welcome new users
2. `pdf_report.html` - PDF delivery
3. `payment_confirmation.html` - Payment success
4. `payment_failed.html` - Payment failure
5. `subscription_canceled.html` - Cancellation
6. `weekly_report.html` - Weekly summary
7. `visibility_alert.html` - Score changes
8. `drip_day1_followup.html` - Day 1 drip
9. `drip_day3_case_study.html` - Day 3 drip
10. `drip_day7_discount.html` - Day 7 drip
11. `drip_day14_urgency.html` - Day 14 drip

### Database Tables

- `email_preferences` - User notification settings
- `drip_campaigns` - Campaign tracking
- `drip_campaign_emails` - Individual sends
- `email_analytics` - Delivery & engagement

### Key Functions

```python
# Email Service
email_service.send_email(to, subject, html)
email_service.send_welcome_email(email, name)
email_service.send_payment_failed(email, plan, attempts)

# Drip Service
drip.create_free_scan_campaign(email, url, score)
drip.process_pending_emails()
drip.pause_campaign(id)
drip.get_campaign_stats()
```

## Support

- Documentation: `/Users/dineshanchetty/Documents/claimtec/iaindex/EMAIL_AUTOMATION_COMPLETE.md`
- Email: support@iaindex.org
- Templates: `/Users/dineshanchetty/Documents/claimtec/iaindex/apps/api/src/templates/emails/`

---

**You're all set! Start sending beautiful, effective emails.**
