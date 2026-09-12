# IAIndex Dashboard

A complete, production-ready SaaS dashboard for managing AI visibility across ChatGPT, Perplexity, Claude, and other AI platforms.

## Features

### Authentication
- **Login/Signup**: Secure authentication with email/password
- **Password strength indicator**: Real-time validation
- **Remember me**: Session persistence
- **Responsive forms**: Mobile-optimized

### Dashboard Home
- **Overview statistics**: Total websites, avg visibility score, active scans, recommendations
- **Visibility trend chart**: 30-day visibility tracking
- **Recent activity timeline**: Latest updates from websites
- **Quick actions**: Add website, run scan, generate schema

### Website Management
- **Website list**: Grid/table view with search and filtering
- **Add websites**: Modal form with domain, name, description
- **Website details**: Comprehensive overview with visibility gauge
- **Platform breakdown**: Scores for ChatGPT, Perplexity, Claude, Gemini
- **Recent scans**: History of visibility checks

### Schema Management
- **Generate schema**: AI-powered schema markup generation
- **Schema editor**: JSON viewer with syntax highlighting
- **Validation**: Real-time schema validation
- **Copy/Download**: Easy export functionality
- **Implementation guide**: Step-by-step instructions

### Visibility Tracking
- **Run checks**: Multi-query visibility testing
- **Visibility charts**: Time-series data visualization
- **Platform charts**: Platform-specific metrics
- **Mention history**: Detailed check results
- **PDF reports**: Downloadable reports

### Settings
- **Profile management**: Update name and email
- **Notification preferences**: Customizable alerts
- **API key management**: Create and revoke keys
- **Account deletion**: Secure account removal

