# IAIndex Email System - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        IAIndex Email System                              │
│                       Production-Ready v1.0                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           USER TRIGGERS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  • Free Scan Complete    • Payment Success    • Weekly Schedule         │
│  • User Signup          • Subscription Event  • Visibility Change       │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        EMAIL SERVICE LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  EmailService (email_service.py)                                        │
│  ├── Template Renderer (Jinja2)                                         │
│  ├── Provider Auto-Detection (SendGrid/Resend)                          │
│  ├── send_welcome_email()                                               │
│  ├── send_pdf_report_email()                                            │
│  ├── send_payment_confirmation()                                        │
│  ├── send_payment_failed()                                              │
│  ├── send_subscription_canceled()                                       │
│  ├── send_weekly_report()                                               │
│  └── send_visibility_alert()                                            │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌─────────────────────┐    ┌─────────────────────┐
│  TRANSACTIONAL      │    │  DRIP CAMPAIGNS     │
│  EMAILS             │    │  (Automated)        │
├─────────────────────┤    ├─────────────────────┤
│ • Welcome           │    │ Day 0: PDF Report   │
│ • Payment Confirm   │    │ Day 1: Follow-up    │
│ • Payment Failed    │    │ Day 3: Case Study   │
│ • Sub Canceled      │    │ Day 7: Discount     │
│ • Weekly Report     │    │ Day 14: Urgency     │
│ • Visibility Alert  │    │                     │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          └────────────┬─────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     PREFERENCE CHECKING                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Check email_preferences table:                                         │
│  • Is user unsubscribed?                                                │
│  • Marketing emails enabled?                                            │
│  • Email type allowed?                                                  │
│  → If NO, skip send and log                                            │
│  → If YES, continue to template                                         │
└──────────────────────┬──────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     TEMPLATE RENDERING                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Jinja2 Template Engine:                                                │
│  • Load template (welcome.html, drip_day1.html, etc.)                   │
│  • Inject context variables (name, score, URLs)                         │
│  • Render final HTML                                                    │
│  • Add unsubscribe link & footer                                        │
└──────────────────────┬──────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      EMAIL PROVIDER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐              ┌──────────────────┐                │
│  │   SENDGRID       │      OR      │     RESEND       │                │
│  ├──────────────────┤              ├──────────────────┤                │
│  │ • High volume    │              │ • Easy setup     │                │
│  │ • Rich analytics │              │ • Modern API     │                │
│  │ • Webhooks       │              │ • Great docs     │                │
│  └────────┬─────────┘              └────────┬─────────┘                │
│           │                                 │                           │
│           └────────────┬────────────────────┘                           │
└────────────────────────┼────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      EMAIL DELIVERY                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  • Sent to recipient inbox                                              │
│  • Provider tracks delivery                                             │
│  • Message ID assigned                                                  │
└──────────────────────┬──────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      WEBHOOK EVENTS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  POST /v1/webhooks/sendgrid or /v1/webhooks/resend                      │
│                                                                          │
│  Events:                                                                │
│  • delivered  → Update email_analytics                                  │
│  • opened     → Track engagement, update drip status                    │
│  • clicked    → Track conversion, update drip status                    │
│  • bounced    → Mark as bounced, pause campaign                         │
│  • complained → Auto-unsubscribe user                                   │
│  • unsubscribe→ Update preferences                                      │
└──────────────────────┬──────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         ANALYTICS                                        │
├─────────────────────────────────────────────────────────────────────────┤
│  email_analytics table:                                                 │
│  • Total sent, delivered, opened, clicked                               │
│  • Bounce rate, complaint rate, unsubscribe rate                        │
│  • Performance by email type                                            │
│  • Campaign conversion tracking                                         │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                         DRIP CAMPAIGN FLOW
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────┐
│  FREE SCAN COMPLETE │
└──────────┬──────────┘
           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  DripCampaignService.create_free_scan_campaign()                        │
