# AIIndex Migration Scripts

Migration utilities for upgrading AIIndex from v1.0 to v1.1.

## Overview

This directory contains migration scripts for:
- Database schema updates (SQL)
- AI Index file format migration (Python)
- Policy file generation (Python)

## Scripts

### 1. v1.0-to-v1.1.sql

**Purpose:** Upgrades PostgreSQL database schema from v1.0 to v1.1

**What it does:**
- Adds new columns to `publishers` table:
  - `c2pa_enabled` - C2PA provenance feature flag
  - `embeddings_enabled` - Embeddings feature flag
  - `render_mode` - Dynamic content rendering mode
  - `policy_config` - JSONB policy configuration
- Creates `bot_reputation` table for client reputation tracking
- Creates `violation_records` table for violation history
- Creates `fraud_detection_logs` table for fraud detection
- Creates `merkle_timestamps` table for blockchain anchoring
- Adds indexes for performance
- Backfills default policies (allow-all)
- Creates helper functions and views

**Usage:**

```bash
# Backup database first!
pg_dump iaindex_db > backup_$(date +%Y%m%d).sql

# Run migration
psql iaindex_db < v1.0-to-v1.1.sql

# Verify migration
psql iaindex_db -c "SELECT version FROM schema_version;"
```

**Rollback:**

```bash
psql iaindex_db < backup_YYYYMMDD.sql
```

**Safety Features:**
- Idempotent (safe to run multiple times)
- Uses IF NOT EXISTS checks
- Wrapped in transaction
- Includes verification assertions

### 2. migrate-ai-index.py

**Purpose:** Migrates `ai-index.json` files from v1.0 to v1.1 format

**What it does:**
- Updates `version` field to "1.1"
- Migrates `access_policy` to new `policy` structure
- Adds `receipts` section with defaults
- Adds `render_fallback` section
- Adds placeholder fields for rendered content
- Creates `.json.bak` backup files
- Generates `.well-known/aiindex-policy.json`

**Usage:**

```bash
# Single file
python3 migrate-ai-index.py /path/to/ai-index.json

# Directory (recursive)
python3 migrate-ai-index.py /path/to/publishers --recursive

# Dry run (preview changes)
python3 migrate-ai-index.py /path/to/publishers --dry-run --recursive

# Verbose output
python3 migrate-ai-index.py /path/to/publishers -v --recursive

# Skip backup creation
python3 migrate-ai-index.py /path/to/ai-index.json --no-backup
```

**Options:**

| Option | Description |
|--------|-------------|
| `path` | Path to file or directory |
| `--recursive, -r` | Recursively search subdirectories |
| `--dry-run` | Show changes without modifying files |
| `--no-backup` | Don't create .bak files |
| `--verbose, -v` | Verbose output |

**Example Output:**

```
2025-10-13 10:00:00 - INFO - Processing: /publishers/example.com/ai-index.json
2025-10-13 10:00:00 - INFO - Created backup: /publishers/example.com/ai-index.json.bak
2025-10-13 10:00:00 - INFO - Validation passed
2025-10-13 10:00:00 - INFO - Migrated: /publishers/example.com/ai-index.json
2025-10-13 10:00:00 - INFO - Generated policy file: /publishers/example.com/.well-known/aiindex-policy.json

Migration Summary:
  Successfully migrated: 1
  Errors: 0
```

### 3. generate-well-known.py

**Purpose:** Generates `.well-known/aiindex-policy.json` from `ai-index.json`

**What it does:**
- Extracts policy, receipts, and rate limit information
- Creates standalone policy file for fast client access
- Validates against schema
- Supports both v1.0 and v1.1 formats

**Usage:**

```bash
# Single file
python3 generate-well-known.py /path/to/ai-index.json

# Directory (recursive)
python3 generate-well-known.py /path/to/publishers --recursive

# Custom output path
python3 generate-well-known.py /path/to/ai-index.json --output /custom/path/policy.json

# Skip validation
python3 generate-well-known.py /path/to/ai-index.json --no-validate

# Verbose output
python3 generate-well-known.py /path/to/publishers -v --recursive
```

**Options:**

| Option | Description |
|--------|-------------|
| `path` | Path to ai-index.json or directory |
| `--output, -o` | Custom output path |
| `--recursive, -r` | Process directory recursively |
| `--no-validate` | Skip validation |
| `--verbose, -v` | Verbose output |

**Generated File Structure:**

```json
{
  "version": "1.1",
  "publisher_id": "example.com",
  "domain": "example.com",
  "last_updated": "2025-10-13T10:00:00Z",
  "policy": {
    "training": "allow",
    "retrieval": "allow",
    "attribution_required": true,
    "commercial_use": true
  },
  "receipts": {
    "require_signed": false,
    "webhook_url": "https://example.com/api/receipts"
  },
  "rate_limits": {
    "requests_per_minute": 60,
    "burst": 120
  }
}
```

