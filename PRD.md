# QueryEngine - Product Requirements Document

**Version:** 1.0  
**Status:** Production  
**Last Updated:** 2026-07-15  
**Owner:** Engineering Team  

---

## 1. Executive Summary

QueryEngine is an NLP-to-SQL platform that generates, executes, and validates SQL queries from natural language requests. Users describe their data analysis needs in plain English, and QueryEngine transforms them into production-ready SQL with automatic test generation and execution.

**Core Value Prop:** 5-minute SQL analytics without writing code.

**Target Users:** Business analysts, data engineers, non-technical stakeholders.

**Success Metric:** User can go from idea → SQL → tested query in < 60 seconds.

---

## 2. Product Vision

### 2.1 Problem Statement

**Current State:**
- Analysts write SQL manually (slow, error-prone)
- Cross-database expertise required (PostgreSQL ≠ Oracle)
- Testing SQL queries is tedious (manual validation)
- Deploying queries requires engineering review

**QueryEngine Solution:**
- Write queries in natural language
- AI generates SQL automatically
- Validate with auto-generated tests
- Deploy immediately

### 2.2 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query generation speed | < 3 sec | Time from submit to SQL shown |
| Test coverage | > 85% | Pytest code coverage |
| User satisfaction | > 4/5 stars | Post-execution survey |
| API uptime | 99.5% | Monthly SLA |
| Cost per query | < $0.10 | Total API spend / queries |

### 2.3 Future Vision (Phase 2+)

- [ ] Multi-user collaboration (shared queries)
- [ ] Query history & undo (audit trail)
- [ ] Performance profiling (query execution plans)
- [ ] Cost estimation (before execution)
- [ ] Saved templates (custom SQL patterns)
- [ ] Slack/Teams integration (bot interface)
- [ ] Role-based access control (enterprise)

---

## 3. Features & Requirements

### 3.1 Core Features

#### Feature 1: Natural Language Query Input
**Requirement:** Users input English-language analytics requests.

| Aspect | Requirement |
|--------|-------------|
| **Input Method** | Textarea with sample queries |
| **Min Length** | 1 character |
| **Max Length** | 2,000 characters |
| **Validation** | Client-side: check length; Server-side: reject SQL keywords |
| **Help Text** | Show 8+ sample queries user can click to populate |
| **Performance** | Submit in < 100ms |

**Acceptance Criteria:**
- ✅ User sees sample queries
- ✅ Clicking sample populates textarea
- ✅ Submit button disabled if empty or > 2000 chars
- ✅ Server rejects queries with DROP/DELETE/ALTER
- ✅ User sees inline error for rejected input

---

#### Feature 2: Phase 1 - SQL Generation
**Requirement:** Generate SQL from natural language using Claude AI.

| Aspect | Requirement |
|--------|-------------|
| **Input** | Natural language query string |
| **Output** | SQL SELECT statement + explanation |
| **Model** | claude-haiku-4-5-20251001 (cost optimized) |
| **Max Tokens** | 1,000 tokens (input + output) |
| **Timeout** | 10 seconds |
| **Databases** | SQLite, PostgreSQL, MySQL, AWS RDS, Azure SQL, Oracle |
| **Safety** | Reject dangerous SQL operations |
| **Cost** | Log tokens used, calculate cost |

**Acceptance Criteria:**
- ✅ Generated SQL is syntactically valid
- ✅ SQL matches requested database dialect
- ✅ Output shown in syntax-highlighted code block
- ✅ Copy-to-clipboard button works
- ✅ Token count logged to database

---

#### Feature 3: Phase 2 - Query Execution
**Requirement:** Execute generated SQL and display results.

| Aspect | Requirement |
|--------|-------------|
| **Input** | Generated SQL statement |
| **Output** | Result rows in table format |
| **Max Rows** | 10,000 rows returned |
| **Max Time** | 10 second timeout per query |
| **Error Handling** | Show user-friendly error message |
| **Performance** | Display results within 500ms of query completion |
| **Databases** | SQLite (local demo), mock data for others |

**Acceptance Criteria:**
- ✅ Query executes successfully
- ✅ Results displayed in formatted table
- ✅ Query error shows meaningful message (not stack trace)
- ✅ Timeout after 10 seconds with graceful message
- ✅ Row count displayed with table

---

#### Feature 4: Phase 3 - Test Generation & Execution
**Requirement:** Generate pytest code to validate SQL results.

