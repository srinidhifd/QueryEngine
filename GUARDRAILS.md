# QueryEngine Guardrails & Standards

This document defines code quality, security, and consistency standards for the QueryEngine project.

## 1. Code Quality Standards

### 1.1 Frontend (React + TypeScript)

**TypeScript Strictness**
- Enable `strict: true` in `tsconfig.json`
- All functions must have explicit return types
- Use `as const` for literal types, not `as any`
- No `any` types without explicit `// @ts-ignore` comment with reason

**Component Structure**
```tsx
// ✅ Good
const HomePage: React.FC = () => {
  const [query, setQuery] = React.useState('');
  return <div>{query}</div>;
};

// ❌ Bad
const HomePage = () => {  // Missing type annotation
  const query: any = '';  // any type
  return <div>{query}</div>;
};
```

**Naming Conventions**
- Components: PascalCase (HomePage.tsx)
- Hooks: camelCase starting with 'use' (useQuery.ts)
- Constants: UPPER_SNAKE_CASE
- Files: match export (HomePage.tsx exports HomePage)

**React Best Practices**
- Use functional components only (no class components)
- Declare hooks at top level (no conditional hooks)
- Use `React.FC<Props>` for type safety
- Keys on lists must be unique, not array indices
- Memoize expensive computations with useMemo

**Imports Order**
1. React/libraries (`import React`)
2. Components (`from './components'`)
3. Hooks (`from './hooks'`)
4. Utils (`from './utils'`)
5. Types (`from './types'`)
6. Styles (`import './style.css'`)

### 1.2 Backend (FastAPI + Python)

**Python Version & Standards**
- Python 3.10+ only
- Follow PEP 8 with 120-char line limit
- Type hints on all functions (`def func(x: str) -> int:`)
- Docstrings on public functions (Google style)

**Code Structure**
```python
# ✅ Good
def execute_query(sql: str, timeout: int = 10) -> QueryResult:
    """Execute SQL query with timeout protection.
    
    Args:
        sql: SQL query string
        timeout: Query timeout in seconds
    
    Returns:
        QueryResult with rows and metadata
    
    Raises:
        QueryTimeoutError: If query exceeds timeout
    """
    # implementation
    pass

# ❌ Bad
def execute_query(sql, timeout=10):  # No type hints
    # No docstring
    return result
```

**Import Organization**
1. Standard library imports
2. Third-party imports (fastapi, sqlalchemy, etc.)
3. Local imports (services, models, etc.)
4. Type imports (`from typing import ...`)

**Async/Await Rules**
- Mark async functions with `async def`
- Use `await` for all async calls
- Never mix sync/async without explicit `asyncio.to_thread()`
- Document which functions are async in docstrings

**Error Handling**
- Custom exceptions in `backend/utils/errors.py`
- Never use bare `except:` (always specify exception type)
- Log exceptions with full context
- Return user-friendly messages in API responses

### 1.3 Configuration

**Environment Variables**
- Define in `.env` (never commit `.env`)
- Use `.env.example` for template with defaults
- Read via `pydantic_settings.BaseSettings`
- Never hardcode secrets or API keys
- Document all env vars in README.md

**Naming Convention for Config**
- Database connections: `DATABASE_URL`
- API keys: `{SERVICE}_API_KEY`
- Feature flags: `FEATURE_*_ENABLED`
- Timeouts: `{SERVICE}_TIMEOUT_SECONDS`

---

## 2. Security Standards

### 2.1 Input Validation

**Frontend**
- Validate all user input before sending to backend
- Use `maxLength` on text inputs
- Show inline validation errors
- Never trust backend data structure

**Backend**
- Validate at API boundary (route layer)
- Use Pydantic models for automatic validation
- Reject requests that don't match schema
- Log invalid input attempts (potential attacks)

### 2.2 SQL Safety

**Query Execution**
```python
# ✅ Good - Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ Bad - SQL injection vulnerability
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Dangerous SQL Operations**
- Reject all user input containing: `DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `CREATE`, `INSERT`, `UPDATE`
- Allow only `SELECT` queries (read-only)
- Enforce query timeout (max 10 seconds)
- Limit result rows (max 10,000)

