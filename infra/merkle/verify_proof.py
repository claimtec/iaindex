#!/usr/bin/env python3
"""
Merkle Proof Verifier
Verifies the validity of inclusion proofs
"""

import json
import hashlib
import argparse
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProofVerifier:
    """Verifies Merkle inclusion proofs"""

    @staticmethod
    def calculate_leaf_hash(receipt_data: Dict[str, Any]) -> str:
        """
        Calculate hash of receipt data (leaf node)

        Args:
            receipt_data: Receipt data dictionary

        Returns:
            Hex string of hash
        """
        return hashlib.sha256(
            json.dumps(receipt_data, sort_keys=True).encode()
        ).hexdigest()

    @staticmethod
    def calculate_parent_hash(left_hash: str, right_hash: str) -> str:
        """
        Calculate hash of parent node

        Args:
            left_hash: Hash of left child
            right_hash: Hash of right child

        Returns:
            Hex string of parent hash
        """
        combined = left_hash + right_hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def verify_proof(
        self,
        receipt_data: Dict[str, Any],
        proof_path: list,
        claimed_root: str
    ) -> bool:
        """
        Verify that a receipt is included in the Merkle tree

        Args:
            receipt_data: Receipt data to verify
            proof_path: List of sibling hashes and positions
            claimed_root: Claimed Merkle root hash

        Returns:
            True if proof is valid, False otherwise
        """
        # Calculate leaf hash
        current_hash = self.calculate_leaf_hash(receipt_data)
        logger.info(f"Leaf hash: {current_hash}")

        # Walk up the tree using proof path
        for i, step in enumerate(proof_path):
            sibling_hash = step['hash']
            position = step['position']

            # Combine with sibling based on position
            if position == 'left':
                current_hash = self.calculate_parent_hash(sibling_hash, current_hash)
            else:  # position == 'right'
                current_hash = self.calculate_parent_hash(current_hash, sibling_hash)

            logger.debug(f"Step {i}: {position} sibling, hash = {current_hash}")

        # Check if we arrived at the claimed root
        is_valid = current_hash == claimed_root

        if is_valid:
            logger.info(f"Proof is VALID - computed root matches claimed root")
        else:
            logger.error(f"Proof is INVALID - computed root: {current_hash}, claimed root: {claimed_root}")

        return is_valid

    def verify_proof_file(self, proof_path: str) -> bool:
        """
        Verify a proof from a JSON file

        Args:
            proof_path: Path to proof file

        Returns:
            True if proof is valid, False otherwise
        """
        try:
            with open(proof_path, 'r') as f:
                proof = json.load(f)

            receipt_data = proof['receipt_data']
            merkle_proof = proof['proof_path']
            merkle_root = proof['merkle_root']

            logger.info(f"Verifying proof for receipt: {proof['receipt_id']}")
            logger.info(f"Merkle root: {merkle_root}")
            logger.info(f"Proof path length: {len(merkle_proof)}")

            return self.verify_proof(receipt_data, merkle_proof, merkle_root)

        except FileNotFoundError:
            logger.error(f"Proof file not found: {proof_path}")
            return False
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in proof file: {proof_path}")
            return False
        except KeyError as e:
            logger.error(f"Missing required field in proof: {e}")
            return False
        except Exception as e:
            logger.error(f"Error verifying proof: {e}")
            return False


def verify_against_attestation(
    proof_path: str,
    attestation_path: str
) -> bool:
    """
    Verify a proof against an attestation file

    Args:
        proof_path: Path to proof file
        attestation_path: Path to attestation file

    Returns:
        True if proof is valid against attestation
    """
    try:
        # Load proof
        with open(proof_path, 'r') as f:
            proof = json.load(f)

        # Load attestation
        with open(attestation_path, 'r') as f:
            attestation = json.load(f)

        # Verify receipt is in attestation
        receipt_id = proof['receipt_id']
        if receipt_id not in attestation.get('receipt_ids', []):
            logger.error(f"Receipt {receipt_id} not found in attestation")
            return False

        # Verify root hash matches
        if proof['merkle_root'] != attestation['root_hash']:
            logger.error("Merkle root mismatch between proof and attestation")
            return False

        # Verify the proof itself
        verifier = ProofVerifier()
        return verifier.verify_proof(
            proof['receipt_data'],
            proof['proof_path'],
            proof['merkle_root']
        )

    except Exception as e:
        logger.error(f"Error verifying against attestation: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Verify Merkle inclusion proof')
    parser.add_argument('--proof', type=str, required=True, help='Path to proof file')
    parser.add_argument('--attestation', type=str, help='Path to attestation file (optional)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Verify proof
    if args.attestation:
        logger.info("Verifying proof against attestation")
        is_valid = verify_against_attestation(args.proof, args.attestation)
    else:
        logger.info("Verifying proof standalone")
        verifier = ProofVerifier()
        is_valid = verifier.verify_proof_file(args.proof)

    # Print result
    if is_valid:
        print("\n✓ PROOF IS VALID")
        print("The receipt is cryptographically proven to be included in the Merkle tree.")
        exit(0)
    else:
        print("\n✗ PROOF IS INVALID")
        print("The receipt cannot be verified against the claimed Merkle root.")
        exit(1)


if __name__ == '__main__':
    main()
