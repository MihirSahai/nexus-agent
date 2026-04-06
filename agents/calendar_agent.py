import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

CALENDAR_MCP_URL = os.getenv("CALENDAR_MCP_URL", "http://localhost:8002/mcp")

calendar_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="calendar_agent",
    instruction="""
        You are a calendar and scheduling specialist.
        You help users create, view and delete calendar events.
        
        When creating events:
        - Extract title, start time, end time, description and location
        - Start time format should be: YYYY-MM-DD HH:MM
        - If end time is not mentioned, leave it empty
        - If location is not mentioned, leave it empty
        
        When showing events:
        - Format them clearly with ID, title, start time and location
        - Always show today's date context
        
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