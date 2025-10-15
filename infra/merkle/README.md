# Merkle Attestation System

A cryptographic attestation system that builds daily Merkle trees from verified receipts, enabling tamper-proof verification of receipt inclusion.

## Overview

The Merkle attestation system provides:

- **Daily Merkle Trees**: Automatically builds Merkle trees from all verified receipts each day
- **Inclusion Proofs**: Generates cryptographic proofs that a receipt is included in a specific tree
- **Proof Verification**: Verifies the validity of inclusion proofs
- **Cloud Publishing**: Publishes attestations to S3, Cloudflare R2, or local storage
- **Automated Scheduling**: Runs on a schedule to maintain continuous attestation

## Architecture

```
Verified Receipts (Database)
         |
         v
    Build Tree (build_tree.py)
         |
         v
   Merkle Tree + Root Hash
         |
         +-- Generate Proofs (generate_proof.py)
         |         |
         |         v
         |   Inclusion Proofs
         |
         +-- Publish (publish.py)
                   |
                   v
            Cloud Storage (S3/R2)
```

## Components

### 1. build_tree.py

Builds daily Merkle trees from verified receipts in the database.

**Usage:**
```bash
python build_tree.py --date 2025-01-15 --output-dir ./attestations
```

**Features:**
- Fetches verified receipts from Supabase
- Constructs balanced Merkle tree
- Generates root hash
- Saves tree metadata to JSON

**Output Format:**
```json
{
  "root_hash": "abc123...",
  "receipt_count": 1234,
  "receipt_ids": ["receipt_001", "receipt_002", ...],
  "timestamp": "2025-01-15T00:00:00Z",
  "version": "1.0.0"
}
```

### 2. generate_proof.py

Generates inclusion proofs for individual receipts.

**Usage:**
```bash
python generate_proof.py --receipt-id receipt_001 --date 2025-01-15 --output-dir ./proofs
```

**Features:**
- Generates Merkle path from leaf to root
- Includes sibling hashes at each level
- Produces verifiable proof artifact

**Output Format:**
```json
{
  "receipt_id": "receipt_001",
  "receipt_data": {...},
  "merkle_root": "abc123...",
  "proof_path": [
    {"hash": "def456...", "position": "right"},
    {"hash": "ghi789...", "position": "left"}
  ],
  "timestamp": "2025-01-15T12:00:00Z",
  "version": "1.0.0",
  "tree_size": 1234
}
```

### 3. verify_proof.py

Verifies the validity of inclusion proofs.

**Usage:**
```bash
python verify_proof.py --proof ./proofs/proof_receipt_001.json
python verify_proof.py --proof ./proofs/proof_receipt_001.json --attestation ./attestations/2025-01-15.json
```

**Features:**
- Recomputes Merkle root from proof path
- Compares with claimed root hash
- Optionally verifies against attestation file
- Returns exit code 0 for valid, 1 for invalid

### 4. publish.py

Publishes attestation artifacts to cloud storage.

**Usage:**
```bash
# Local storage
python publish.py --attestation ./attestations/2025-01-15.json --storage local

# AWS S3
python publish.py --attestation ./attestations/2025-01-15.json --storage s3

# Cloudflare R2
python publish.py --attestation ./attestations/2025-01-15.json --storage r2
```

**Supported Storage:**
- **S3**: AWS S3 buckets
- **R2**: Cloudflare R2 (S3-compatible)
- **Local**: Local filesystem (for testing)

**Environment Variables:**
```bash
# For S3
export S3_BUCKET=my-attestations-bucket
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# For R2
export R2_BUCKET=my-attestations-bucket
export R2_ACCOUNT_ID=...
export R2_ACCESS_KEY_ID=...
export R2_SECRET_ACCESS_KEY=...

# For Local
export LOCAL_STORAGE_PATH=./published
```

### 5. cron.py

Scheduled task runner for automated attestation.

**Usage:**
```bash
# Run once for today
python cron.py --mode once

# Run once for specific date
python cron.py --mode once --date 2025-01-15

# Run continuously every 24 hours
python cron.py --mode continuous --interval 24

# Run at specific time daily
python cron.py --mode scheduled --time 00:00

# Backfill previous 7 days
python cron.py --mode once --backfill 7
```

**Features:**
- One-time execution
- Continuous mode with interval
- Scheduled mode at specific time
- Backfill support for historical data
- Error handling and logging

## Installation

```bash
cd infra/merkle
pip install -r requirements.txt
```

## Configuration

### Database Connection

Set Supabase credentials:
```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-anon-key
```

### Storage Configuration

Configure storage backend (see publish.py section above).

## Workflow

### Daily Attestation Process

1. **Build Tree** (runs daily at 00:00 UTC)
   ```bash
   python cron.py --mode scheduled --time 00:00 --storage s3
   ```

2. **Generate Proofs** (on-demand)
   ```bash
   python generate_proof.py --receipt-id <id> --date <date>
   ```

3. **Verify Proofs** (by users/auditors)
   ```bash
   python verify_proof.py --proof <proof-file> --attestation <attestation-file>
   ```

### Manual Operations

**Build tree for specific date:**
```bash
python build_tree.py --date 2025-01-15 --output-dir ./attestations
```

**Publish existing attestation:**
```bash
python publish.py --attestation ./attestations/2025-01-15.json --storage s3
```

## Testing

```bash
# Build test tree with mock data
python build_tree.py --output-dir ./test-attestations

# Generate proof
python generate_proof.py --receipt-id receipt_0001 --output-dir ./test-proofs

# Verify proof
python verify_proof.py --proof ./test-proofs/proof_receipt_0001.json
```

## Security Considerations

1. **Immutability**: Once published, attestations should never be modified
2. **Timestamping**: All attestations include UTC timestamps
3. **Versioning**: Version numbers track format changes
4. **Access Control**: Storage buckets should have appropriate ACLs
5. **Key Management**: Use IAM roles or secure secret management for cloud credentials

## API Integration

The attestation system can be integrated with the IA Index API:

```python
# Example: Verify receipt in application
from verify_proof import ProofVerifier

verifier = ProofVerifier()
is_valid = verifier.verify_proof_file('proof.json')

if is_valid:
    print("Receipt is cryptographically verified")
else:
    print("Receipt verification failed")
```

## Monitoring

Key metrics to monitor:
- Daily attestation success rate
- Tree size (number of receipts)
- Proof generation time
- Storage upload success
- Verification requests

## Troubleshooting

**No receipts found:**
- Check database connection
- Verify receipts have `verification_status = 'verified'`
- Check date range

**Upload failed:**
- Verify storage credentials
- Check bucket permissions
- Ensure network connectivity

**Proof verification failed:**
- Ensure proof and attestation are from same date
- Check for file corruption
- Verify receipt hasn't been modified

## Future Enhancements

- [ ] Batch proof generation
- [ ] Webhook notifications on attestation
- [ ] Multi-signature root attestation
- [ ] Blockchain anchoring
- [ ] GraphQL API for proof queries
- [ ] Real-time proof streaming

## License

Part of the IA Index project.
