#!/usr/bin/env python3
"""
Scheduled Task Runner for Merkle Attestation System
Runs daily to build trees and publish attestations
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
import time
import argparse

from build_tree import build_daily_tree, save_tree_metadata
from publish import publish_with_metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CronJob:
    """Scheduled job runner"""

    def __init__(
        self,
        output_dir: str = './attestations',
        storage_type: str = 'local',
        backfill_days: int = 0
    ):
        self.output_dir = output_dir
        self.storage_type = storage_type
        self.backfill_days = backfill_days

    def run_daily_attestation(self, date: str) -> bool:
        """
        Run daily attestation build and publish

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting daily attestation for {date}")

            # Build Merkle tree
            logger.info("Building Merkle tree...")
            tree = build_daily_tree(date)

            if not tree.receipts:
                logger.warning(f"No receipts found for {date}, skipping")
                return True

            # Save tree metadata
            logger.info("Saving tree metadata...")
            attestation_path = save_tree_metadata(tree, self.output_dir, date)

            # Publish to storage
            logger.info(f"Publishing to {self.storage_type}...")
            metadata = publish_with_metadata(attestation_path, date, self.storage_type)

            logger.info(f"Daily attestation completed for {date}")
            logger.info(f"Root hash: {metadata['root_hash']}")
            logger.info(f"Receipt count: {metadata['receipt_count']}")
            logger.info(f"Published URL: {metadata['url']}")

            return True

        except Exception as e:
            logger.error(f"Failed to run daily attestation for {date}: {e}", exc_info=True)
            return False

    def run_backfill(self):
        """Run backfill for previous days"""
        if self.backfill_days <= 0:
            return

        logger.info(f"Running backfill for {self.backfill_days} days")

        today = datetime.now(timezone.utc).date()
        success_count = 0
        failure_count = 0

        for i in range(self.backfill_days, 0, -1):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')

            # Check if attestation already exists
            attestation_path = os.path.join(self.output_dir, f'{date}.json')
            if os.path.exists(attestation_path):
                logger.info(f"Attestation already exists for {date}, skipping")
                continue

            if self.run_daily_attestation(date):
                success_count += 1
            else:
                failure_count += 1

            # Small delay between backfill runs
            time.sleep(1)

        logger.info(f"Backfill completed: {success_count} successful, {failure_count} failed")

    def run_once(self, date: str = None):
        """
        Run once for a specific date or today

        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        """
        if date is None:
            date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        success = self.run_daily_attestation(date)
        sys.exit(0 if success else 1)

    def run_continuous(self, interval_hours: int = 24):
        """
        Run continuously at specified interval

        Args:
            interval_hours: Hours between runs
        """
        logger.info(f"Starting continuous mode with {interval_hours}h interval")

        # Run backfill first
        self.run_backfill()

        while True:
            # Run for today
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            self.run_daily_attestation(today)

            # Sleep until next run
            sleep_seconds = interval_hours * 3600
            logger.info(f"Sleeping for {interval_hours} hours until next run")
            time.sleep(sleep_seconds)

    def run_scheduled(self, run_time: str = "00:00"):
        """
        Run at a specific time each day

        Args:
            run_time: Time in HH:MM format (UTC)
        """
        logger.info(f"Starting scheduled mode, running daily at {run_time} UTC")

        # Run backfill first
        self.run_backfill()

        while True:
            now = datetime.now(timezone.utc)
            target_hour, target_minute = map(int, run_time.split(':'))

            # Calculate next run time
            next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            # If we've passed today's run time, schedule for tomorrow
            if now >= next_run:
                next_run += timedelta(days=1)

            # Calculate sleep time
            sleep_seconds = (next_run - now).total_seconds()

            logger.info(f"Next run scheduled for {next_run.isoformat()}")
            logger.info(f"Sleeping for {sleep_seconds/3600:.1f} hours")

            time.sleep(sleep_seconds)

            # Run the job
            yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
            self.run_daily_attestation(yesterday)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Merkle attestation cron job')
    parser.add_argument('--mode', type=str, default='once', choices=['once', 'continuous', 'scheduled'], help='Run mode')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (for once mode)')
    parser.add_argument('--output-dir', type=str, default='./attestations', help='Output directory for attestations')
    parser.add_argument('--storage', type=str, default='local', choices=['s3', 'r2', 'local'], help='Storage type')
    parser.add_argument('--interval', type=int, default=24, help='Interval in hours (for continuous mode)')
    parser.add_argument('--time', type=str, default='00:00', help='Run time in HH:MM UTC (for scheduled mode)')
    parser.add_argument('--backfill', type=int, default=0, help='Number of days to backfill')

    args = parser.parse_args()

    # Create cron job
    cron = CronJob(
        output_dir=args.output_dir,
        storage_type=args.storage,
        backfill_days=args.backfill
    )

    # Run based on mode
    try:
        if args.mode == 'once':
            cron.run_once(args.date)
        elif args.mode == 'continuous':
            cron.run_continuous(args.interval)
        elif args.mode == 'scheduled':
            cron.run_scheduled(args.time)
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