├─────────────────────────────────────────────────────────────────────────┤
│  1. Create campaign record (drip_campaigns)                             │
│  2. Set visibility_score, website_url, email                            │
│  3. Schedule Day 1 email                                                │
│  4. Return campaign_id                                                  │
└──────────────────────┬──────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│              BACKGROUND SCHEDULER (runs every 15 min)                    │
├─────────────────────────────────────────────────────────────────────────┤
│  drip_scheduler.py:                                                     │
│                                                                          │
│  LOOP:                                                                  │
│    1. Get pending emails (get_pending_drip_emails())                    │
│    2. For each email:                                                   │
│       • Check user preferences                                          │
│       • Render template with context                                    │
│       • Send via EmailService                                           │
│       • Update status to 'sent' or 'failed'                             │
│       • Schedule next email in sequence                                 │
│       • Track analytics                                                 │
│    3. Sleep 15 minutes                                                  │
│    4. Repeat                                                            │
└─────────────────────────────────────────────────────────────────────────┘

           Day 0          Day 1          Day 3          Day 7         Day 14
             │              │              │              │              │
             ↓              ↓              ↓              ↓              ↓
        ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
        │  PDF   │    │ Follow │    │  Case  │    │ 20%    │    │Urgency │
        │ Report │    │  Up    │    │ Study  │    │Discount│    │Message │
        └────────┘    └────────┘    └────────┘    └────────┘    └────────┘
        Immediate     +1 day        +2 days       +4 days       +7 days

                Expected Conversion: 5-10% → Paid Customer


═══════════════════════════════════════════════════════════════════════════
                      EMAIL PREFERENCES SYSTEM
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                    USER PREFERENCE CENTER                                │
├─────────────────────────────────────────────────────────────────────────┤
│  GET /v1/email-preferences/                                             │
│  PUT /v1/email-preferences/                                             │
│                                                                          │
│  User Controls:                                                         │
│  ┌───────────────────────────────────────────────┐                     │
│  │ [ ✓ ] Marketing Emails                        │                     │
│  │ [ ✓ ] Product Updates                         │                     │
│  │ [ ✓ ] Weekly Reports                          │                     │
│  │ [ ✓ ] Visibility Alerts                       │                     │
│  │ [ ✓ ] Transactional (always on)               │                     │
│  └───────────────────────────────────────────────┘                     │
│                                                                          │
│  ┌─────────────────────────────────┐                                   │
│  │  [ Unsubscribe from All ]       │                                   │
│  └─────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                  email_preferences TABLE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  • user_id                                                              │
│  • email                                                                │
│  • marketing_emails (true/false)                                        │
│  • product_updates (true/false)                                         │
│  • weekly_reports (true/false)                                          │
│  • visibility_alerts (true/false)                                       │
│  • transactional_emails (always true)                                   │
│  • unsubscribed_all (true/false)                                        │
│  • unsubscribe_token (unique, auto-generated)                           │
│  • unsubscribed_at (timestamp)                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    ONE-CLICK UNSUBSCRIBE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  Email Footer Link:                                                     │
│  https://app.iaindex.org/unsubscribe?token=abc123xyz                    │
│                                                                          │
│  POST /v1/email-preferences/unsubscribe                                 │
│  { "token": "abc123xyz", "unsubscribe_all": true }                      │
│                                                                          │
│  Result:                                                                │
│  • Update email_preferences: unsubscribed_all = true                    │
│  • Update drip_campaigns: status = 'unsubscribed'                       │
│  • Stop all future marketing emails                                     │
│  • Transactional emails still allowed (legal requirement)               │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                           DATABASE SCHEMA
═══════════════════════════════════════════════════════════════════════════

┌───────────────────────┐
│  email_preferences    │
├───────────────────────┤
│  id (PK)              │
│  user_id (FK)         │
│  email                │
│  marketing_emails     │
│  product_updates      │
│  weekly_reports       │
│  visibility_alerts    │
│  unsubscribed_all     │
│  unsubscribe_token    │
│  created_at           │
└───────────┬───────────┘
            │
            │ 1:N
            │
┌───────────▼───────────┐
│  drip_campaigns       │
├───────────────────────┤
│  id (PK)              │
│  email                │
│  website_url          │
│  user_id (FK)         │
│  campaign_type        │
│  current_step         │
│  total_steps          │
│  status               │
│  visibility_score     │
│  next_send_at         │
│  started_at           │
│  completed_at         │
└───────────┬───────────┘
            │
            │ 1:N
            │
