# agents/notes_agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

NOTES_MCP_URL = os.getenv("NOTES_MCP_URL", "http://localhost:8003/mcp")

notes_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="notes_agent",
    instruction="""
        You are a note‑taking specialist.
        You help users create, view, update, and delete notes.
        
        When creating notes:
        - Extract the title, content, and optional tags (comma‑separated)
        - If title is missing, ask for it or use a default like "Untitled"
        
        When showing notes:
        - Format them clearly with ID, title, first few words of content, and tags
        - If the user asks for notes with a specific tag, filter accordingly
        
        Always confirm actions taken with a clear summary.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=NOTES_MCP_URL
            )
        )
    ]
)