# Frontend Dockerfile (Next.js)
# Frontend Dockerfile (Next.js)
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

# Production runner
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
