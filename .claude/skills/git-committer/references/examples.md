# Conventional Commits Examples

Common commit message patterns for different scenarios.

## Features

### New feature without scope
```
feat: add dark mode toggle
```

### New feature with scope
```
feat(auth): implement OAuth2 authentication
```

### New feature with body
```
feat(api): add user profile endpoints

Add GET, PUT, and DELETE endpoints for managing
user profiles with proper authentication.
```

### Breaking change feature
```
feat(api)!: redesign task endpoints

BREAKING CHANGE: Task endpoints now use `/api/v2/tasks`
instead of `/api/tasks`. Update client applications accordingly.
```

## Bug Fixes

### Simple fix
```
fix: resolve null pointer exception in login
```

### Fix with scope
```
fix(database): correct migration rollback script
```

### Fix with issue reference
```
fix(auth): prevent token expiration race condition

Fixes #456
```

### Critical fix
```
fix(security): patch SQL injection vulnerability

Closes #789
```

## Documentation

### Simple docs update
```
docs: update README installation steps
```

### API documentation
```
docs(api): add examples for authentication endpoints
```

### Multiple documentation files
```
docs: improve getting started guide

- Update installation instructions
- Add troubleshooting section
- Include Docker setup steps
```

## Code Style

### Formatting changes
```
style: format code with prettier
```

### Linting fixes
```
style(backend): fix eslint warnings
```

## Refactoring

### Simple refactor
```
refactor: extract validation logic into utility
```

### Large refactor with body
```
refactor(auth): reorganize authentication module

- Split authentication logic into separate services
- Extract token validation into middleware
- Improve error handling consistency
```

## Performance

### Performance improvement
```
perf: optimize database queries in user lookup
```

### Performance improvement with measurements
```
perf(api): reduce response time by 40%

Implement Redis caching for frequently accessed
user data. Response time reduced from 500ms to 300ms.
```

## Tests

### Adding tests
```
test: add unit tests for user service
```

### Test coverage improvement
```
test(auth): increase coverage to 95%

Add integration tests for authentication flows
and edge cases.
```

## Build

### Dependency update
```
build: upgrade React to v18
```

### Build configuration
```
build(webpack): optimize bundle size

- Enable tree shaking
- Add code splitting
- Compress assets
```

## CI/CD

### CI pipeline update
```
ci: add automated deployment to staging
```

### CI configuration fix
```
ci(github): fix failing deployment workflow

Closes #234
```

## Chore

### General maintenance
```
chore: update dependencies
```

### Tool configuration
```
chore(eslint): update linting rules
```

### Release preparation
```
chore: prepare for v2.0.0 release

- Update version numbers
- Generate changelog
- Update documentation
```

## Revert

### Revert previous commit
```
revert: revert "feat: add dark mode toggle"

This reverts commit abc123def456.
The feature caused performance issues on mobile devices.
```

## Multi-Scope Changes

### Multiple areas affected
```
feat(api,ui): implement task filtering

Backend:
- Add filter parameters to task endpoints
- Implement database query optimization

Frontend:
- Add filter dropdowns to task list
- Update API client with filter support

Closes #567
```

## Complex Example with All Elements

```
feat(auth)!: implement two-factor authentication

Add support for TOTP-based two-factor authentication
to enhance account security. Users can enable 2FA in
their account settings.

Implementation details:
- Generate and store encrypted TOTP secrets
- Add QR code generation for authenticator apps
- Implement backup codes for account recovery
- Add 2FA verification to login flow

BREAKING CHANGE: Login API now requires `twoFactorCode`
parameter when 2FA is enabled. Update all API clients.

Closes #123
Refs #456
Reviewed-by: @security-team
```

## Real-World Project Examples

### Backend Development
```
feat(database): add user roles and permissions

Implement role-based access control with:
- User roles table (admin, editor, viewer)
- Permission associations
- Middleware for authorization checks

Closes #890
```

### Frontend Development
```
fix(ui): resolve table pagination bug

Table was showing incorrect page numbers when
filtered results had fewer pages than previous query.

Fixes #345
```

### DevOps
```
ci(docker): optimize build time

- Use multi-stage builds
- Add layer caching
- Reduce image size from 1.2GB to 400MB

Build time reduced from 10min to 3min.
```

### Documentation
```
docs(contributing): add PR submission guidelines

Include:
- Branch naming conventions
- Commit message format (Conventional Commits)
- Code review checklist
- Testing requirements
```

## Tips for Writing Good Commits

1. **Keep description concise**: Under 50 characters if possible
2. **Use lowercase for description**: Start with lowercase letter
3. **No period at end**: Description should not end with period
4. **Use imperative mood**: "add feature" not "added feature"
5. **Explain why, not what**: Body should explain motivation
6. **Reference issues**: Link to relevant issue tracker items
7. **Group related changes**: One commit per logical change
8. **Test before committing**: Ensure code works before commit
