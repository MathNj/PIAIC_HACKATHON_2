# Production-Optimized Next.js 16+ Dockerfile
# Multi-stage build for minimal image size

# ============================================================================
# Stage 1: Dependencies - Install all dependencies
# ============================================================================
FROM node:20-alpine AS deps

# Install libc6-compat for Alpine compatibility
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# ============================================================================
# Stage 2: Builder - Build the Next.js application
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js application
RUN npm run build

# ============================================================================
# Stage 3: Runner - Minimal runtime image
# ============================================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set ownership to nextjs user
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set port environment variable
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Run the application
CMD ["node", "server.js"]

# ============================================================================
# Build & Run Instructions
# ============================================================================
# Prerequisites:
#   1. Add to next.config.js:
#      module.exports = {
#        output: 'standalone',
#      }
#
#   2. Create API health check at: app/api/health/route.ts
#
# Build:
#   docker build -t nextjs-app -f nextjs.Dockerfile .
#
# Run:
#   docker run -p 3000:3000 nextjs-app
#
# With environment variables:
#   docker run -p 3000:3000 -e DATABASE_URL=... nextjs-app
