#!/usr/bin/env python3
"""
Merkle Tree Builder for Verified Receipts
Builds a daily Merkle tree from all verified receipts in the database
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MerkleNode:
    """Represents a node in the Merkle tree"""

    def __init__(self, left=None, right=None, data=None, hash_value=None):
        self.left = left
        self.right = right
        self.data = data
        self.hash = hash_value or self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash of node"""
        if self.data:
            # Leaf node - hash the data
            return hashlib.sha256(json.dumps(self.data, sort_keys=True).encode()).hexdigest()
        else:
            # Internal node - hash concatenation of children
            left_hash = self.left.hash if self.left else ""
            right_hash = self.right.hash if self.right else ""
            combined = left_hash + right_hash
            return hashlib.sha256(combined.encode()).hexdigest()


class MerkleTree:
    """Merkle tree implementation for receipt attestation"""

    def __init__(self, receipts: List[Dict[str, Any]]):
        self.receipts = receipts
        self.leaves = []
        self.root = None
        self._build_tree()

    def _build_tree(self):
        """Build the Merkle tree from receipts"""
        if not self.receipts:
            logger.warning("No receipts provided, creating empty tree")
            self.root = MerkleNode(data={}, hash_value=hashlib.sha256(b"").hexdigest())
            return

        # Create leaf nodes
        self.leaves = [MerkleNode(data=receipt) for receipt in self.receipts]

        # Build tree bottom-up
        current_level = self.leaves[:]

        while len(current_level) > 1:
            next_level = []

            # Process pairs of nodes
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number of nodes, duplicate the last one
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                parent = MerkleNode(left=left, right=right)
                next_level.append(parent)

            current_level = next_level

        self.root = current_level[0]
        logger.info(f"Built Merkle tree with {len(self.receipts)} receipts, root hash: {self.root.hash}")

    def get_root_hash(self) -> str:
        """Get the root hash of the tree"""
        return self.root.hash if self.root else ""

    def get_proof(self, receipt_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Generate inclusion proof for a specific receipt
        Returns list of sibling hashes needed to verify inclusion
        """
        # Find the leaf index
        leaf_index = None
        for i, receipt in enumerate(self.receipts):
            if receipt.get('id') == receipt_id:
                leaf_index = i
                break

        if leaf_index is None:
            logger.error(f"Receipt {receipt_id} not found in tree")
            return None

        proof = []
        current_level = self.leaves[:]
        index = leaf_index

        # Traverse up the tree collecting sibling hashes
        while len(current_level) > 1:
            next_level = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                # If current index is in this pair, record the sibling
                if i == index or i + 1 == index:
                    sibling_index = i + 1 if i == index else i
                    sibling = current_level[sibling_index] if sibling_index < len(current_level) else left

                    proof.append({
                        'hash': sibling.hash,
                        'position': 'right' if i == index else 'left'
                    })

                    # Update index for next level
                    index = i // 2

                parent = MerkleNode(left=left, right=right)
                next_level.append(parent)

            current_level = next_level

        return proof

    def to_dict(self) -> Dict[str, Any]:
        """Export tree metadata as dictionary"""
        return {
            'root_hash': self.get_root_hash(),
            'receipt_count': len(self.receipts),
            'receipt_ids': [r.get('id') for r in self.receipts],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0'
        }


def fetch_verified_receipts(date: str) -> List[Dict[str, Any]]:
    """
    Fetch verified receipts from database for a specific date

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        List of verified receipt records
    """
    # TODO: Implement actual database connection
    # For now, return mock data structure
    try:
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            logger.warning("Database credentials not configured, using mock data")
            return _get_mock_receipts()

        supabase = create_client(supabase_url, supabase_key)

        # Query verified receipts for the date
        response = supabase.table('receipts').select('*').eq('verification_status', 'verified').gte('created_at', f'{date}T00:00:00Z').lt('created_at', f'{date}T23:59:59Z').execute()

        logger.info(f"Fetched {len(response.data)} verified receipts for {date}")
        return response.data

    except ImportError:
        logger.warning("Supabase client not installed, using mock data")
        return _get_mock_receipts()
    except Exception as e:
        logger.error(f"Error fetching receipts: {e}")
        return _get_mock_receipts()


def _get_mock_receipts() -> List[Dict[str, Any]]:
    """Generate mock receipts for testing"""
    return [
        {
            'id': f'receipt_{i:04d}',
            'agent_id': f'agent_{i % 3}',
            'action': 'verification',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'verification_status': 'verified',
            'data': {'test': True}
        }
        for i in range(10)
    ]


def build_daily_tree(date: Optional[str] = None) -> MerkleTree:
    """
    Build Merkle tree for a specific date

    Args:
        date: Date in YYYY-MM-DD format, defaults to today

    Returns:
        MerkleTree instance
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    logger.info(f"Building Merkle tree for date: {date}")

    # Fetch verified receipts
    receipts = fetch_verified_receipts(date)

    if not receipts:
        logger.warning(f"No verified receipts found for {date}")

    # Build tree
    tree = MerkleTree(receipts)

    return tree


def save_tree_metadata(tree: MerkleTree, output_dir: str, date: str):
    """
    Save tree metadata to file

    Args:
        tree: MerkleTree instance
        output_dir: Directory to save metadata
        date: Date string for filename
    """
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f'{date}.json')

    metadata = tree.to_dict()

    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved tree metadata to {output_path}")
    return output_path


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Build Merkle tree from verified receipts')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (defaults to today)')
    parser.add_argument('--output-dir', type=str, default='./attestations', help='Output directory for attestations')

    args = parser.parse_args()

    # Build tree
    tree = build_daily_tree(args.date)

    # Save metadata
    date = args.date or datetime.now(timezone.utc).strftime('%Y-%m-%d')
    output_path = save_tree_metadata(tree, args.output_dir, date)

    print(f"Merkle tree built successfully!")
    print(f"Root hash: {tree.get_root_hash()}")
    print(f"Receipt count: {len(tree.receipts)}")
    print(f"Metadata saved to: {output_path}")


if __name__ == '__main__':
    main()