| Aspect | Requirement |
|--------|-------------|
| **Input** | Generated SQL + execution results |
| **Output** | Pytest code + execution output |
| **Model** | claude-haiku-4-5-20251001 |
| **Timeout** | 5 seconds for test execution |
| **Safety** | Scan code for dangerous imports before execution |
| **Output** | Show test code + pass/fail status + output |

**Acceptance Criteria:**
- ✅ Generated pytest code runs without errors
- ✅ Dangerous imports (os, sys, subprocess) rejected
- ✅ Test output shown in code block (not just status)
- ✅ Exit code indicates pass (0) or fail (non-zero)
- ✅ Execution time logged

---

#### Feature 5: Database Selection
**Requirement:** Let users choose target database.

| Aspect | Requirement |
|--------|-------------|
| **Options** | SQLite, PostgreSQL, MySQL, AWS RDS, Azure SQL, Oracle |
| **Behavior** | Dropdown selector on home page |
| **Default** | SQLite (local demo) |
| **Impact** | SQL dialect changes based on selection |

**Acceptance Criteria:**
- ✅ All 6 databases selectable
- ✅ Selection carries through entire flow
- ✅ SQL generated uses correct dialect

---

#### Feature 6: Results Visualization
**Requirement:** Display all 3 phases on one page without scrolling.

| Aspect | Requirement |
|--------|-------------|
| **Layout** | All phases visible simultaneously |
| **Organization** | Phase 1 → Phase 2 → Phase 3 → Summary |
| **Responsive** | Works on desktop (mobile secondary) |
| **Skeleton Loading** | Show skeleton on Phase 1/2/3 during load |
| **Summary Card** | Status + metrics for each phase |

**Acceptance Criteria:**
- ✅ No vertical scrolling needed to see all phases
- ✅ Skeleton loaders shown during execution
- ✅ Summary shows pass/fail for each phase
- ✅ Colors match Version 1 brand

---

### 3.2 Non-Functional Requirements

#### Performance
- API response times < 1 second (excluding LLM)
- Frontend renders in < 2 seconds
- Copy-to-clipboard < 100ms
- Database queries < 10 seconds

#### Scalability
- Support 100 concurrent users
- Handle 1,000 queries/day
- Database connection pooling enabled

#### Security
- No hardcoded secrets
- Input sanitization (SQL injection prevention)
- Code execution sandboxing (pytest)
- HTTPS in production
- Secrets scan in pre-commit hooks

#### Reliability
- API uptime 99.5% (SLA)
- Graceful error handling
- Request ID tracking for debugging
- Structured JSON logging

#### Maintainability
- TypeScript for frontend type safety
- Python type hints (3.10+)
- Minimum 80% code coverage (backend)
- ESLint + Prettier + pre-commit hooks
- Self-documenting code with clear naming

#### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- ARIA labels on form controls
- Color contrast > 4.5:1

---

## 4. User Flows

### 4.1 Happy Path: Generate SQL from Query

```
User                   Frontend              Backend               LLM
 |                        |                    |                   |
 +---Select DB----------->|                    |                   |
 |                        |                    |                   |
 +---Enter Query-------->|                    |                   |
 |                        |                    |                   |
 +---Click Submit-------->|----POST /api/sql/generate----->|
 |                        |                    |                   |
 |                        |                    +--Generate SQL---->|
 |                        |                    |<---Return SQL-----+
 |                        |<---Return Response-|                   |
 |<---Show SQL------------|                    |                   |
 |                        |                    |                   |
 +---[Copy SQL]--------->|                    |                   |
```

### 4.2 Error Path: Invalid SQL Query

```
User                   Frontend              Backend
 |                        |                    |
 +---Enter "DROP TABLE"-->|                    |
 |                        |--POST /api/sql---->|
 |                        |<--400 Bad Request--|
 |<--Show Error Toast-----|                    |
```

### 4.3 Complete Flow: Submit → Execute → Test

```
1. User selects database (SQLite)
2. User enters query ("Show top 10 customers")
3. User clicks "Generate SQL & Tests"
   → Frontend validates input
   → Backend generates SQL
   → Backend executes SQL
   → Backend generates pytest
   → Backend runs pytest
4. Frontend displays all 3 phases
5. User copies SQL or runs again
```

---

## 5. Data Model

### 5.1 Request/Response Schemas

#### POST /api/query/process
```json
{
  "query": "Show top 10 customers by revenue",
  "database_type": "sqlite"
}
```

