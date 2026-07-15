# QueryEngine - Database Configuration Guide

QueryEngine is **database-agnostic**. Switch from SQLite to PostgreSQL, MySQL, AWS RDS, Azure Database, Oracle, or even NoSQL with a single configuration change.

## Quick Switch: Change One Line

All database configuration lives in one place:

```bash
backend/.env
```

**Current (SQLite):**
```env
DATABASE_URL=sqlite:///./queryengine.db
```

Change the `DATABASE_URL` value, install the driver, and restart. That's it.

---

## Database Options & Connection Strings

### 1. **SQLite** (Default - No Setup Needed)

**Best for:** Local development, prototyping, small deployments

```env
DATABASE_URL=sqlite:///./queryengine.db
```

**Why:** No server required. Queries run against local file. Perfect for demos.

---

### 2. **PostgreSQL** (Production-Ready)

**Best for:** Most production deployments, excellent for analytics queries

**Local PostgreSQL:**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/queryengine
```

**Install driver:**
```bash
pip install psycopg2-binary
```

---

### 3. **AWS RDS for PostgreSQL**

**Best for:** AWS-hosted production, managed backups, auto-scaling

1. Create RDS instance via AWS Console (PostgreSQL engine)
2. Get endpoint: `your-instance.xxxx.us-east-1.rds.amazonaws.com`
3. Set in `.env`:

```env
DATABASE_URL=postgresql://admin:your-password@your-instance.xxxx.us-east-1.rds.amazonaws.com:5432/queryengine
```

**Install driver:**
```bash
pip install psycopg2-binary
```

**SSL Connection (Recommended):**
```env
DATABASE_URL=postgresql://admin:password@instance.rds.amazonaws.com:5432/queryengine?sslmode=require&sslrootcert=rds-ca-bundle.pem
```

---

### 4. **Azure Database for PostgreSQL**

**Best for:** Azure-hosted, integrated with Azure services, managed backups

1. Create "Azure Database for PostgreSQL" resource
2. Get connection details from Azure Portal
3. Set in `.env`:

```env
DATABASE_URL=postgresql://admin-user@servername:password@servername.postgres.database.azure.com:5432/queryengine
```

**Install driver:**
```bash
pip install psycopg2-binary
```

**SSL Connection (Required for Azure):**
```env
DATABASE_URL=postgresql://admin@servername:password@servername.postgres.database.azure.com:5432/queryengine?sslmode=require
```

---

### 5. **Azure SQL Database** (T-SQL)

**Best for:** Azure environments, MS SQL Server integration

1. Create "SQL Database" resource in Azure
2. Get connection string from Portal
3. Set in `.env`:

```env
DATABASE_URL=mssql+pyodbc://admin:password@servername.database.windows.net:1433/queryengine?driver=ODBC+Driver+17+for+SQL+Server
```

**Install drivers:**
```bash
pip install pyodbc
# On Windows: ODBC Driver 17 for SQL Server (from Microsoft)
# On Linux: sudo apt install unixodbc-dev odbc-mssql
```

---

### 6. **MySQL / MariaDB**

**Best for:** Existing MySQL environments, WordPress integrations

**Local MySQL:**
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/queryengine
```

**AWS RDS for MySQL:**
```env
DATABASE_URL=mysql+pymysql://admin:password@instance.xxxx.us-east-1.rds.amazonaws.com:3306/queryengine
```

**Install driver:**
```bash
pip install pymysql
```

---

### 7. **Oracle Database**

**Best for:** Enterprise environments, existing Oracle systems

```env
DATABASE_URL=oracle+cx_oracle://user:password@localhost:1521/ORCL
```

**Install driver:**
```bash
pip install cx_Oracle
# Download Oracle Instant Client from Oracle website
```

---

### 8. **MongoDB Atlas** (NoSQL)

**Best for:** Document-based queries, flexible schema, cloud-native

Currently, QueryEngine generates SQL queries. MongoDB support requires:
- MongoEngine ORM wrapper OR
- Custom MongoDB adapter

**For now, use MongoDB with a SQL-to-MongoDB translator (future enhancement).**

---

## How to Change Database

### Step 1: Update `.env`

```bash
cd backend
nano .env  # or edit with your editor
```

Change:
```env
DATABASE_URL=postgresql://user:password@host:port/db
```

