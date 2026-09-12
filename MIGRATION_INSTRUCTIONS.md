# Database Migration Instructions

## Apply Schema Pivot Migration to Supabase

The migration file has been created at:
`/Users/dineshanchetty/Documents/claimtec/iaindex/migrations/001_schema_pivot_migration.sql`

### Option 1: Supabase SQL Editor (Recommended)

1. Go to Supabase SQL Editor:
   https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/sql

2. Click "New Query"

3. Copy and paste the entire contents of `migrations/001_schema_pivot_migration.sql`

4. Click "Run" to execute

This will create:
- `websites` table - Publisher websites for schema optimization
- `ai_mentions` table - Tracks AI search engine mentions
- `recommendations` table - AI-generated optimization suggestions
- Indexes for performance
- RLS policies for security
- Updated `publishers` table with new fields

### Option 2: Using psql (If you have PostgreSQL client)

```bash
psql "postgresql://postgres.casuupkmbqytgqnksnwd:Rockford@85@aws-0-us-east-1.pooler.supabase.com:6543/postgres" \
  -f migrations/001_schema_pivot_migration.sql
```

### Verify Migration

After running the migration, verify the tables were created:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('websites', 'ai_mentions', 'recommendations');
```

You should see all three tables listed.

### Next Steps

Once migration is complete:
1. Deploy updated backend to Azure with new environment variables
2. Test schema generation endpoint
3. Test visibility checking endpoint
