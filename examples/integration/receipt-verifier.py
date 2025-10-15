#!/usr/bin/env python3
"""
AIIndex Receipt Verifier

This script verifies access receipts for integrity and compliance:
1. Validates receipt schema
2. Verifies signatures (if present)
3. Checks required fields
4. Validates timestamps
5. Reports validation results

Usage:
    python receipt-verifier.py receipt.json
    python receipt-verifier.py --batch receipts/

Requirements:
    pip install jsonschema cryptography requests
"""

import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from jsonschema import validate, ValidationError
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, padding
    from cryptography.exceptions import InvalidSignature
    import requests
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install with: pip install jsonschema cryptography requests")
    exit(1)


# Receipt schema (based on receipts.schema.json)
RECEIPT_SCHEMA = {
    "type": "object",
    "required": ["version", "receipt_id", "publisher_id", "client_id", "timestamp"],
    "properties": {
        "version": {"type": "string", "pattern": "^1\\.0$"},
        "receipt_id": {"type": "string", "minLength": 1},
        "publisher_id": {"type": "string", "minLength": 3},
        "publisher_domain": {"type": "string"},
        "client_id": {"type": "string", "minLength": 3},
        "client_name": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "access": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string"},
                "status_code": {"type": "integer"},
                "content_hash": {"type": "string"},
                "pages_accessed": {"type": "array", "items": {"type": "string"}},
            },
        },
        "purpose": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["training", "inference", "research", "indexing", "other"],
                },
                "description": {"type": "string"},
                "commercial": {"type": "boolean"},
            },
        },
        "attribution": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["citation", "link", "inline", "none"],
                },
                "citation_text": {"type": "string"},
                "url": {"type": "string"},
            },
        },
        "signature": {
            "type": "object",
            "required": ["algorithm", "kid", "signature", "payload_hash"],
            "properties": {
                "algorithm": {"type": "string", "enum": ["ES256", "RS256"]},
                "kid": {"type": "string"},
                "signature": {"type": "string"},
                "payload_hash": {"type": "string"},
            },
        },
    },
}


