import type { Metadata } from 'next'
import { Inter, Noto_Sans_Devanagari } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

import { BackgroundBeams } from '@/components/ui/background-beams'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

// Devanagari companion for the bilingual wordmark. Inter carries no Devanagari
// glyphs, so without this the Hindi mark falls back to whatever the OS ships.
const notoDevanagari = Noto_Sans_Devanagari({
  subsets: ['devanagari'],
  variable: '--font-devanagari',
})

export const metadata: Metadata = {
  title: 'Kaushalya | PM Internship Smart Allocation Engine',
  description: 'Kaushalya is the AI-based internship recommendation engine for the PM Internship Scheme. Find personalized, government-verified internships across India with our smart matching engine.',
  keywords: [
    'Kaushalya',
    'Kaushalya internship',
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
  authors: [{ name: 'Kaushalya' }],
  openGraph: {
    title: 'Kaushalya | AI Internship Recommendation Engine',
    description: 'Find your perfect internship match using Kaushalya, the AI-driven PM Internship Scheme allocation engine.',
    url: 'https://pmis-demo.vercel.app', // Update to actual production URL
    siteName: 'Kaushalya',
    images: [
      {
        url: '/og-image.png', // Fallback, would need an actual public image path
        width: 1200,
        height: 630,
        alt: 'Kaushalya Platform Preview',
      },
    ],
    locale: 'en_IN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Kaushalya | PM Internship Smart Allocation Engine',
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
    <html lang="en" className={`${inter.variable} ${notoDevanagari.variable}`}>
      <body className={`${inter.className} flex flex-col min-h-screen relative`}>
        <BackgroundBeams />
        <Navbar />
        <main className="flex-1">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  )
}
