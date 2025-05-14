import requests
from google.adk.agents import Agent

API_ENDPOINT = "https://beta.dedi.global/dedi/internal/get-all-namepace"

def get_all_namespace_data() -> str:
    """
    Calls the namespace API to retrieve all namespace data.
    This function will be used as a tool by the agent.

    Returns:
        A string representation of the JSON response from the API, containing all namespaces.
    """
    try:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

# The function itself will be passed as a tool

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash", # You can choose a different model if needed
    description="Agent that calls an API to get all namespace information and handles the response.",
    instruction="""
    You are an agent responsible for fetching all namespace information from an external API.
    When the user asks to "get all namespace data", "get namespaces", or "turn on services",
    you must use the 'get_all_namespace_data' tool to call the API.
    This tool does not require any parameters.
    Return the full response from the API to the user.
    For example, if the user says "get all namespaces", you should call the tool.
    """,
    tools=[get_all_namespace_data], # Pass the function directly
)