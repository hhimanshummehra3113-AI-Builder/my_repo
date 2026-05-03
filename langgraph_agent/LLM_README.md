# 🤖 LLM-Powered Banking CRM Agent with Ollama + LangGraph

A sophisticated agentic AI system that leverages Ollama (local LLM) and LangGraph to intelligently identify high-value customers and generate personalized loan product recommendations with ReAct-style reasoning.

## 🎯 Key Capabilities

### ✨ LLM-Powered Reasoning
- **Ollama Integration**: Uses local Llama2 model for intelligent decision-making
- **ReAct-Style Agent**: Reason, Act, Observe loop with LLM guidance
- **Dynamic Decision Making**: LLM decides what to analyze and when
- **Intelligent Interpretation**: LLM analyzes tool outputs and generates insights

### 🔧 MCP Tool Integration
Seamlessly orchestrates 6 specialized tools via HTTP:
- `identify_high_value_prospects` - Find top customers
- `calculate_conversion_score` - Multi-factor scoring
- `analyze_transactions` - Pattern analysis with stability metrics
- `get_recommended_products` - Product eligibility matching
- `generate_outreach_message` - Template-based personalization
- `get_customer_profile` - Complete customer context

### 📊 State Management
- **Structured AgentState**: Tracks all execution context
- **Thought Logging**: Records agent reasoning and LLM insights
- **Execution Metrics**: Monitors iterations, tools called, and results

## 🏗️ Architecture

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│                    User Request                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   LangGraph StateGraph Agent   │
        │     (5 Processing Nodes)       │
        └────────────────┬───────────────┘
                         │
        ┌────────────────┴──────────────┐
        │                               │
        ▼                               ▼
  ┌─────────────┐              ┌──────────────┐
  │ Ollama LLM  │              │ MCP Server   │
  │ (Reasoning) │              │ (Tools)      │
  └─────────────┘              └──────────────┘
        │                               │
        │      PostgreSQL Database      │
        └───────────────┬───────────────┘
                        │
            ┌───────────┴──────────────┐
            ▼                          ▼
        Customers              Transactions
```

### Agent Nodes (5-Node Pipeline)

#### 1. **plan_node** 🎯
- **Role**: Initial strategy planning
- **LLM Input**: User query + available tools
- **LLM Output**: Which tool to call first
- **State Update**: Thoughts, next_node decision
- **Example**: "Should we identify prospects first or get specific customer profiles?"

#### 2. **identify_prospects_node** 🔍
- **Role**: Find high-value customers
- **MCP Call**: `identify_high_value_prospects()`
- **LLM Analysis**: Interpret results and identify patterns
- **Output**: Top 10 customers with conversion scores
- **Reasoning**: "We found 10 prospects, 2 with immediate priority"

#### 3. **analyze_customers_node** 📈
- **Role**: Deep customer analysis
- **MCP Calls**: 
  - `calculate_conversion_score(customer_id)` 
  - `analyze_transactions(customer_id, months=6)`
- **LLM Interpretation**: 
  - Assess each customer's potential
  - Identify patterns
  - Determine next steps
- **Output**: Detailed profiles of top 5 customers
- **Reasoning**: "High conversion score + stable transactions = strong candidate"

#### 4. **generate_recommendations_node** 💡
- **Role**: Product matching and message optimization
- **MCP Calls**:
  - `get_recommended_products(customer_id)`
  - `generate_outreach_message(customer_id, product_id)`
- **LLM Optimization**:
  - Select best product from options
  - Enhance outreach messages
  - Personalize tone and content
- **Output**: 3 personalized recommendations
- **Reasoning**: "This product's 8% rate is better than competitors"

#### 5. **finalize_node** 📋
- **Role**: Summary and reporting
- **LLM Generation**: Create executive summary
- **Output**: Final report with insights
- **Metrics**: Campaign overview with key stats

## 🔄 Execution Flow

```
User Query
    │
    ├─→ [plan_node] ─→ LLM decides: "Identify prospects first"
    │
    ├─→ [identify_prospects_node]
    │   ├─→ MCP: identify_high_value_prospects()
    │   ├─→ LLM: "Interpret these 10 prospects"
    │   └─→ State: customer_ids, high_value_prospects
    │
    ├─→ [analyze_customers_node]
    │   ├─→ MCP: calculate_conversion_score(1)
    │   ├─→ MCP: analyze_transactions(1, months=6)
    │   ├─→ LLM: "Assess customer's profile and potential"
    │   ├─→ (Repeat for customers 2-5)
    │   └─→ State: analyzed_customers
    │
    ├─→ [generate_recommendations_node]
    │   ├─→ MCP: get_recommended_products(1)
    │   ├─→ LLM: "Which product is best for this customer?"
    │   ├─→ MCP: generate_outreach_message(1, product_1)
    │   ├─→ LLM: "Enhance this message for better conversion"
    │   ├─→ (Repeat for customers 2-3)
    │   └─→ State: recommendations
    │
    ├─→ [finalize_node]
    │   ├─→ LLM: "Generate executive summary"
    │   └─→ State: summary
    │
    └─→ Return Results
