# QueryEngine - NLP-to-SQL Platform

**Transform natural language into production-ready SQL with AI-powered generation, automatic testing, and real-time execution.**

![Status](https://img.shields.io/badge/status-production-brightgreen?style=flat)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

---

## Overview

QueryEngine is an end-to-end platform that enables non-technical users to analyze data by describing what they need in plain English. The system automatically:

1. **Phase 1:** Generates SQL using Claude AI
2. **Phase 2:** Executes the query and returns results
3. **Phase 3:** Creates comprehensive pytest cases and validates them

**Perfect for:** Business analysts, data engineers, anyone without SQL expertise.

**Time saved:** 5-minute analytics vs. manual SQL writing.

---

## Features

### Core Capabilities

- **Natural Language to SQL** - Describe queries in English, get production-ready SQL
- **Multi-Database Support** - SQLite, PostgreSQL, MySQL, AWS RDS, Azure SQL, Oracle
- **Automatic Test Generation** - Generate and run pytest cases for validation
- **Real-Time Execution** - See results instantly with formatting
- **Safe by Default** - Input sanitization, code execution sandboxing, SQL injection prevention
- **Professional UI** - Version 1 brand colors, glassmorphism effects, responsive design
- **Copy-Paste Ready** - One-click code block copying

### Sample Queries

- "Show total revenue by region"
- "List top 10 customers by spend"
- "Which products had zero sales last month?"
- "Average order value by customer segment"
- "Compare Q1 vs Q2 revenue"

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key (free tier available)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# OR Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Edit .env and add your ANTHROPIC_API_KEY
# Windows: notepad .env
# macOS/Linux: nano .env

# Run backend server
python -m uvicorn main:app --reload
```

**Backend runs on:** http://0.0.0.0:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend runs on:** http://localhost:5173

### Verify Both Are Running

```bash
# In another terminal, check backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## Project Structure

```
QueryEngine/
├── backend/                          # FastAPI application
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configuration from .env
│   ├── api/
│   │   ├── routes.py                # API endpoints
│   │   └── middleware.py            # Error handling, CORS
│   ├── services/
│   │   ├── database.py              # SQL execution
│   │   ├── sql_generator.py         # Phase 1 (Claude)
│   │   ├── test_generator.py        # Phase 3 (pytest)
│   │   └── sanitizer.py             # Input validation
│   ├── models/
│   │   ├── db_models.py             # SQLAlchemy models
│   │   └── schemas.py               # Pydantic request/response
│   ├── utils/
│   │   ├── logger.py                # Structured JSON logging
│   │   ├── errors.py                # Custom exceptions
│   │   └── constants.py             # System prompts
│   ├── tests/                       # Unit tests
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                         # React + TypeScript application
│   ├── src/
│   │   ├── main.tsx                 # Entry point with Router
│   │   ├── App.tsx                  # Route definitions
│   │   ├── pages/
│   │   │   ├── HomePage.tsx         # Query input & samples
│   │   │   └── ResultsPage.tsx      # 3 phases + summary
│   │   ├── components/              # Reusable UI components
│   │   ├── services/
│   │   │   └── api.ts               # API client with retry
│   │   ├── types/                   # TypeScript interfaces
│   │   └── index.css                # Global styles + theme
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docs/                             # Documentation
│   ├── API.md                       # Endpoint specifications
│   └── SETUP.md                     # Detailed setup guide
│
├── .eslintrc.json                   # Frontend linting rules
├── .prettierrc.json                 # Code formatting config
├── .gitignore
├── .env.example
├── GUARDRAILS.md                    # Code quality standards
├── PRD.md                           # Product requirements
└── README.md                        # This file
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | Component-based UI with type safety |
| **Frontend Build** | Vite | Fast dev server & optimized builds |
| **Styling** | Tailwind CSS | Utility-first CSS with custom theme |
| **Backend** | FastAPI (async) | Modern async Python framework |
| **Server** | Uvicorn | ASGI server for async handling |
| **Database** | SQLite (demo), PostgreSQL (prod) | Data persistence |
| **ORM** | SQLAlchemy | Database abstraction layer |
| **LLM** | Claude Haiku API | SQL & test generation |
| **Testing** | Jest (frontend), pytest (backend) | Automated test suites |
| **Code Quality** | ESLint, Prettier, Pylint | Standards enforcement |

---

## API Endpoints

### Core Endpoint

**POST** `/api/query/process`

Submit natural language query and get full pipeline results.

**Request:**
```json
{
  "query": "Show top 10 customers by revenue",
  "database_type": "sqlite"
}
```

**Response:**
```json
{
  "status": "success",
  "phases": {
    "phase1": {
      "sql_query": "SELECT customer_id, SUM(amount) AS revenue FROM orders GROUP BY customer_id ORDER BY revenue DESC LIMIT 10",
      "tokens_used": 145
    },
    "phase2": {
      "rows_returned": 10,
      "data": [...]
    },
    "phase3": {
      "test_code": "def test_top_customers(): ...",
      "exit_code": 0,
      "test_output": "===== 1 passed ====="
    }
  }
}
```

### Health Check

**GET** `/health`

Check API availability.

**Response:**
```json
{
  "status": "healthy"
}
```

See [API Documentation](./docs/API.md) for complete endpoint reference.

---

## Configuration

### Environment Variables

1. **Copy the template:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` with your settings:**
   ```env
   # Required
   ANTHROPIC_API_KEY=sk-ant-...

   # Optional (defaults shown)
   MODEL=claude-haiku-4-5-20251001
   DATABASE_URL=sqlite:///./queryengine.db
   LOG_LEVEL=INFO
   QUERY_TIMEOUT_SECONDS=10
   TEST_TIMEOUT_SECONDS=5
   ```

**Important:**
- ✅ Commit `backend/.env.example` (it's documentation)
- ❌ Never commit `backend/.env` (contains secrets)
- Location: Always in `backend/` directory

### Color Theme

QueryEngine uses Version 1 branding:

```css
--midnight-black: #052831      /* Primary background */
--primary-teal: #00c6c2        /* Accents & buttons */
--card-dark: #0d1117           /* Secondary background */
--text-primary: #ffffff        /* Primary text */
--text-secondary: #a8b5b9      /* Secondary text */
```

All theme colors are centralized in Tailwind config. Do not hardcode hex values.

---

## Database

### Sample Data (Demo)

- **35 Customers** across 8 countries
- **168 Orders** with various statuses
- **12 Product Categories**
- **Customer Segments** (Enterprise, Mid-Market, SMB, Startup)

Data auto-loads on first run. No manual database setup needed for SQLite demo.

### Schema

See `backend/models/db_models.py` for table definitions:
- `query_history` - Tracks executed queries
- `cost_tracking` - LLM spending metrics

---

## Running Tests

### Frontend Tests
```bash
cd frontend
npm test                          # Run all tests
npm run test:coverage             # Coverage report
npm run type-check               # TypeScript check
npm run lint                     # ESLint check
```

### Backend Tests
```bash
cd backend
# Activate venv first
pytest tests/ -v                 # Run all tests
pytest tests/ --cov=backend      # Coverage report
pylint backend/**/*.py           # Code quality check
```

### Pre-Commit Checks
```bash
# Runs before commit to catch issues early
npx husky install               # Install git hooks
```

---

## Development Workflow

### Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes** and test locally:
   ```bash
   npm run lint && npm run type-check    # Frontend
   pytest tests/ --cov=backend           # Backend
   ```

3. **Commit with meaningful message:**
   ```bash
   git commit -m "feat: add SQL caching"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   ```

### Code Standards

Follow [GUARDRAILS.md](./GUARDRAILS.md) for:
- Code quality requirements
- Security best practices
- Testing expectations
- Documentation standards
- Pre-commit enforcement

**Quick checklist before committing:**
- [ ] TypeScript compiles (`npm run type-check`)
- [ ] ESLint passes (`npm run lint`)
- [ ] Tests pass (`npm test`, `pytest`)
- [ ] No hardcoded secrets
- [ ] Functions have type hints / docstrings

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Activate venv
cd backend && .\venv\Scripts\activate  # Windows
cd backend && source venv/bin/activate # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt

# Check port 8000 is free
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux
```

### Frontend won't start
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### LLM API errors
```bash
# Verify API key
echo $ANTHROPIC_API_KEY  # Should print your key

# Check rate limits
# CloudFlare may throttle at 60+ requests/min
# Add exponential backoff if seeing 429 errors
```

### Database errors
```bash
# SQLite path issues (Windows vs Unix)
DATABASE_URL=sqlite:///./queryengine.db  # Absolute path works better

# Check file permissions
# If readonly, delete and let it recreate
```

---

## Performance

### Typical Response Times

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1 (SQL gen) | 2-4 sec | Claude API latency |
| Phase 2 (Execute) | 100-500 ms | DB query time |
| Phase 3 (Test) | 1-3 sec | Pytest execution |
| **Total** | **~5-8 sec** | User sees skeleton loaders |

### Optimization Tips

- Use sample queries (often cached)
- Keep queries under 500 characters
- Avoid massive result sets (10K+ rows)
- Run during off-peak hours if cost-sensitive

---

## Costs

QueryEngine uses Claude Haiku (cost-optimized):
- **Input:** $0.80 per 1M tokens
- **Output:** $4.00 per 1M tokens
- **Typical cost per query:** $0.01-$0.05

**Example:**
- 200 input tokens + 150 output tokens = 350 tokens
- Cost: (200 * 0.80 + 150 * 4.00) / 1M = ~0.0008 cents

Set daily budget in `.env` to prevent overspending:
```env
MAX_DAILY_COST_USD=50  # Default: $50/day
```

---

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Production (Future)

Deployment guides coming soon:
- Vercel (frontend)
- AWS ECS / Google Cloud Run (backend)
- AWS RDS (database)
- Monitoring & logging setup

See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) when ready.

---

## Security

QueryEngine implements multiple security layers:

1. **Input Validation** - Reject dangerous SQL keywords (DROP, DELETE, ALTER, etc.)
2. **Code Scanning** - Block dangerous imports in pytest (os, sys, subprocess, etc.)
3. **Query Timeouts** - Max 10 seconds per query
4. **Execution Sandboxing** - Run pytest in isolated subprocess
5. **Secret Scanning** - Pre-commit hooks block exposed API keys
6. **Type Safety** - TypeScript + Pydantic enforce correct types
7. **Structured Logging** - Request IDs for audit trails

See [GUARDRAILS.md](./GUARDRAILS.md) for detailed security policies.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`feature/my-feature`)
3. Follow [GUARDRAILS.md](./GUARDRAILS.md) standards
4. Write tests for new functionality
5. Submit a pull request with clear description

---

## Roadmap

### Phase 1: MVP ✅
- Natural language query input
- SQL generation (Phase 1)
- Query execution (Phase 2)
- Test generation & execution (Phase 3)
- Multi-database support
- Professional UI
- Guardrails & standards

### Phase 2: Enhancements (Q3 2026)
- Query history & undo
- Multi-user collaboration
- Performance profiling
- Cost estimation before execution
- Slack/Teams bot integration

### Phase 3: Enterprise (Q4 2026)
- Role-based access control
- Single Sign-On (SSO)
- Advanced caching
- API rate limiting
- Audit logging

---

## 🤖 Future Scope: Agentic AI Era

QueryEngine v1.0 is a **deterministic, production-grade application** with straightforward SQL generation, execution, and testing. The next evolution will introduce **agentic AI patterns** to make the system more intelligent, self-healing, and user-adaptive.

### Current Architecture (v1.0): Deterministic Pipelines

```
User Query → Phase 1 (SQL Gen) → Phase 2 (Execute) → Phase 3 (Test) → Results
  (single shot)   (single shot)     (deterministic)   (single shot)
```

**Strengths:** Fast, predictable, auditable, cost-controlled  
**Limitation:** No self-refinement or error recovery

### Future Architecture: Agentic Layers (v2.0+)

```
User Query → Agent 1: SQL Refinement → Agent 2: Test Generation → 
Agent 3: Debugging → Results (with explanations & optimizations)
  (multi-turn)      (multi-turn + tools)  (iterative fix)
```

### Planned Agentic Agents

#### 1. **SQL Generation Agent** (Replaces Phase 1)
**Today:** One-shot SQL generation  
**Tomorrow:** Multi-turn refinement with validation
- Generate initial SQL
- Validate syntax automatically
- Check safety constraints
- Refine if issues found
- Iterate until perfect (max 3 attempts)
- Return SQL + confidence score + explanation

**Benefits:**
- Self-validates before returning
- Recovers from syntax errors automatically
- Explains why query matches user intent
- Handles complex multi-step queries

**Complexity Reduction:** Eliminates manual SQL debugging

---

#### 2. **Test Generation Agent** (Enhances Phase 3)
**Today:** Generate test code once  
**Tomorrow:** Intelligent coverage with schema analysis
- Analyze SQL structure (aggregations, joins, subqueries)
- Generate diverse test cases automatically
- Run tests and detect failures
- Fix failing tests in real-time
- Ensure >85% coverage
- Return test suite + coverage report

**Benefits:**
- Schema-aware test generation (edge cases auto-discovered)
- Iterative test refinement
- High confidence in SQL correctness
- Educates users on test best practices

**Complexity Reduction:** Users don't need to think about test cases

---

#### 3. **Query Debugging Agent** (New: Recovery)
**Today:** Query fails → Manual fix required  
**Tomorrow:** Automatic error recovery
- Detect Phase 2 failures
- Analyze error message
- Suggest fixes (missing columns, wrong joins, etc.)
- Regenerate SQL
- Test new SQL automatically
- Report what was fixed

**Benefits:**
- Self-healing queries
- Learn from failures
- Explain mistakes to users
- Zero manual intervention

**Complexity Reduction:** No more failed queries—agents fix them

---

#### 4. **Schema Learning Agent** (New: Exploration)
**Today:** Assume user knows schema  
**Tomorrow:** Discover schema dynamically
- Connect to any database
- Scan table structures
- Analyze relationships (foreign keys, patterns)
- Build semantic schema map
- Suggest relevant tables/columns
- Use learned schema for better SQL generation

**Benefits:**
- Work with unknown databases instantly
- Suggest smart queries ("You could join X to Y")
- Understand domain-specific patterns
- Reduce user exploration time

**Complexity Reduction:** No need for manual schema documentation

---

#### 5. **Optimization Agent** (New: Performance)
**Today:** Return results as-is  
**Tomorrow:** Optimize working queries
- Analyze query execution plan
- Identify bottlenecks
- Suggest optimizations (indexes, rewrite)
- Show before/after performance comparison
- Explain trade-offs
- Educate users on query tuning

**Benefits:**
- Make queries faster automatically
- Teach query optimization
- Show execution plans visually
- Recommend best practices

**Complexity Reduction:** Users learn optimization while system optimizes

---

### Why Agentic Patterns?

| Capability | v1.0 (Today) | v2.0+ (Agentic) |
|-----------|-------------|-----------------|
| **Self-validation** | ❌ User validates | ✅ Agent validates in loop |
| **Error recovery** | ❌ User fixes | ✅ Agent auto-fixes |
| **Test coverage** | ❌ Manual cases | ✅ Agent-generated diverse cases |
| **Schema discovery** | ❌ Assume known | ✅ Agent learns dynamically |
| **Performance tuning** | ❌ Results only | ✅ Agent optimizes + explains |
| **User education** | ❌ No explanations | ✅ Agent teaches best practices |
| **Confidence** | ⚠️ Medium | ✅ High (multi-turn validation) |
| **Autonomy** | ❌ Manual intervention | ✅ Self-healing |

### Implementation Timeline

**Q3 2026:** SQL Generation Agent + Test Generation Agent  
**Q4 2026:** Query Debugging Agent  
**2027 H1:** Schema Learning Agent  
**2027 H2:** Optimization Agent + Multi-agent orchestration  

### Technology Stack (Agentic Era)

- **Agentic Framework:** Claude SDK with tool calling + multi-turn loops
- **Tools:** SQL parser, query executor, schema analyzer, test runner
- **Orchestration:** Agent composition patterns (sequential, parallel, conditional)
- **Reliability:** Automatic retries, fallbacks, confidence scoring
- **Cost Control:** Token budgets per agent, caching for repeated analysis

### Developer Experience (Agentic Era)

```typescript
// v2.0: Agentic query pipeline
const result = await queryEngine.executeWithAgents({
  query: "Show revenue by region",
  database: "postgresql",
  options: {
    refineSql: true,        // SQL refinement agent
    generateTests: true,    // Test generation agent
    optimizeQuery: true,    // Query optimization agent
    explainSteps: true      // Educational explanations
  }
});

// Returns
{
  sql: "...",
  explanation: "This query groups orders by region...",
  tests: [...],
  coverage: 87,
  performance: { before: "2.3s", after: "0.8s", optimizations: [...] },
  confidence: 0.98          // Multi-turn validation confidence
}
```

### No Breaking Changes

- v1.0 API remains unchanged
- Agentic features are **opt-in** (`refineSql: true`)
- Deterministic mode still available for production pipelines
- Backward compatible with existing integrations

---

## Support & Feedback

- **Issues:** [GitHub Issues](https://github.com/version-1-com/queryengine/issues)
- **Documentation:** See `docs/` folder
- **Product Spec:** [PRD.md](./PRD.md)
- **Code Standards:** [GUARDRAILS.md](./GUARDRAILS.md)

---

## License

MIT License - See LICENSE file

---

## Acknowledgments

Built with:
- **Claude API** by Anthropic
- **FastAPI** by Sebastián Ramírez
- **React** by Facebook
- **Tailwind CSS** by Tailwind Labs

---

**Version:** 1.0.0  
**Last Updated:** 2026-07-15  
**Status:** Production Ready
