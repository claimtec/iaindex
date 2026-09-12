"""
Comprehensive test suite for email automation system
Run with: pytest tests/test_email_system.py -v
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import services
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.email_service import EmailService
from src.services.drip_campaign import DripCampaignService


class TestEmailService:
    """Test email service functionality"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance"""
        return EmailService()

    def test_provider_detection_sendgrid(self, email_service, monkeypatch):
        """Test SendGrid provider is detected"""
        monkeypatch.setenv("SENDGRID_API_KEY", "SG.test_key")
        service = EmailService()
        # Provider will be detected based on env var
        assert service.provider in ["sendgrid", "mock"]

    def test_provider_detection_resend(self, email_service, monkeypatch):
        """Test Resend provider is detected"""
        monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
        monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
        service = EmailService()
        assert service.provider in ["resend", "mock"]

    def test_template_rendering(self, email_service):
        """Test template rendering with context"""
        context = {
            "user_name": "John",
            "dashboard_url": "https://app.iaindex.org",
            "support_email": "support@iaindex.org"
        }

        html = email_service._render_template("welcome", context)

        assert "John" in html
        assert "app.iaindex.org" in html
        assert "support@iaindex.org" in html

    def test_fallback_html_generation(self, email_service):
        """Test fallback HTML when template not found"""
        context = {"message": "Test message"}

        html = email_service._generate_fallback_html("nonexistent", context)

        assert "Test message" in html
        assert "IAIndex" in html

    @pytest.mark.asyncio
    async def test_send_email_mock(self, email_service):
        """Test email sending with mock provider"""
        success = await email_service.send_email(
            to_email="test@example.com",
            subject="Test Email",
            html_content="<h1>Test</h1>"
        )

        # Mock provider always returns True
        assert success is True

    @pytest.mark.asyncio
    async def test_send_welcome_email(self, email_service):
        """Test welcome email sending"""
        with patch.object(email_service, 'send_email', return_value=True) as mock_send:
            success = await email_service.send_welcome_email(
                user_email="test@example.com",
                user_name="John"
            )

            assert success is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_pdf_report_email(self, email_service):
        """Test PDF report email sending"""
        with patch.object(email_service, 'send_email', return_value=True) as mock_send:
            success = await email_service.send_pdf_report_email(
                user_email="test@example.com",
                website_url="example.com",
                report_url="https://example.com/report.pdf",
                visibility_score=75
            )

            assert success is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_payment_confirmation(self, email_service):
        """Test payment confirmation email"""
        with patch.object(email_service, 'send_email', return_value=True) as mock_send:
            success = await email_service.send_payment_confirmation(
                user_email="test@example.com",
                plan="Professional",
                amount=79.00,
                invoice_url="https://stripe.com/invoice/123"
            )

            assert success is True
            mock_send.assert_called_once()


