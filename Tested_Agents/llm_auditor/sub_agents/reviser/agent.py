from google.adk import Agent

reviser_agent = Agent(
    model="gemini-2.5-flash",
    name="reviser_agent",
    instruction="",
    # TODO: Add model callback
)