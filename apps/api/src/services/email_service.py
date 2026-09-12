"""
Email delivery service with SendGrid and Resend support
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import os

# Email provider imports (optional dependencies)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"


class EmailService:
    """Email delivery service supporting SendGrid and Resend"""

    def __init__(self):
        self.provider = self._detect_provider()
        self._setup_templates()

    def _detect_provider(self) -> str:
        """Detect which email provider to use"""
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        resend_key = os.getenv("RESEND_API_KEY")

        if sendgrid_key and SENDGRID_AVAILABLE:
            self.sendgrid_client = SendGridAPIClient(sendgrid_key)
            logger.info("Email service initialized with SendGrid")
            return "sendgrid"
        elif resend_key and RESEND_AVAILABLE:
            resend.api_key = resend_key
            logger.info("Email service initialized with Resend")
            return "resend"
        else:
            logger.warning("No email provider configured. Emails will be logged only.")
            return "mock"

    def _setup_templates(self):
        """Set up Jinja2 template environment"""
        if TEMPLATES_DIR.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(TEMPLATES_DIR),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            logger.warning(f"Email templates directory not found: {TEMPLATES_DIR}")
            self.jinja_env = None

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        if not self.jinja_env:
            return self._generate_fallback_html(template_name, context)

        try:
            template = self.jinja_env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            return self._generate_fallback_html(template_name, context)

    def _generate_fallback_html(self, template_name: str, context: Dict[str, Any]) -> str:
        """Generate basic HTML when template is not available"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>IAIndex - {template_name}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">IAIndex</h2>
                <div>{context.get('message', 'Email content')}</div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated email from IAIndex. Please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            from_email: Sender email (optional, uses default)
            from_name: Sender name (optional)

        Returns:
            True if sent successfully
        """
        from_email = from_email or "noreply@iaindex.org"
        from_name = from_name or "IAIndex"

        try:
            if self.provider == "sendgrid":
                return await self._send_sendgrid(to_email, subject, html_content, from_email, from_name)
            elif self.provider == "resend":
                return await self._send_resend(to_email, subject, html_content, from_email, from_name)
            else:
                return await self._send_mock(to_email, subject, html_content, from_email, from_name)

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str,
        from_name: str
    ) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=Email(from_email, from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            response = self.sendgrid_client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent via SendGrid to {to_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False

    async def _send_resend(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str,
        from_name: str
    ) -> bool:
        """Send email via Resend"""
        try:
            response = resend.Emails.send({
                "from": f"{from_name} <{from_email}>",
                "to": to_email,
                "subject": subject,
                "html": html_content
            })

            logger.info(f"Email sent via Resend to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Resend error: {e}")
            return False

    async def _send_mock(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str,
        from_name: str
    ) -> bool:
        """Mock email sending (logs only)"""
        logger.info(f"""
        ========== EMAIL (MOCK) ==========
        From: {from_name} <{from_email}>
        To: {to_email}
        Subject: {subject}
        ==================================
        """)
        return True

    async def send_welcome_email(self, user_email: str, user_name: Optional[str] = None) -> bool:
        """Send welcome email to new user"""
        context = {
            "user_name": user_name or "there",
            "dashboard_url": f"{settings.app_url}/dashboard",
            "support_email": "support@iaindex.org"
        }

        html_content = self._render_template("welcome", context)

        return await self.send_email(
            to_email=user_email,
            subject="Welcome to IAIndex - Get Started",
            html_content=html_content
        )

    async def send_pdf_report_email(
        self,
        user_email: str,
        website_url: str,
        report_url: str,
        visibility_score: int
    ) -> bool:
        """Send PDF report delivery email"""
        context = {
            "website_url": website_url,
            "report_url": report_url,
            "visibility_score": visibility_score,
            "dashboard_url": f"{settings.app_url}/dashboard"
        }

        html_content = self._render_template("pdf_report", context)

        return await self.send_email(
            to_email=user_email,
            subject=f"Your AI Visibility Report for {website_url}",
            html_content=html_content
        )

    async def send_payment_confirmation(
        self,
        user_email: str,
        plan: str,
        amount: float,
        invoice_url: Optional[str] = None
    ) -> bool:
        """Send payment confirmation email"""
        context = {
            "plan": plan,
            "amount": amount,
            "invoice_url": invoice_url,
            "dashboard_url": f"{settings.app_url}/dashboard"
        }

        html_content = self._render_template("payment_confirmation", context)

        return await self.send_email(
            to_email=user_email,
            subject=f"Payment Confirmed - {plan} Plan",
            html_content=html_content
        )

    async def send_payment_failed(
        self,
        user_email: str,
        plan: str,
        attempt_count: int
    ) -> bool:
        """Send payment failure notification"""
        context = {
            "plan": plan,
            "attempt_count": attempt_count,
            "billing_url": f"{settings.app_url}/settings/billing"
        }

        html_content = self._render_template("payment_failed", context)

        return await self.send_email(
            to_email=user_email,
            subject="Payment Failed - Action Required",
            html_content=html_content
        )

    async def send_subscription_canceled(self, user_email: str, cancel_date: str) -> bool:
        """Send subscription cancellation confirmation"""
        context = {
            "cancel_date": cancel_date,
            "dashboard_url": f"{settings.app_url}/dashboard"
        }

        html_content = self._render_template("subscription_canceled", context)

        return await self.send_email(
            to_email=user_email,
            subject="Subscription Canceled",
            html_content=html_content
        )

    async def send_weekly_report(
        self,
        user_email: str,
        websites_data: List[Dict[str, Any]]
    ) -> bool:
        """Send weekly visibility report"""
        context = {
            "websites": websites_data,
            "dashboard_url": f"{settings.app_url}/dashboard"
        }

        html_content = self._render_template("weekly_report", context)

        return await self.send_email(
            to_email=user_email,
            subject="Your Weekly AI Visibility Report",
            html_content=html_content
        )

    async def send_visibility_alert(
        self,
        user_email: str,
        website_url: str,
        old_score: int,
        new_score: int,
        change_percent: float
    ) -> bool:
        """Send visibility change alert"""
        context = {
            "website_url": website_url,
            "old_score": old_score,
            "new_score": new_score,
            "change_percent": change_percent,
            "is_improvement": new_score > old_score,
            "dashboard_url": f"{settings.app_url}/dashboard"
        }

        html_content = self._render_template("visibility_alert", context)

        subject = f"Visibility {'Increased' if new_score > old_score else 'Decreased'} for {website_url}"

        return await self.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )


# Global email service instance
email_service = EmailService()
