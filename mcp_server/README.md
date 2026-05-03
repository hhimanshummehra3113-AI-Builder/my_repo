# Banking CRM MCP Server

## Overview

FastAPI-based Model Context Protocol (MCP) server for the Banking CRM Agentic AI system. This server exposes all CRM tools that an AI agent can use to identify high-value customers and generate personalized outreach.

## Architecture

```
MCP Server (FastAPI)
├── Database Layer (PostgreSQL)
│   ├── Customer Repository
│   ├── Transaction Repository
│   ├── Product Repository
│   └── Loan Repository
├── Tool Layer
│   ├── Customer Profile Tool
│   ├── Transaction Analysis Tool
│   ├── Conversion Score Calculation Tool
│   ├── Product Recommendation Tool
│   ├── Message Generation Tool
│   └── Prospect Identification Tool
└── API Layer (HTTP/REST)
    ├── MCP Tool Endpoints
    ├── CRM Operation Endpoints
    └── Workflow Endpoints
```

## Available Tools

### 1. `get_customer_profile`
Fetch complete customer profile including financials and account info.

**Parameters:**
- `customer_id` (int): Customer ID

**Returns:** Customer details, loan history, contact info

### 2. `analyze_transactions`
Analyze customer transaction patterns and spending behavior.

**Parameters:**
- `customer_id` (int): Customer ID
- `months` (int, optional): Analysis period (default: 6)

**Returns:** Transaction summary, category breakdown, monthly trends, stability score

### 3. `calculate_conversion_score`
Calculate likelihood of loan conversion (0-100 score).

**Parameters:**
- `customer_id` (int): Customer ID

**Returns:** Conversion score, breakdown by factors, risk assessment

### 4. `get_recommended_products`
Get suitable loan products for the customer.

**Parameters:**
- `customer_id` (int): Customer ID

**Returns:** Top 3 recommended products with eligibility and terms

### 5. `generate_outreach_message`
Generate personalized WhatsApp/SMS message for outreach.

**Parameters:**
- `customer_id` (int): Customer ID
- `product_id` (int): Product ID

**Returns:** Personalized message, tone, offer details

### 6. `identify_high_value_prospects`
Identify and rank top high-value customers for campaigns.

**Parameters:** None

**Returns:** Top 10 prospects with scores and priority

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- PostgreSQL database with tables created

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Start the Server
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### List Available Tools
```bash
curl http://localhost:8000/mcp/tools
```

### Get Customer Profile
```bash
curl http://localhost:8000/crm/customers/1/profile
```

### Analyze Customer Transactions
```bash
curl "http://localhost:8000/crm/customers/1/transactions?months=6"
```

### Get Conversion Score
```bash
curl http://localhost:8000/crm/customers/1/score
```

### Get Product Recommendations
```bash
curl http://localhost:8000/crm/customers/1/recommendations
```

### Generate Outreach Message
```bash
curl -X POST "http://localhost:8000/crm/customers/1/message?product_id=1"
```

### Get High-Value Prospects
```bash
curl http://localhost:8000/crm/prospects
```

### Complete Customer Analysis
```bash
curl http://localhost:8000/crm/customers/1/complete-analysis
```

### Run Outreach Campaign Workflow
```bash
curl http://localhost:8000/crm/workflow/outreach-campaign
```

## MCP Tool Calling

### Method 1: Direct POST to /mcp/call
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_customer_profile",
    "params": {"customer_id": 1}
  }'
