# AIIndex v1.1 Migration Quick Start

## TL;DR - 5 Minute Migration

```bash
# 1. Backup (30 seconds)
pg_dump iaindex_db > backup_$(date +%Y%m%d).sql

# 2. Run database migration (2-5 minutes)
psql iaindex_db < migrations/v1.0-to-v1.1.sql

# 3. Migrate files (30 seconds - 2 minutes)
python3 migrations/migrate-ai-index.py /path/to/publishers --recursive

# 4. Generate policy files (30 seconds)
python3 migrations/generate-well-known.py /path/to/publishers --recursive

# 5. Verify (1 minute)
pytest tests/e2e/ -v
```

**Total Time:** 5-10 minutes

---

## Pre-flight Checklist

- [ ] Database backup created
- [ ] File backups created
- [ ] Migration tested in staging
- [ ] Maintenance window scheduled
- [ ] Team notified
- [ ] Rollback procedure documented

---

## Migration Commands

### Database
```bash
# Test connection
psql iaindex_db -c "SELECT version();"

# Run migration
psql iaindex_db < migrations/v1.0-to-v1.1.sql

# Verify tables created
psql iaindex_db -c "\dt bot_reputation"
```

### Files
```bash
# Preview changes (dry run)
python3 migrations/migrate-ai-index.py /publishers --recursive --dry-run

# Run migration
python3 migrations/migrate-ai-index.py /publishers --recursive

# Check results
grep -r '"version": "1.1"' /publishers | wc -l
```

### Policy Files
```bash
# Generate policy files
python3 migrations/generate-well-known.py /publishers --recursive

# Verify
find /publishers -name "aiindex-policy.json" | head -5
```

### Testing
```bash
# Install test dependencies
pip install -r tests/e2e/requirements.txt

# Run all tests
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/test_policy_enforcement.py -v
```

---

## Rollback (if needed)

```bash
# 1. Restore database
psql aiindex_db < backup_YYYYMMDD.sql

# 2. Restore files
find /publishers -name "*.json.bak" -exec sh -c 'mv "$1" "${1%.bak}"' _ {} \;

# 3. Remove policy files
find /publishers -path "*/.well-known/aiindex-policy.json" -delete

# 4. Verify
curl https://api.aiindex.org/version  # Should return 1.0
```

---

## Quick Verification

### Database
```bash
# Check new tables exist
psql iaindex_db -c "SELECT COUNT(*) FROM bot_reputation;"
psql aiindex_db -c "SELECT COUNT(*) FROM fraud_detection_logs;"

# Check new columns
psql aiindex_db -c "\d publishers" | grep -E "c2pa|embeddings|render"
```

### Files
```bash
# Check version updated
jq '.version' /publishers/example.com/ai-index.json
# Should return: "1.1"

# Check policy section exists
jq '.policy' /publishers/example.com/ai-index.json
# Should return policy object

# Check policy file exists
curl https://example.com/.well-known/aiindex-policy.json
```

### API
```bash
# Check API version
curl https://api.aiindex.org/version

# Test policy endpoint
curl https://api.aiindex.org/.well-known/aiindex-policy.json?domain=example.com

# Test with client headers
curl -H "X-AI-Client-ID: test-client" \
     -H "X-AI-Intent: retrieval" \
     https://example.com/ai-index.json
```

---

## Troubleshooting

### "relation does not exist"
```bash
# Wrong database?
psql -l | grep iaindex

# Connect to correct DB
psql aiindex_db
```

### "permission denied"
```bash
# Run as DB owner
sudo -u postgres psql aiindex_db < migrations/v1.0-to-v1.1.sql
```

### "FileNotFoundError: .well-known"
```bash
# Create directory
mkdir -p /publishers/example.com/.well-known
chmod 755 /publishers/example.com/.well-known
```

### Tests fail with "connection refused"
```bash
# Start API server
cd apps/api
python -m uvicorn src.main:app --reload

# Check it's running
curl http://localhost:3000/health
```

---

## Feature Flags

Enable optional features after migration:

```bash
# Environment variables
export ENABLE_BOT_REPUTATION=true
export ENABLE_FRAUD_DETECTION=true
export ENABLE_RENDER_FALLBACK=false
export ENABLE_EMBEDDINGS=false
export ENABLE_C2PA=false

# Restart services
docker-compose restart
```

---

## Monitoring

### Key Metrics
```bash
# Database size
psql aiindex_db -c "SELECT pg_size_pretty(pg_database_size('aiindex_db'));"

# Table counts
psql aiindex_db -c "
  SELECT
    'publishers' as table, COUNT(*) as count FROM publishers
  UNION ALL
  SELECT 'bot_reputation', COUNT(*) FROM bot_reputation
  UNION ALL
  SELECT 'receipts', COUNT(*) FROM receipts;
"

# Fraud alerts
psql aiindex_db -c "
  SELECT fraud_type, COUNT(*)
  FROM fraud_detection_logs
  WHERE detected_at > NOW() - INTERVAL '24 hours'
  GROUP BY fraud_type;
"
```

### Log Monitoring
```bash
# API logs
tail -f logs/api.log | grep -E "policy|fraud|reputation"

# Migration logs
tail -f migration.log
```

---

## Support

**Need Help?**
- 📖 Full Guide: `MIGRATION_V1.0_TO_V1.1.md`
- 📊 Summary: `MIGRATION_SUMMARY.md`
- 🧪 Tests: `tests/e2e/README.md`
- 💬 Discord: https://discord.gg/aiindex
- 📧 Email: support@aiindex.org
- 🐛 Issues: https://github.com/aiindex/aiindex/issues

---

## Success!

After migration, you should see:
- ✅ All tests passing
- ✅ Zero data loss
- ✅ Backward compatibility working
- ✅ New features available
- ✅ Dashboard showing new data
- ✅ No error rate increase

**You're now running AIIndex v1.1!** 🎉
