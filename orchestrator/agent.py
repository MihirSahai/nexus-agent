# orchestrator/agent.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent
from agents.notes_agent import notes_agent

class DeterministicOrchestrator:
    """
    Calls sub-agents based on keyword matching.
    For production, improve with regex or a small LLM classifier.
    """
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.sub_agents = {
            "task": task_agent,
            "calendar": calendar_agent,
            "notes": notes_agent,
        }

    async def run(self, user_message: str, session_id: str) -> str:
        # Determine which agents to call based on keywords
        agents_to_call = []
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ["task", "todo", "buy", "create a task", "mark task", "delete task"]):
            agents_to_call.append(("task", task_agent))
        if any(word in msg_lower for word in ["schedule", "meeting", "appointment", "event", "calendar", "today's schedule"]):
            agents_to_call.append(("calendar", calendar_agent))
        if any(word in msg_lower for word in ["note", "notes", "memo"]):
            agents_to_call.append(("notes", notes_agent))
        
        # If no keywords match, default to task agent (or you can use LLM fallback)
        if not agents_to_call:
            agents_to_call.append(("task", task_agent))
        
        # Call each agent sequentially and collect responses
        responses = {}
        for name, agent in agents_to_call:
            runner = Runner(
                agent=agent,
                app_name=f"orchestrator_{name}",
                session_service=self.session_service
            )
            content = Content(role="user", parts=[Part(text=user_message)])
            final_response = ""
            async for event in runner.run_async(
                user_id="user",
                session_id=session_id,
                new_message=content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text
            responses[name] = final_response
        
        # Combine responses into a single answer
        if len(responses) == 1:
            return list(responses.values())[0]
        else:
            combined = []
            for name, resp in responses.items():
                if resp:
                    combined.append(f"**{name.capitalize()} Agent:** {resp}")
            return "\n\n".join(combined)

orchestrator = DeterministicOrchestrator()