```

## 📥 Installation & Setup

### 1. Prerequisites
```bash
# Ollama must be installed and running
# Download: https://ollama.ai

# Start Ollama
ollama serve

# Pull a model (if not already available)
ollama pull llama2  # ~4GB
```

### 2. Install Python Dependencies
```bash
cd langgraph_agent
pip install -r requirements.txt
```

### 3. Start MCP Server
```bash
cd mcp_server
python main.py
# Server running on http://localhost:8000
```

### 4. Run the Agent
```bash
cd practice_mcp
python langgraph_agent/main.py
```

## 🚀 Usage Examples

### Basic Usage
```python
from langgraph_agent.agent import run_agent

result = run_agent()
```

### Custom Query
```python
result = run_agent(
    user_query="Find premium customers with stable transaction history for auto loans"
)
```

### Access Results
```python
final_state = run_agent()

# Agent reasoning steps
print(final_state.thoughts)

# Identified customers
print(final_state.high_value_prospects)

# Detailed analysis
print(final_state.analyzed_customers)

# Final recommendations
print(final_state.recommendations)

# Summary
print(final_state.summary)
```

## 📊 Agent Output Example

```
================================================================================
🤖 LLM-Powered Banking CRM Agent Starting (Ollama + LangGraph)
================================================================================
Task: Identify high-value customers with 70+ conversion score for personal loan outreach

================================================================================
📊 Agent Execution Log (with LLM Reasoning)
================================================================================
[2026-05-02T03:15:22.123456] Agent Planning: identify_high_value_prospects
✓ Identified 10 high-value prospects. Immediate: 2, High: 5, Medium: 3
📊 LLM Analysis: These prospects show strong conversion potential. We should analyze 
   their transaction patterns to identify the most stable customers.
[2026-05-02T03:15:28.234567] Analyzing 10 customers
💭 LLM Assessment: Customer 1 has 85/100 conversion score with high stability - 
   excellent candidate for premium personal loan.
✓ Successfully analyzed 5 customers
🎯 Product Selection: Personal Loan Premium at 8% rate is optimal for this customer's 
   income level and credit profile.
✍️ Message Enhanced by LLM
✓ Generated 3 LLM-optimized recommendations

================================================================================
📋 Executive Summary
================================================================================
LLM Executive Summary:
The campaign identified 10 high-value prospects with strong conversion potential. 
After detailed analysis and LLM optimization, 3 customers received personalized 
recommendations with tailored messaging for maximum engagement.

================================================================================
💼 LLM-Optimized Recommendations
================================================================================

1. Customer ID: 1
   Conversion Score: 85.5/100 (Very High)
   Recommended Product: Personal Loan Premium
   Personalization Tier: PERSONALIZED
   LLM-Enhanced Message: Exclusive offer for Premium members - Rajesh Kumar, 
                         secure your 15 lakhs at 8% interest today...

2. Customer ID: 3
   Conversion Score: 78.2/100 (High)
   Recommended Product: Personal Loan Standard
   Personalization Tier: PERSONALIZED
   LLM-Enhanced Message: Amit Patel, qualified for personal loan up to 12 lakhs...

3. Customer ID: 5
   Conversion Score: 72.1/100 (High)
   Recommended Product: Personal Loan Standard
   Personalization Tier: PERSONALIZED
   LLM-Enhanced Message: Priya Sharma, your credit profile qualifies you for our 
                         affordable personal loan...

