"""
Agent State Definition - Tracks all agent execution context
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    State object for the Banking CRM Agent
    Tracks all information throughout the agent's execution
    """
    # Input
    user_query: str  # Initial user request/task
    
    # Analysis tracking
    customer_ids: List[int] = field(default_factory=list)  # Customers to analyze
    high_value_prospects: List[Dict[str, Any]] = field(default_factory=list)  # Identified prospects
    analyzed_customers: List[Dict[str, Any]] = field(default_factory=list)  # Detailed analysis results
    
    # Tool interactions
    tools_called: List[str] = field(default_factory=list)  # Track which tools were used
    tool_results: Dict[str, Any] = field(default_factory=dict)  # Store tool outputs
    
    # Agent reasoning
    thoughts: List[str] = field(default_factory=list)  # Agent's reasoning steps
    current_action: str = ""  # Current action the agent is taking
    
    # Results
    recommendations: List[Dict[str, Any]] = field(default_factory=list)  # Final recommendations
    summary: str = ""  # Executive summary
    error: Optional[str] = None  # Any errors encountered
    
    # Execution control
    next_node: str = "identify_prospects"  # Next node to execute
    max_iterations: int = 10
    iterations_count: int = 0