### Step 2: Install Database Driver

```bash
pip install psycopg2-binary  # for PostgreSQL
# OR
pip install pymysql  # for MySQL
# OR
pip install pyodbc  # for SQL Server
```

### Step 3: Restart Backend

```bash
python -m uvicorn main:app --reload
```

The app will:
- ✅ Connect to new database
- ✅ Create tables if they don't exist
- ✅ Seed sample data on first run

---

## Behind the Scenes: How It Works

### Configuration Loading

**File:** `backend/config.py`

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./queryengine.db"
    # ^ Single source of truth
```

The app reads `DATABASE_URL` from `.env` using Pydantic. No hardcoded URLs anywhere.

### SQLAlchemy Abstraction

**File:** `backend/services/database.py`

```python
engine = create_engine(
    settings.DATABASE_URL,  # <- Works with any database
    echo=False,
    pool_pre_ping=True
)
```

SQLAlchemy translates SQL to the target database dialect:
- SQLite → `SELECT * FROM ...`
- PostgreSQL → `SELECT * FROM ...` (with RETURNING for advanced features)
- MySQL → `SELECT * FROM ...` (with backticks for reserved words)
- SQL Server → `SELECT * FROM [...]` (with brackets)
- Oracle → Works with synonyms and schemas

**No code changes needed.** Same SQL, different backend.

---

## Recommended Setups by Use Case

### Local Development
```env
DATABASE_URL=sqlite:///./queryengine.db
```
✅ No setup. Works immediately. Easy debugging.

### Small Team / Testing
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/queryengine
```
✅ Run local PostgreSQL via Docker:
```bash
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
```

### Production (AWS)
```env
DATABASE_URL=postgresql://admin:password@instance.rds.amazonaws.com/queryengine?sslmode=require
```
✅ Managed service. Auto-backups. Scaling built-in.

### Production (Azure)
```env
DATABASE_URL=postgresql://admin@server:password@server.postgres.database.azure.com/queryengine?sslmode=require
```
✅ Native Azure integration. AAD auth possible.

### Enterprise (Existing Oracle)
```env
DATABASE_URL=oracle+cx_oracle://user:password@host:1521/ORCL
```
✅ Use existing database. No migration needed.

---

## Connection Pooling & Performance

SQLAlchemy automatically manages connection pooling:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,           # Connections to keep open
    max_overflow=20,        # Extra connections if needed
    pool_pre_ping=True      # Verify connections are alive
)
```

For high traffic, adjust in `config.py`:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
)
```

---

## Troubleshooting

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Connection refused"
- Check DATABASE_URL is correct
- Verify database server is running
- Check firewall/security groups allow connection

### "Authentication failed"
- Verify username/password
- Check user has permission on database

### "Timezone error" (PostgreSQL)
Add to connection string:
```env
DATABASE_URL=postgresql://user:pass@host/db?options=-c%20timezone=UTC
```

---

## Demo Strategy: "Plug & Use Any Database"

**Messaging:**
> "QueryEngine connects to any SQL database. PostgreSQL, MySQL, Oracle, AWS RDS, Azure SQL, or keep it simple with SQLite. Change one line in config. No code changes. Same API, different backend."

**Demo Flow:**
1. **Start with SQLite** (instant, no setup)
   ```env
   DATABASE_URL=sqlite:///./queryengine.db
   ```
   → Show it works

2. **Switch to PostgreSQL** (10 seconds)
   ```bash
   # Change .env and restart
   DATABASE_URL=postgresql://localhost/queryengine
   ```
   → Same app, different database

3. **Show AWS RDS string** (same logic, cloud scale)
   ```env
   DATABASE_URL=postgresql://admin:pass@instance.rds.amazonaws.com/queryengine
   ```
   → Point out: only line 8 changes

**Talking Points:**
- ✅ No vendor lock-in
- ✅ Works with your existing database
- ✅ Scale from local to cloud in minutes
- ✅ Same SQL generation, same AI features
- ✅ Perfect for proof-of-concepts → production migration

---

## Next: Add Database to UI

For future versions, add a "Configure Database" page:
1. Dropdown: SQLite | PostgreSQL | MySQL | RDS | Azure | Oracle
2. Input fields: host, port, username, password, database
3. "Test Connection" button
4. Save to backend `.env`

This makes QueryEngine a true "plug & play" platform.

