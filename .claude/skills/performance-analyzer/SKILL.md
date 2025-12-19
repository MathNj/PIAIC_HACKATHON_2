---
name: "performance-analyzer"
description: "Analyzes application performance including API response times, database queries, frontend rendering, bundle sizes, and resource usage. Identifies bottlenecks and provides optimization recommendations. Use when performance issues arise or for proactive performance audits."
version: "1.0.0"
---

# Performance Analyzer Skill

## When to Use
- User says "Analyze performance" or "Why is this slow?"
- API endpoints have high response times
- Frontend pages load slowly
- Database queries are inefficient
- Need to identify performance bottlenecks
- Before production deployment for performance audit
- After significant code changes

## Context
This skill analyzes performance across the Todo App stack:
- **Backend**: API response times, database query performance, N+1 queries
- **Frontend**: Page load times, bundle sizes, rendering performance
- **Database**: Query execution plans, index usage, slow queries
- **Infrastructure**: Resource usage (CPU, memory), network latency

## Workflow

### 1. Identify Performance Area
- **API Performance**: Endpoint response times
- **Database Performance**: Query optimization
- **Frontend Performance**: Load times, rendering
- **Infrastructure Performance**: Resource usage

### 2. Collect Metrics
- Response time measurements
- Database query logs
- Frontend performance metrics
- Resource usage data

### 3. Analyze Bottlenecks
- Identify slow operations
- Find inefficient queries
- Detect unnecessary re-renders
- Spot resource constraints

### 4. Generate Recommendations
- Optimization strategies
- Code improvements
- Infrastructure adjustments

## Output Format

### Backend API Performance Analysis

**Script**: `scripts/analyze-api-performance.py`
```python
#!/usr/bin/env python3
"""Analyze API endpoint performance."""

import time
import statistics
from typing import List, Dict
import httpx
from tabulate import tabulate

class APIPerformanceAnalyzer:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

    def measure_endpoint(self, method: str, path: str, iterations: int = 100) -> Dict:
        """Measure endpoint performance over multiple iterations."""
        response_times = []
        errors = 0

        for _ in range(iterations):
            start = time.time()
            try:
                if method == "GET":
                    response = httpx.get(f"{self.base_url}{path}", headers=self.headers, timeout=10)
                elif method == "POST":
                    response = httpx.post(f"{self.base_url}{path}", headers=self.headers, timeout=10)

                elapsed = (time.time() - start) * 1000  # Convert to ms

                if response.status_code < 400:
                    response_times.append(elapsed)
                else:
                    errors += 1
            except Exception:
                errors += 1

        if not response_times:
            return {
                "endpoint": f"{method} {path}",
                "error": "All requests failed"
            }

        return {
            "endpoint": f"{method} {path}",
            "min_ms": round(min(response_times), 2),
            "max_ms": round(max(response_times), 2),
            "mean_ms": round(statistics.mean(response_times), 2),
            "median_ms": round(statistics.median(response_times), 2),
            "p95_ms": round(statistics.quantiles(response_times, n=20)[18], 2),  # 95th percentile
            "p99_ms": round(statistics.quantiles(response_times, n=100)[98], 2),  # 99th percentile
            "errors": errors,
            "success_rate": round((len(response_times) / iterations) * 100, 2)
        }

    def analyze_endpoints(self, endpoints: List[Dict]) -> None:
        """Analyze multiple endpoints and generate report."""
        results = []

        for endpoint in endpoints:
            print(f"Analyzing {endpoint['method']} {endpoint['path']}...")
            result = self.measure_endpoint(
                endpoint['method'],
                endpoint['path'],
                iterations=endpoint.get('iterations', 100)
            )
            results.append(result)

        # Generate report
        self.generate_report(results)

    def generate_report(self, results: List[Dict]) -> None:
        """Generate performance report."""
        print("\n" + "="*80)
        print("API PERFORMANCE ANALYSIS REPORT")
        print("="*80 + "\n")

        # Table of results
        headers = ["Endpoint", "Min (ms)", "Mean (ms)", "Median (ms)", "P95 (ms)", "P99 (ms)", "Max (ms)", "Success %"]
        table_data = []

        for result in results:
            if "error" in result:
                table_data.append([result["endpoint"], "-", "-", "-", "-", "-", "-", "0%"])
            else:
                table_data.append([
                    result["endpoint"],
                    result["min_ms"],
                    result["mean_ms"],
                    result["median_ms"],
                    result["p95_ms"],
                    result["p99_ms"],
                    result["max_ms"],
                    f"{result['success_rate']}%"
                ])

        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80 + "\n")

        for result in results:
            if "error" in result:
                print(f"❌ {result['endpoint']}")
                print(f"   Issue: {result['error']}")
                print()
                continue

            if result['mean_ms'] > 1000:
                print(f"🔴 {result['endpoint']}")
                print(f"   Issue: High average response time ({result['mean_ms']}ms)")
                print(f"   Recommendation: Optimize database queries, add caching, or consider async processing")
                print()
            elif result['mean_ms'] > 500:
                print(f"🟡 {result['endpoint']}")
                print(f"   Issue: Moderate response time ({result['mean_ms']}ms)")
                print(f"   Recommendation: Review query efficiency and add database indexes")
                print()
            elif result['p99_ms'] > result['mean_ms'] * 3:
                print(f"🟡 {result['endpoint']}")
                print(f"   Issue: High P99 latency variance ({result['p99_ms']}ms vs mean {result['mean_ms']}ms)")
                print(f"   Recommendation: Investigate slow outliers, check for slow queries or GC pauses")
                print()
            else:
                print(f"✅ {result['endpoint']}")
                print(f"   Status: Good performance ({result['mean_ms']}ms average)")
                print()

if __name__ == "__main__":
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    token = sys.argv[2] if len(sys.argv) > 2 else None

    analyzer = APIPerformanceAnalyzer(base_url, token)

    # Define endpoints to test
    endpoints = [
        {"method": "GET", "path": "/health"},
        {"method": "GET", "path": "/api/v1/tasks/"},
        {"method": "POST", "path": "/api/v1/tasks/", "iterations": 50},
        {"method": "GET", "path": "/api/v1/tasks/stats"},
    ]

    analyzer.analyze_endpoints(endpoints)
```