### 2.3 Code Execution Safety

**Test Code Validation**
- Scan pytest code for dangerous imports:
  - ❌ `os`, `sys`, `subprocess` (shell access)
  - ❌ `requests`, `urllib`, `socket` (network access)
  - ❌ `__import__`, `eval`, `exec` (dynamic code)
- Allow only safe test imports:
  - ✅ `pytest`, `unittest`
  - ✅ `sqlalchemy` (for DB testing)
  - ✅ Standard library (math, json, datetime, etc.)

**Execution Isolation**
- Run user pytest in subprocess with timeout
- Set resource limits (memory, CPU time)
- Capture stdout/stderr, don't expose internal paths
- Clean up temp files after execution

### 2.4 Authentication & Authorization

**Not implemented in Phase 1**
- In future: Add JWT or OAuth2
- For now: Request ID tracking for audit logs
- Log all API calls with source IP

### 2.5 Data Privacy

**PII Handling**
- Never log user query content in production
- Store query metadata only (length, type, execution time)
- Hash sensitive data before storage
- Purge old query history (>90 days)

---

## 3. Testing Standards

### 3.1 Frontend Testing

**Coverage Requirements**
- Minimum 60% line coverage for components
- Test happy path and error states
- Mock API calls with `jest.mock`
- Run: `npm run test:coverage`

**Test Structure**
```tsx
describe('HomePage', () => {
  it('should render query input', () => {
    render(<HomePage />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('should handle submission', async () => {
    render(<HomePage />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'test' } });
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect(mockApi).toHaveBeenCalled());
  });
});
```

### 3.2 Backend Testing

**Coverage Requirements**
- Minimum 80% line coverage for services
- Test all error paths
- Use pytest fixtures for setup
- Run: `pytest tests/ --cov=backend`

**Test Structure**
```python
@pytest.mark.asyncio
async def test_sql_generation_valid_query():
    result = await sql_gen_service.generate("Show revenue by region")
    assert "SELECT" in result.sql_query
    assert result.is_valid is True

def test_sql_generation_rejects_malicious_query():
    with pytest.raises(ValidationError):
        sql_gen_service.generate("DROP TABLE sales")
```

### 3.3 Integration Testing

**End-to-End Flow**
1. Backend starts (health check passes)
2. Frontend connects
3. User enters query
4. Full pipeline executes
5. Results display correctly

**Run:** `npm run test:e2e` (future implementation)

---

## 4. Documentation Standards

### 4.1 Code Comments

**When to Comment**
- ✅ Why a non-obvious decision was made
- ✅ Workarounds for specific bugs/limitations
- ✅ Important assumptions or invariants
- ❌ What the code does (code should be self-explanatory)
- ❌ Block comments at function top

**Example**
```python
# Rate limiter uses sliding window, not token bucket
# (cheaper on memory for cloud deployments)
def rate_limit(user_id: str) -> bool:
    # implementation
    pass
```

### 4.2 README Structure

Required sections:
1. **Overview** - What is QueryEngine?
2. **Quick Start** - Get running in 5 minutes
3. **Project Structure** - Where files are
4. **Development Setup** - Full setup instructions
5. **Running Tests** - How to run test suites
6. **API Documentation** - Endpoint specifications
7. **Deployment** - Production setup
8. **Guardrails** - Reference to this file

### 4.3 API Documentation

**Every endpoint must have:**
- Description of what it does
- Request body schema (if POST/PUT)
- Response schema (success and error)
- Example curl commands
- Rate limits (if applicable)

---

## 5. Performance Standards

### 5.1 Frontend

**Bundle Size**
- Main bundle: < 200KB (gzipped)
- Lazy load routes
- Tree-shake unused code
- Use Code Splitting for large components

**Runtime Performance**
- First Contentful Paint: < 2 seconds
- Time to Interactive: < 3 seconds
- Monitor with Lighthouse

