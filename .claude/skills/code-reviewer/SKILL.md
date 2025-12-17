# Code Reviewer Skill

## Metadata
```yaml
name: code-reviewer
description: Performs comprehensive code reviews checking code quality, security, performance, testing, and best practices. Provides actionable feedback and improvement suggestions for Python, TypeScript, and SQL code.
version: 1.0.0
category: quality
tags: [code-review, quality, security, performance, best-practices, static-analysis, linting]
dependencies: [ruff, mypy, eslint, prettier, bandit, safety]
```

## When to Use This Skill

Use this skill when:
- User says "Review this code" or "Check code quality"
- Pull request needs review before merging
- Want to ensure code follows best practices
- Need security vulnerability scan
- Checking performance bottlenecks
- Validating test coverage
- Before production deployment

## What This Skill Provides

### 1. Code Quality Checks
- **Readability**: Clear naming, proper structure
- **Maintainability**: DRY principle, modularity
- **Complexity**: Cyclomatic complexity, nesting depth
- **Documentation**: Docstrings, comments
- **Type safety**: Type hints, TypeScript types

### 2. Security Review
- **SQL injection**: Parameterized queries
- **XSS vulnerabilities**: Input sanitization
- **Authentication**: Proper JWT handling
- **Secrets**: No hardcoded credentials
- **Dependencies**: Known vulnerabilities

### 3. Performance Analysis
- **N+1 queries**: Database query optimization
- **Memory leaks**: Resource cleanup
- **Algorithmic complexity**: O(n) vs O(n²)
- **Caching opportunities**: Redundant computations
- **Bundle size**: Frontend optimization

### 4. Testing Requirements
- **Test coverage**: Minimum 80%
- **Critical paths**: Integration tests
- **Edge cases**: Error handling
- **Test quality**: Assertions, fixtures

### 5. Best Practices
- **Framework conventions**: FastAPI, Next.js patterns
- **Error handling**: Try-except, error boundaries
- **Logging**: Structured logging
- **Configuration**: Environment variables

---

## Review Checklist

### Backend Python (FastAPI + SQLModel)

