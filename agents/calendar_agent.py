import os
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

CALENDAR_MCP_URL = os.getenv("CALENDAR_MCP_URL", "http://localhost:8002/mcp")

current_date = datetime.now().strftime("%Y-%m-%d")
current_day = datetime.now().strftime("%A")

calendar_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="calendar_agent",
    instruction=f"""
        You are a calendar and scheduling specialist.
        TODAY'S DATE IS {current_date} ({current_day}).
        
        When a user says "tomorrow", it means {current_date} + 1 day.
        When a user says "today", it means {current_date}.
        
        Always convert relative dates to absolute YYYY-MM-DD format before calling tools.
        
        Always confirm actions taken with a clear summary.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=CALENDAR_MCP_URL
            )
        )
    ]
)