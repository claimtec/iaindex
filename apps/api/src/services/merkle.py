"""
Merkle tree service for attestations
"""
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class MerkleTreeService:
    """Service for building and managing Merkle trees"""

    @staticmethod
    def hash_data(data: str) -> str:
        """
        Hash data using SHA256

        Args:
            data: Data to hash

        Returns:
            Hex-encoded hash
        """
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def hash_pair(left: str, right: str) -> str:
        """
        Hash a pair of hashes together

        Args:
            left: Left hash
            right: Right hash

        Returns:
            Combined hash
        """
        combined = left + right
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def build_merkle_tree(receipt_hashes: List[str]) -> Tuple[str, List[List[str]]]:
        """
        Build a Merkle tree from receipt hashes

        Args:
            receipt_hashes: List of receipt hashes (leaf nodes)

        Returns:
            Tuple of (root_hash, tree_levels)
        """
        if not receipt_hashes:
            return MerkleTreeService.hash_data("empty"), [[]]

        if len(receipt_hashes) == 1:
            return receipt_hashes[0], [receipt_hashes]

        # Build tree bottom-up
        tree_levels = [receipt_hashes]
        current_level = receipt_hashes[:]

        while len(current_level) > 1:
            next_level = []

            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]

                # If odd number of nodes, duplicate the last one
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = current_level[i]

                parent_hash = MerkleTreeService.hash_pair(left, right)
                next_level.append(parent_hash)

            tree_levels.append(next_level)
            current_level = next_level

        root_hash = current_level[0]
        return root_hash, tree_levels

    @staticmethod
    def get_merkle_proof(
        receipt_hash: str,
        tree_levels: List[List[str]]
    ) -> Optional[List[Tuple[str, str]]]:
        """
        Generate Merkle proof for a receipt

        Args:
            receipt_hash: Hash to generate proof for
            tree_levels: Complete tree structure

        Returns:
            List of (hash, position) tuples for proof path, or None if not found
        """
        if not tree_levels:
            return None

        # Find receipt in leaf level
        try:
            index = tree_levels[0].index(receipt_hash)
        except ValueError:
            return None

        proof = []

        # Build proof path
        for level in tree_levels[:-1]:  # Exclude root level
            # Determine sibling
            if index % 2 == 0:
                # Left node, sibling is to the right
                if index + 1 < len(level):
                    sibling = level[index + 1]
                    position = "right"
                else:
                    sibling = level[index]  # Duplicate for odd count
                    position = "right"
            else:
                # Right node, sibling is to the left
                sibling = level[index - 1]
                position = "left"

            proof.append((sibling, position))
            index = index // 2

        return proof

    @staticmethod
    def verify_merkle_proof(
        receipt_hash: str,
        merkle_root: str,
        proof: List[Tuple[str, str]]
    ) -> bool:
        """
        Verify a Merkle proof

        Args:
            receipt_hash: Hash to verify
            merkle_root: Expected root hash
            proof: Proof path

        Returns:
            True if proof is valid
        """
        current_hash = receipt_hash

        for sibling_hash, position in proof:
            if position == "left":
                current_hash = MerkleTreeService.hash_pair(sibling_hash, current_hash)
            else:
                current_hash = MerkleTreeService.hash_pair(current_hash, sibling_hash)

        return current_hash == merkle_root

    @staticmethod
    def format_date_key(date_obj: datetime | date) -> str:
        """
        Format date for use as attestation key

        Args:
            date_obj: Date object

        Returns:
            Date string in YYYY-MM-DD format
        """
        if isinstance(date_obj, datetime):
            return date_obj.date().isoformat()
        return date_obj.isoformat()
