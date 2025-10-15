# Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/web
   npm install
   ```

2. **Configure Supabase:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Supabase credentials:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your-project-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

3. **Set up database tables:**

   Run these SQL commands in your Supabase SQL Editor:

   ```sql
   -- Create receipts table
   CREATE TABLE receipts (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     user_id UUID REFERENCES auth.users(id),
     merchant TEXT NOT NULL,
     amount DECIMAL NOT NULL,
     date DATE NOT NULL,
     status TEXT NOT NULL CHECK (status IN ('verified', 'pending', 'failed')),
     category TEXT NOT NULL,
     verification_method TEXT NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create settings table
   CREATE TABLE settings (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     user_id UUID REFERENCES auth.users(id) UNIQUE,
     domain TEXT,
     domain_verified BOOLEAN DEFAULT FALSE,
     api_key TEXT,
     webhook_url TEXT,
     webhook_secret TEXT,
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Enable Row Level Security
   ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
   ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

   -- Create policies for receipts
   CREATE POLICY "Users can view their own receipts"
     ON receipts FOR SELECT
     USING (auth.uid() = user_id);

   CREATE POLICY "Users can insert their own receipts"
     ON receipts FOR INSERT
     WITH CHECK (auth.uid() = user_id);

   CREATE POLICY "Users can update their own receipts"
     ON receipts FOR UPDATE
     USING (auth.uid() = user_id);

   CREATE POLICY "Users can delete their own receipts"
     ON receipts FOR DELETE
     USING (auth.uid() = user_id);

   -- Create policies for settings
   CREATE POLICY "Users can view their own settings"
     ON settings FOR SELECT
     USING (auth.uid() = user_id);

   CREATE POLICY "Users can insert their own settings"
     ON settings FOR INSERT
     WITH CHECK (auth.uid() = user_id);

   CREATE POLICY "Users can update their own settings"
     ON settings FOR UPDATE
     USING (auth.uid() = user_id);

   -- Create indexes for better performance
   CREATE INDEX receipts_user_id_idx ON receipts(user_id);
   CREATE INDEX receipts_created_at_idx ON receipts(created_at DESC);
   CREATE INDEX receipts_status_idx ON receipts(status);
   CREATE INDEX settings_user_id_idx ON settings(user_id);
   ```

4. **Enable Realtime (Optional):**

   In Supabase Dashboard > Database > Replication:
   - Enable replication for the `receipts` table

5. **Run the development server:**
   ```bash
   npm run dev
   ```

6. **Open your browser:**
   Navigate to http://localhost:3000

## First Time Setup

1. Go to http://localhost:3000/login
2. Click "Sign up" to create a new account
3. Check your email for the confirmation link (if email confirmation is enabled)
4. Sign in with your credentials
5. You'll be redirected to the dashboard

## Testing with Sample Data

You can insert sample data using Supabase SQL Editor:

```sql
-- Insert sample receipts (replace 'your-user-id' with your actual user ID)
INSERT INTO receipts (user_id, merchant, amount, date, status, category, verification_method)
VALUES
  ('your-user-id', 'Starbucks', 15.99, '2024-01-15', 'verified', 'Food & Drink', 'QR Code'),
  ('your-user-id', 'Amazon', 89.99, '2024-01-16', 'verified', 'Shopping', 'Email Receipt'),
  ('your-user-id', 'Target', 45.50, '2024-01-17', 'pending', 'Shopping', 'Manual Entry'),
  ('your-user-id', 'Shell Gas', 60.00, '2024-01-18', 'verified', 'Transportation', 'API Integration'),
  ('your-user-id', 'Whole Foods', 120.75, '2024-01-19', 'verified', 'Groceries', 'QR Code');

-- Initialize settings for the user
INSERT INTO settings (user_id, api_key, webhook_secret)
VALUES ('your-user-id', 'sk_test_' || gen_random_uuid()::text, 'whsec_' || gen_random_uuid()::text);
```

To get your user ID:
1. Sign in to the dashboard
2. Open browser DevTools > Console
3. Run: `await supabase.auth.getUser()`
4. Copy the `id` field

## Troubleshooting

### Authentication Issues
- Verify your Supabase URL and anon key in `.env`
- Check if email confirmation is required in Supabase Auth settings
- Ensure cookies are enabled in your browser

### Database Connection Issues
- Verify RLS policies are set up correctly
- Check that your user has the correct permissions
- Ensure the tables are created in the `public` schema

### Build Errors
- Delete `node_modules` and `.next` directories
- Run `npm install` again
- Check TypeScript errors with `npm run build`

### Real-time Updates Not Working
- Enable replication for the `receipts` table in Supabase
- Check browser console for WebSocket connection errors
- Verify your Supabase project is not paused

## Production Deployment

### Environment Variables
Set these in your production environment:
```
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Vercel Deployment
1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Performance Optimization
- Enable database indexes (already included in setup SQL)
- Configure Supabase connection pooling
- Set up CDN for static assets
- Enable Next.js image optimization

## Features Checklist

After setup, verify these features work:

- [ ] User registration and login
- [ ] Dashboard overview with statistics
- [ ] Receipt table with search and filters
- [ ] Date range filtering
- [ ] CSV export
- [ ] Analytics charts display correctly
- [ ] Dark mode toggle
- [ ] Settings page saves successfully
- [ ] Badge generator creates badges
- [ ] Public verification page works
- [ ] Real-time updates (create a receipt in Supabase and watch it appear)
- [ ] Sign out functionality

## Support

If you encounter issues:
1. Check the browser console for errors
2. Review Supabase logs
3. Verify all environment variables are set
4. Ensure database tables and policies are created correctly
