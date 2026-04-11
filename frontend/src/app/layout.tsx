import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'

import { BackgroundBeams } from '@/components/ui/background-beams'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PM Internship Smart Allocation Engine',
  description: 'AI-Based Internship Recommendation Engine for the PM Internship Scheme',
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
