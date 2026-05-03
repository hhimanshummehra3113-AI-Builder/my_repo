# 🤖 Conversational Banking CRM Agent

## Overview

The **Conversational Banking CRM Agent** is an intelligent, intent-aware AI system that processes natural language queries and dynamically routes to the most relevant CRM tools. Unlike traditional hardcoded workflows, it understands user intent and optimally selects which tools to execute.

**Key Innovation**: Users can now ask questions in natural language, and the agent figures out what data and analysis is needed - no rigid workflows!

## Architecture

### Components

1. **Intent Analyzer**
   - Uses LLM (when available) or heuristic keyword matching
   - Detects user intent and determines required tools
   - Assigns confidence score to the detected intent

2. **MCPClient (HTTP-based Tool Caller)**
   - Communicates with MCP Server via HTTP API
   - Handles nested response structures
   - Gracefully manages errors

3. **Tool Executor**
   - Runs tools in optimal order
   - Limits results (top 5 customers) to avoid performance issues
   - Handles missing/incomplete data gracefully

4. **Response Generator**
   - Uses LLM for natural language responses (when available)
   - Falls back to heuristic formatting
   - Directly answers the user's query

### Tools Available

| Tool | Purpose | When Used |
|------|---------|-----------|
| `identify_prospects` | Find high-value customers | Keywords: find, identify, list, who, prospects |
| `analyze_transactions` | Examine transaction patterns | Keywords: analyze, examine, pattern, stability |
| `conversion_score` | Calculate conversion probability | Keywords: convert, score, likelihood, probability |
| `recommended_products` | Get eligible loan products | Keywords: recommend, product, loan, eligible |
| `generate_message` | Create personalized outreach | Keywords: generate, message, outreach, personalize |

## Usage

### Mode 1: Interactive Mode (Recommended)
```bash
cd practice_mcp
python langgraph_agent/main.py
# Select option 2: CONVERSATIONAL
# Enter natural language queries at the prompt
```

### Mode 2: Programmatic Usage
```python
from langgraph_agent.conversational_agent import ConversationalCRMAgent

agent = ConversationalCRMAgent()
agent.process_query("Find high-value customers for personal loan outreach")
```

### Mode 3: With Custom Configuration
```python
from langgraph_agent.conversational_agent import ConversationalCRMAgent

agent = ConversationalCRMAgent()

# Store multiple responses
agent.process_query("Identify premium customers")
agent.process_query("Show me conversion scores")
agent.process_query("Generate outreach messages")

# Access conversation history
for context in agent.conversation_history:
    print(f"Query: {context.user_query}")
    print(f"Response: {context.final_response}")
```

## Example Queries

### Example 1: Comprehensive Analysis with Messages
```
Input: "Find high-value customers likely to convert for a personal loan this month and generate personalized messages"

Agent Flow:
  1. Detects intent: identify_prospects (80% confidence)
  2. Identifies required tools: identify_prospects, recommended_products, 
     generate_message, conversion_score
  3. Executes tools:
     - Identifies 10 high-value prospects
     - Analyzes 5 of them in detail
     - Gets conversion scores
     - Retrieves recommended products
     - Generates personalized messages
  4. Compiles response with all insights

Output:
📊 Found 10 high-value prospects
  • Customer 3: 78.6/100 (High)
  • Customer 17: 77.2/100 (High)
  ...

💼 Analyzed 5 customers with personalized recommendations
```

### Example 2: Transaction-Focused Analysis
```
Input: "Analyze transaction patterns for premium customers and recommend auto loans"

Agent Flow:
  1. Detects intent: analyze_customer (90% confidence)
  2. Identifies required tools: identify_prospects, analyze_transactions, 
     recommended_products
  3. Only executes selected tools (skips generate_message and conversion_score)
  4. Returns analysis focused on transaction stability and product eligibility

Output:
(Only tools relevant to the query are executed - more efficient!)
```

### Example 3: Simple Prospect List
```
Input: "Show me the top conversion prospects"

Agent Flow:
  1. Detects intent: identify_prospects
  2. Calls only identify_prospects tool
  3. Returns list without unnecessary analysis

Output:
(Quick, focused response - minimal tool execution)
```

