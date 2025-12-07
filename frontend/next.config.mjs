/** การตั้งค่า Next.js หลักของโปรเจ็กต์
 *  - reactStrictMode: เปิดแจ้งเตือนพฤติกรรมไม่เหมาะสม
 *  - output: 'standalone' เพื่อใช้กับ Docker stage runner
 *  - experimental.typedRoutes: เปิดตรวจ type ในเส้นทาง dynamic
 */
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