**Response:**
```json
{
  "request_id": "req_12345",
  "status": "success",
  "phases": {
    "phase1": {
      "sql_query": "SELECT customer_id, SUM(amount) as revenue FROM orders GROUP BY customer_id ORDER BY revenue DESC LIMIT 10",
      "explanation": "This query groups orders by customer and sums revenue...",
      "tokens_used": 150
    },
    "phase2": {
      "rows_returned": 10,
      "sample_data": [
        {"customer_id": 1, "revenue": 5000.00},
        {"customer_id": 2, "revenue": 4500.00}
      ]
    },
    "phase3": {
      "test_code": "def test_top_customers():\n    result = execute_query(...)\n    assert len(result) == 10",
      "exit_code": 0,
      "test_output": "===== 1 passed in 0.05s =====",
      "execution_time_ms": 50
    }
  }
}
```

### 5.2 Database Schema

#### query_history
```sql
CREATE TABLE query_history (
  id SERIAL PRIMARY KEY,
  request_id VARCHAR(50) UNIQUE,
  user_query TEXT,
  database_type VARCHAR(50),
  generated_sql TEXT,
  execution_status VARCHAR(50),  -- success, error, timeout
  rows_returned INT,
  phase1_tokens_used INT,
  phase3_exit_code INT,
  execution_time_ms INT,
  cost_usd DECIMAL(10, 4),
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### cost_tracking
```sql
CREATE TABLE cost_tracking (
  id SERIAL PRIMARY KEY,
  date DATE,
  total_queries INT,
  total_tokens INT,
  total_cost_usd DECIMAL(10, 4),
  UNIQUE(date)
);
```

---

## 6. Technical Architecture

### 6.1 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + TypeScript | Type safety, component reusability |
| **Frontend Build** | Vite | Fast dev server, optimized builds |
| **Styling** | Tailwind CSS + custom theme | Utility-first, Version 1 branding |
| **Backend** | FastAPI (async Python) | Modern, performant, built-in validation |
| **Server** | Uvicorn | ASGI server, handles async well |
| **Database** | PostgreSQL (prod), SQLite (demo) | ACID compliance, audit trail |
| **LLM** | Claude Haiku API | Cost optimized, fast inference |
| **Subprocess** | asyncio.to_thread() | Non-blocking pytest execution |
| **Validation** | Pydantic | Runtime type checking |
| **Logging** | Python logging + JSON formatter | Structured logs for aggregation |
| **Linting** | ESLint, Pylint | Code quality enforcement |
| **Testing** | Jest (frontend), pytest (backend) | Industry standard |

### 6.2 System Diagram

```
┌─────────────────────────────────────────────────────────┐
│ User Browser                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │ React App (Vite)                                   │  │
│ │ HomePage → ResultsPage (Router)                    │  │
│ └────────────────────────────────────────────────────┘  │
└─────────────────────┬──────────────────────────────────┘
                      │ HTTPS
    ┌─────────────────▼──────────────────┐
    │ FastAPI Backend (Uvicorn)          │
    │ ┌──────────────────────────────┐   │
    │ │ API Routes                   │   │
    │ │ /query/process               │   │
    │ │ /health                      │   │
    │ └──────────────────────────────┘   │
    │ ┌──────────────────────────────┐   │
    │ │ Services                     │   │
    │ │ - sql_generator (Claude AI)  │   │
    │ │ - executor (SQL + pytest)    │   │
    │ │ - sanitizer (input safety)   │   │
    │ └──────────────────────────────┘   │
    └─────────────────┬──────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌────────┐  ┌──────────┐  ┌────────────┐
    │Claude  │  │SQLite DB │  │PostgreSQL  │
    │API     │  │(local)   │  │(metrics)   │
    └────────┘  └──────────┘  └────────────┘
