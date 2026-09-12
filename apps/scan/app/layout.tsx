import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Free AI Visibility Scan | IAIndex',
  description: 'Check if your website is visible in ChatGPT, Perplexity, Claude, and other AI search engines. Get your free visibility score in 60 seconds.',
  keywords: 'AI visibility, ChatGPT SEO, Perplexity optimization, AI search, schema markup, answer engine optimization',
  openGraph: {
    title: 'Free AI Visibility Scan | IAIndex',
    description: 'Check if your website is visible in AI search engines. Free scan in 60 seconds.',
    type: 'website',
    url: 'https://scan.iaindex.org',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Free AI Visibility Scan | IAIndex',
    description: 'Check if your website is visible in AI search engines. Free scan in 60 seconds.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
          {children}
        </div>
      </body>
    </html>
  )
}
