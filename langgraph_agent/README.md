# 🏦 Banking CRM LangGraph Agent

Agentic AI system for identifying high-value customers and generating personalized loan product outreach.

## Overview

The Banking CRM Agent is a LangGraph-based multi-node agent that orchestrates the entire customer analysis and outreach pipeline:

1. **Identify Prospects**: Find high-value customers with 70+ conversion probability
2. **Analyze Customers**: Deep dive into customer profiles, stability scores, and transaction patterns
3. **Generate Recommendations**: Match customers with suitable loan products
4. **Create Outreach**: Generate personalized SMS/WhatsApp messages
5. **Finalize**: Summarize results and compile recommendations

## Architecture

### State Management

The agent uses a structured `AgentState` (TypedDict) to track:

```python
AgentState = {
    "user_query": str,                           # Initial task
    "customer_ids": List[int],                   # Customers to analyze
    "high_value_prospects": List[Dict],          # Top prospects identified
    "analyzed_customers": List[Dict],            # Detailed analysis
    "tools_called": List[str],                   # Tool usage tracking
    "tool_results": Dict,                        # Tool output storage
    "thoughts": List[str],                       # Agent reasoning
    "recommendations": List[Dict],               # Final recommendations
    "summary": str,                              # Execution summary
    "error": Optional[str],                      # Error tracking
    "next_node": str,                            # Flow control
    "iterations_count": int,                     # Execution tracking
}
```

### Agent Nodes

#### 1. **identify_prospects_node**
   - Calls MCP Server: `identify_high_value_prospects()`
   - Returns: Top 10 customers ranked by conversion score
   - Output: Customer IDs and priority tiers (IMMEDIATE/HIGH/MEDIUM)

#### 2. **analyze_customers_node**
   - Calls MCP Server:
     - `calculate_conversion_score(customer_id)` - Multi-factor scoring (0-100)
     - `analyze_transactions(customer_id, months=6)` - Stability analysis
   - Processes: Top 5 prospects for detailed analysis
   - Output: Customer profiles with conversion & stability metrics

#### 3. **generate_recommendations_node**
   - Calls MCP Server:
     - `get_recommended_products(customer_id)` - Eligible products
     - `generate_outreach_message(customer_id, product_id)` - Personalized messaging
   - Processes: Top 3 analyzed customers
   - Output: Recommendations with outreach templates

#### 4. **finalize_node**
   - Aggregates results
   - Generates executive summary
   - Compiles all recommendations
   - Output: Complete execution report

### Data Flow

```
User Query
    ↓
[identify_prospects] → Identify top 10 high-value customers
    ↓
[analyze_customers] → Deep analysis of top 5
    ↓
[generate_recommendations] → Product match + outreach for top 3
    ↓
[finalize] → Summarize and compile results
    ↓
Final Report
```

## Installation

### Prerequisites
- Python 3.10+
- MCP Server running on `http://localhost:8000`
- PostgreSQL database (populated with customer data)

### Setup

1. **Install Dependencies**
```bash
pip install -r langgraph_agent/requirements.txt
```

Or install individually:
```bash
pip install langgraph==0.0.13 langchain-core==0.1.22 requests==2.31.0
```

2. **Start MCP Server**
```bash
cd mcp_server
python main.py
```
Server will be available at `http://localhost:8000`

3. **Run the Agent**
```bash
python langgraph_agent/main.py
```

## Usage

### Basic Usage

```python
from langgraph_agent.agent import run_agent

# Run with default query
result = run_agent()
```

### Custom Query

```python
from langgraph_agent.agent import run_agent

result = run_agent(
    user_query="Find premium segment customers with stable transaction history for auto loans"
)
```

### Access Results

```python
final_state = run_agent()

# Get identified prospects
prospects = final_state.high_value_prospects

# Get detailed analysis
analyzed = final_state.analyzed_customers

# Get recommendations
recommendations = final_state.recommendations

# Get execution log
thoughts = final_state.thoughts
```

## Output Structure

### High-Value Prospects
```python
{
    "customer_id": 1,
    "name": "Rajesh Kumar",
    "email": "rajesh.kumar@gmail.com",
    "phone": "+919876543210",
    "segment": "Premium",
    "annual_income": 850000.0,
    "credit_score": 820,
    "account_tenure_months": 36,
    "conversion_score": 85.5,
    "conversion_likelihood": "Very High",
    "priority": "IMMEDIATE"
}
```