### 5.2 Backend

**API Response Times**
- Health check: < 10ms
- SQL generation: < 5 seconds (with LLM)
- Query execution: < 10 seconds
- Test execution: < 5 seconds
- P95 latency: < 8 seconds

**Database**
- Index frequently filtered columns
- Connection pooling enabled
- Query timeouts enforced
- Batch operations where possible

### 5.3 Monitoring

**Metrics to Track**
- API response times (per endpoint)
- Error rate (4xx, 5xx)
- Query success rate
- LLM token usage & cost
- Database connection pool usage

---

## 6. Deployment Standards

### 6.1 Version Control

**Branch Strategy**
- `main` - Production-ready code only
- `develop` - Integration branch
- Feature branches: `feature/description`
- Hotfix branches: `hotfix/description`

**Commit Messages**
- Format: `<type>: <description>`
- Types: feat, fix, docs, test, refactor, chore
- Example: `feat: add SQL generation caching`
- Keep commits atomic (one change per commit)

### 6.2 Code Review

**Before Merging**
- [ ] All tests pass (`npm test`, `pytest`)
- [ ] Linting passes (`npm run lint`, `pylint`)
- [ ] TypeScript type-checks (`npm run type-check`)
- [ ] No hardcoded secrets
- [ ] Updated tests for new code
- [ ] Updated README if behavior changed
- [ ] Meaningful commit messages

### 6.3 Release Checklist

```bash
# 1. Update version
npm version minor  # or major, patch

# 2. Update CHANGELOG
# 3. Run full test suite
npm test && npm run build
cd ../backend && pytest

# 4. Create git tag
git tag -a v1.0.0 -m "Release 1.0.0"

# 5. Push to main
git push origin main --tags

# 6. Deploy
# ... deployment steps ...
```

---

## 7. Enforcement

### 7.1 Automated Checks

**Pre-commit Hooks** (`.husky/pre-commit`)
- Format check: Prettier
- Lint check: ESLint (frontend), Pylint (backend)
- Type check: TypeScript compiler
- Secret scan: grep for API keys

**Install Hooks**
```bash
npm install husky --save-dev
npx husky install
```

### 7.2 CI/CD Pipeline

**GitHub Actions** (future implementation)
- Run tests on every PR
- Check linting, types, coverage
- Block merge if checks fail
- Automated deployment on merge to main

### 7.3 Manual Audits

**Quarterly Code Review**
- Security audit (OWASP top 10)
- Performance review (profiling results)
- Dependency audit (update checks)
- Technical debt assessment

---

## 8. Escalation Path

If guardrail violations are found:

1. **Minor** (formatting, naming) - Auto-fix in pre-commit
2. **Medium** (missing tests, no types) - Block PR merge, request fixes
3. **Major** (security, SQL injection) - Immediately block, notify team
4. **Critical** (secrets exposed) - Rotate keys immediately, investigate

---

## Quick Reference Checklist

Before committing code:

- [ ] TypeScript: `npm run type-check` passes
- [ ] Linting: `npm run lint` passes
- [ ] Formatting: Code matches `.prettierrc.json`
- [ ] Tests: `npm test` has > 60% coverage
- [ ] Python: `pylint backend/**/*.py` passes
- [ ] Backend: `pytest tests/ --cov` > 80% coverage
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] All functions have types/docstrings
- [ ] Imports organized correctly
- [ ] Comments explain "why", not "what"
- [ ] No SQL injection vulnerabilities
- [ ] Error handling at boundaries
- [ ] Logging with context (request ID, etc.)

---

## Questions?

Refer to specific sections or reach out to tech lead.

**Related:**
- [README.md](./README.md) - Project overview
- [PRD.md](./PRD.md) - Product requirements
- [.eslintrc.json](./.eslintrc.json) - Frontend linting rules
- [.prettierrc.json](./.prettierrc.json) - Code formatting rules
- [backend/pyproject.toml](./backend/pyproject.toml) - Backend configuration