```python
"""
Code review checklist for backend Python code.
"""

BACKEND_CHECKLIST = {
    "Code Quality": [
        "✓ Functions have type hints for parameters and return values",
        "✓ Docstrings present for all public functions (Google style)",
        "✓ Variable names are descriptive (no single letters except i, j in loops)",
        "✓ Functions are focused and single-purpose (< 30 lines)",
        "✓ No code duplication (DRY principle)",
        "✓ Proper use of constants for magic numbers/strings",
        "✓ Import statements organized (stdlib, third-party, local)",
    ],

    "SQLModel & Database": [
        "✓ All models have proper field constraints (nullable, unique, default)",
        "✓ Foreign keys defined with proper ON DELETE behavior",
        "✓ Indexes created for frequently queried fields",
        "✓ Relationships use back_populates for bidirectional",
        "✓ No raw SQL queries (use SQLModel/SQLAlchemy)",
        "✓ Alembic migrations generated for schema changes",
        "✓ No N+1 query problems (use joinedload if needed)",
    ],

    "FastAPI Endpoints": [
        "✓ Endpoints follow RESTful conventions",
        "✓ Proper HTTP status codes returned (200, 201, 404, 422, 500)",
        "✓ Request/response use Pydantic schemas",
        "✓ Protected endpoints use JWT authentication",
        "✓ Pagination implemented for list endpoints",
        "✓ Error responses are structured and consistent",
        "✓ OpenAPI documentation accurate",
    ],

    "Security": [
        "✓ No SQL injection vulnerabilities (parameterized queries)",
        "✓ Passwords hashed with bcrypt (never plaintext)",
        "✓ JWT tokens validated and expired properly",
        "✓ No hardcoded secrets (use environment variables)",
        "✓ User input validated and sanitized",
        "✓ CORS configured correctly",
        "✓ Rate limiting on public endpoints",
    ],

    "Error Handling": [
        "✓ Try-except blocks for risky operations",
        "✓ Specific exceptions caught (not bare except)",
        "✓ Errors logged with appropriate level",
        "✓ User-friendly error messages returned",
        "✓ Database transactions rolled back on error",
        "✓ Resources cleaned up in finally blocks",
    ],

    "Testing": [
        "✓ Unit tests for business logic functions",
        "✓ Integration tests for API endpoints",
        "✓ Test coverage ≥ 80%",
        "✓ Happy path and error cases tested",
        "✓ Fixtures used for test data",
        "✓ Tests are isolated and independent",
        "✓ No hard-coded test data in tests",
    ],

    "Performance": [
        "✓ Database queries optimized (no N+1)",
        "✓ Appropriate use of indexing",
        "✓ Lazy loading vs eager loading considered",
        "✓ No unnecessary database calls in loops",
        "✓ Caching used where appropriate",
        "✓ Async/await used for I/O operations",
    ],
}


def review_python_file(file_path: str) -> dict:
    """
    Automated review of Python file.

    Returns dict with issues found.
    """
    issues = {
        "critical": [],
        "warnings": [],
        "suggestions": []
    }

    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    # Check for hardcoded secrets
    secret_patterns = ['password =', 'api_key =', 'secret =', 'token =']
    for i, line in enumerate(lines, 1):
        for pattern in secret_patterns:
            if pattern in line.lower() and '"' in line:
                issues['critical'].append({
                    "line": i,
                    "message": f"Possible hardcoded secret: {line.strip()}",
                    "suggestion": "Use environment variables or secrets manager"
                })

    # Check for missing type hints
    import re
    func_pattern = re.compile(r'def\s+(\w+)\s*\((.*?)\)\s*:')
    for i, line in enumerate(lines, 1):
        match = func_pattern.search(line)
        if match and '->' not in line:
            func_name = match.group(1)
            if not func_name.startswith('_'):  # Ignore private methods
                issues['warnings'].append({
                    "line": i,
                    "message": f"Function '{func_name}' missing return type hint",
                    "suggestion": "Add -> ReturnType to function signature"
                })

    # Check for bare except
    for i, line in enumerate(lines, 1):
        if line.strip() == 'except:':
            issues['critical'].append({
                "line": i,
                "message": "Bare except clause catches all exceptions",
                "suggestion": "Catch specific exception types"
            })

    # Check for print statements (should use logging)
    for i, line in enumerate(lines, 1):
        if 'print(' in line and 'DEBUG' not in content[:i]:
            issues['suggestions'].append({
                "line": i,
                "message": "Using print() instead of logging",
                "suggestion": "Use logger.info() or logger.debug()"
            })

    return issues
```

### Frontend TypeScript (Next.js + React)

