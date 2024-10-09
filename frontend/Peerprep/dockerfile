ARG NODE_VERSION=20.17.0

# Build stage
FROM node:${NODE_VERSION}-slim as build

WORKDIR /src

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:${NODE_VERSION}-slim

WORKDIR /app

# Environment variables
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# Copy built assets from build stage
COPY --from=build /src/.output /app

EXPOSE 3000

CMD [ "node", "/app/server/index.mjs" ]