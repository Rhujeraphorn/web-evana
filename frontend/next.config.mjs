/** การตั้งค่า Next.js หลักของโปรเจ็กต์ */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Emit a standalone production server bundle for the container runtime
  output: 'standalone',
  experimental: {
    typedRoutes: true,
  },
}

export default nextConfig
