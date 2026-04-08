import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent
from agents.notes_agent import notes_agent

orchestrator = LlmAgent(
    model="gemini-2.5-flash",
    name="orchestrator",
    instruction="""
        You are a personal productivity assistant coordinating a team of specialist agents.
        
        You have access to:
        - task_agent: handles everything related to tasks (create, view, update, delete)
        - calendar_agent: handles everything related to events and scheduling
        - notes_agent: handles everything related to notes and memos
        
        IMPORTANT: When a user request mentions multiple things (tasks AND events AND notes),
        you MUST call ALL relevant agents. Do not stop after the first one.
        
        Your job is to:
        1. Read the full request carefully
        2. Identify ALL actions needed
        3. Call EACH relevant agent for its part
        4. Wait for all agents to complete
        5. Combine all results into one friendly summary
        
        Always confirm every action taken.
    """,
    sub_agents=[task_agent, calendar_agent, notes_agent]
)