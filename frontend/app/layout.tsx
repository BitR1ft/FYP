import './globals.css'
import type { Metadata } from 'next'
import { QueryProvider } from '@/lib/query-provider'

export const metadata: Metadata = {
  title: 'AutoPenTest AI',
  description: 'AI-Powered Penetration Testing Framework',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
