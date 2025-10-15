# IAIndex Dashboard

A comprehensive Next.js 14+ dashboard for receipt verification and analytics with Supabase authentication.

## Features

- **Authentication**: Secure login with Supabase Auth
- **Dashboard Overview**: Real-time statistics and analytics
- **Receipt Explorer**: Advanced filtering, search, and CSV export
- **Analytics**: Detailed charts and insights using Recharts
- **Settings**: Domain verification, API keys, and webhook configuration
- **Badge Generator**: Create verification badges for receipts
- **Public Verification**: Public receipt verification pages
- **Dark Mode**: Full dark mode support with theme switching
- **Real-time Updates**: Live data updates using Supabase subscriptions
- **Responsive Design**: Mobile-first responsive design

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Authentication**: Supabase Auth (@supabase/ssr)
- **Charts**: Recharts
- **Icons**: Lucide React
- **Date Formatting**: date-fns

## Project Structure

```
apps/web/
├── app/
│   ├── layout.tsx              # Root layout with theme provider
│   ├── page.tsx                # Home page (redirects to dashboard)
│   ├── globals.css             # Global styles and CSS variables
│   ├── login/
│   │   └── page.tsx            # Authentication page
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout with sidebar
│   │   ├── page.tsx            # Overview page with stats
│   │   ├── receipts/
│   │   │   └── page.tsx        # Receipt explorer with filters
│   │   ├── analytics/
│   │   │   └── page.tsx        # Detailed analytics page
│   │   ├── settings/
│   │   │   └── page.tsx        # Settings configuration
│   │   └── badge/
│   │       └── page.tsx        # Badge generator
│   ├── verify/[id]/
│   │   └── page.tsx            # Public verification page
│   └── not-found.tsx           # 404 page
├── components/
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   └── select.tsx
│   ├── charts/
│   │   ├── overview-chart.tsx  # Line chart for trends
│   │   └── category-chart.tsx  # Bar chart for categories
│   └── layout/
│       ├── sidebar.tsx         # Navigation sidebar
│       ├── header.tsx          # Header with theme toggle
│       └── theme-provider.tsx  # Theme context provider
├── lib/
│   ├── utils.ts                # Utility functions
│   ├── api.ts                  # API functions and types
│   └── supabase/
│       ├── client.ts           # Client-side Supabase client
│       ├── server.ts           # Server-side Supabase client
│       └── middleware.ts       # Session refresh middleware
├── middleware.ts               # Next.js middleware
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── next.config.js
└── .env.example
```

## Getting Started

### Prerequisites

- Node.js 18+
- Supabase account and project

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Database Schema

The application expects the following Supabase tables:

### receipts

```sql
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
```

### settings

```sql
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
```

## Features Overview

### Dashboard Pages

1. **Login** (`/login`)
   - Email/password authentication
   - Sign up and sign in flows
   - Supabase Auth integration

2. **Overview** (`/dashboard`)
   - Total receipts, verified receipts, total amount, average amount
   - Daily activity chart (last 30 days)
   - Top merchants list

3. **Receipts** (`/dashboard/receipts`)
   - Searchable and filterable receipt table
   - Status filters (verified, pending, failed)
   - Date range filtering
   - CSV export functionality
   - Real-time updates via Supabase subscriptions

4. **Analytics** (`/dashboard/analytics`)
   - Verification rate metrics
   - Daily trends line chart
   - Category breakdown bar chart
   - Top merchants with detailed stats
   - Category summary cards

5. **Settings** (`/dashboard/settings`)
   - Domain verification setup
   - API key management
   - Webhook configuration
   - Copy-to-clipboard functionality

6. **Badge Generator** (`/dashboard/badge`)
   - Customizable verification badges
   - Multiple styles and sizes
   - HTML, Markdown, and URL code snippets
   - Live preview

7. **Verify** (`/verify/[id]`)
   - Public receipt verification page
   - Displays merchant, amount, date, category
   - Verification status and method
   - Verification explanation

## Customization

### Theme

The application uses CSS variables for theming. Edit `app/globals.css` to customize colors:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... more variables */
}
```

### Components

shadcn/ui components can be customized by editing files in `components/ui/`.

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Other Platforms

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Development

### Adding New Pages

1. Create a new directory in `app/dashboard/`
2. Add a `page.tsx` file
3. Update the navigation in `components/layout/sidebar.tsx`

### Adding New Components

```bash
# Example: Adding a new shadcn/ui component
npx shadcn-ui@latest add dialog
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
