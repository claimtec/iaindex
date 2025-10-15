#!/usr/bin/env python3
"""
Attestation Publisher
Publishes attestation artifacts to cloud storage (S3/Cloudflare R2)
"""

import json
import os
import argparse
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StoragePublisher:
    """Base class for storage publishers"""

    def publish(self, file_path: str, object_key: str) -> str:
        """
        Publish file to storage

        Args:
            file_path: Local file path
            object_key: Storage object key/path

        Returns:
            Public URL of published object
        """
        raise NotImplementedError


class S3Publisher(StoragePublisher):
    """Publishes attestations to AWS S3"""

    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        self.region = region
        self._client = None

    def _get_client(self):
        """Lazy load S3 client"""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('s3', region_name=self.region)
                logger.info(f"Initialized S3 client for bucket: {self.bucket_name}")
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise

        return self._client

    def publish(self, file_path: str, object_key: str) -> str:
        """
        Publish file to S3

        Args:
            file_path: Local file path
            object_key: S3 object key

        Returns:
            Public URL of published object
        """
        try:
            client = self._get_client()

            # Upload file
            with open(file_path, 'rb') as f:
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=f,
                    ContentType='application/json',
                    CacheControl='public, max-age=31536000',  # 1 year cache
                )

            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_key}"

            logger.info(f"Published to S3: {url}")
            return url

        except Exception as e:
            logger.error(f"Failed to publish to S3: {e}")
            raise


class R2Publisher(StoragePublisher):
    """Publishes attestations to Cloudflare R2"""

    def __init__(self, bucket_name: str, account_id: str, access_key_id: str, secret_access_key: str):
        self.bucket_name = bucket_name
        self.account_id = account_id
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self._client = None

    def _get_client(self):
        """Lazy load R2 client (uses S3 compatible API)"""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    's3',
                    endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name='auto'
                )
                logger.info(f"Initialized R2 client for bucket: {self.bucket_name}")
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize R2 client: {e}")
                raise

        return self._client

    def publish(self, file_path: str, object_key: str) -> str:
        """
        Publish file to R2

        Args:
            file_path: Local file path
            object_key: R2 object key

        Returns:
            Public URL of published object
        """
        try:
            client = self._get_client()

            # Upload file
            with open(file_path, 'rb') as f:
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=f,
                    ContentType='application/json',
                    CacheControl='public, max-age=31536000',  # 1 year cache
                )

            # Generate public URL (assumes custom domain or R2.dev)
            url = f"https://{self.bucket_name}.r2.dev/{object_key}"

            logger.info(f"Published to R2: {url}")
            return url

        except Exception as e:
            logger.error(f"Failed to publish to R2: {e}")
            raise


class LocalPublisher(StoragePublisher):
    """Publishes attestations to local filesystem (for testing)"""

    def __init__(self, base_path: str):
        self.base_path = base_path

    def publish(self, file_path: str, object_key: str) -> str:
        """
        Copy file to local storage

        Args:
            file_path: Source file path
            object_key: Destination path relative to base_path

        Returns:
            File URL
        """
        import shutil

        dest_path = os.path.join(self.base_path, object_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        shutil.copy2(file_path, dest_path)

        logger.info(f"Published locally: {dest_path}")
        return f"file://{dest_path}"


def get_publisher(storage_type: str) -> StoragePublisher:
    """
    Get appropriate publisher based on storage type

    Args:
        storage_type: Type of storage (s3, r2, local)

    Returns:
        StoragePublisher instance
    """
    if storage_type == 's3':
        bucket = os.getenv('S3_BUCKET')
        region = os.getenv('AWS_REGION', 'us-east-1')

        if not bucket:
            raise ValueError("S3_BUCKET environment variable not set")

        return S3Publisher(bucket, region)

    elif storage_type == 'r2':
        bucket = os.getenv('R2_BUCKET')
        account_id = os.getenv('R2_ACCOUNT_ID')
        access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')

        if not all([bucket, account_id, access_key_id, secret_access_key]):
            raise ValueError("R2 environment variables not set")

        return R2Publisher(bucket, account_id, access_key_id, secret_access_key)

    elif storage_type == 'local':
        base_path = os.getenv('LOCAL_STORAGE_PATH', './published')
        return LocalPublisher(base_path)

    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


def publish_attestation(
    attestation_path: str,
    date: str,
    storage_type: str = 'local'
) -> str:
    """
    Publish attestation to storage

    Args:
        attestation_path: Path to attestation file
        date: Date string (YYYY-MM-DD)
        storage_type: Type of storage (s3, r2, local)

    Returns:
        Public URL of published attestation
    """
    publisher = get_publisher(storage_type)

    # Generate object key
    object_key = f"attestations/{date}.json"

    # Publish
    url = publisher.publish(attestation_path, object_key)

    return url


def publish_with_metadata(
    attestation_path: str,
    date: str,
    storage_type: str = 'local'
) -> Dict[str, Any]:
    """
    Publish attestation and return metadata

    Args:
        attestation_path: Path to attestation file
        date: Date string (YYYY-MM-DD)
        storage_type: Type of storage

    Returns:
        Publication metadata dictionary
    """
    # Publish attestation
    url = publish_attestation(attestation_path, date, storage_type)

    # Load attestation to get root hash
    with open(attestation_path, 'r') as f:
        attestation = json.load(f)

    # Create metadata
    metadata = {
        'date': date,
        'url': url,
        'root_hash': attestation['root_hash'],
        'receipt_count': attestation['receipt_count'],
        'published_at': datetime.now(timezone.utc).isoformat(),
        'storage_type': storage_type
    }

    logger.info(f"Published attestation for {date}: {url}")
    return metadata


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Publish attestation to cloud storage')
    parser.add_argument('--attestation', type=str, required=True, help='Path to attestation file')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('--storage', type=str, default='local', choices=['s3', 'r2', 'local'], help='Storage type')
    parser.add_argument('--output', type=str, help='Path to save publication metadata')

    args = parser.parse_args()

    # Extract date from attestation filename if not provided
    date = args.date
    if not date:
        basename = os.path.basename(args.attestation)
        date = os.path.splitext(basename)[0]

    # Publish
    try:
        metadata = publish_with_metadata(args.attestation, date, args.storage)

        # Save metadata if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"Metadata saved to: {args.output}")

        print(f"\nAttestation published successfully!")
        print(f"Date: {metadata['date']}")
        print(f"URL: {metadata['url']}")
        print(f"Root hash: {metadata['root_hash']}")
        print(f"Receipt count: {metadata['receipt_count']}")

    except Exception as e:
        logger.error(f"Failed to publish attestation: {e}")
        exit(1)


if __name__ == '__main__':
    main()
