import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

TASKS_MCP_URL = os.getenv("TASKS_MCP_URL", "http://localhost:8001/mcp")

task_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="task_agent",
    instruction="""
        You are a task management specialist.
        You help users create, view, update and delete tasks.
        
        When creating tasks:
        - Extract the title, description, priority (low/medium/high) and due date from the user's message
        - If priority is not mentioned, default to medium
        - If due date is not mentioned, leave it empty
        
        When showing tasks:
        - Format them clearly with ID, title, status and priority
        - Group by status if showing all tasks
        
        Always confirm actions taken with a clear summary.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=TASKS_MCP_URL
            )
        )
    ]
)