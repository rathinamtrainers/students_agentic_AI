from typing import Dict, Any, Tuple

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import State
from google.adk.tools import BaseTool
from pydantic import ValidationError

from Customer_Service.entities.customer import Customer


def lowercase_value(value):
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

    return None