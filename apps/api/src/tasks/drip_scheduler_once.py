"""
Drip campaign scheduler - single run version for cron jobs
Processes pending emails once and exits
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from supabase import create_client
from src.services.drip_campaign import DripCampaignService
from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Process pending drip emails once"""
    logger.info("Processing pending drip campaign emails...")

    # Create Supabase client
    supabase = create_client(settings.supabase_url, settings.supabase_key)

    # Create service
    service = DripCampaignService(supabase)

    # Process pending emails
    result = await service.process_pending_emails()

    logger.info(
        f"Processing complete: {result['sent']} sent, "
        f"{result['failed']} failed, {result['processed']} total"
    )

    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result['success'] else 1)