**Usage**:
```bash
# Basic usage
python scripts/analyze-api-performance.py http://localhost:8000

# With authentication
python scripts/analyze-api-performance.py http://localhost:8000 "your-jwt-token"
```

---

### Database Query Performance Analysis

**Script**: `scripts/analyze-db-queries.py`
```python
#!/usr/bin/env python3
"""Analyze database query performance."""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd

class DatabasePerformanceAnalyzer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)

    def analyze_slow_queries(self, threshold_ms: int = 100):
        """Identify slow queries from PostgreSQL logs."""
        # Enable query logging
        query = text("""
            SELECT
                query,
                calls,
                total_time,
                mean_time,
                min_time,
                max_time,
                stddev_time
            FROM pg_stat_statements
            WHERE mean_time > :threshold
            ORDER BY mean_time DESC
            LIMIT 20;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {"threshold": threshold_ms})
            rows = result.fetchall()

        print("\n" + "="*80)
        print(f"SLOW QUERIES (> {threshold_ms}ms)")
        print("="*80 + "\n")

        if not rows:
            print("✅ No slow queries found!")
            return

        for row in rows:
            print(f"Query: {row.query[:100]}...")
            print(f"  Calls: {row.calls}")
            print(f"  Mean Time: {row.mean_time:.2f}ms")
            print(f"  Total Time: {row.total_time:.2f}ms")
            print(f"  Min/Max: {row.min_time:.2f}ms / {row.max_time:.2f}ms")
            print()

    def analyze_table_stats(self):
        """Analyze table statistics."""
        query = text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                n_live_tup AS row_count,
                n_dead_tup AS dead_rows,
                last_vacuum,
                last_autovacuum,
                last_analyze
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()

        print("\n" + "="*80)
        print("TABLE STATISTICS")
        print("="*80 + "\n")

        for row in rows:
            print(f"Table: {row.schemaname}.{row.tablename}")
            print(f"  Size: {row.size}")
            print(f"  Live Rows: {row.row_count:,}")
            print(f"  Dead Rows: {row.dead_rows:,}")

            if row.dead_rows > row.row_count * 0.1:
                print(f"  ⚠️  High dead row count - consider VACUUM")

            print()

    def analyze_index_usage(self):
        """Analyze index usage."""
        query = text("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan ASC
            LIMIT 20;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()

        print("\n" + "="*80)
        print("UNUSED OR RARELY USED INDEXES")
        print("="*80 + "\n")

        for row in rows:
            if row.idx_scan < 100:  # Less than 100 scans
                print(f"Index: {row.indexname}")
                print(f"  Table: {row.schemaname}.{row.tablename}")
                print(f"  Scans: {row.idx_scan}")
                print(f"  Size: {row.index_size}")
                print(f"  ⚠️  Consider removing this index if not needed")
                print()

    def analyze_missing_indexes(self):
        """Suggest missing indexes based on sequential scans."""
        query = text("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch,
                seq_tup_read / NULLIF(seq_scan, 0) AS avg_seq_read
            FROM pg_stat_user_tables
            WHERE seq_scan > 0
            ORDER BY seq_tup_read DESC
            LIMIT 10;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()

        print("\n" + "="*80)
        print("TABLES WITH HIGH SEQUENTIAL SCANS")
        print("="*80 + "\n")

        for row in rows:
            if row.seq_scan > row.idx_scan:
                print(f"Table: {row.schemaname}.{row.tablename}")
                print(f"  Sequential Scans: {row.seq_scan:,}")
                print(f"  Rows Read: {row.seq_tup_read:,}")
                print(f"  Avg Rows/Scan: {row.avg_seq_read:.0f}")
                print(f"  💡 Consider adding indexes on frequently queried columns")
                print()

if __name__ == "__main__":
    database_url = sys.argv[1] if len(sys.argv) > 1 else "postgresql://user:pass@localhost/dbname"

    analyzer = DatabasePerformanceAnalyzer(database_url)

    print("Starting database performance analysis...\n")

    # Run all analyses
    analyzer.analyze_slow_queries(threshold_ms=100)
    analyzer.analyze_table_stats()
    analyzer.analyze_index_usage()
    analyzer.analyze_missing_indexes()

    print("\n" + "="*80)
    print("✅ Database performance analysis complete!")
    print("="*80)
```