================================================================================
✅ Agent execution completed!
   Iterations: 5
   Tools called: 6
   LLM reasoning steps: 7
================================================================================
```

## 🧠 LLM Integration Points

### 1. **Tool Descriptions**
```python
TOOL_DESCRIPTIONS = {
    "identify_high_value_prospects": "Identifies top 10 high-value customers...",
    "calculate_conversion_score": "Calculates multi-factor conversion score...",
    ...
}
```

### 2. **LLM Prompting in Nodes**
```python
# Plan Node
prompt = "You are a Banking CRM agent. Your task is: {query}. 
          Which tool should we use first?"

# Analyze Node
prompt = "Analyze this customer's profile and provide insights on conversion potential"

# Recommendations Node
prompt = "Given these product options, which is best for this customer? Why?"

# Enhancement Node
prompt = "Improve this outreach message to make it more compelling"
```

### 3. **Response Processing**
```python
response = llm.invoke(prompt)
state.thoughts.append(f"LLM Output: {response.strip()}")
# Use LLM response to inform next steps
```

## 🔧 Configuration

### Change LLM Model
```python
# In llm_config.py
llm = get_ollama_llm(model="mistral", temperature=0.3)  # Swap "llama2" for "mistral"
```

Available Ollama models:
- `llama2` (default) - Balanced reasoning
- `mistral` - Faster responses
- `neural-chat` - Conversation-optimized
- `dolphin-mixtral` - Advanced reasoning

### Adjust Temperature
```python
llm = get_ollama_llm(model="llama2", temperature=0.1)  # More deterministic
llm = get_ollama_llm(model="llama2", temperature=0.7)  # More creative
```

## 📈 Performance Metrics

- **Total Execution Time**: ~20-30 seconds
  - Plan: 1s
  - Identify: 2s (1 DB query)
  - Analyze: 8s (10 DB queries)
  - Recommend: 12s (6 DB queries + LLM processing)
  - Finalize: 2s

- **LLM Processing**: ~5-8 seconds
  - Each LLM call: 1-2 seconds on CPU
  - 5-7 LLM invocations per run

## 🎓 Assignment Requirements Coverage

✅ **Agentic AI System**: True agent with multi-step reasoning  
✅ **LLM Integration**: Ollama with ReAct-style prompting  
✅ **State Management**: Structured AgentState with TypedDict  
✅ **Tool Orchestration**: 6 MCP tools via HTTP  
✅ **Dynamic Decision Making**: LLM decides what to do  
✅ **Banking CRM**: High-value customer identification  
✅ **Loan Outreach**: Personalized product recommendations  
✅ **Intelligent Analysis**: LLM interpretation of data  

## 🔗 Integration Points

### Ollama ↔ LangGraph
- Uses `langchain_community.llms.Ollama`
- Sends prompts via HTTP to `http://localhost:11434`
- Receives text responses for reasoning

### LangGraph ↔ MCP Server
- StateGraph with 5 connected nodes
- Each node calls MCP tools via HTTP POST
- Responses integrated into agent state

### MCP Server ↔ PostgreSQL
- All tool executions query customer database
- Transactions, products, loan history retrieved
- Results returned as JSON

## ⚠️ Troubleshooting

### "Ollama LLM not available"
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### "Cannot connect to MCP Server"
```bash
# Start MCP Server
cd mcp_server && python main.py

# Verify health
curl http://localhost:8000/health
```

### LLM Responses Too Slow
- Use smaller model: `mistral` instead of `llama2`
- Reduce `num_predict` in llm_config.py
- Reduce `temperature` for faster convergence

## 📚 Files Structure

```
langgraph_agent/
├── __init__.py              # Package initialization
├── state.py                 # AgentState dataclass
├── llm_config.py            # Ollama LLM setup
├── llm_nodes.py             # 5 processing nodes with LLM
├── agent.py                 # StateGraph & orchestration
├── main.py                  # Entry point
├── nodes.py                 # Original nodes (deprecated)
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## 🚀 Next Steps

1. ✅ Start Ollama: `ollama serve`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Start MCP Server: `python mcp_server/main.py`
4. ✅ Run agent: `python langgraph_agent/main.py`

Enjoy your LLM-powered Banking CRM Agent! 🎉