```

### Method 2: POST to /mcp/tools/{tool_name}
```bash
curl -X POST "http://localhost:8000/mcp/tools/calculate_conversion_score" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1}'
```

## API Endpoints

### Status & Health
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `GET /status` - Server status with database connection

### MCP Tools
- `GET /mcp/tools` - List all available tools
- `POST /mcp/call` - Call any tool
- `POST /mcp/tools/{tool_name}` - Call tool by name

### Customer Profiles
- `GET /crm/customers/{id}/profile` - Get customer profile
- `GET /crm/customers/{id}/transactions` - Analyze transactions
- `GET /crm/customers/{id}/score` - Get conversion score
- `GET /crm/customers/{id}/recommendations` - Get product recommendations
- `POST /crm/customers/{id}/message` - Generate outreach message
- `GET /crm/customers/{id}/complete-analysis` - Complete analysis

### Prospects & Campaigns
- `GET /crm/prospects` - Get high-value prospects
- `GET /crm/workflow/outreach-campaign` - Run outreach workflow

## Scoring Methodology

### Conversion Score (0-100)
The conversion score is calculated as a weighted combination of:

1. **Credit Score Component (30%)**
   - Customer's credit score normalized to 0-100
   - Higher score = better creditworthiness

2. **Income Component (25%)**
   - Annual income normalized to 0-100
   - Higher income = higher loan capacity

3. **Transaction Stability (25%)**
   - Based on transaction frequency, consistency, and regularity
   - Calculated from last 6 months of transactions

4. **Account Tenure (10%)**
   - Years with bank normalized to 0-100
   - Longer tenure = more reliable customer

5. **Loan Behavior (10%)**
   - Existing loan EMI payment history
   - Penalty for any defaults
   - Bonus for active loans with good standing

**Likelihood Categories:**
- **Very High (80-100):** Immediate outreach recommended
- **High (70-79):** Strong candidate for conversion
- **Medium (60-69):** Good prospect with targeted offer
- **Low-Medium (50-59):** Potential prospect, monitor
- **Low (<50):** Lower priority for current campaign

## Database Schema

The server works with PostgreSQL database containing:

- `customers` - Customer master data
- `transactions` - Customer transactions
- `products` - Loan product catalog
- `customer_products` - Historical/current loans
- `loan_offers` - Outreach and offer tracking
- `customer_segments` - Customer segmentation

## Features

✅ **6 Core CRM Tools** - All functionality needed for agentic AI

✅ **Multi-Tool Integration** - Tools use repositories for clean data access

✅ **Conversion Scoring** - Multi-factor algorithm for realistic assessment

✅ **Personalization** - Messages based on customer patterns and scores

✅ **RESTful API** - Easy integration with agents and clients

✅ **Comprehensive Logging** - Detailed operation tracking

✅ **Error Handling** - Graceful error responses

✅ **Documentation** - Built-in API docs at `/docs`

## Future Enhancements

- [ ] Database connection pooling for scale
- [ ] Caching layer for frequently accessed data
- [ ] ML-based conversion score model
- [ ] A/B testing framework for message variations
- [ ] Real-time offer tracking and analytics
- [ ] Multi-channel campaign management
- [ ] Advanced segmentation and targeting
- [ ] Fraud detection integration

## Performance Notes

- **Database:** Queries optimized with indexes on key columns
- **Response Time:** ~100-200ms average for tool execution
- **Scalability:** Ready for 10K+ customers with connection pooling
- **Concurrency:** Supports multiple concurrent tool calls

## Security Considerations

- ⚠️ **Current:** No authentication (suitable for local/internal use)
- 🔒 **Production:** Add API key/OAuth authentication
- 🔐 **Database:** Use SSL connections to PostgreSQL
- 📝 **Logging:** Ensure no sensitive data logged

## Development & Testing

### Run Tests
```bash
# (Coming soon)
```

### Check Linting
```bash
pylint tools/crm_tools.py
pylint db/*.py
```

## Troubleshooting

### Database Connection Error
```
✗ Database connection failed: connection refused
```
**Solution:** Ensure PostgreSQL is running and credentials in .env are correct

### Tool Not Found
```
Tool 'tool_name' not found
```
**Solution:** Check tool name at `/mcp/tools` endpoint

### Customer Not Found
```
Customer 1 not found
```
**Solution:** Verify customer_id exists in database

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Swagger UI:** http://localhost:8000/docs

---

**Part of:** Banking CRM Agentic AI Assignment
**Version:** 1.0.0
