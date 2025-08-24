from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from . import prompt

def _render_reference(
        callback_context: CallbackContext,
        llm_response: LlmResponse
) -> LlmResponse:
    """Appends grounding references to the response"""
    del callback_context

    for chunk in llm_response.grounding_metadata.grounding_chunks:
        title = chunk.web.title
        url = chunk.web.url

    # TODO: Add the grounding references to the response

    return llm_response

critic_agent = Agent(
    model="gemini-2.5-flash",
    name="critic_agent",
    instruction=prompt.CRITIC_PROMPT,
    tools=[google_search],
    after_model_callback=_render_reference
)