#!/usr/bin/env python3
"""
AIIndex v1.0 to v1.1 File Migration Script

Migrates existing v1.0 ai-index.json files to v1.1 format by:
- Adding new v1.1 fields with sensible defaults
- Preserving all v1.0 fields (backward compatible)
- Updating version to "1.1"
- Generating .well-known/aiindex-policy.json
- Validating against v1.1 schema
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIIndexMigrator:
    """Migrates AIIndex files from v1.0 to v1.1"""

    def __init__(self, dry_run: bool = False, backup: bool = True):
        """
        Initialize migrator

        Args:
            dry_run: If True, only show changes without writing
            backup: If True, create .bak files before modifying
        """
        self.dry_run = dry_run
        self.backup = backup
        self.migrated_count = 0
        self.error_count = 0

    def migrate_file(self, file_path: Path) -> bool:
        """
        Migrate a single ai-index.json file

        Args:
            file_path: Path to ai-index.json file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing: {file_path}")

            # Read existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check version
            current_version = data.get('version', '1.0')
            if current_version == '1.1':
                logger.info(f"Already v1.1, skipping: {file_path}")
                return True

            # Backup if enabled
            if self.backup and not self.dry_run:
                backup_path = file_path.with_suffix('.json.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created backup: {backup_path}")

            # Migrate to v1.1
            migrated_data = self._migrate_to_v1_1(data)

            # Validate migrated data
            self._validate_v1_1(migrated_data)

            # Write migrated file
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(migrated_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Migrated: {file_path}")

                # Generate policy file
                self._generate_policy_file(file_path.parent, migrated_data)
            else:
                logger.info(f"[DRY RUN] Would migrate: {file_path}")
                logger.info(f"Changes:\n{json.dumps(self._get_diff(data, migrated_data), indent=2)}")

            self.migrated_count += 1
            return True

        except Exception as e:
            logger.error(f"Error migrating {file_path}: {e}", exc_info=True)
            self.error_count += 1
            return False

    def _migrate_to_v1_1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v1.0 data structure to v1.1

        Args:
            data: v1.0 data

        Returns:
            v1.1 data
        """
        # Update version
        data['version'] = '1.1'
        data['last_updated'] = datetime.now(timezone.utc).isoformat()

        # Add policy section (v1.1 enhanced)
        if 'policy' not in data:
            # Migrate from old access_policy if it exists
            old_policy = data.get('access_policy', {})
            data['policy'] = {
                'training': 'allow' if old_policy.get('allowed', True) else 'block',
                'retrieval': 'allow',
                'attribution_required': old_policy.get('attribution_required', True),
                'commercial_use': old_policy.get('commercial_use', True)
            }
        else:
            # Ensure new fields exist
            if 'training' not in data['policy']:
                data['policy']['training'] = 'allow'
            if 'retrieval' not in data['policy']:
                data['policy']['retrieval'] = 'allow'

        # Add receipts section (v1.1)
        if 'receipts' not in data:
            old_policy = data.get('access_policy', {})
            data['receipts'] = {
                'require_signed': old_policy.get('receipt_required', False),
            }
            # Add webhook URL if it exists
            if old_policy.get('webhook_url'):
                data['receipts']['webhook_url'] = old_policy['webhook_url']

        # Add render_fallback section (v1.1)
        if 'render_fallback' not in data:
            data['render_fallback'] = {
                'mode': 'none'
            }

        # Enhance pages with optional v1.1 fields
        if 'pages' in data:
            for page in data['pages']:
                # Add placeholders for rendered_text and content_hash
                # These will be populated by the rendering system
                if 'rendered_text' not in page:
                    page['rendered_text'] = None
                if 'content_hash' not in page:
                    page['content_hash'] = None

        # Remove deprecated access_policy (moved to policy)
        if 'access_policy' in data:
            logger.info("Migrating access_policy to policy section")
            del data['access_policy']

        # Add verification badge_url if verified
        if 'verification' in data and data['verification'].get('verified'):
            publisher_id = data.get('publisher_id')
            if 'badge_url' not in data['verification'] and publisher_id:
                data['verification']['badge_url'] = f"https://aiindex.org/badges/{publisher_id}"

        return data

    def _validate_v1_1(self, data: Dict[str, Any]) -> None:
        """
        Validate v1.1 data structure

        Args:
            data: Data to validate

        Raises:
            ValueError: If validation fails
        """
        # Required fields
        required = ['version', 'publisher_id', 'domain', 'last_updated']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Version check
        if data['version'] != '1.1':
            raise ValueError(f"Invalid version: {data['version']}")

        # Policy validation
        if 'policy' in data:
            valid_training = ['allow', 'block', 'require_offer']
            valid_retrieval = ['allow', 'block']

            training = data['policy'].get('training')
            if training and training not in valid_training:
                raise ValueError(f"Invalid training policy: {training}")

            retrieval = data['policy'].get('retrieval')
            if retrieval and retrieval not in valid_retrieval:
                raise ValueError(f"Invalid retrieval policy: {retrieval}")

        # Render mode validation
        if 'render_fallback' in data:
            valid_modes = ['none', 'edge', 'local']
            mode = data['render_fallback'].get('mode')
            if mode and mode not in valid_modes:
                raise ValueError(f"Invalid render mode: {mode}")

        logger.info("Validation passed")

    def _generate_policy_file(self, base_dir: Path, data: Dict[str, Any]) -> None:
        """
        Generate .well-known/aiindex-policy.json

        Args:
            base_dir: Base directory (where ai-index.json lives)
            data: Migrated data
        """
        well_known_dir = base_dir / '.well-known'
        well_known_dir.mkdir(exist_ok=True)

        policy_file = well_known_dir / 'aiindex-policy.json'

        policy_data = {
            'version': '1.1',
            'publisher_id': data.get('publisher_id'),
            'domain': data.get('domain'),
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'policy': data.get('policy', {}),
            'receipts': data.get('receipts', {}),
            'rate_limits': {
                'requests_per_minute': data.get('policy', {}).get('rate_hint', 60),
                'burst': data.get('policy', {}).get('rate_hint', 60) * 2
            }
        }

        with open(policy_file, 'w', encoding='utf-8') as f:
            json.dump(policy_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated policy file: {policy_file}")

    def _get_diff(self, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get differences between old and new data

        Args:
            old: Old data
            new: New data

        Returns:
            Diff summary
        """
        added = {}
        modified = {}

        for key, value in new.items():
            if key not in old:
                added[key] = value
            elif old[key] != value:
                modified[key] = {'old': old[key], 'new': value}

        return {
            'added_fields': list(added.keys()),
            'modified_fields': list(modified.keys()),
            'version_change': f"{old.get('version', '1.0')} -> {new.get('version')}"
        }

    def migrate_directory(self, directory: Path, recursive: bool = True) -> None:
        """
        Migrate all ai-index.json files in directory

        Args:
            directory: Directory to search
            recursive: If True, search subdirectories
        """
        pattern = '**/ai-index.json' if recursive else 'ai-index.json'
        files = list(directory.glob(pattern))

        logger.info(f"Found {len(files)} ai-index.json files to migrate")

        for file_path in files:
            self.migrate_file(file_path)

        logger.info(f"\nMigration Summary:")
        logger.info(f"  Successfully migrated: {self.migrated_count}")
        logger.info(f"  Errors: {self.error_count}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate AIIndex files from v1.0 to v1.1'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to ai-index.json file or directory'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively search directory for ai-index.json files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without modifying files'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Initialize migrator
    migrator = AIIndexMigrator(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    # Check if path exists
    if not args.path.exists():
        logger.error(f"Path not found: {args.path}")
        sys.exit(1)

    # Migrate file or directory
    if args.path.is_file():
        success = migrator.migrate_file(args.path)
        sys.exit(0 if success else 1)
    elif args.path.is_dir():
        migrator.migrate_directory(args.path, recursive=args.recursive)
        sys.exit(0 if migrator.error_count == 0 else 1)
    else:
        logger.error(f"Invalid path: {args.path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