```

### 6.3 Deployment Architecture

**Local Development:**
- React dev server (Vite): http://localhost:5173
- FastAPI dev server: http://localhost:8000
- SQLite database (local file)

**Production (Future):**
- Frontend: Vercel or AWS CloudFront + S3
- Backend: AWS ECS / Google Cloud Run (serverless)
- Database: AWS RDS (PostgreSQL)
- Logging: CloudWatch or Datadog
- LLM: Claude API (Anthropic)

---

## 7. Constraints & Assumptions

### 7.1 Constraints

| Constraint | Impact |
|-----------|--------|
| Max query length: 2,000 chars | Users must be concise in natural language |
| Max result rows: 10,000 | Prevents memory overload on client/server |
| Query timeout: 10 seconds | Long-running queries fail (acceptable for analytics) |
| Test timeout: 5 seconds | Complex tests not supported |
| No multi-user: Phase 1 only | No concurrent query execution |
| SQLite for demo only | Not suitable for production data |

### 7.2 Assumptions

| Assumption | Rationale |
|-----------|-----------|
| Users have valid databases | No invalid connection strings tested |
| Internet connection available | Cloud LLM calls require connectivity |
| Python 3.10+ available | Not testing on older Python |
| Read-only access needed | No INSERT/UPDATE/DELETE support |
| English language only | Localization not in Phase 1 |

---

## 8. Success Metrics & KPIs

### 8.1 User Engagement

| KPI | Target | Measurement |
|-----|--------|-------------|
| Time to first SQL | < 30 sec | Analytics from frontend |
| Queries per session | > 3 | Session duration tracking |
| Copy/paste rate | > 70% | Click tracking on copy buttons |
| Sample query clicks | > 40% | Event tracking |

### 8.2 Quality Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| SQL generation success | > 90% | Valid/executable SQL rate |
| Test generation success | > 85% | Non-crashing pytest rate |
| Query execution success | > 95% | Successful result sets |
| Error rate | < 1% | 5xx errors / total requests |

### 8.3 Performance Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| P50 latency | < 2 sec | Request time including LLM |
| P95 latency | < 5 sec | 95th percentile response time |
| API uptime | 99.5% | Monthly monitoring |
| Page load time | < 2 sec | Lighthouse score |

### 8.4 Cost Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| Cost per query | < $0.10 | LLM tokens × rate |
| Daily spending limit | $50 | Alert if exceeded |
| Cost per user | < $5/month | At 1,000 queries/month/user |

---

## 9. Roadmap

### Phase 1: MVP (Completed)
- [x] Natural language query input
- [x] SQL generation (Phase 1)
- [x] Query execution (Phase 2)
- [x] Test generation (Phase 3)
- [x] 6 database types supported
- [x] Professional UI with branding
- [x] Guardrails & standards

### Phase 2: Enhancements (Q3 2026)
- [ ] Query history & undo
- [ ] Multi-user collaboration
- [ ] Performance profiling
- [ ] Cost estimation before execution
- [ ] Slack bot integration
- [ ] Role-based access control

### Phase 3: Scale (Q4 2026)
- [ ] Caching layer (Redis)
- [ ] Database clustering
- [ ] Advanced logging (ELK stack)
- [ ] API rate limiting
- [ ] Custom SQL templates

### Phase 4: Intelligence (2027)
- [ ] Query optimization suggestions
- [ ] Anomaly detection in results
- [ ] Schema learning from database
- [ ] Multi-step query chains

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Claude API rate limits | Medium | High | Implement exponential backoff + user messaging |
| SQL injection vulnerability | Low | Critical | Input sanitization + parameterized queries |
| Harmful test code execution | Low | Critical | Code scanning before execution + sandboxing |
| Database connection limits | Medium | Medium | Connection pooling + max concurrent connections |
| High LLM costs | Medium | Medium | Token limit + cost tracking + alerts |
| Poor query generation | Medium | Medium | User feedback + prompt refinement |

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Phase 1** | SQL generation from natural language |
| **Phase 2** | SQL execution on database |
| **Phase 3** | Test generation & execution |
| **Claude** | Large language model by Anthropic |
| **Tokens** | Billing unit for LLM (roughly 4 chars = 1 token) |
| **Pytest** | Python testing framework |
| **Sanitization** | Removing/escaping dangerous input |
| **Version 1 Brand** | Company branding colors & typography |
| **QueryEngine** | Product name |

---

## 12. Approval & Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | — | 2026-07-15 | ✓ |
| Tech Lead | — | 2026-07-15 | ✓ |
| QA Lead | — | 2026-07-15 | ✓ |

---

## Related Documents

- [README.md](./README.md) - Setup & usage instructions
- [GUARDRAILS.md](./GUARDRAILS.md) - Code quality standards
- [API Documentation](./docs/API.md) - Endpoint specifications
- [Architecture Diagram](#62-system-diagram) - System design

---

**Last Updated:** 2026-07-15  
**Next Review:** 2026-10-15 (quarterly)
