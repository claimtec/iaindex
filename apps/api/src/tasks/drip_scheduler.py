"""
Drip campaign scheduler - runs continuously as a background service
Processes pending drip campaign emails every 15 minutes
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supabase import create_client
from src.services.drip_campaign import run_drip_campaign_scheduler
from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/iaindex/drip-scheduler.log')
        if Path('/var/log/iaindex').exists()
        else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for drip campaign scheduler"""
    logger.info("=" * 60)
    logger.info("IAIndex Drip Campaign Scheduler Starting")
    logger.info("=" * 60)

    # Validate configuration
    if not settings.supabase_url or not settings.supabase_key:
        logger.error("Missing Supabase configuration")
        sys.exit(1)

    # Create Supabase client
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        logger.info(f"Connected to Supabase: {settings.supabase_url}")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Check email service configuration
    if not settings.sendgrid_api_key and not settings.resend_api_key:
        logger.warning("No email provider configured - emails will be logged only")
    else:
        logger.info("Email service configured")

    # Start scheduler
    logger.info("Starting scheduler loop (checks every 15 minutes)")
    logger.info("Press Ctrl+C to stop")

    try:
        asyncio.run(run_drip_campaign_scheduler(supabase))
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
