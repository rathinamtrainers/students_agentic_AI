from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report of the specified city.

    :param city (str): The name of the city for which to retrieve the weather report.
    :return:
        dict: status and result or error message.
    """
    if city.lower() == "coimbatore":
        return {
            "status": "success",
            "report": (
                "The weather in Coimbatore is cloudy with a temperature of 25 degrees Celsius."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather report for {city} is not available.",
        }

def get_current_time(city: str) -> dict:
    """Retrieves the current time in the specified city.

    :param city (str): The name of the city for which to retrieve the current time.
    :return:
        dict: status and result or error message.
    """
    if city.lower() == "coimbatore":
        return {
            "status": "success",
            "time": "10:00 AM",
        }
    else:
        return {
            "status": "error",
            "error_message": f"Time in {city} is not available.",
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description=("Agent to answer questions about the time and weather in a city"),
    instruction=("You are a helpful agent that answers questions about the time and weather in a city."),
    tools=[get_weather, get_current_time]
)