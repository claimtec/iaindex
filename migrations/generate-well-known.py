#!/usr/bin/env python3
"""
Generate .well-known/aiindex-policy.json from ai-index.json

This script extracts policy, receipts, and rate limit information from
ai-index.json and generates a standalone policy file for fast client access.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PolicyGenerator:
    """Generates .well-known/aiindex-policy.json"""

    def __init__(self, validate: bool = True):
        """
        Initialize generator

        Args:
            validate: If True, validate against schema
        """
        self.validate = validate

    def generate(
        self,
        ai_index_path: Path,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate policy file from ai-index.json

        Args:
            ai_index_path: Path to ai-index.json
            output_path: Optional output path (default: .well-known/aiindex-policy.json)

        Returns:
            Path to generated file
        """
        try:
            logger.info(f"Reading ai-index.json from: {ai_index_path}")

            # Read ai-index.json
            with open(ai_index_path, 'r', encoding='utf-8') as f:
                ai_index = json.load(f)

            # Extract policy information
            policy_data = self._extract_policy(ai_index)

            # Validate if enabled
            if self.validate:
                self._validate_policy(policy_data)

            # Determine output path
            if output_path is None:
                base_dir = ai_index_path.parent
                well_known_dir = base_dir / '.well-known'
                well_known_dir.mkdir(exist_ok=True)
                output_path = well_known_dir / 'aiindex-policy.json'

            # Write policy file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(policy_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Generated policy file: {output_path}")
            logger.info(f"Policy summary: {self._summarize_policy(policy_data)}")

            return output_path

        except Exception as e:
            logger.error(f"Error generating policy file: {e}", exc_info=True)
            raise

    def _extract_policy(self, ai_index: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract policy information from ai-index.json

        Args:
            ai_index: AIIndex data

        Returns:
            Policy data
        """
        # Base policy structure
        policy_data = {
            'version': ai_index.get('version', '1.1'),
            'publisher_id': ai_index.get('publisher_id'),
            'domain': ai_index.get('domain'),
            'last_updated': datetime.now(timezone.utc).isoformat(),
        }

        # Extract policy section
        if 'policy' in ai_index:
            policy_data['policy'] = ai_index['policy'].copy()
        else:
            # Fallback to access_policy (v1.0 compatibility)
            old_policy = ai_index.get('access_policy', {})
            policy_data['policy'] = {
                'training': 'allow' if old_policy.get('allowed', True) else 'block',
                'retrieval': 'allow',
                'attribution_required': old_policy.get('attribution_required', True),
                'commercial_use': old_policy.get('commercial_use', True)
            }

        # Extract receipts section
        if 'receipts' in ai_index:
            policy_data['receipts'] = ai_index['receipts'].copy()
        else:
            # Fallback to access_policy
            old_policy = ai_index.get('access_policy', {})
            policy_data['receipts'] = {
                'require_signed': old_policy.get('receipt_required', False)
            }
            if old_policy.get('webhook_url'):
                policy_data['receipts']['webhook_url'] = old_policy['webhook_url']

        # Extract or generate rate limits
        rate_hint = ai_index.get('policy', {}).get('rate_hint', 60)
        policy_data['rate_limits'] = {
            'requests_per_minute': rate_hint,
            'burst': rate_hint * 2,
            'description': 'Recommended rate limits for this publisher'
        }

        # Add render information if available
        if 'render_fallback' in ai_index:
            render_config = ai_index['render_fallback']
            if render_config.get('mode') != 'none':
                policy_data['render_available'] = {
                    'mode': render_config.get('mode'),
                    'last_rendered_at': render_config.get('last_rendered_at'),
                    'ttl': render_config.get('ttl')
                }

        # Add embeddings information if available
        if 'embeddings_manifest' in ai_index:
            embeddings = ai_index['embeddings_manifest']
            policy_data['embeddings_available'] = {
                'model': embeddings.get('model'),
                'dimensions': embeddings.get('dimensions'),
                'vector_url': embeddings.get('vector_url'),
                'last_updated': embeddings.get('last_updated')
            }

        # Add C2PA provenance if available
        if 'c2pa_provenance' in ai_index:
            c2pa = ai_index['c2pa_provenance']
            policy_data['c2pa_provenance'] = {
                'enabled': True,
                'credential_url': c2pa.get('credential_url'),
                'verify_url': f"https://verify.contentauthenticity.org/inspect?url={c2pa.get('credential_url')}"
            }

        # Add contact information
        if 'publisher' in ai_index and 'contact' in ai_index['publisher']:
            policy_data['contact'] = ai_index['publisher']['contact']

        return policy_data

    def _validate_policy(self, policy_data: Dict[str, Any]) -> None:
        """
        Validate policy data

        Args:
            policy_data: Policy data to validate

        Raises:
            ValueError: If validation fails
        """
        # Required fields
        required = ['version', 'publisher_id', 'domain', 'policy']
        for field in required:
            if field not in policy_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate policy values
        policy = policy_data.get('policy', {})

        valid_training = ['allow', 'block', 'require_offer']
        training = policy.get('training')
        if training and training not in valid_training:
            raise ValueError(f"Invalid training policy: {training}")

        valid_retrieval = ['allow', 'block']
        retrieval = policy.get('retrieval')
        if retrieval and retrieval not in valid_retrieval:
            raise ValueError(f"Invalid retrieval policy: {retrieval}")

        # Validate receipts section
        if 'receipts' in policy_data:
            receipts = policy_data['receipts']
            if 'require_signed' in receipts and not isinstance(receipts['require_signed'], bool):
                raise ValueError("receipts.require_signed must be boolean")

            # If signed receipts required, webhook or supported algorithms should be present
            if receipts.get('require_signed', False):
                if not receipts.get('webhook_url') and not receipts.get('supported_algorithms'):
                    logger.warning("Signed receipts required but no webhook_url or supported_algorithms specified")

        logger.info("Policy validation passed")

    def _summarize_policy(self, policy_data: Dict[str, Any]) -> str:
        """
        Create human-readable policy summary

        Args:
            policy_data: Policy data

        Returns:
            Summary string
        """
        policy = policy_data.get('policy', {})
        receipts = policy_data.get('receipts', {})

        parts = []
        parts.append(f"Training: {policy.get('training', 'unknown')}")
        parts.append(f"Retrieval: {policy.get('retrieval', 'unknown')}")

        if policy.get('attribution_required'):
            parts.append("Attribution required")

        if receipts.get('require_signed'):
            parts.append("Signed receipts required")

        if 'embeddings_available' in policy_data:
            parts.append("Embeddings available")

        if 'c2pa_provenance' in policy_data:
            parts.append("C2PA provenance enabled")

        return ", ".join(parts)

    def generate_multiple(
        self,
        directory: Path,
        recursive: bool = True
    ) -> int:
        """
        Generate policy files for all ai-index.json files in directory

        Args:
            directory: Directory to search
            recursive: If True, search subdirectories

        Returns:
            Number of policy files generated
        """
        pattern = '**/ai-index.json' if recursive else 'ai-index.json'
        files = list(directory.glob(pattern))

        logger.info(f"Found {len(files)} ai-index.json files")

        success_count = 0
        error_count = 0

        for ai_index_path in files:
            try:
                self.generate(ai_index_path)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to generate policy for {ai_index_path}: {e}")
                error_count += 1

        logger.info(f"\nGeneration Summary:")
        logger.info(f"  Successfully generated: {success_count}")
        logger.info(f"  Errors: {error_count}")

        return success_count


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate .well-known/aiindex-policy.json from ai-index.json'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to ai-index.json file or directory'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output path for policy file'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively process directory'
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Initialize generator
    generator = PolicyGenerator(validate=not args.no_validate)

    # Check if path exists
    if not args.path.exists():
        logger.error(f"Path not found: {args.path}")
        sys.exit(1)

    # Generate policy file(s)
    try:
        if args.path.is_file():
            generator.generate(args.path, args.output)
            sys.exit(0)
        elif args.path.is_dir():
            count = generator.generate_multiple(args.path, recursive=args.recursive)
            sys.exit(0 if count > 0 else 1)
        else:
            logger.error(f"Invalid path: {args.path}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
