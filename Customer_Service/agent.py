from google.adk import Agent
from .prompts import INSTRUCTION, GLOBAL_INSTRUCTION
from .tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code
)

from .shared_libraries.callbacks import before_tool, before_agent, rate_limit_callback, after_tool

# Create a customer service agent
root_agent = Agent(
    model = "gemini-2.5-flash",
    name = "customer_service_agent",
    instruction = INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_planting_service,
        get_available_planting_times,
        send_care_instructions,
        generate_qr_code
    ],
    # TODO: add callbacks
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
    before_tool_callback=before_tool,
    after_tool_callback=after_tool
)