## Migration Workflow

### Standard Migration

```bash
# Step 1: Backup
pg_dump iaindex_db > backup.sql
find /publishers -name "*.json" -exec cp {} {}.bak \;

# Step 2: Database Migration
psql iaindex_db < v1.0-to-v1.1.sql

# Step 3: File Migration (dry run first)
python3 migrate-ai-index.py /publishers --recursive --dry-run

# Step 4: File Migration (actual)
python3 migrate-ai-index.py /publishers --recursive

# Step 5: Generate Policy Files
python3 generate-well-known.py /publishers --recursive

# Step 6: Verify
curl https://example.com/.well-known/aiindex-policy.json
```

### Rollback

```bash
# Restore database
psql iaindex_db < backup.sql

# Restore files
find /publishers -name "*.json.bak" -exec sh -c 'mv "$1" "${1%.bak}"' _ {} \;

# Remove policy files
find /publishers -path "*/.well-known/aiindex-policy.json" -delete
```

## Dependencies

### Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
# No external dependencies required!
# All scripts use Python standard library only
```

### Database Requirements

- PostgreSQL 12+
- `uuid-ossp` extension (usually included)

## Testing

### Test Database Migration

```bash
# Create test database
createdb aiindex_test

# Copy schema
pg_dump -s iaindex_db | psql aiindex_test

# Run migration
psql aiindex_test < v1.0-to-v1.1.sql

# Verify
psql aiindex_test -c "\dt"  # List tables
psql aiindex_test -c "SELECT * FROM bot_reputation LIMIT 1;"
```

### Test File Migration

```bash
# Create test directory
mkdir test_migration
cp /path/to/real/ai-index.json test_migration/

# Run migration
python3 migrate-ai-index.py test_migration/ai-index.json --dry-run

# Check output
cat test_migration/ai-index.json
cat test_migration/.well-known/aiindex-policy.json
```

## Performance

### Database Migration

- Small database (<10k publishers): ~2 minutes
- Medium database (10k-100k publishers): ~5 minutes
- Large database (>100k publishers): ~10-15 minutes

**Optimization tips:**
- Run during low-traffic hours
- Use `CREATE INDEX CONCURRENTLY` for large tables
- Consider partitioning if >1M receipts

### File Migration

- ~10-50ms per file
- I/O bound (SSD recommended)
- Can be parallelized:

```bash
# Parallel migration (GNU parallel)
find /publishers -name "ai-index.json" | \
  parallel -j 4 python3 migrate-ai-index.py {}
```

## Troubleshooting

### Database Migration Fails

**Error:** `relation "publishers" does not exist`

**Solution:** Ensure you're connected to correct database:
```bash
psql iaindex_db -c "\dt"
```

**Error:** `permission denied`

**Solution:** Run as database owner:
```bash
sudo -u postgres psql iaindex_db < v1.0-to-v1.1.sql
```

### File Migration Fails

**Error:** `FileNotFoundError: .well-known`

**Solution:** Create directory:
```bash
mkdir -p /path/to/publisher/.well-known
chmod 755 /path/to/publisher/.well-known
```

**Error:** `json.decoder.JSONDecodeError`

**Solution:** Validate JSON:
```bash
python3 -m json.tool < ai-index.json
```

### Validation Errors

**Error:** `Missing required field: publisher_id`

**Solution:** Add required fields to ai-index.json:
```json
{
  "version": "1.0",
  "publisher_id": "example.com",
  "domain": "example.com",
  "last_updated": "2025-10-13T10:00:00Z"
}
```

## Best Practices

1. **Always backup before migration**
   ```bash
   pg_dump iaindex_db > backup.sql
   ```

2. **Test in staging first**
   ```bash
   # Use staging database
   psql staging_db < v1.0-to-v1.1.sql
   ```

3. **Use dry-run mode**
   ```bash
   python3 migrate-ai-index.py /publishers --dry-run --recursive
   ```

4. **Monitor logs**
   ```bash
   python3 migrate-ai-index.py /publishers --recursive 2>&1 | tee migration.log
   ```

5. **Verify after migration**
   ```bash
   # Check database
   psql iaindex_db -c "SELECT COUNT(*) FROM bot_reputation;"

   # Check files
   grep -r '"version": "1.1"' /publishers
   ```

6. **Plan for rollback**
   - Keep backups for at least 7 days
   - Document rollback procedure
   - Test rollback in staging

## Security Considerations

- Migration scripts don't modify permissions
- `.well-known` directory should be publicly readable
- Backup files contain sensitive data - protect appropriately
- Database migration preserves RLS policies

## Support

For issues or questions:
- **Documentation:** https://docs.aiindex.org/migration
- **GitHub Issues:** https://github.com/aiindex/aiindex/issues
- **Discord:** https://discord.gg/aiindex
- **Email:** support@aiindex.org

## License

Same as main AIIndex project (MIT).
