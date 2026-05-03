# 🔧 Setup & Installation Guide

Complete step-by-step guide to set up the Banking CRM Agentic AI system.

## Prerequisites

- **Python**: 3.13.7 or higher
- **PostgreSQL**: 17 or higher
- **Ollama**: Latest version
- **Git**: For version control
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: 10GB for models and database

## System-Specific Setup

### Windows 10/11

#### Step 1: Install Python 3.13.7

1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Choose "Install Now"
5. Verify installation:
```bash
python --version
# Python 3.13.7
```

#### Step 2: Install PostgreSQL 17

1. Download from [postgresql.org](https://www.postgresql.org/download/)
2. Run installer
3. Keep default port `5432`
4. Set password for `postgres` user
5. Verify:
```bash
psql --version
# psql (PostgreSQL) 17.0
```

#### Step 3: Create Database

```bash
# Open PowerShell as Administrator
psql -U postgres

# In psql prompt:
CREATE DATABASE mydb;
\q

# Verify:
psql -U postgres -d mydb -c "SELECT 1;"
```

#### Step 4: Install Ollama

1. Download from [ollama.ai](https://ollama.ai)
2. Install and run
3. Download llama2 model:
```bash
ollama pull llama2
# Wait for 3.8GB download to complete
```

#### Step 5: Clone Repository

```bash
# Choose a directory
cd C:\Users\YourUsername\Desktop

# Clone (if you have a GitHub repo)
git clone https://github.com/yourusername/banking-crm-agentic-ai.git
cd banking-crm-agentic-ai

# Or create locally
mkdir banking-crm-agentic-ai
cd banking-crm-agentic-ai
git init
```

#### Step 6: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Update pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected output**:
```
Successfully installed fastapi-0.109.0 langchain-0.0.x langgraph-0.2.0 ...
```

#### Step 7: Verify Installation

```bash
# Check all packages
pip list | findstr "fastapi|langchain|langgraph|pg8000"

# Test imports
python -c "import fastapi, langchain, langgraph, pg8000; print('All packages OK!')"
```

---

### macOS/Linux

#### Step 1-4: Similar to Windows (use brew on macOS)

```bash
# macOS using Homebrew
brew install python@3.13 postgresql ollama

# Linux (Ubuntu/Debian)
sudo apt-get install python3.13 postgresql postgresql-client
# Download Ollama from ollama.ai
```

#### Step 5-7: Same as Windows

```bash
cd ~/Desktop/banking-crm-agentic-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Project Directory Structure

Create this structure in your project root:

```
banking-crm-agentic-ai/
│
├── mcp_server/
│   ├── main.py                 # FastAPI server (CREATE THIS)
│   ├── config/
│   │   └── database.py         # DB connection (CREATE THIS)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── customer_repo.py    # (CREATE THIS)
│   │   ├── transaction_repo.py # (CREATE THIS)
│   │   ├── loan_repo.py        # (CREATE THIS)
│   │   └── product_repo.py     # (CREATE THIS)
│   ├── tools/
│   │   └── crm_tools.py        # (CREATE THIS)
│   └── requirements.txt
│
├── langgraph_agent/
│   ├── main.py                 # Interactive mode (CREATE THIS)
│   ├── conversational_agent.py # Main agent (CREATE THIS)
│   ├── agent.py               # LangGraph (CREATE THIS)
│   ├── state.py               # State definition (CREATE THIS)
│   ├── llm_config.py          # LLM setup (CREATE THIS)
│   ├── CONVERSATIONAL_README.md
│   └── LLM_README.md
│
├── ARCHITECTURE.md             # (CREATE THIS)
├── README.md                   # (CREATE THIS)
├── SETUP.md                    # (THIS FILE)
├── requirements.txt            # Main dependencies
└── .gitignore
```

---

## Verify Database Setup

```bash
# Connect to database
psql -U postgres -d mydb

# Check if tables exist (should be empty initially)
\dt

# Exit
\q
```

---

## Start All Services

**Terminal 1: Start Ollama**
```bash
ollama serve
# Output: Ollama is running on http://localhost:11434
```

**Terminal 2: Start MCP Server**
```bash
cd mcp_server
python main.py
# Output: INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3: Test Agent**
```bash
# Activate venv first
.venv\Scripts\activate

# Run agent
python -c "
from langgraph_agent.conversational_agent import ConversationalCRMAgent

agent = ConversationalCRMAgent()
query = 'Find high-value customers for personal loans'
agent.process_query(query)
"
```

---

## Verification Checklist

- [ ] Python 3.13.7 installed
- [ ] PostgreSQL database created and accessible
- [ ] Ollama installed and llama2 model downloaded
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] MCP Server starts without errors (port 8000)
- [ ] Ollama service running (port 11434)
- [ ] Agent can process queries successfully
- [ ] Database connection working

---

## Troubleshooting

### Issue: "pg8000 module not found"
```bash
# Solution
pip install pg8000
```

### Issue: "Connection refused" on port 8000
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID {PID} /F

# Then restart MCP server
```

### Issue: "Ollama connection error"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Issue: "PostgreSQL connection refused"
```bash
# Verify PostgreSQL is running
# Windows: Check Services > PostgreSQL
# macOS: brew services list | grep postgres
# Linux: sudo systemctl status postgresql

# Verify database exists
psql -U postgres -d mydb -c "SELECT 1;"
```

### Issue: "Module import errors"
```bash
# Ensure venv is activated
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

---

## Performance Optimization

### Enable Query Caching
```sql
-- In PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
SELECT pg_reload_conf();
```

### Optimize Ollama
```bash
# Increase GPU memory (if available)
ollama run llama2 --gpu true
```

---

## Development Workflow

### 1. Activate Environment (Every Terminal Session)
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. Run Tests
```bash
# Test MCP Server
curl http://localhost:8000/health

# Test Ollama
curl http://localhost:11434/api/tags

# Test Agent
python -c "from langgraph_agent.conversational_agent import ConversationalCRMAgent; print('Agent OK')"
```

### 3. Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG  # Linux/macOS
set LOG_LEVEL=DEBUG     # Windows

# Run agent with detailed output
python langgraph_agent/main.py
```

---

## Configuration Files

### .env (Optional)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb
OLLAMA_HOST=http://localhost:11434
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO
```

### .gitignore
```
.venv/
__pycache__/
*.pyc
.env
.DS_Store
*.log
```

---

## Next Steps

1. ✅ Complete setup from this guide
2. 📖 Read [README.md](./README.md) for overview
3. 🏗️ Study [ARCHITECTURE.md](./ARCHITECTURE.md) for design
4. 💬 Review [CONVERSATIONAL_README.md](./langgraph_agent/CONVERSATIONAL_README.md) for usage
5. 🧠 Check [LLM_README.md](./langgraph_agent/LLM_README.md) for LLM details

---

## Support

If you encounter issues:
1. Check troubleshooting section above
2. Verify all services are running
3. Check logs in terminals for error messages
4. Ensure all prerequisites are installed

---

**Status**: ✅ Setup Complete  
**Last Updated**: May 2026
