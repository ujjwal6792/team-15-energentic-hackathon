import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
from .sub_agents.subsidy import get_all_subsidies_data,search_subsidies_data,status_subsidies_data
from .sub_agents.demand_flexibility_program import search_demand_flexibility_program_data,confirm_demand_flexibility_program_data,status_demand_flexibility_program_data
from .sub_agents.connection import search_connection_data,select_connection_data,initiate_connection_data,confirm_connection_data,status_connection_data
from .sub_agents.solar_retail import search_solar_retail_data,select_solar_retail_data,init_solar_retail_data,confirm_solar_retail_data,status_solar_retail_data
from .sub_agents.solar_service import search_solar_service_data,select_solar_service_data,init_solar_service_data,confirm_solar_service_data,status_solar_service_data

import asyncio

load_dotenv()
from google.adk.sessions import InMemorySessionService, Session

temp_service = InMemorySessionService()
example_session: Session = temp_service.create_session(
    app_name="tool_agent",
    user_id="example_user",
)

print(f"--- Examining Session Properties (Before Interaction) ---")
print(f"ID (`id`):                {example_session.id}")
print(f"Application Name (`app_name`): {example_session.app_name}")
print(f"User ID (`user_id`):         {example_session.user_id}")
print(f"Events (`events`):         {example_session.events}") # Initially empty
print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
print(f"-------------------------------------------------------")

# Initialize the root_agent *first*
root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash", # You can choose a different model if needed
    description="Agent that acts as an assistant to the user to get the list of Subsidies for solar panel installation provided by the government.",
    instruction="""
    You are an intelligent agent responsible for fetching and managing solar-related services and subsidy information via API tools.

    Use the **relevant tool** based on the user's intent. Provide **concise, helpful responses** using only the relevant parts of the API's response.

    ---

    ### 1. Subsidies

    - Use `get_all_subsidies_data` when the user says:
        - "fetch all subsidies", "list all subsidies", "show me subsidies", "get subsidies", "available subsidies"
        - or anything similar indicating a **request to view all available subsidies**.

    - Use `search_subsidies_data` when the user says:
        - "search subsidies", "search subsidy by name", "search subsidy by ID", "find a subsidy", "lookup subsidy"
        - or anything that **requires filtering or searching for a specific subsidy**.

    - Use `status_subsidies_data` when the user says:
        - "check subsidy status", "track subsidy", "subsidy application status", "what is the status of my subsidy"
        - or anything indicating the **user wants to know the current state of a subsidy request or application**.

    ---

    ### 2. Demand Flexibility Program

    - Use `search_demand_flexibility_program_data` when the user says:
        - "search demand flexibility program", "find programs", "lookup demand programs"
        - or anything suggesting the user wants to **explore available demand flexibility programs**.

    - Use `confirm_demand_flexibility_program_data` when the user says:
        - "confirm participation in demand program", "enroll in demand flexibility program", "opt into demand program"
        - or anything that indicates **confirmation or joining** of such a program.

    - Use `status_demand_flexibility_program_data` when the user says:
        - "check status of demand program", "my participation status", "demand program progress"
        - or anything related to **checking status of their enrollment or actions in the demand flexibility program**.

    ---

    ### 3. Solar Connection

    - Use `search_connection_data` when the user says:
        - "search connection options", "available solar connections", "lookup connection plans"
        - or anything about **browsing available solar connection choices**.

    - Use `select_connection_data` when the user says:
        - "select a connection", "choose this connection", "I want this connection"
        - or anything indicating the **user has made a choice** and wants to proceed.

    - Use `initiate_connection_data` when the user says:
        - "initiate connection", "start solar connection process", "begin connection setup"
        - or anything about **starting a connection application**.

    - Use `confirm_connection_data` when the user says:
        - "confirm connection request", "submit connection", "finalize solar connection"
        - or anything indicating **confirmation/submission of connection setup**.

    - Use `status_connection_data` when the user says:
        - "check connection status", "track my solar connection", "connection application status"
        - or anything related to **tracking the progress** of a solar connection.

    ---

    ### 4. Solar Retail Services

    - Use `search_solar_retail_data` when the user says:
        - "search solar retailers", "find solar providers", "solar retail options"
        - or anything about **finding companies or providers** who sell solar panels.

    - Use `select_solar_retail_data` when the user says:
        - "select solar retailer", "choose this retailer", "pick solar vendor"
        - or anything indicating **selection of a solar retailer**.

    - Use `init_solar_retail_data` when the user says:
        - "initiate solar retail process", "start purchase", "begin retail process"
        - or anything about **beginning the transaction** with a selected solar retailer.

    - Use `confirm_solar_retail_data` when the user says:
        - "confirm purchase", "confirm retailer selection", "submit retail request"
        - or anything that suggests **confirmation of the retail process**.

    - Use `status_solar_retail_data` when the user says:
        - "check status of solar purchase", "retail process status", "track retailer status"
        - or anything related to **monitoring progress or status of a retail interaction**.

    ---

    ### 5. Solar Service (Installation, Maintenance, etc.)

    - Use `search_solar_service_data` when the user says:
        - "search solar services", "available solar maintenance", "find installers"
        - or anything related to **browsing installation or post-purchase services**.

    - Use `select_solar_service_data` when the user says:
        - "select this service", "choose installer", "pick solar maintenance plan"
        - or anything about **selecting a specific service**.

    - Use `init_solar_service_data` when the user says:
        - "initiate solar service", "start installation", "begin maintenance request"
        - or anything about **starting service engagement**.

    - Use `confirm_solar_service_data` when the user says:
        - "confirm service request", "submit service", "finalize maintenance request"
        - or anything indicating **confirmation of service initiation**.

    - Use `status_solar_service_data` when the user says:
        - "check service status", "track installation", "what's the progress of my service"
        - or anything about **tracking the current state of the service**.

    ---

    Always use the **full API response**, but return only **relevant, clear, and concise information** based on the user's query.
    """,
    tools=[
        get_all_subsidies_data,
        search_subsidies_data,
        status_subsidies_data,
        search_demand_flexibility_program_data,
        confirm_demand_flexibility_program_data,
        status_demand_flexibility_program_data,
        search_connection_data,
        select_connection_data,
        initiate_connection_data,
        confirm_connection_data,
        status_connection_data,
        search_solar_retail_data,
        select_solar_retail_data,
        init_solar_retail_data,
        confirm_solar_retail_data,
        status_solar_retail_data,
        search_solar_service_data,
        select_solar_service_data,
        init_solar_service_data,
        confirm_solar_service_data,
        status_solar_service_data
        ], # Pass the function directly
)

async def main():
    response = await root_agent.handle(
        text="What are the available subsidies?",
        session_id=example_session.id,
    )
    print(f"Agent Response: {response}")

    # After the interaction, retrieve the session details again
    session_details_url = f"http://0.0.0.0:8000/apps/tool_agent/users/example_user/sessions"
    new_response = requests.get(session_details_url)
    print(f"--- Session Details After Interaction ---")
    print(new_response.json())
    print("---------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())