# 🚀 Quick Start Guide - Banking CRM Agentic AI

**TL;DR**: Get the system running in 15 minutes!

---

## ⚡ 60-Second Overview

This is an **LLM-powered Banking CRM system** that:
- 🧠 Understands what you're asking
- 🎯 Automatically selects the right tools
- 👥 Identifies high-value OR low-value customers
- 💬 Generates personalized recommendations
- ⚡ Responds in 2-5 seconds

**Example Queries**:
- "Find high-value customers for premium offers" → Analyzes top customers, recommends products
- "Find customers to recover" → Identifies at-risk customers, suggests retention strategies

---

## ✅ Prerequisites (5 minutes)

### Required Software
```bash
# Check Python 3.13+
python --version

# Check PostgreSQL 17
psql --version

# Check Ollama running
curl http://localhost:11434/api/tags
```

### If Missing
1. **Python**: Download from python.org
2. **PostgreSQL**: Download and install
3. **Ollama**: Download from ollama.ai (includes llama2 model)

---

## 📦 Installation (5 minutes)

### Step 1: Clone Repository
```bash
cd C:\Users\hm255038\OneDrive - Teradata Corporation\Desktop
git clone <your-repo-url> banking-crm-ai
cd banking-crm-ai
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Database
```bash
# Start PostgreSQL
psql -U postgres

# Run in psql:
CREATE DATABASE mydb;
\q

# Initialize tables (from SETUP.md or use provided script)
python mcp_server/config/database.py
```

---

## 🚀 Launch (3 minutes)

### Terminal 1: Start PostgreSQL
```bash
# Already running from installation
```

### Terminal 2: Start MCP Server (Tools)
```bash
cd mcp_server
python main.py
# Should show: "Server running on 0.0.0.0:8000"
```

### Terminal 3: Start Ollama
```bash
ollama serve
# Should show: "Listening on 127.0.0.1:11434"
```

### Terminal 4: Run Agent
```bash
cd langgraph_agent
python main.py
# Enter queries at the prompt
```

---

## 🎯 Try These Queries

### Test 1: High-Value Customers
```
Query: Find high-value customers for premium loan offers
Expected: 10 customers with scores 70+, personalized offers
Time: 4-5 seconds
```

### Test 2: Low-Value Customers
```
Query: Find least value customers for recovery strategies
Expected: 10 customers with scores <50, retention strategies
Time: 2-3 seconds
```

### Test 3: Specific Analysis
```
Query: Analyze transaction patterns for our top customers
Expected: Detailed transaction analysis, product recommendations
Time: 3-4 seconds
```

### Test 4: Natural Language
```
Query: Which customers should we focus on to improve retention?
Expected: At-risk customers with recovery strategies
Time: 2-3 seconds
```

---

## 📊 Expected Output Format

```
📍 Step 1: Analyzing intent...
  ✓ Mode: 🧠 LLM-Based Agentic AI
  ✓ Tools: identify_prospects, analyze_transactions, ...

📍 Step 2: Executing tools...
  ✓ Identified 10 high-value prospects
  ✓ Analyzed 2 customers with 5 transactions
  ✓ Calculated conversion scores
  ✓ Retrieved product recommendations
  ✓ Generated outreach messages

📍 Step 3: Generating response...
[Natural language response from LLM explaining findings and recommendations]
```

---

## ✅ Verification Checklist

Run this to verify everything works:

```bash
# 1. Check Python env
python --version
pip list | grep -E "(fastapi|langchain|ollama)"

# 2. Check PostgreSQL
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname = 'mydb';"

# 3. Check Ollama
curl http://localhost:11434/api/tags | findstr "llama2"

# 4. Check MCP Server
curl http://0.0.0.0:8000/health

# 5. Run test query
python langgraph_agent/main.py
# Enter: "Find high-value customers"
```

**All checks green?** ✅ You're ready!

---

## 🛠️ Troubleshooting (1 minute)

| Issue | Solution |
|-------|----------|
| "psql: command not found" | PostgreSQL not installed. Download from postgresql.org |
| "ModuleNotFoundError: No module named 'langchain'" | Run `pip install -r requirements.txt` |
| "Connection refused on 11434" | Ollama not running. Run `ollama serve` in terminal |
| "Connection refused on 8000" | MCP server not running. Run `python mcp_server/main.py` |
| "Database 'mydb' does not exist" | Create database: `createdb mydb` |
| "Query timeout" | LLM taking long. Check Ollama is running smoothly |

---

## 📚 Learn More

| Topic | File |
|-------|------|
| Full Installation | [SETUP.md](SETUP.md) |
| System Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| How to Use Agent | [langgraph_agent/CONVERSATIONAL_README.md](langgraph_agent/CONVERSATIONAL_README.md) |
| LLM Configuration | [langgraph_agent/LLM_README.md](langgraph_agent/LLM_README.md) |
| Publishing to GitHub | [GITHUB_SETUP.md](GITHUB_SETUP.md) |
| Complete Docs | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

---

## 🎯 What's Happening Behind the Scenes?

```
User Types:
"Find high-value customers"
        ↓
[Intent Analyzer] → Detects: "high-value" intent
        ↓
[Tool Router] → Selects: identify_prospects, 
                         analyze_transactions,
                         calculate_scores, etc.
        ↓
[Tool Executor] → Calls MCP server tools
        ↓
[LLM Response] → Generates natural language response
        ↓
User Sees:
"I found 10 high-value customers. Customer 3 (John Doe,
score: 78.6) is best for premium loan offers..."
```

---

## 🎯 Key Commands

```bash
# Activate environment
.venv\Scripts\activate

# Start MCP Server
cd mcp_server && python main.py

# Start Agent
cd langgraph_agent && python main.py

# Stop server
taskkill /F /PID <PID>

# View database
psql -U postgres -d mydb -c "SELECT COUNT(*) FROM customers;"

# Check all services
python langgraph_agent/main.py
# (Type "health" and press Enter)
```

---

## 💡 Pro Tips

1. **Multiple Queries**: The agent remembers context in one session
2. **Natural Language**: Ask however you want - "at-risk customers", "recovery candidates", etc.
3. **Service Check**: If things slow down, verify:
   - PostgreSQL still running
   - Ollama still responding
   - MCP server still accessible

4. **Debugging**: Check terminal output for which tools were selected

---

## 🎉 You're Ready!

Your Banking CRM Agentic AI system is now running. Go ahead and ask it questions!

### Next Steps:
1. ✅ Run test queries above
2. ✅ Verify outputs match expected format
3. ✅ Explore different query types
4. ✅ Check ARCHITECTURE.md for deeper understanding
5. ✅ Follow GITHUB_SETUP.md to publish

---

## 📞 Need Help?

1. Check the relevant documentation file (see "Learn More" above)
2. Review SETUP.md for detailed troubleshooting
3. Check terminal output for error messages
4. Verify all services are running (PostgreSQL, Ollama, MCP Server)

---

**Enjoy! 🚀**

*Ready in 15 minutes. Powerful for years.*