## How Intent Detection Works

### Using LLM (When Ollama is Ready)
The agent sends this prompt to Ollama:
```
Analyze this banking CRM query and determine required tools:
Query: "Find high-value customers likely to convert for a personal loan..."
[LLM analyzes and returns tool recommendations]
```

### Using Heuristic Fallback (Current Mode)
The agent scans for keywords:
- "find", "identify" → `identify_prospects`
- "analyze", "transaction", "pattern" → `analyze_transactions`
- "recommend", "product", "loan" → `recommended_products`
- "generate", "message", "outreach" → `generate_message`
- "convert", "score", "likelihood" → `conversion_score`

## Response Generation

### LLM-Powered (Preferred)
When Ollama is available:
1. Summarizes tool results
2. Sends to LLM with user query context
3. Generates natural, insightful response
4. Directly answers the user's question

### Heuristic Fallback (Current)
Automatically used when LLM unavailable:
1. Formats results into readable sections
2. Highlights key metrics and insights
3. Provides structured, clear output
4. No LLM latency

## Data Flow Diagram

```
User Query
    ↓
[Intent Analyzer] → Detects intent & selects tools
    ↓
[Tool Executor] → Calls relevant MCP tools via HTTP
    ├─ identify_prospects
    ├─ analyze_transactions
    ├─ conversion_score
    ├─ recommended_products
    └─ generate_message
    ↓
[Response Generator] → Synthesizes results into answer
    ├─ LLM Enhancement (if available)
    └─ Heuristic Fallback
    ↓
Natural Language Response to User
```

## Current Status

✅ **Fully Functional**
- Intent detection: Heuristic + LLM-ready
- Tool execution: All 5 tools working
- Response generation: Heuristic fallback active
- HTTP communication: Stable and robust

⏳ **Awaiting LLM Enhancement**
- Ollama model (llama2) downloading
- Once ready: LLM will handle intent analysis and response generation
- Expected improvement: More natural, context-aware responses

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Intent Detection | ~100ms (heuristic) |
| Tool Execution (5 customers) | ~2-5s |
| Response Generation | ~100ms (heuristic) |
| **Total Query Time** | **~3-6s** |

## Error Handling

The agent gracefully handles:
- ✅ Missing tool results
- ✅ Incomplete customer data
- ✅ Tool execution failures
- ✅ Network timeouts
- ✅ Invalid responses
- ✅ LLM unavailability

## Future Enhancements

1. **Multi-turn Conversations**: Remember previous queries in same session
2. **Follow-up Questions**: "Tell me more about Customer 3"
3. **Parameter Extraction**: "Find customers with income > 500k"
4. **Explanation Mode**: "Why are these customers recommended?"
5. **Batch Queries**: "Process this list of 50 customers"

## Troubleshooting

### "MCP Server is NOT running"
```bash
cd mcp_server
python main.py  # In another terminal
```

### "Ollama is NOT running"
```bash
ollama serve  # In another terminal
```

### "Ollama call failed with status code 404"
```bash
ollama pull llama2  # Pull the model (one-time)
```

### Agent returns empty results
- Check MCP server logs for tool execution errors
- Verify database has customer data (should have 25+ customers)
- Ensure PostgreSQL is running

## Architecture Notes

**Why HTTP instead of direct imports?**
- Avoids Python path issues when importing MCP tools
- Clean separation between agent and tool layers
- Makes agent stateless and scalable
- Supports multiple languages/frameworks for agents

**Why heuristic fallback?**
- Agent works immediately without LLM
- No dependency on Ollama availability
- Instant processing for simple queries
- LLM used for enhancement, not requirement

## Next: Try It Now!

```bash
# Run the interactive agent
python langgraph_agent/main.py
```

Then ask questions like:
- "Find high-value customers for personal loans"
- "Show me customers with stable transaction histories"
- "Generate outreach messages for auto loan customers"
- "Identify premium segment prospects"