**Usage**:
```bash
python scripts/analyze-db-queries.py "postgresql://user:pass@localhost/dbname"
```

---

### Frontend Performance Analysis

**Script**: `scripts/analyze-frontend-performance.js`
```javascript
#!/usr/bin/env node
/**
 * Analyze frontend performance metrics.
 */

const fs = require('fs');
const path = require('path');

class FrontendPerformanceAnalyzer {
  constructor(buildDir = '.next') {
    this.buildDir = buildDir;
  }

  analyzeBundleSize() {
    console.log('\n' + '='.repeat(80));
    console.log('BUNDLE SIZE ANALYSIS');
    console.log('='.repeat(80) + '\n');

    // Read Next.js build stats
    const statsPath = path.join(this.buildDir, 'build-manifest.json');

    if (!fs.existsSync(statsPath)) {
      console.log('❌ Build manifest not found. Run `npm run build` first.');
      return;
    }

    const stats = JSON.parse(fs.readFileSync(statsPath, 'utf-8'));

    // Analyze page sizes
    const pageSizes = {};
    let totalSize = 0;

    for (const [page, files] of Object.entries(stats.pages)) {
      let pageSize = 0;

      for (const file of files) {
        const filePath = path.join(this.buildDir, file);
        if (fs.existsSync(filePath)) {
          pageSize += fs.statSync(filePath).size;
        }
      }

      pageSizes[page] = pageSize;
      totalSize += pageSize;
    }

    // Sort by size
    const sortedPages = Object.entries(pageSizes)
      .sort(([, a], [, b]) => b - a);

    // Display results
    console.log('Page Sizes:');
    for (const [page, size] of sortedPages) {
      const sizeKB = (size / 1024).toFixed(2);
      const status = sizeKB > 500 ? '🔴' : sizeKB > 200 ? '🟡' : '✅';
      console.log(`  ${status} ${page}: ${sizeKB} KB`);
    }

    console.log(`\nTotal Size: ${(totalSize / 1024).toFixed(2)} KB`);

    // Recommendations
    console.log('\nRecommendations:');
    for (const [page, size] of sortedPages) {
      const sizeKB = size / 1024;
      if (sizeKB > 500) {
        console.log(`  🔴 ${page} is too large (${sizeKB.toFixed(2)} KB)`);
        console.log(`     - Use dynamic imports for heavy components`);
        console.log(`     - Enable code splitting`);
        console.log(`     - Remove unused dependencies`);
      }
    }
  }

  analyzeDependencies() {
    console.log('\n' + '='.repeat(80));
    console.log('DEPENDENCY ANALYSIS');
    console.log('='.repeat(80) + '\n');

    const packageJsonPath = path.join(process.cwd(), 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    const heavyPackages = [
      'moment',  // Use date-fns instead
      'lodash',  // Use lodash-es or native methods
      'jquery',  // Usually not needed with React
    ];

    console.log('Checking for heavy dependencies...\n');

    for (const [pkg, version] of Object.entries(deps)) {
      if (heavyPackages.includes(pkg)) {
        console.log(`  ⚠️  ${pkg} (${version})`);
        console.log(`     Consider lighter alternatives`);
      }
    }
  }

  analyzeWebVitals() {
    console.log('\n' + '='.repeat(80));
    console.log('WEB VITALS RECOMMENDATIONS');
    console.log('='.repeat(80) + '\n');

    console.log('To measure Web Vitals in production:');
    console.log('1. Add web-vitals package: npm install web-vitals');
    console.log('2. Create pages/_app.tsx with reportWebVitals function');
    console.log('3. Use Vercel Analytics or Google Analytics');
    console.log('\nTarget Metrics:');
    console.log('  ✅ LCP (Largest Contentful Paint): < 2.5s');
    console.log('  ✅ FID (First Input Delay): < 100ms');
    console.log('  ✅ CLS (Cumulative Layout Shift): < 0.1');
    console.log('  ✅ FCP (First Contentful Paint): < 1.8s');
    console.log('  ✅ TTFB (Time to First Byte): < 600ms');
  }

  generateReport() {
    console.log('\n' + '='.repeat(80));
    console.log('FRONTEND PERFORMANCE ANALYSIS');
    console.log('='.repeat(80));

    this.analyzeBundleSize();
    this.analyzeDependencies();
    this.analyzeWebVitals();

    console.log('\n' + '='.repeat(80));
    console.log('✅ Frontend performance analysis complete!');
    console.log('='.repeat(80) + '\n');
  }
}

const analyzer = new FrontendPerformanceAnalyzer();
analyzer.generateReport();
```