### Billing
- **Current plan**: Subscription status and details
- **Usage tracking**: Monitor limits (websites, checks)
- **Plan upgrades**: Switch between Free/Starter/Pro/Enterprise
- **Payment method**: Manage payment information
- **Invoice history**: Download past invoices
- **Stripe integration**: Checkout and customer portal

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_URL=https://api.iaindex.org
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3002](http://localhost:3002)

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
apps/dashboard/
├── app/
│   ├── (auth)/                    # Authentication routes
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/               # Protected dashboard routes
│   │   ├── layout.tsx             # Dashboard layout
│   │   ├── page.tsx               # Home/overview
│   │   ├── websites/
│   │   │   ├── page.tsx           # List websites
│   │   │   └── [id]/
│   │   │       ├── page.tsx       # Website details
│   │   │       ├── schema/page.tsx
│   │   │       └── visibility/page.tsx
│   │   ├── settings/page.tsx
│   │   └── billing/page.tsx
│   ├── layout.tsx                 # Root layout
│   ├── providers.tsx              # React Query provider
│   └── globals.css
├── components/
│   ├── ui/                        # Base UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   └── progress.tsx
│   ├── charts/                    # Chart components
│   │   ├── VisibilityGauge.tsx
│   │   └── VisibilityChart.tsx
│   └── dashboard/                 # Dashboard-specific
│       ├── Sidebar.tsx
│       └── Header.tsx
├── lib/
│   ├── api.ts                     # API client
│   ├── store.ts                   # Zustand store
│   └── utils.ts                   # Utility functions
├── types/
│   └── index.ts                   # TypeScript types
└── package.json
```

## API Integration

The dashboard integrates with the IAIndex API at `https://api.iaindex.org`.

### Authentication
- `POST /v1/auth/login` - User login
- `POST /v1/auth/signup` - User registration
- `GET /v1/auth/profile` - Get user profile
- `PATCH /v1/auth/profile` - Update profile

### Websites
- `GET /v1/websites` - List websites
- `GET /v1/websites/:id` - Get website
- `POST /v1/websites` - Create website
- `PATCH /v1/websites/:id` - Update website
- `DELETE /v1/websites/:id` - Delete website

### Schema
- `GET /v1/schema/:websiteId` - Get schema
- `POST /v1/schema/generate` - Generate schema
- `PATCH /v1/schema/:websiteId` - Update schema
- `POST /v1/schema/validate` - Validate schema

### Visibility
- `POST /v1/visibility/check` - Run visibility check
- `GET /v1/visibility/:websiteId/history` - Get history
- `GET /v1/visibility/:websiteId/checks` - Get checks

### Analytics
- `GET /v1/analytics/dashboard` - Dashboard stats
- `GET /v1/analytics/activity` - Recent activity
- `GET /v1/analytics/visibility-trend` - Visibility trend

### Billing
- `GET /v1/billing/subscription` - Get subscription
- `GET /v1/billing/invoices` - Get invoices
- `POST /v1/billing/checkout` - Create checkout
- `POST /v1/billing/portal` - Customer portal

## Features Implemented

### ✅ Authentication
- [x] Login page with email/password
- [x] Signup page with password strength
- [x] Remember me functionality
- [x] Form validation
- [x] Error handling

### ✅ Dashboard Layout
- [x] Responsive sidebar navigation
- [x] Top header with search and user menu
- [x] Mobile hamburger menu
- [x] Logout functionality

### ✅ Dashboard Home
- [x] Statistics cards (websites, score, scans, recommendations)
- [x] Visibility trend chart
- [x] Recent activity timeline
- [x] Quick actions section
- [x] Loading states

### ✅ Websites
- [x] List view with search/filter
- [x] Add website modal
- [x] Website cards with scores
- [x] Empty states
- [x] Pagination support

### ✅ Website Details
- [x] Visibility gauge
- [x] Platform breakdown
- [x] Schema status
- [x] Recent scans
- [x] Quick actions
- [x] Recommendations

### ✅ Schema Management
- [x] Schema status display
- [x] Generate schema functionality
- [x] JSON editor/viewer
- [x] Copy to clipboard
- [x] Download as JSON
- [x] Validation status
- [x] Implementation instructions

### ✅ Visibility Tracking
- [x] Run visibility checks
- [x] Time-series chart
- [x] Platform-specific charts
- [x] Mention history table
- [x] Download report button

### ✅ Settings
- [x] Profile management
- [x] Notification preferences
- [x] API key management
- [x] Create/revoke keys
- [x] Delete account

### ✅ Billing
- [x] Current plan display
- [x] Usage tracking
- [x] Plan comparison
- [x] Upgrade/downgrade
- [x] Payment method
- [x] Invoice history
- [x] Stripe integration hooks

## Design System

### Colors
- **Primary**: `#0ea5e9` (Sky Blue)
- **Secondary**: `#a855f7` (Purple)
- **Success**: `#10b981` (Green)
- **Warning**: `#f59e0b` (Amber)
- **Danger**: `#ef4444` (Red)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: Bold, 2xl-3xl
- **Body**: Regular, sm-base

### Components
- Consistent spacing (Tailwind)
- Smooth transitions
- Loading states
- Error states
- Empty states

## Responsive Design

- **Mobile**: < 768px (hamburger menu, stacked layouts)
- **Tablet**: 768px - 1024px (2-column grids)
- **Desktop**: > 1024px (full sidebar, multi-column)

## Performance

- Server Components for static content
- Client Components for interactive elements
- React Query caching
- Optimistic updates
- Code splitting
- Image optimization

## Security

- JWT token authentication
- Secure token storage
- API request interceptors
- CSRF protection
- Input validation
- XSS prevention

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3002
CMD ["npm", "start"]
```

### Environment Variables

Production environment variables:
- `NEXT_PUBLIC_API_URL`: API endpoint
- `NEXTAUTH_URL`: Dashboard URL
- `NEXTAUTH_SECRET`: Auth secret

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Email: support@iaindex.org
- Documentation: https://docs.iaindex.org
- GitHub Issues: https://github.com/iaindex/dashboard/issues
