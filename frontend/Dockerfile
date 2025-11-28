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
# Build the app
RUN npm run build

# Export static assets for Nginx
FROM node:20-alpine AS export
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=build /app ./
# `next export` writes to ./dist (adjusted for the Nginx stage below)
RUN npx next export -o dist

# Serve with Nginx
FROM nginx:alpine AS nginx
COPY --from=export /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