```typescript
/**
 * Code review checklist for frontend TypeScript code.
 */

const FRONTEND_CHECKLIST = {
  "Code Quality": [
    "✓ All variables and functions have proper TypeScript types",
    "✓ No 'any' types used (unless absolutely necessary)",
    "✓ Components are functional (no class components)",
    "✓ Custom hooks extracted for reusable logic",
    "✓ Props interfaces defined and exported",
    "✓ Component files < 300 lines",
    "✓ Consistent naming (PascalCase for components, camelCase for functions)",
  ],

  "React Best Practices": [
    "✓ useCallback for functions passed as props",
    "✓ useMemo for expensive computations",
    "✓ useEffect cleanup functions present",
    "✓ No state updates on unmounted components",
    "✓ Keys used in lists (unique and stable)",
    "✓ Controlled components for form inputs",
    "✓ Error boundaries for error handling",
  ],

  "Next.js App Router": [
    "✓ Server Components used by default",
    "✓ 'use client' directive only when needed",
    "✓ Loading.tsx for loading states",
    "✓ Error.tsx for error handling",
    "✓ Metadata exported from pages",
    "✓ API routes in app/api directory",
    "✓ Proper data fetching (fetch with cache options)",
  ],

  "Performance": [
    "✓ Images use next/image component",
    "✓ Dynamic imports for code splitting",
    "✓ No unnecessary re-renders",
    "✓ Bundle size optimized (< 500KB initial)",
    "✓ Lazy loading for below-the-fold content",
    "✓ Debouncing/throttling for frequent events",
    "✓ React.memo for expensive components",
  ],

  "Accessibility": [
    "✓ Semantic HTML elements used",
    "✓ ARIA labels present where needed",
    "✓ Keyboard navigation works",
    "✓ Focus management for modals",
    "✓ Alt text for images",
    "✓ Color contrast meets WCAG standards",
    "✓ Form validation messages accessible",
  ],

  "Security": [
    "✓ User input sanitized (prevent XSS)",
    "✓ No dangerouslySetInnerHTML (or properly sanitized)",
    "✓ JWT tokens stored securely (httpOnly cookies)",
    "✓ API calls use HTTPS",
    "✓ No sensitive data in console.log",
    "✓ CSRF protection on form submissions",
  ],

  "Testing": [
    "✓ Unit tests for utility functions",
    "✓ Component tests for UI logic",
    "✓ Integration tests for user flows",
    "✓ Test coverage ≥ 80%",
    "✓ Testing Library queries (not getByTestId)",
    "✓ User events tested (clicks, typing)",
    "✓ API mocked with MSW",
  ],

  "Styling": [
    "✓ Tailwind CSS classes used consistently",
    "✓ No inline styles (use Tailwind utilities)",
    "✓ Responsive design (mobile-first)",
    "✓ Dark mode support if applicable",
    "✓ No !important in CSS",
    "✓ Consistent spacing (use Tailwind spacing scale)",
  ],
};


function reviewTypeScriptFile(filePath: string): ReviewResult {
  const issues: Issue[] = [];

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  // Check for 'any' types
  lines.forEach((line, index) => {
    if (line.includes(': any') || line.includes('<any>')) {
      issues.push({
        line: index + 1,
        severity: 'warning',
        message: "Using 'any' type defeats TypeScript's type safety",
        suggestion: "Define proper type or use 'unknown'",
      });
    }
  });

  // Check for console.log in production code
  lines.forEach((line, index) => {
    if (line.includes('console.log') && !filePath.includes('.test.')) {
      issues.push({
        line: index + 1,
        severity: 'suggestion',
        message: 'console.log present in production code',
        suggestion: 'Remove or use proper logging library',
      });
    }
  });

  // Check for dangerouslySetInnerHTML
  lines.forEach((line, index) => {
    if (line.includes('dangerouslySetInnerHTML')) {
      issues.push({
        line: index + 1,
        severity: 'critical',
        message: 'Potential XSS vulnerability with dangerouslySetInnerHTML',
        suggestion: 'Sanitize HTML with DOMPurify before rendering',
      });
    }
  });

  // Check for missing useCallback
  const hasEventHandlers = content.match(/onClick=|onChange=|onSubmit=/);
  const hasUseCallback = content.includes('useCallback');

  if (hasEventHandlers && !hasUseCallback) {
    issues.push({
      line: 0,
      severity: 'suggestion',
      message: 'Event handlers without useCallback',
      suggestion: 'Wrap event handlers in useCallback to prevent re-renders',
    });
  }

  return {
    filePath,
    issues,
    score: calculateScore(issues),
  };
}
```

---

## Automated Review Tools

### Python Static Analysis

```python
"""
Run automated code review tools for Python.
"""

import subprocess
from typing import Dict, List

def run_ruff(file_path: str) -> Dict:
    """Run Ruff linter."""
    result = subprocess.run(
        ['ruff', 'check', file_path, '--output-format=json'],
        capture_output=True,
        text=True
    )

    return {
        "tool": "ruff",
        "issues": json.loads(result.stdout) if result.stdout else []
    }

def run_mypy(file_path: str) -> Dict:
    """Run MyPy type checker."""
    result = subprocess.run(
        ['mypy', file_path, '--show-error-codes'],
        capture_output=True,
        text=True
    )

    return {
        "tool": "mypy",
        "output": result.stdout
    }

def run_bandit(file_path: str) -> Dict:
    """Run Bandit security scanner."""
    result = subprocess.run(
        ['bandit', '-f', 'json', file_path],
        capture_output=True,
        text=True
    )

    return {
        "tool": "bandit",
        "issues": json.loads(result.stdout) if result.stdout else []
    }

def run_pytest_cov(directory: str) -> Dict:
    """Run pytest with coverage."""
    result = subprocess.run(
        ['pytest', '--cov=' + directory, '--cov-report=json'],
        capture_output=True,
        text=True
    )

    with open('coverage.json') as f:
        coverage_data = json.load(f)

    return {
        "tool": "pytest-cov",
        "coverage_percent": coverage_data['totals']['percent_covered'],
        "missing_lines": coverage_data['totals']['missing_lines']
    }


def comprehensive_review(file_or_dir: str) -> Dict:
    """Run all review tools."""
    results = {
        "ruff": run_ruff(file_or_dir),
        "mypy": run_mypy(file_or_dir),
        "bandit": run_bandit(file_or_dir),
    }

    if os.path.isdir(file_or_dir):
        results["coverage"] = run_pytest_cov(file_or_dir)

    # Aggregate issues
    total_issues = sum(
        len(r.get('issues', [])) for r in results.values()
    )

    return {
        "results": results,
        "total_issues": total_issues,
        "passed": total_issues == 0
    }
```

