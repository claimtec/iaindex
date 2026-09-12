# IAIndex Dashboard - Quick Start Guide

## Run Locally

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/dashboard

# Install dependencies (already done)
npm install

# Start development server
npm run dev

# Open browser
open http://localhost:3002
```

## Test Authentication

1. **Register a new account:**
   - Visit http://localhost:3002/signup
   - Enter email, password, full name
   - Accept terms and privacy policy
   - Click "Create account"

2. **Login:**
   - Visit http://localhost:3002/login
   - Enter your credentials
   - Check "Remember me" for persistent session
   - Click "Sign in"

3. **Explore Dashboard:**
   - View overview stats at `/`
   - Add a website at `/websites`
   - Generate schema at `/websites/[id]/schema`
   - Run visibility checks at `/websites/[id]/visibility`
   - Manage settings at `/settings`
   - View billing at `/billing`

## Deploy to Production

### Vercel (Fastest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/dashboard
vercel

# Set environment variables in Vercel dashboard:
# - NEXT_PUBLIC_API_URL=https://api.iaindex.org
# - NEXTAUTH_URL=https://app.iaindex.org
# - NEXTAUTH_SECRET=<generate-random-string>
# - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=<your-stripe-key>
```

### Configure DNS

Add CNAME record:
```
app.iaindex.org CNAME <your-vercel-domain>.vercel.app
```

## Environment Variables

### Development (`.env.local`)
```env
NEXT_PUBLIC_API_URL=https://api.iaindex.org
NEXTAUTH_URL=http://localhost:3002
NEXTAUTH_SECRET=iaindex-dashboard-secret-key-2024
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Production
Same variables, but update:
- `NEXTAUTH_URL` to your production domain
- `NEXTAUTH_SECRET` to a secure random string
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` to production key

## Troubleshooting

### Build Fails
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### API Connection Issues
- Verify backend is running at https://api.iaindex.org
- Check CORS settings allow your domain
- Verify API endpoints match backend routes

### Authentication Not Working
- Clear localStorage/sessionStorage
- Check JWT token expiration
- Verify backend auth endpoints are working
- Check NEXTAUTH_SECRET is set correctly

## Next Steps

1. Test all pages and features
2. Verify Stripe integration works
3. Deploy to production (Vercel)
4. Set up custom domain (app.iaindex.org)
5. Monitor errors with Sentry
6. Set up analytics tracking

## Support

For issues or questions, see:
- Full documentation: `README.md`
- Integration report: `INTEGRATION_COMPLETE.md`
- Deployment details: `DEPLOYMENT_SUMMARY.md`
