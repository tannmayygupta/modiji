import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'

import { BackgroundBeams } from '@/components/ui/background-beams'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PM Internship Smart Allocation Engine | PMIS',
  description: 'AI-Based Internship Recommendation Engine for the PM Internship Scheme. Find personalized, government-verified internships across India with our smart matching engine.',
  keywords: [
    'PM Internship Scheme',
    'PMIS',
    'Government Internship',
    'Government Internships India',
    'MCA Internship',
    'Internship',
    'Top Internships',
    'AI Recommendation Engine',
    'Skill India',
    'Students Internship',
    'Youth Employment',
    'Best Internships for students'
  ],
  authors: [{ name: 'PMIS Platform' }],
  openGraph: {
    title: 'PMIS AI Recommendation Engine',
    description: 'Find your perfect internship match using our AI-driven PM Internship Scheme allocation engine.',
    url: 'https://pmis-demo.vercel.app', // Update to actual production URL
    siteName: 'PM Internship Module',
    images: [
      {
        url: '/og-image.png', // Fallback, would need an actual public image path
        width: 1200,
        height: 630,
        alt: 'PMIS Platform Preview',
      },
    ],
    locale: 'en_IN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PM Internship Smart Allocation Engine',
    description: 'Discover the best government internships tailored exactly to your skills using AI.',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex flex-col min-h-screen relative`}>
        <BackgroundBeams />
        <Navbar />
        <main className="flex-1">
          {children}
        </main>
      </body>
    </html>
  )
}
