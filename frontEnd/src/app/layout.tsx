// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import NavBar from './components/NavBar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Ayurveda Remedy Bot',
  description: 'Your personal Ayurvedic remedy assistant',
  themeColor: '#2E7D32',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body
        className={`${inter.className} bg-ayurveda-light text-ayurveda-brown min-h-screen flex flex-col`}
      >
        <NavBar />
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  )
}
