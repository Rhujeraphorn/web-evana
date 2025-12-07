# Frontend Dockerfile (Next.js)
# สร้างแอป Next.js เป็น standalone server bundle ด้วย multi-stage:
# 1) deps: ติดตั้ง node_modules
# 2) build: สร้างไฟล์ .next/standalone
# 3) runner: ใช้ node:20-alpine เสิร์ฟ server.js ที่ build มา
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund || npm install

FROM node:20-alpine AS build
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . ./
# Build the app into a standalone server bundle
RUN npm run build

# Production runner: ใช้ output standalone จากขั้น build
FROM node:20-alpine AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
ENV PORT=80
EXPOSE 80
CMD ["node", "server.js"]