**Usage**:
```bash
node scripts/analyze-frontend-performance.js
```

---

### Resource Usage Monitor

**Script**: `scripts/monitor-resources.sh`
```bash
#!/bin/bash
# Monitor resource usage

echo "========================================="
echo "RESOURCE USAGE MONITORING"
echo "========================================="

# CPU Usage
echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print "  Usage: " $2 + $4 "%"}'

# Memory Usage
echo ""
echo "Memory Usage:"
free -h | awk 'NR==2{printf "  Total: %s\n  Used: %s (%.2f%%)\n  Free: %s\n", $2, $3, $3*100/$2, $4}'

# Disk Usage
echo ""
echo "Disk Usage:"
df -h | awk '$NF=="/"{printf "  Total: %s\n  Used: %s (%s)\n  Available: %s\n", $2, $3, $5, $4}'

# Docker Container Stats (if Docker is running)
if command -v docker &> /dev/null; then
  echo ""
  echo "Docker Container Resources:"
  docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || echo "  No containers running"
fi

# Kubernetes Pod Resources (if kubectl is available)
if command -v kubectl &> /dev/null; then
  echo ""
  echo "Kubernetes Pod Resources:"
  kubectl top pods 2>/dev/null || echo "  Kubernetes not available"
fi

echo ""
echo "========================================="
```

**Usage**:
```bash
bash scripts/monitor-resources.sh
```

## Quality Checklist

Before finalizing performance analysis:
- [ ] Metrics collected from multiple iterations
- [ ] Baseline measurements established
- [ ] Bottlenecks identified
- [ ] Recommendations specific and actionable
- [ ] Performance targets defined
- [ ] Analysis scripts tested
- [ ] Reports generated successfully

## Common Performance Issues

### 1. N+1 Query Problem
**Symptom**: Many database queries for related data

**Detection**:
```python
# Enable SQLAlchemy query logging
engine = create_engine(database_url, echo=True)
```

**Fix**: Use eager loading
```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = select(Task).options(selectinload(Task.comments))
tasks = session.exec(statement).all()
```

### 2. Large API Response Payloads
**Symptom**: Slow endpoint response times

**Detection**: Check response sizes in network tab

**Fix**: Implement pagination and field selection
```python
@router.get("/tasks/")
async def list_tasks(
    fields: str = Query("id,title,status"),  # Limit fields
    page_size: int = Query(20, le=100)  # Limit page size
):
    pass
```

### 3. Slow Frontend Rendering
**Symptom**: UI lag, slow initial page load

**Detection**: Use React DevTools Profiler

**Fix**: Memoization and code splitting
```typescript
import { memo } from 'react';
import dynamic from 'next/dynamic';

// Memoize expensive components
const TaskList = memo(({ tasks }) => { /* ... */ });

// Lazy load heavy components
const Chart = dynamic(() => import('./Chart'), { ssr: false });
```

### 4. Missing Database Indexes
**Symptom**: Sequential scans on large tables

**Detection**: Check query execution plans
```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'xxx';
```

**Fix**: Add indexes
```python
user_id: UUID = Field(foreign_key="users.id", index=True)
```

## Post-Analysis

After performance analysis:
1. **Prioritize Issues**: Focus on highest impact bottlenecks
2. **Set Targets**: Define performance goals (e.g., P95 < 200ms)
3. **Implement Fixes**: Apply optimizations
4. **Re-measure**: Verify improvements
5. **Monitor**: Set up continuous monitoring
6. **Document**: Update PHR with findings and fixes
