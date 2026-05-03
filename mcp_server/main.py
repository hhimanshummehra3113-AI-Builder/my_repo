"""
Banking CRM Agentic AI - MCP Server
FastAPI-based Model Context Protocol Server
Exposes CRM tools for agent consumption
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and tools
from config.database import db
from tools.crm_tools import TOOLS, CRMTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Banking CRM MCP Server",
    description="Model Context Protocol Server for Banking CRM Agentic AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Health & Status Endpoints
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Banking CRM MCP Server",
        "version": "1.0.0"
    }


@app.get("/status")
async def status():
    """Server status with database info"""
    try:
        db.connect()
        return {
            "status": "ready",
            "database": "connected",
            "tools_available": len(TOOLS),
            "tools": list(TOOLS.keys())
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


# ============================================================
# MCP Tool Endpoints
# ============================================================

@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    tools_list = []
    for tool_name, tool_info in TOOLS.items():
        tools_list.append({
            "name": tool_name,
            "description": tool_info.get("description", ""),
            "parameters": tool_info.get("parameters", {})
        })
    
    return {
        "success": True,
        "total_tools": len(tools_list),
        "tools": tools_list
    }


@app.post("/mcp/call")
async def call_tool(request: Dict[str, Any]):
    """
    Execute MCP tool
    
    Request format:
    {
        "tool": "tool_name",
        "params": {
            "param1": value1,
            "param2": value2
        }
    }
    """
    try:
        tool_name = request.get("tool")
        params = request.get("params", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        if tool_name not in TOOLS:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        # Execute tool with provided parameters
        tool_func = TOOLS[tool_name]["function"]
        result = tool_func(**params)
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tool": request.get("tool", "unknown")
        }


@app.post("/mcp/tools/{tool_name}")
async def call_tool_by_name(tool_name: str, params: Dict[str, Any] = None):
    """
    Alternative endpoint to call tool by name in URL
    
    Example: POST /mcp/tools/get_customer_profile
    Body: {"customer_id": 1}
    """
    try:
        if tool_name not in TOOLS:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        params = params or {}
        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        tool_func = TOOLS[tool_name]["function"]
        result = tool_func(**params)
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name
        }


# ============================================================
# CRM Operation Endpoints (Convenience endpoints)
# ============================================================

@app.get("/crm/customers/{customer_id}/profile")
async def get_customer_profile_endpoint(customer_id: int):
    """Get customer profile"""
    result = CRMTools.get_customer_profile(customer_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.get("/crm/customers/{customer_id}/transactions")
async def analyze_customer_transactions(customer_id: int, months: int = 6):
    """Analyze customer transactions"""
    result = CRMTools.analyze_transactions(customer_id, months)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.get("/crm/customers/{customer_id}/score")
async def get_conversion_score(customer_id: int):
    """Get conversion score for customer"""
    result = CRMTools.calculate_conversion_score(customer_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.get("/crm/customers/{customer_id}/recommendations")
async def get_product_recommendations(customer_id: int):
    """Get product recommendations"""
    result = CRMTools.get_recommended_products(customer_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.post("/crm/customers/{customer_id}/message")
async def generate_message(customer_id: int, product_id: int):
    """Generate outreach message"""
    result = CRMTools.generate_outreach_message(customer_id, product_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/crm/prospects")
async def get_high_value_prospects():
    """Get high-value customer prospects"""
    result = CRMTools.identify_high_value_prospects()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


# ============================================================
# Compound Operations (Multi-step workflows)
# ============================================================

@app.get("/crm/customers/{customer_id}/complete-analysis")
async def complete_customer_analysis(customer_id: int):
    """Get complete analysis for a customer (profile + transactions + score + recommendations)"""
    try:
        profile = CRMTools.get_customer_profile(customer_id)
        transactions = CRMTools.analyze_transactions(customer_id, 6)
        score = CRMTools.calculate_conversion_score(customer_id)
        recommendations = CRMTools.get_recommended_products(customer_id)
        
        if not all([profile.get("success"), transactions.get("success"), 
                   score.get("success"), recommendations.get("success")]):
            raise HTTPException(status_code=404, detail="Customer analysis failed")
        
        return {
            "success": True,
            "customer_id": customer_id,
            "profile": profile.get("data"),
            "transactions": transactions.get("data"),
            "conversion_score": score.get("data"),
            "recommendations": recommendations.get("data")
        }
    
    except Exception as e:
        logger.error(f"Complete analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crm/workflow/outreach-campaign")
async def outreach_campaign_workflow():
    """Complete workflow: Identify prospects → Analyze → Score → Generate messages"""
    try:
        # Step 1: Identify high-value prospects
        prospects_result = CRMTools.identify_high_value_prospects()
        if not prospects_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to identify prospects")
        
        prospects = prospects_result.get("data", {}).get("top_prospects", [])
        
        # Step 2: For each top prospect, generate top product message
        campaign_data = []
        for prospect in prospects[:5]:  # Top 5 prospects
            customer_id = prospect['customer_id']
            
            # Get recommendations
            rec_result = CRMTools.get_recommended_products(customer_id)
            if rec_result.get("success") and rec_result.get("data", {}).get("recommendations"):
                top_product = rec_result.get("data", {}).get("recommendations", [])[0]
                
                # Generate message
                msg_result = CRMTools.generate_outreach_message(customer_id, top_product['product_id'])
                
                if msg_result.get("success"):
                    campaign_data.append({
                        "prospect": prospect,
                        "recommended_product": top_product,
                        "outreach_message": msg_result.get("data", {}).get("messages", {})
                    })
        
        return {
            "success": True,
            "workflow": "outreach_campaign",
            "total_prospects": len(prospects),
            "campaign_messages_generated": len(campaign_data),
            "campaign_data": campaign_data
        }
    
    except Exception as e:
        logger.error(f"Outreach campaign workflow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Root and Info Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Banking CRM Agentic AI - MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server for Banking CRM customer analysis and outreach",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "documentation": "/docs",
            "tools": {
                "list_tools": "GET /mcp/tools",
                "call_tool": "POST /mcp/call",
                "call_tool_by_name": "POST /mcp/tools/{tool_name}"
            },
            "crm_operations": {
                "customer_profile": "GET /crm/customers/{customer_id}/profile",
                "transactions": "GET /crm/customers/{customer_id}/transactions",
                "conversion_score": "GET /crm/customers/{customer_id}/score",
                "recommendations": "GET /crm/customers/{customer_id}/recommendations",
                "message": "POST /crm/customers/{customer_id}/message",
                "prospects": "GET /crm/prospects",
                "complete_analysis": "GET /crm/customers/{customer_id}/complete-analysis"
            },
            "workflows": {
                "outreach_campaign": "GET /crm/workflow/outreach-campaign"
            }
        }
    }


# ============================================================
# Startup and Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        db.connect()
        logger.info("✓ Database connected successfully")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {str(e)}")
        logger.info("Server will attempt to connect on first request")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        db.disconnect()
        logger.info("✓ Database disconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Banking CRM MCP Server on {host}:{port}")
    logger.info("📚 API Documentation available at http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