### Analyzed Customer
```python
{
    "customer_id": 1,
    "conversion_score": 85.5,
    "conversion_likelihood": "Very High",
    "stability_score": 78.3,
    "transaction_data": {
        "total_transactions_6m": 42,
        "monthly_avg": 7.0,
        "avg_transaction_amount": 25000.0,
        "stability_score": 78.3,
        "total_volume": 1050000.0
    }
}
```

### Recommendation
```python
{
    "customer_id": 1,
    "conversion_score": 85.5,
    "conversion_likelihood": "Very High",
    "recommended_product": {
        "product_id": 1,
        "product_name": "Personal Loan Premium",
        "product_type": "Personal Loan",
        "estimated_rate": 8.0,
        "tenure_months": 60,
        "recommended_amount": 170000.0,
        "monthly_emi_estimate": 3228.45
    },
    "outreach_message": "Exclusive offer for Premium members...",
    "personalization": "PERSONALIZED",
    "timestamp": "2026-05-02T02:56:22.123456"
}
```

## Configuration

### Agent Settings

Edit `langgraph_agent/agent.py` to configure:

```python
# Maximum iterations (safety limit)
max_iterations = 10

# MCP Server URL
mcp_url = "http://localhost:8000"

# Number of customers to analyze
analyze_limit = 5

# Number of recommendations to generate
recommendation_limit = 3
```

### Query Customization

The agent can handle various queries:

```python
# Personal loans for high-income earners
"Find customers earning 700k+ with conversion score 75+ for personal loans"

# Product cross-sell
"Identify existing loan customers for home loan upsell opportunities"

# Segment-based outreach
"Premium segment customers with 6-month stable transaction history for exclusive offers"

# Risk-based targeting
"Customers with default-free history and high credit scores for premium products"
```

## State Graph Visualization

```
┌─────────────────────┐
│   identify_prospects │  ← Entry Point
└──────────┬──────────┘
           │
           ↓
┌──────────────────────┐
│  analyze_customers   │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────────────────┐
│  generate_recommendations         │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────┐
│     finalize         │
└──────────┬───────────┘
           │
           ↓
         [END]
```

## Monitoring & Debugging

### Agent Execution Log

The agent prints real-time thoughts during execution:

```
[2026-05-02T02:56:10.123456] Starting high-value prospect identification
✓ Identified 10 high-value prospects. Immediate priority: 2
[2026-05-02T02:56:15.234567] Analyzing 10 customers
✓ Successfully analyzed 5 customers
[2026-05-02T02:56:25.345678] Generating recommendations
✓ Generated 3 recommendations
[2026-05-02T02:56:30.456789] Finalizing execution
✓ Banking CRM Agent Execution Complete
```

### Error Handling

If an error occurs:
- Agent logs the error in `state.error`
- Immediately transitions to `finalize` node
- Returns partial results with error information

## Integration with MCP Server

The agent communicates with the MCP Server via HTTP:

```python
POST http://localhost:8000/mcp/call

{
    "tool": "identify_high_value_prospects",
    "params": {}
}

Response:
{
    "success": true,
    "result": {
        "data": {
            "top_prospects": [...]
        }
    }
}
```

## Performance

- **Prospect Identification**: ~500ms (1 database query)
- **Customer Analysis**: ~2-3s per customer (2 queries each)
- **Recommendation Generation**: ~2-3s per customer (2 queries each)
- **Full Pipeline**: ~15-20s for top 5 prospects

## Limitations

- Currently analyzes top 5 prospects for depth
- Generates recommendations for top 3 prospects
- Maximum 10 iterations to prevent infinite loops
- Limited to product recommendations in current loan portfolio

## Future Enhancements

- [ ] Integration with actual SMS/WhatsApp delivery APIs
- [ ] Feedback loop for conversion tracking
- [ ] Machine learning-based personalization improvements
- [ ] A/B testing framework for messaging variants
- [ ] Real-time dashboard for campaign performance
- [ ] Multi-product recommendation engine
- [ ] Dynamic conversion score refinement based on feedback
- [ ] Async message queue for batch outreach

## Support

For issues or questions:
1. Check MCP Server is running on `http://localhost:8000`
2. Verify database connection and customer data exists
3. Review agent logs in console output
4. Check `state.error` field for detailed error messages