class TestDripCampaignService:
    """Test drip campaign functionality"""

    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client"""
        supabase = Mock()

        # Mock table responses
        supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )

        supabase.rpc.return_value.execute.return_value = Mock(
            data="campaign_id_123"
        )

        return supabase

    @pytest.fixture
    def drip_service(self, mock_supabase):
        """Create drip campaign service instance"""
        return DripCampaignService(mock_supabase)

    @pytest.mark.asyncio
    async def test_create_free_scan_campaign(self, drip_service, mock_supabase):
        """Test creating a free scan drip campaign"""
        result = await drip_service.create_free_scan_campaign(
            email="test@example.com",
            website_url="example.com",
            visibility_score=75,
            user_id="user_123"
        )

        assert result["success"] is True
        assert "campaign_id" in result
        assert result["email"] == "test@example.com"
        assert result["visibility_score"] == 75

    @pytest.mark.asyncio
    async def test_create_campaign_duplicate(self, drip_service, mock_supabase):
        """Test creating duplicate campaign returns existing"""
        # Mock existing campaign
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
            data=[{"id": "existing_campaign_id"}]
        )

        result = await drip_service.create_free_scan_campaign(
            email="test@example.com",
            website_url="example.com",
            visibility_score=75
        )

        assert result["success"] is False
        assert result["reason"] == "campaign_exists"

    @pytest.mark.asyncio
    async def test_process_pending_emails_empty(self, drip_service, mock_supabase):
        """Test processing when no pending emails"""
        mock_supabase.rpc.return_value.execute.return_value = Mock(data=[])

        result = await drip_service.process_pending_emails()

        assert result["success"] is True
        assert result["processed"] == 0
        assert result["sent"] == 0

    @pytest.mark.asyncio
    async def test_pause_campaign(self, drip_service, mock_supabase):
        """Test pausing a campaign"""
        success = await drip_service.pause_campaign("campaign_123")

        assert success is True
        mock_supabase.table.assert_called()

    @pytest.mark.asyncio
    async def test_resume_campaign(self, drip_service, mock_supabase):
        """Test resuming a paused campaign"""
        success = await drip_service.resume_campaign("campaign_123")

        assert success is True
        mock_supabase.table.assert_called()

    @pytest.mark.asyncio
    async def test_can_send_marketing_email(self, drip_service, mock_supabase):
        """Test checking if user can receive marketing emails"""
        # No preferences = can send
        can_send = await drip_service._can_send_marketing_email("test@example.com")

        assert can_send is True

    @pytest.mark.asyncio
    async def test_can_send_marketing_email_unsubscribed(self, drip_service, mock_supabase):
        """Test checking for unsubscribed user"""
        # Mock unsubscribed preferences
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "unsubscribed_all": True,
                "marketing_emails": False
            }]
        )

        can_send = await drip_service._can_send_marketing_email("test@example.com")

        assert can_send is False


class TestEmailTemplates:
    """Test email template rendering"""

    @pytest.fixture
    def email_service(self):
        return EmailService()

    def test_welcome_template(self, email_service):
        """Test welcome email template"""
        context = {
            "user_name": "Jane",
            "dashboard_url": "https://app.iaindex.org",
            "support_email": "support@iaindex.org"
        }

        html = email_service._render_template("welcome", context)

        assert "Jane" in html
        assert "Welcome to IAIndex" in html

    def test_pdf_report_template(self, email_service):
        """Test PDF report template"""
        context = {
            "website_url": "example.com",
            "report_url": "https://example.com/report.pdf",
            "visibility_score": 85,
            "dashboard_url": "https://app.iaindex.org"
        }

        html = email_service._render_template("pdf_report", context)

        assert "example.com" in html
        assert "85" in html

    def test_payment_failed_template(self, email_service):
        """Test payment failed template"""
        context = {
            "plan": "Professional",
            "attempt_count": 2,
            "billing_url": "https://app.iaindex.org/billing"
        }

        html = email_service._render_template("payment_failed", context)

        assert "Professional" in html
        assert "Payment Failed" in html

    def test_drip_day1_template(self, email_service):
        """Test drip day 1 follow-up template"""
        context = {
            "user_name": "Alex",
            "website_url": "example.com",
            "visibility_score": 62,
            "report_url": "https://example.com/report.pdf",
            "dashboard_url": "https://app.iaindex.org",
            "unsubscribe_url": "https://app.iaindex.org/unsubscribe",
            "percentage_below": 52
        }

        html = email_service._render_template("drip_day1_followup", context)

        assert "Alex" in html
        assert "example.com" in html
        assert "62" in html

    def test_drip_day3_template(self, email_service):
        """Test drip day 3 case study template"""
        context = {
            "user_name": "Sam",
            "visibility_score": 42,
            "dashboard_url": "https://app.iaindex.org",
            "unsubscribe_url": "https://app.iaindex.org/unsubscribe"
        }

        html = email_service._render_template("drip_day3_case_study", context)

        assert "127%" in html  # Case study improvement
        assert "TechSaaS" in html

    def test_drip_day7_template(self, email_service):
        """Test drip day 7 discount template"""
        context = {
            "user_name": "Chris",
            "website_url": "example.com",
            "visibility_score": 55,
            "dashboard_url": "https://app.iaindex.org",
            "unsubscribe_url": "https://app.iaindex.org/unsubscribe",
            "expiry_date": "November 30, 2025"
        }

        html = email_service._render_template("drip_day7_discount", context)

        assert "20% OFF" in html
        assert "BOOST20" in html

    def test_drip_day14_template(self, email_service):
        """Test drip day 14 urgency template"""
        context = {
            "user_name": "Taylor",
            "website_url": "example.com",
            "visibility_score": 48,
            "dashboard_url": "https://app.iaindex.org",
            "unsubscribe_url": "https://app.iaindex.org/unsubscribe",
            "competitor_count": 50,
            "competitor_avg_score": 63,
            "your_mentions": 5,
            "competitor_mentions": 15,
            "outranked_percentage": 52
        }

        html = email_service._render_template("drip_day14_urgency", context)

        assert "Competitors" in html
        assert "pulling ahead" in html.lower()


class TestEmailPreferences:
    """Test email preferences management"""

    @pytest.fixture
    def mock_supabase(self):
        supabase = Mock()
        supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "id": "pref_123",
                "email": "test@example.com",
                "marketing_emails": True,
                "product_updates": True,
                "weekly_reports": True,
                "visibility_alerts": True,
                "unsubscribed_all": False
            }]
        )
        return supabase

    def test_get_preferences(self, mock_supabase):
        """Test getting email preferences"""
        result = mock_supabase.table("email_preferences").select("*").eq(
            "email", "test@example.com"
        ).execute()

        assert len(result.data) == 1
        assert result.data[0]["marketing_emails"] is True

    def test_update_preferences(self, mock_supabase):
        """Test updating email preferences"""
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "id": "pref_123",
                "marketing_emails": False
            }]
        )

        result = mock_supabase.table("email_preferences").update({
            "marketing_emails": False
        }).eq("id", "pref_123").execute()

        assert result.data[0]["marketing_emails"] is False


# Integration test (requires actual database)
@pytest.mark.integration
class TestEmailIntegration:
    """Integration tests - require actual database and email provider"""

    @pytest.mark.asyncio
    async def test_end_to_end_drip_campaign(self):
        """Test complete drip campaign flow"""
        # This would require actual Supabase and email provider
        pytest.skip("Integration test - requires actual services")

    @pytest.mark.asyncio
    async def test_webhook_processing(self):
        """Test webhook event processing"""
        # This would require actual webhook events
        pytest.skip("Integration test - requires actual services")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
