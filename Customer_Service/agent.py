from google.adk import Agent
from .prompts import INSTRUCTION

# Create a customer service agent
root_agent = Agent(
    model = "gemini-2.5-flash",
    name = "customer_service_agent",
    instruction = INSTRUCTION,
    tools=[]
)
