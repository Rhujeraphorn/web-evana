// โครงร่างหลักของแอป Next.js ตั้งฟอนต์ ธีม และ Navbar
import './globals.css'
import type { ReactNode } from 'react'
import { Prompt } from 'next/font/google'
import { Navbar } from '@/components/Navbar'

// Disable static generation for all routes to avoid build-time API fetch failures on Vercel
export const dynamic = 'force-dynamic'
export const revalidate = 0

const prompt = Prompt({
  subsets: ['latin', 'thai'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-sans',
  display: 'swap',
})

export const metadata = {
  title: 'EVANA — North',
  description: 'ท่องเที่ยว EV ภาคเหนือ แบบมินิมอล คลีน',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="th">
      <body className={`${prompt.variable} bg-slate-50 text-slate-800 antialiased`}>
        <div className="relative min-h-screen">
          <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_20%_20%,#dbeafe,transparent_35%),radial-gradient(circle_at_80%_10%,#e0f2fe,transparent_25%),radial-gradient(circle_at_70%_70%,#e5e7eb,transparent_28%)]" />
          <Navbar />
          <main className="max-w-screen-2xl mx-auto px-4 py-8 lg:px-8 lg:py-12">{children}</main>
        </div>
      </body>
    </html>
  )
}
