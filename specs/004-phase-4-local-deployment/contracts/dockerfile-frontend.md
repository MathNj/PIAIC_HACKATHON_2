# Contract: Frontend Dockerfile

**Service**: Frontend (Next.js)
**Base Image**: node:20-alpine
**Target Size**: <150MB (excluding base layers)
**Build Strategy**: Multi-stage (dependencies + builder + runner)

## Dockerfile Specification

### Stage 1: Dependencies
**Purpose**: Install all dependencies (production + development)

```dockerfile
FROM node:20-alpine AS dependencies

# Install libc6-compat for compatibility
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (needed for build)
RUN npm ci --legacy-peer-deps
```

### Stage 2: Builder
**Purpose**: Build Next.js application with standalone output

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy source code
COPY . .

# Set environment variable for standalone output
ENV NEXT_TELEMETRY_DISABLED 1

# Build Next.js application
RUN npm run build
```

### Stage 3: Runner
**Purpose**: Run optimized production server with minimal dependencies

```dockerfile
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Run Next.js standalone server
CMD ["node", "server.js"]
```

## next.config.js Requirements

**Standalone output must be enabled**:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    // Enable server actions if used
  },
}

module.exports = nextConfig
```

## .dockerignore Specification

```
.git
.env
.env.*
node_modules
.next
.vercel
.vscode
.idea
*.md
README.md
.gitignore
Dockerfile
.dockerignore
.eslintrc.json
.prettierrc
jest.config.js
tests/
docs/
coverage/
.github/
```

## Build Commands

### Local Development (Minikube)
```bash
# Connect to Minikube Docker daemon
eval $(minikube docker-env)

# Build image
docker build -t todo-frontend:local -f Dockerfile .

# Verify image
docker images | grep todo-frontend
docker inspect todo-frontend:local | grep Size
```

### Production Build
```bash
docker build -t todo-frontend:v1.0.0 -f Dockerfile .
docker tag todo-frontend:v1.0.0 registry.example.com/todo-frontend:v1.0.0
docker push registry.example.com/todo-frontend:v1.0.0
```

## Environment Variables (Runtime)

**Build-time** (embedded in client bundle):
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://backend-service:8000)

**Runtime** (server-side):
- `PORT`: 3000
- `NODE_ENV`: production
- `HOSTNAME`: 0.0.0.0

## Optimization Techniques

1. **Multi-stage build**: 3 stages separate concerns (deps, build, run)
2. **Standalone output**: Next.js bundles only required dependencies (~70% size reduction)
3. **Alpine Linux**: Minimal base image (~5MB vs ~150MB for full node image)
4. **Layer caching**: Package install cached separately from source code
5. **.dockerignore**: Excludes node_modules, .next, tests from build context
6. **Non-root user**: Security best practice (nextjs user, UID 1001)
7. **Static asset optimization**: Separate copy of .next/static for efficient caching

## Expected Results

- **Build time** (cold): 3-4 minutes
- **Build time** (cached dependencies): <1 minute
- **Build time** (cached build): <30 seconds (only source changes)
- **Final image size**: ~120MB (excluding node:20-alpine base ~40MB)
- **Layer count**: ~12-15 layers
- **Standalone output size**: ~30MB (vs ~200MB full node_modules)

## Next.js Standalone Output Benefits

**Without standalone**:
```
.next/              ~200MB (full node_modules + build artifacts)
node_modules/       ~250MB
Total: ~450MB
```

**With standalone**:
```
.next/standalone/   ~30MB (pruned dependencies + server)
.next/static/       ~5MB (static assets)
public/             ~2MB (public assets)
Total: ~37MB
```

**Size reduction**: 92% smaller runtime footprint

## Health Check Details

**Endpoint**: `GET /`
- Returns 200 if Next.js server rendering
- Returns 500 if server crashed or unresponsive

**Alternative health endpoint** (custom):
```javascript
// pages/api/health.ts
export default function handler(req, res) {
  res.status(200).json({ status: 'healthy' })
}
```

Then update Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"
```
