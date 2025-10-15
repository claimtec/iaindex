#!/usr/bin/env python3
"""
Merkle Proof Generator
Generates inclusion proofs for individual receipts
"""

import json
import os
import argparse
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from build_tree import build_daily_tree, MerkleTree

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProofGenerator:
    """Generates and manages inclusion proofs"""

    def __init__(self, tree: MerkleTree):
        self.tree = tree

    def generate_proof(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate inclusion proof for a specific receipt

        Args:
            receipt_id: ID of the receipt to generate proof for

        Returns:
            Proof dictionary or None if receipt not found
        """
        # Get the receipt data
        receipt = None
        for r in self.tree.receipts:
            if r.get('id') == receipt_id:
                receipt = r
                break

        if not receipt:
            logger.error(f"Receipt {receipt_id} not found in tree")
            return None

        # Get Merkle proof
        proof_path = self.tree.get_proof(receipt_id)

        if proof_path is None:
            logger.error(f"Failed to generate proof for receipt {receipt_id}")
            return None

        # Build proof object
        proof = {
            'receipt_id': receipt_id,
            'receipt_data': receipt,
            'merkle_root': self.tree.get_root_hash(),
            'proof_path': proof_path,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'tree_size': len(self.tree.receipts)
        }

        logger.info(f"Generated proof for receipt {receipt_id}")
        return proof

    def generate_batch_proofs(self, receipt_ids: list) -> Dict[str, Any]:
        """
        Generate proofs for multiple receipts

        Args:
            receipt_ids: List of receipt IDs

        Returns:
            Dictionary mapping receipt IDs to proofs
        """
        proofs = {}
        for receipt_id in receipt_ids:
            proof = self.generate_proof(receipt_id)
            if proof:
                proofs[receipt_id] = proof

        logger.info(f"Generated {len(proofs)} proofs out of {len(receipt_ids)} requested")
        return proofs

    def save_proof(self, proof: Dict[str, Any], output_dir: str) -> str:
        """
        Save proof to file

        Args:
            proof: Proof dictionary
            output_dir: Directory to save proof

        Returns:
            Path to saved proof file
        """
        os.makedirs(output_dir, exist_ok=True)

        receipt_id = proof['receipt_id']
        output_path = os.path.join(output_dir, f'proof_{receipt_id}.json')

        with open(output_path, 'w') as f:
            json.dump(proof, f, indent=2)

        logger.info(f"Saved proof to {output_path}")
        return output_path


def load_tree_metadata(attestation_path: str) -> Dict[str, Any]:
    """
    Load tree metadata from attestation file

    Args:
        attestation_path: Path to attestation file

    Returns:
        Tree metadata dictionary
    """
    with open(attestation_path, 'r') as f:
        return json.load(f)


def generate_proof_from_attestation(
    receipt_id: str,
    attestation_path: str,
    output_dir: str
) -> Optional[str]:
    """
    Generate proof for a receipt from existing attestation

    Args:
        receipt_id: Receipt ID to generate proof for
        attestation_path: Path to attestation file
        output_dir: Directory to save proof

    Returns:
        Path to saved proof file or None
    """
    # Load tree metadata
    metadata = load_tree_metadata(attestation_path)

    # Check if receipt is in tree
    if receipt_id not in metadata.get('receipt_ids', []):
        logger.error(f"Receipt {receipt_id} not found in attestation")
        return None

    # Rebuild tree (would need to fetch receipts again)
    # For now, we'll need to have the tree already built
    logger.warning("Proof generation from attestation requires rebuilding tree")
    return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate Merkle inclusion proof for receipt')
    parser.add_argument('--receipt-id', type=str, required=True, help='Receipt ID to generate proof for')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (defaults to today)')
    parser.add_argument('--output-dir', type=str, default='./proofs', help='Output directory for proofs')
    parser.add_argument('--attestation', type=str, help='Path to existing attestation file')

    args = parser.parse_args()

    # If attestation file provided, use it
    if args.attestation:
        output_path = generate_proof_from_attestation(
            args.receipt_id,
            args.attestation,
            args.output_dir
        )
        if output_path:
            print(f"Proof generated and saved to: {output_path}")
        else:
            print("Failed to generate proof from attestation")
            exit(1)
        return

    # Otherwise, rebuild tree for the date
    date = args.date or datetime.now(timezone.utc).strftime('%Y-%m-%d')
    logger.info(f"Rebuilding tree for date: {date}")

    tree = build_daily_tree(date)

    # Generate proof
    generator = ProofGenerator(tree)
    proof = generator.generate_proof(args.receipt_id)

    if not proof:
        print(f"Failed to generate proof for receipt {args.receipt_id}")
        exit(1)

    # Save proof
    output_path = generator.save_proof(proof, args.output_dir)

    print(f"Proof generated successfully!")
    print(f"Receipt ID: {args.receipt_id}")
    print(f"Merkle root: {proof['merkle_root']}")
    print(f"Proof path length: {len(proof['proof_path'])}")
    print(f"Saved to: {output_path}")


if __name__ == '__main__':
    main()
