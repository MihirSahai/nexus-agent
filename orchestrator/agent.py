import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent

orchestrator = LlmAgent(
    model="gemini-2.5-flash",
    name="orchestrator",
    instruction="""
        You are a personal productivity assistant coordinating a team of specialist agents.
        
        You have access to:
        - task_agent: handles everything related to tasks (create, view, update, delete)
        - calendar_agent: handles everything related to events and scheduling
        
        Your job is to:
        1. Understand what the user wants to accomplish
        2. Decide which agent(s) to involve
        3. Coordinate between agents for multi-step requests
        4. Synthesize responses into a single helpful reply
        
        Examples:
        - "Add a meeting tomorrow at 3pm and create a task to prepare slides" 
          → use calendar_agent AND task_agent together
        - "What's on my schedule today and what tasks are pending?"
          → use calendar_agent AND task_agent together
        - "Create a task to review the report"
          → use task_agent only
        - "Schedule a dentist appointment next Monday at 10am"
          → use calendar_agent only
        
        Always give a clear, friendly summary of everything that was done.
    """,
    sub_agents=[task_agent, calendar_agent]
)