### TypeScript/JavaScript Tools

```bash
# ESLint
npx eslint src/**/*.{ts,tsx} --format json

# TypeScript compiler
npx tsc --noEmit

# Prettier
npx prettier --check src/**/*.{ts,tsx}

# Bundle analyzer
npx @next/bundle-analyzer

# Lighthouse (performance)
npx lighthouse https://localhost:3000 --output json
```

---

## Review Template

```markdown
# Code Review: [Feature Name]

## Summary
Brief description of changes and purpose.

## Files Changed
- `path/to/file1.py` - Description of changes
- `path/to/file2.tsx` - Description of changes

## Review Checklist

### ✅ Code Quality
- [x] Code follows project conventions
- [x] Functions are properly documented
- [x] No code duplication
- [ ] **ISSUE**: Function `processData` is too complex (cyclomatic complexity 15)

### ✅ Security
- [x] No hardcoded secrets
- [x] Input validation present
- [ ] **ISSUE**: SQL query not parameterized (line 45)

### ✅ Performance
- [x] No obvious performance issues
- [ ] **SUGGESTION**: Consider caching result of expensive calculation (line 78)

### ✅ Testing
- [x] Tests added for new functionality
- [ ] **ISSUE**: Integration test missing for error case

## Critical Issues (Must Fix)
1. **SQL Injection Risk** (`app/database.py:45`)
   - Problem: Raw SQL query with string interpolation
   - Fix: Use parameterized queries
   ```python
   # Before
   query = f"SELECT * FROM users WHERE id = {user_id}"

   # After
   query = "SELECT * FROM users WHERE id = :user_id"
   session.execute(query, {"user_id": user_id})
   ```

## Warnings (Should Fix)
1. **Missing Type Hint** (`app/services.py:23`)
   - Add return type hint to `get_user()` function

## Suggestions (Nice to Have)
1. **Extract Magic Number** (`app/config.py:15`)
   - Move `MAX_RETRIES = 3` to constant

## Test Coverage
- Overall: 85% ✅
- New files: 90% ✅
- Critical paths covered ✅

## Performance Impact
- No significant performance concerns
- Bundle size increased by 5KB (acceptable)

## Approval Status
- [x] Code quality acceptable
- [x] Security reviewed
- [x] Tests adequate
- [ ] **BLOCKED**: Critical issues must be fixed

## Next Steps
1. Fix SQL injection vulnerability
2. Add missing type hints
3. Re-run automated checks
4. Request re-review
```

---

## Best Practices

1. **Be Constructive**:
   - Focus on code, not person
   - Explain "why" for suggestions
   - Offer solutions, not just problems

2. **Prioritize**:
   - Critical (security, bugs) first
   - Warnings (best practices) second
   - Suggestions (style) last

3. **Automate**:
   - Use linters and formatters
   - Run security scanners
   - Check coverage automatically

4. **Test Changes**:
   - Run tests locally
   - Check builds pass
   - Verify functionality

5. **Document**:
   - Explain complex changes
   - Link to related issues/PRs
   - Update documentation

---

## Quality Checklist

Before approving PR:
- [ ] All automated checks pass (linting, tests, type checking)
- [ ] No critical security issues
- [ ] Code coverage ≥ 80%
- [ ] No obvious performance problems
- [ ] Code follows project conventions
- [ ] New features have tests
- [ ] Documentation updated if needed
- [ ] No breaking changes (or properly documented)
- [ ] Error handling comprehensive
- [ ] Resource cleanup proper

This skill provides comprehensive code review guidance and automation to maintain high code quality and prevent bugs before production.