┌───────────▼───────────────┐
│  drip_campaign_emails     │
├───────────────────────────┤
│  id (PK)                  │
│  campaign_id (FK)         │
│  step_number              │
│  email_type               │
│  subject                  │
│  to_email                 │
│  status                   │
│  scheduled_for            │
│  sent_at                  │
│  opened_at                │
│  clicked_at               │
│  provider_message_id      │
└───────────┬───────────────┘
            │
            │ 1:1
            │
┌───────────▼───────────────┐
│  email_analytics          │
├───────────────────────────┤
│  id (PK)                  │
│  campaign_email_id (FK)   │
│  email_type               │
│  to_email                 │
│  subject                  │
│  sent_at                  │
│  delivered_at             │
│  opened_at                │
│  clicked_at               │
│  bounced_at               │
│  complained_at            │
│  unsubscribed_at          │
│  provider                 │
│  provider_message_id      │
│  bounce_reason            │
│  click_url                │
└───────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                         TECH STACK
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  • Python 3.10+                                                         │
│  • FastAPI (API framework)                                              │
│  • Jinja2 (template engine)                                             │
│  • AsyncIO (async/await)                                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  • PostgreSQL (via Supabase)                                            │
│  • Row Level Security (RLS)                                             │
│  • Triggers & Functions                                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     EMAIL PROVIDERS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  • SendGrid (recommended for high volume)                               │
│  • Resend (recommended for simplicity)                                  │
│  • Auto-detection (uses whichever is configured)                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKGROUND TASKS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  • Python AsyncIO event loop                                            │
│  • Runs every 15 minutes                                                │
│  • Systemd service or Docker container                                  │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                      DEPLOYMENT ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                          AZURE CLOUD                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Azure Container Apps                                         │      │
│  │  ┌────────────────────┐  ┌────────────────────┐             │      │
│  │  │  API Service       │  │  Drip Scheduler    │             │      │
│  │  │  (FastAPI)         │  │  (Background)      │             │      │
│  │  │                    │  │                    │             │      │
│  │  │  • Email Routes    │  │  • Process Queue   │             │      │
│  │  │  • Webhooks        │  │  • Send Emails     │             │      │
│  │  │  • Preferences     │  │  • Update Stats    │             │      │
│  │  └────────────────────┘  └────────────────────┘             │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Supabase (PostgreSQL)                                        │      │
│  │  • email_preferences                                          │      │
│  │  • drip_campaigns                                             │      │
│  │  • drip_campaign_emails                                       │      │
│  │  • email_analytics                                            │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
                    External Services
                              ↓
          ┌─────────────────────────────────┐
          │  SendGrid / Resend              │
          │  • Email Delivery               │
          │  • Webhook Events               │
          │  • Analytics                    │
          └─────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                         MONITORING & ALERTS
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                         KEY METRICS                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Daily Monitoring:                                                      │
│  • Emails sent                                                          │
│  • Delivery rate (target: >98%)                                         │
│  • Bounce rate (alert if >2%)                                           │
│  • Complaint rate (alert if >0.1%)                                      │
│                                                                          │
│  Weekly Review:                                                         │
│  • Open rate by email type                                              │
│  • Click rate by email type                                             │
│  • Drip campaign conversion rate                                        │
│  • Unsubscribe rate                                                     │
│                                                                          │
│  Monthly Analysis:                                                      │
│  • Revenue attributed to email                                          │
│  • A/B test results                                                     │
│  • Template performance                                                 │
│  • List growth/churn                                                    │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            SECURITY
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                      SECURITY FEATURES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  • Row Level Security (RLS) on all tables                               │
│  • JWT authentication for API endpoints                                 │
│  • Unsubscribe token cryptographically secure (32 bytes)                │
│  • Webhook signature verification (SendGrid/Resend)                     │
│  • Rate limiting on email sends                                         │
│  • Input validation on all user inputs                                  │
│  • SQL injection protection (parameterized queries)                     │
│  • Environment variable secrets (no hardcoded keys)                     │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                        PROJECT STATUS: COMPLETE
═══════════════════════════════════════════════════════════════════════════

✓ All templates created (11 total)
✓ Database schema designed and migrated
✓ Drip campaign system implemented
✓ Email preferences management built
✓ Unsubscribe functionality working
✓ Analytics tracking configured
✓ SendGrid/Resend integration complete
✓ Background scheduler implemented
✓ API endpoints functional
✓ Test suite written
✓ Documentation complete

READY FOR PRODUCTION DEPLOYMENT
