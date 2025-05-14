import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
from .sub_agents.subsidy import get_all_subsidies_data,search_subsidies_data,status_subsidies_data
from .sub_agents.demand_flexibility_program import search_demand_flexibility_program_data,confirm_demand_flexibility_program_data,status_demand_flexibility_program_data
from .sub_agents.connection import search_connection_data,select_connection_data,initiate_connection_data,confirm_connection_data,status_connection_data

load_dotenv()


    

# The function itself will be passed as a tool

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash", # You can choose a different model if needed
    description="Agent that acts as an assistant to the user to get the list of Subsidies for solar panel installation provided by the government.",
    instruction="""
    You are an agent responsible for fetching all available subsidies information from an external API.
    When the user asks to "fetch all subsidies", "Subsidies","What are the available subsidies" ,"get subsidies", "List subsidies" or something which indicates the user is asking for the list of subsidies,
    you must use the 'get_all_subsidies_data' tool to call the API.
    This tool requires parameters.
    Use the full response from the API  and provide only relevant response to the user according to the user's query not the whole response.
    For example, if the user says "get all subsidies", you should call the tool.
    When the user asks to "search subsidies", "Search subsidies", "Search subsidy", "Search subsidy by name", "Search subsidy by id", "Search subsidy by description" or something which indicates the user is asking for the list of subsidies,
    you must use the 'search_subsidies_data' tool to call the API.
    This tool requires parameters.
    Use the full response from the API  and provide only relevant response to the user according to the user's query not the whole response.
    For example, if the user says "search subsidies", you should call the tool.
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
        ], # Pass the function directly
)