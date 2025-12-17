---
name: "monorepo-setup"
description: "Sets up and configures monorepo structure with workspace management, shared dependencies, build orchestration, and cross-package tooling. Use when initializing a new monorepo, migrating to monorepo architecture, or configuring workspace tools."
version: "1.0.0"
---

# Monorepo Setup Skill

## When to Use
- User says "Set up monorepo" or "Configure workspace"
- Need to organize multiple projects in single repository
- Want shared dependencies and tooling across packages
- Migrating from polyrepo to monorepo architecture
- Setting up new full-stack project with frontend and backend
- Need coordinated versioning and releases

## Context
This skill configures monorepo architecture for the Todo App:
- **Package Manager**: npm/pnpm workspaces (recommended: pnpm for efficiency)
- **Build Tool**: Turborepo for fast, cached builds
- **Linting**: Shared ESLint/Prettier configs
- **TypeScript**: Shared tsconfig base
- **Scripts**: Root-level scripts for workspace operations

## Workflow

### 1. Choose Monorepo Strategy
- **npm workspaces**: Native npm support
- **pnpm workspaces**: Fast, efficient (recommended)
- **yarn workspaces**: Alternative option
- **Turborepo**: Build orchestration layer
- **Nx**: Full-featured monorepo toolkit (heavyweight)

### 2. Define Package Structure
```
.
├── apps/
│   ├── frontend/       # Next.js app
│   └── backend/        # FastAPI app
├── packages/
│   ├── shared/         # Shared utilities
│   ├── types/          # Shared TypeScript types
│   └── config/         # Shared configs
├── package.json        # Root workspace config
├── pnpm-workspace.yaml # pnpm workspaces
└── turbo.json          # Turborepo config
```

### 3. Configure Workspace
- Set up workspace roots
- Configure dependency hoisting
- Set up shared scripts
- Configure build pipeline

### 4. Add Shared Packages
- Shared utilities
- Type definitions
- Configuration presets

## Output Format

### pnpm Workspace Configuration

**File**: `pnpm-workspace.yaml`
```yaml
packages:
  # Applications
  - 'apps/*'
  # Shared packages
  - 'packages/*'
```

**File**: `package.json` (root)
```json
{
  "name": "todo-app-monorepo",
  "version": "1.0.0",
  "private": true,
  "description": "Todo App Monorepo",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\"",
    "clean": "turbo run clean && rm -rf node_modules",
    "typecheck": "turbo run typecheck"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "typescript": "^5.2.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  },
  "packageManager": "pnpm@8.10.0"
}
```

### Turborepo Configuration

**File**: `turbo.json`
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "clean": {
      "cache": false
    }
  }
}
```

### Frontend App Package

**File**: `apps/frontend/package.json`
```json
{
  "name": "@todo-app/frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "test": "jest",
    "clean": "rm -rf .next node_modules"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@todo-app/types": "workspace:*",
    "@todo-app/shared": "workspace:*"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "typescript": "^5.2.0",
    "eslint": "^8.50.0",
    "eslint-config-next": "^15.0.0"
  }
}
```

### Backend App Package

**File**: `apps/backend/package.json`
```json
{
  "name": "@todo-app/backend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "uvicorn app.main:app --reload",
    "start": "uvicorn app.main:app",
    "test": "pytest tests/ -v",
    "test:cov": "pytest tests/ --cov=app --cov-report=html",
    "lint": "ruff check app/ tests/",
    "format": "black app/ tests/",
    "typecheck": "mypy app/",
    "migrate": "alembic upgrade head",
    "migrate:create": "alembic revision --autogenerate",
    "clean": "rm -rf __pycache__ .pytest_cache .coverage htmlcov"
  },
  "dependencies": {
    "fastapi": "^0.100.0",
    "sqlmodel": "^0.0.8",
    "uvicorn": "^0.24.0"
  },
  "devDependencies": {
    "pytest": "^7.4.0",
    "black": "^23.9.0",
    "ruff": "^0.0.290",
    "mypy": "^1.5.0"
  }
}
```

### Shared Types Package

**File**: `packages/types/package.json`
```json
{
  "name": "@todo-app/types",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "clean": "rm -rf dist node_modules"
  },
  "devDependencies": {
    "typescript": "^5.2.0"
  }
}
```

**File**: `packages/types/tsconfig.json`
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**File**: `packages/types/src/index.ts`
```typescript
// Shared TypeScript types across frontend and backend

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'normal' | 'high';
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
```

### Shared Utilities Package

**File**: `packages/shared/package.json`
```json
{
  "name": "@todo-app/shared",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "jest",
    "clean": "rm -rf dist node_modules"
  },
  "dependencies": {
    "@todo-app/types": "workspace:*"
  },
  "devDependencies": {
    "typescript": "^5.2.0",
    "jest": "^29.7.0"
  }
}
```

**File**: `packages/shared/src/index.ts`
```typescript
// Shared utility functions