@dataclass
class ValidationResult:
    """Result of receipt validation"""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ReceiptVerifier:
    """Verify AIIndex access receipts"""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def verify_receipt(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Verify a single receipt"""
        result = ValidationResult(valid=True)

        # 1. Schema validation
        schema_result = self._validate_schema(receipt)
        if not schema_result.valid:
            result.valid = False
            result.errors.extend(schema_result.errors)
            return result  # Stop if schema is invalid

        # 2. Field validation
        field_result = self._validate_fields(receipt)
        result.errors.extend(field_result.errors)
        result.warnings.extend(field_result.warnings)

        # 3. Timestamp validation
        timestamp_result = self._validate_timestamp(receipt)
        result.errors.extend(timestamp_result.errors)
        result.warnings.extend(timestamp_result.warnings)

        # 4. Signature validation (if present)
        if "signature" in receipt:
            sig_result = self._validate_signature(receipt)
            result.errors.extend(sig_result.errors)
            result.warnings.extend(sig_result.warnings)
            result.details["signature_valid"] = len(sig_result.errors) == 0

        # 5. Policy compliance check
        policy_result = self._check_policy_compliance(receipt)
        result.warnings.extend(policy_result.warnings)

        # Determine overall validity
        result.valid = len(result.errors) == 0

        return result

    def _validate_schema(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Validate receipt against JSON schema"""
        result = ValidationResult(valid=True)

        try:
            validate(instance=receipt, schema=RECEIPT_SCHEMA)
        except ValidationError as e:
            result.valid = False
            result.errors.append(f"Schema validation failed: {e.message}")

        return result

    def _validate_fields(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Validate individual fields"""
        result = ValidationResult(valid=True)

        # Check version
        if receipt.get("version") != "1.0":
            result.errors.append(f"Unsupported version: {receipt.get('version')}")

        # Check receipt_id format (should be UUID-like)
        receipt_id = receipt.get("receipt_id", "")
        if len(receipt_id) < 10:
            result.errors.append("receipt_id too short")

        # Check publisher_id and client_id
        if len(receipt.get("publisher_id", "")) < 3:
            result.errors.append("publisher_id too short")

        if len(receipt.get("client_id", "")) < 3:
            result.errors.append("client_id too short")

        # Warn if optional fields are missing
        if not receipt.get("client_name"):
            result.warnings.append("client_name not provided")

        if not receipt.get("publisher_domain"):
            result.warnings.append("publisher_domain not provided")

        # Validate access section
        access = receipt.get("access", {})
        if access:
            if access.get("status_code") != 200:
                result.warnings.append(
                    f"Non-200 status code: {access.get('status_code')}"
                )

            if not access.get("url"):
                result.warnings.append("access.url not provided")

        return result

    def _validate_timestamp(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Validate timestamp"""
        result = ValidationResult(valid=True)

        timestamp_str = receipt.get("timestamp")
        if not timestamp_str:
            result.errors.append("timestamp missing")
            return result

        try:
            # Parse ISO 8601 timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            # Check if timestamp is reasonable (not too old, not in future)
            now = datetime.now(timestamp.tzinfo)
            age = now - timestamp

            if age > timedelta(days=30):
                result.warnings.append(f"Receipt is old: {age.days} days")

            if age < timedelta(seconds=0):
                result.errors.append("Timestamp is in the future")

            result.details["receipt_age_days"] = age.days

        except ValueError as e:
            result.errors.append(f"Invalid timestamp format: {e}")

        return result

    def _validate_signature(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Validate cryptographic signature"""
        result = ValidationResult(valid=True)

        signature = receipt.get("signature", {})

        # Check required signature fields
        if not signature.get("algorithm"):
            result.errors.append("signature.algorithm missing")
            return result

        if not signature.get("signature"):
            result.errors.append("signature.signature missing")
            return result

        if not signature.get("payload_hash"):
            result.errors.append("signature.payload_hash missing")
            return result

        # For this example, we'll just validate the structure
        # In production, you would:
        # 1. Fetch the public key using signature.kid
        # 2. Reconstruct the signed payload
        # 3. Verify the signature using the public key

        algorithm = signature.get("algorithm")
        if algorithm not in ["ES256", "RS256"]:
            result.errors.append(f"Unsupported signature algorithm: {algorithm}")

        # Validate hash format
        payload_hash = signature.get("payload_hash", "")
        if not payload_hash.startswith("sha256:") and len(payload_hash) > 7:
            result.warnings.append("payload_hash does not follow sha256: format")

        # Note: Actual signature verification would happen here
        result.warnings.append(
            "Signature structure valid, but cryptographic verification not performed (requires public key)"
        )

        return result

    def _check_policy_compliance(self, receipt: Dict[str, Any]) -> ValidationResult:
        """Check for policy compliance indicators"""
        result = ValidationResult(valid=True)

        # Check if attribution is provided when it might be required
        attribution = receipt.get("attribution", {})
        if not attribution or attribution.get("method") == "none":
            result.warnings.append(
                "No attribution provided (may be required by publisher policy)"
            )

        # Check purpose type
        purpose = receipt.get("purpose", {})
        if not purpose.get("type"):
            result.warnings.append("Purpose type not specified")

        # Check commercial use flag
        if purpose.get("commercial") is None:
            result.warnings.append("Commercial use flag not specified")

        return result

    def verify_batch(self, receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify multiple receipts and return summary"""
        results = []
        stats = {"total": len(receipts), "valid": 0, "invalid": 0, "warnings": 0}

        for i, receipt in enumerate(receipts):
            result = self.verify_receipt(receipt)
            results.append(
                {
                    "index": i,
                    "receipt_id": receipt.get("receipt_id", "unknown"),
                    "valid": result.valid,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }
            )

            if result.valid:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1

            if result.warnings:
                stats["warnings"] += 1

        return {"stats": stats, "results": results}


def main():
    parser = argparse.ArgumentParser(description="Verify AIIndex access receipts")
    parser.add_argument("path", help="Path to receipt JSON file or directory")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Verify all JSON files in directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation mode",
    )
    parser.add_argument(
        "--output",
        help="Output file for validation report (JSON)",
    )

    args = parser.parse_args()

    verifier = ReceiptVerifier(strict_mode=args.strict)

    # Single file or batch?
    path = Path(args.path)

    if args.batch or path.is_dir():
        # Batch verification
        print(f"🔍 Verifying receipts in {path}...")

        receipt_files = list(path.glob("*.json"))
        receipts = []

        for file in receipt_files:
            try:
                with open(file) as f:
                    data = json.load(f)
                    # Handle both single receipt and array of receipts
                    if isinstance(data, list):
                        receipts.extend(data)
                    else:
                        receipts.append(data)
            except Exception as e:
                print(f"✗ Failed to load {file}: {e}")

        result = verifier.verify_batch(receipts)

        # Print summary
        print(f"\n📊 Verification Summary:")
        print(f"   Total receipts: {result['stats']['total']}")
        print(f"   Valid: {result['stats']['valid']}")
        print(f"   Invalid: {result['stats']['invalid']}")
        print(f"   With warnings: {result['stats']['warnings']}")

        # Print details for invalid receipts
        print(f"\n{'='*60}")
        for res in result["results"]:
            if not res["valid"] or res["warnings"]:
                print(f"\n Receipt: {res['receipt_id']}")
                print(f" Status: {'✓ Valid' if res['valid'] else '✗ Invalid'}")

                if res["errors"]:
                    print(f" Errors:")
                    for error in res["errors"]:
                        print(f"   - {error}")

                if res["warnings"]:
                    print(f" Warnings:")
                    for warning in res["warnings"]:
                        print(f"   - {warning}")

        # Save report if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Report saved to {args.output}")

    else:
        # Single file verification
        print(f"🔍 Verifying receipt: {path}")

        try:
            with open(path) as f:
                receipt = json.load(f)

            result = verifier.verify_receipt(receipt)

            print(f"\n{'='*60}")
            print(f"Receipt ID: {receipt.get('receipt_id', 'unknown')}")
            print(f"Status: {'✓ VALID' if result.valid else '✗ INVALID'}")

            if result.errors:
                print(f"\nErrors:")
                for error in result.errors:
                    print(f"  ✗ {error}")

            if result.warnings:
                print(f"\nWarnings:")
                for warning in result.warnings:
                    print(f"  ⚠ {warning}")

            if result.details:
                print(f"\nDetails:")
                for key, value in result.details.items():
                    print(f"  {key}: {value}")

            print(f"{'='*60}\n")

        except Exception as e:
            print(f"✗ Failed to verify receipt: {e}")


if __name__ == "__main__":
    main()
