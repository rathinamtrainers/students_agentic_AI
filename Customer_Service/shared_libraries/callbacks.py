from typing import Dict, Any, Tuple, Optional
import time
import logging

from google.adk.agents import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.sessions import State
from google.adk.tools import BaseTool
from pydantic import ValidationError
from google.adk.tools.tool_context import ToolContext

from Customer_Service.entities.customer import Customer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def lowercase_value(value):
    """Make dictionary/list/set/tuple of strings or string lowercase"""
    if isinstance(value, dict):
        return (dict(key, lowercase_value(val)) for key, val in value.items())
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(val) for val in value)
    else:
        return value


def validate_customer_id(customer_id: str, session_state: State) -> Tuple[bool, str]:
    """
    Validates the customer ID against the customer profit in the session state.

    :param customer_id: The ID of the customer to validate.
    :param session_state:  The session state containing the customer profile.
    :return: A tuple containing a boolean (True/False) indicating whether the customer ID is valid and an error message if not.

    """

    if 'customer_profile' not in session_state:
        return False, "No customer profile selected. Please select a profile"

    try:
        c = Customer.model_validate_json(session_state['customer_profile'])
        if c.customer_id == customer_id:
            return True, None
        else:
            return False, f"You cannot use the tool with customer_id {customer_id}. Please use the tool with customer_id {c.customer_id}"
    except ValidationError as e:
        return False, f"Customer profile couldn't be parsed. Please reload the customer data. Error: {e}"

def before_tool(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: CallbackContext
):

    # Makesure all values that the agent is sending to tools are lowercase.
    lowercase_value(args)

    if 'customer_id' in args:
        valid, err = validate_customer_id(args['customer_id'], tool_context.state)
        if not valid:
            return err

    if tool.name == "sync_ask_for_approval":
        amount = args.get("value", None)

        if amount <= 10:
            return {
                "status": "approved",
                "message": "You can approve this discount; no manager approval needed."
            }


    if tool.name == "modify_cart":
        if (
            args.get("items_added") is True and
            args.get("items_removed") is True
        ):
            return {"result": "I have added and removed the requested items."}

    return None

def after_tool(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext,
        tool_response: Dict
) -> Optional[Dict]:
    # After approvals, we can apply discount in the cart. Try to avoid AI calls where possible.
    if tool.name == "sync_ask_for_approval":
        if tool_response.get("status") == "approved":
            logger.debug("Applying disocunt to the cart")
            # TODO: Make changes to the cart for the discount udpate.

    if tool.name == "approve_discount":
        if tool_response.get("status") == "ok":
            logger.debug("Applying disocunt to the cart")
            # TODO: Make changes to the cart for the discount udpate.


def before_agent(callback_context: InvocationContext):
    # TODO: Once we implement authentication logic (Google/Microsoft SSO), get the corresponding
    # Customer profile based on login auth details.
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer("CUST001").to_json()


RPM_QUOTA = 10
RATE_LIMIT_SECS = 60

def rate_limit_callback(
        callback_context: InvocationContext,
        llm_request: LlmRequest
) -> None:

    now = time.time()
    if "timer_start" not in callback_context.state:
        # First request in the time window.
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            f"rate_limit_callback [timestamp: {now}, request_count: 1, elapsed_secs: 0]"
        )
        return

    # Increment the request count from second request onwards.
    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        f"rate_limit_callback [timestamp: {now}, request_count: {request_count}, elapsed_secs: {elapsed_secs}]"
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug(f"Sleeping for {delay} seconds")
            time.sleep(delay)

        # Reset the timer and request count as the time window has elapsed.
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return