export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const truncate = (text: string, length: number): string => {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};
```

### Shared Config Package

**File**: `packages/config/package.json`
```json
{
  "name": "@todo-app/config",
  "version": "1.0.0",
  "main": "./index.js",
  "files": [
    "eslint-preset.js",
    "prettier.config.js",
    "tsconfig.base.json"
  ]
}
```

**File**: `packages/config/eslint-preset.js`
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn'
  }
};
```

**File**: `packages/config/prettier.config.js`
```javascript
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false
};
```

**File**: `packages/config/tsconfig.base.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  }
}
```

### Root TypeScript Config

**File**: `tsconfig.json` (root)
```json
{
  "extends": "./packages/config/tsconfig.base.json",
  "files": [],
  "references": [
    { "path": "./apps/frontend" },
    { "path": "./packages/types" },
    { "path": "./packages/shared" }
  ]
}
```

### GitHub Actions Workflow

**File**: `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm run lint

      - name: Type check
        run: pnpm run typecheck

      - name: Build
        run: pnpm run build

      - name: Test
        run: pnpm run test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

## Installation Steps

### 1. Initialize pnpm Workspace

```bash
# Install pnpm globally
npm install -g pnpm@8

# Initialize root package.json
pnpm init

# Create workspace file
cat > pnpm-workspace.yaml << EOF
packages:
  - 'apps/*'
  - 'packages/*'
EOF

# Install Turborepo
pnpm add -Dw turbo
```

### 2. Create Directory Structure

```bash
# Create directories
mkdir -p apps/frontend apps/backend
mkdir -p packages/types/src packages/shared/src packages/config

# Move existing projects
mv frontend apps/frontend
mv backend apps/backend
```

### 3. Update Package Names

```bash
# Update package.json in each app
# frontend: "name": "@todo-app/frontend"
# backend: "name": "@todo-app/backend"
```

### 4. Install Dependencies

```bash
# Install all dependencies
pnpm install

# Build shared packages
pnpm --filter @todo-app/types build
pnpm --filter @todo-app/shared build
```

### 5. Run Development

```bash
# Run all apps in dev mode
pnpm dev

# Run specific app
pnpm --filter @todo-app/frontend dev

# Run backend only
pnpm --filter @todo-app/backend dev
```

## Common Commands

```bash
# Development
pnpm dev                           # Start all apps
pnpm --filter frontend dev         # Start frontend only
pnpm --filter backend dev          # Start backend only

# Building
pnpm build                         # Build all packages
pnpm --filter types build          # Build types only

# Testing
pnpm test                          # Run all tests
pnpm --filter frontend test        # Test frontend only

# Linting
pnpm lint                          # Lint all packages
pnpm format                        # Format all code

# Dependencies
pnpm add <pkg> -w                  # Add to root workspace
pnpm add <pkg> --filter frontend   # Add to frontend
pnpm add <pkg> --filter backend    # Add to backend

# Cleaning
pnpm clean                         # Clean all packages
rm -rf node_modules **/node_modules # Deep clean
```

## Quality Checklist

Before finalizing monorepo setup:
- [ ] pnpm-workspace.yaml configured
- [ ] turbo.json with build pipeline
- [ ] Root package.json with workspace scripts
- [ ] Shared packages created (types, shared, config)
- [ ] Apps use workspace dependencies (workspace:*)
- [ ] TypeScript project references configured
- [ ] ESLint and Prettier shared configs
- [ ] CI/CD workflow updated for monorepo
- [ ] .gitignore includes all build artifacts
- [ ] README.md updated with monorepo commands
- [ ] All packages build successfully
- [ ] Dev mode works for all apps

## Migration from Polyrepo

### Step 1: Backup
```bash
git checkout -b monorepo-migration
git tag pre-monorepo
```

### Step 2: Move Projects
```bash
mkdir -p apps packages
mv frontend apps/
mv backend apps/
```

### Step 3: Update Imports
```typescript
// Before
import { formatDate } from '../utils/date'

// After
import { formatDate } from '@todo-app/shared'
```

### Step 4: Update CI/CD
```yaml
# Update build commands to use pnpm
- pnpm install
- pnpm build
- pnpm test
```

## Troubleshooting

### Issue: Package not found
```bash
# Rebuild all packages
pnpm run build

# Clear cache
rm -rf node_modules .turbo
pnpm install
```

### Issue: Circular dependencies
```bash
# Check dependency graph
pnpm list --depth=999 --long

# Fix by removing circular references
```

### Issue: Slow builds
```yaml
# Enable Turborepo caching
{
  "pipeline": {
    "build": {
      "outputs": ["dist/**", ".next/**"],
      "dependsOn": ["^build"]
    }
  }
}
```

## Post-Setup

After setting up monorepo:
1. **Test All Commands**: Verify dev, build, test work
2. **Update Documentation**: Document workspace commands
3. **Train Team**: Share monorepo best practices
4. **Monitor Performance**: Check build times
5. **Configure CI/CD**: Update pipelines for monorepo
6. **Create PHR**: Document monorepo setup process
