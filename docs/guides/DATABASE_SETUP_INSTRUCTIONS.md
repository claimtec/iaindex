# AIIndex v1.1 - Database Setup Instructions

**Updated**: 2025-10-14 16:25:00
**For**: Fresh Supabase installation

---

## ✅ Use the Complete Schema

Since you're starting with a fresh Supabase database, use the **complete schema** instead of the migration:

### File to Use
**`migrations/complete-schema-v1.1.sql`** (490 lines)

This includes:
- ✅ Base tables (publishers, receipts, merkle_roots, merkle_nodes)
- ✅ v1.1 tables (bot_reputation, violation_records, fraud_detection_logs, merkle_timestamps)
- ✅ All indexes for performance
- ✅ Helper functions
- ✅ Row Level Security policies
- ✅ Dashboard views
- ✅ Seed data (7 verified AI clients)

---

## 🚀 Step-by-Step Setup (5 minutes)

### Step 1: Open Supabase SQL Editor

Go to: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/sql/new

### Step 2: Copy the Complete Schema

```bash
# From your terminal (copies to clipboard)
cat migrations/complete-schema-v1.1.sql | pbcopy
```

Or open the file in your editor and copy all 490 lines.

### Step 3: Paste and Run

1. Paste the entire SQL script into Supabase SQL Editor
2. Click **"Run"** (bottom right button)
3. Wait ~5-10 seconds

### Step 4: Verify Success

You should see output like:
```
Success. No rows returned

message: "Schema created successfully!"

table_name
---------
bot_reputation
fraud_detection_logs
merkle_nodes
merkle_roots
merkle_timestamps
publishers
receipts
violation_records
```

**Expected**: 8 tables created

---

## ✅ Verification Queries

Run these in SQL Editor to confirm everything is set up:

### Check All Tables
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should return 8 tables
```

### Check Verified AI Clients
```sql
SELECT client_id, status, reputation_score
FROM bot_reputation
WHERE status = 'verified'
ORDER BY reputation_score DESC;

-- Should return 7 clients (OpenAI, Anthropic, Google, etc.)
```

### Check Publishers Table Structure
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'publishers'
ORDER BY ordinal_position;

-- Should include: c2pa_enabled, embeddings_enabled, render_mode, policy_config
```

### Check Indexes
```sql
SELECT indexname
FROM pg_indexes
WHERE tablename IN ('publishers', 'receipts', 'bot_reputation', 'fraud_detection_logs')
ORDER BY indexname;

-- Should return 30+ indexes
```

---

## 🎯 What Gets Created

### Base Tables (v1.0)
1. **publishers** - Publisher accounts and domains
2. **receipts** - AI access receipts with cryptographic signatures
3. **merkle_roots** - Merkle tree roots for batched verification
4. **merkle_nodes** - Merkle tree nodes for proof generation

### v1.1 Tables
5. **bot_reputation** - Bot/client reputation scores (7 pre-seeded)
6. **violation_records** - Policy violations and fraud attempts
7. **fraud_detection_logs** - Fraud detection alerts
8. **merkle_timestamps** - Blockchain anchoring records

### Views
- **bot_reputation_summary** - Reputation stats by status
- **fraud_alerts_summary** - Fraud detection summary
- **publisher_policy_summary** - Publisher policy overview

### Functions
- **get_client_reputation()** - Get reputation for a client
- **record_violation()** - Record a policy violation
- **update_updated_at()** - Trigger function for timestamps

### Seed Data
7 verified AI clients:
- openai-gpt (100.0 score)
- anthropic-claude (100.0)
- google-gemini (100.0)
- meta-llama (100.0)
- cohere-ai (100.0)
- perplexity-ai (95.0)
- you-com (95.0)

---

## 📋 After Database Setup

Once the schema is created, you're ready to:

### 1. Test Locally (Optional)
```bash
# Start dashboard
cd apps/web
npm run dev
# Open http://localhost:3000
```

### 2. Deploy to Staging
```bash
./deploy.sh staging
```

### 3. Run Smoke Tests
```bash
./scripts/smoke-tests.sh staging
```

---

## 🔧 Troubleshooting

### Error: "relation already exists"
**Cause**: Tables already created
**Solution**: This is safe - the script uses `IF NOT EXISTS`. Continue.

### Error: "permission denied"
**Cause**: Insufficient database permissions
**Solution**: Make sure you're logged in as the project owner in Supabase

### Error: "syntax error near..."
**Cause**: Incomplete SQL copied
**Solution**: Make sure you copied the entire file (490 lines from BEGIN to end)

### Want to Start Fresh?
```sql
-- WARNING: This deletes all data!
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Then run the complete-schema-v1.1.sql again
```

---

## 📚 Files Reference

| File | Purpose | Use When |
|------|---------|----------|
| **complete-schema-v1.1.sql** | Fresh install | Starting from scratch (NEW) |
| v1.0-to-v1.1.sql | Migration | Upgrading existing v1.0 database |

**You should use**: `complete-schema-v1.1.sql` ✅

---

## ✅ Quick Checklist

- [ ] Open Supabase SQL Editor
- [ ] Copy `migrations/complete-schema-v1.1.sql`
- [ ] Paste into SQL Editor
- [ ] Click "Run"
- [ ] Verify 8 tables created
- [ ] Verify 7 AI clients seeded
- [ ] Ready to deploy!

---

## 🎉 Next Steps

After database setup is complete:

1. ✅ Database schema created
2. 🔄 Update DATABASE_URL password in `apps/api/.env.staging`
3. 🚀 Run `./deploy.sh staging`
4. ✅ Run `./scripts/smoke-tests.sh staging`

---

**Quick Links**:
- **SQL Editor**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/sql/new
- **Tables**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/database/tables
- **Complete Schema File**: [migrations/complete-schema-v1.1.sql](../migrations/complete-schema-v1.1.sql)

---

**Last Updated**: 2025-10-14 16:25:00
