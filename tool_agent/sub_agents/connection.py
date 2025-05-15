import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json # Added for loading string templates as JSON
from .meter_reading import create_meter_data
from .er_house_hold import create_er_house_hold

load_dotenv()

# Globa list to store order IDs
order_ids = []

# Provided Mappings
provider_name_to_id = {
    "San Francisco Electric Authority": "334"
}
provider_id_to_items = {
    "334": {
        "Residential Electricity Connection": "471",
        "Commercial Electricity Connection": "472"
    }
}

API_CONFIRM_ENDPOINT = os.getenv("base_url") + "confirm"
API_SEARCH_ENDPOINT = os.getenv("base_url") + "search"
API_SELECT_ENDPOINT = os.getenv("base_url") + "select"
API_INITIATE_ENDPOINT = os.getenv("base_url") + "init"
API_STATUS_ENDPOINT = os.getenv("base_url") + "status"

SEARCH_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:service",
        "action": "search",
        "location": {
            "country": {
                "code": "USA"
            }
        },
        "version": "1.1.0",
        "bap_id": "{{bap_id}}",
        "bap_uri": "{{bap_uri}}",
        "bpp_id": "{{bpp_id}}",
        "bpp_uri": "{{bpp_uri}}",
        "transaction_id": "{{transaction_id}}",
        "message_id": "{{message_id}}",
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "intent": {
            "item": {
                "descriptor": {
                    "name": "Connection"
                }
            }
        }
    }
}
"""

SELECT_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:service",
        "action": "select",
        "location": {
            "country": {
                "code": "USA"
            },
            "city": {
                "code": "NANP:628"
            }
        },
        "version": "1.1.0",
        "bap_id": "{{bap_id}}",
        "bap_uri": "{{bap_uri}}",
        "bpp_id": "{{bpp_id}}",
        "bpp_uri": "{{bpp_uri}}",
        "transaction_id": "{{transaction_id}}",
        "message_id": "{{message_id}}",
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "order": {
            "provider": {
                "id": "{{provider_id}}"
            },
            "items": [
                {
                    "id": "{{item_id}}"
                }
            ]
        }
    }
}
"""

INITIATE_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:service",
        "action": "init",
        "location": {
            "country": {
                "code": "USA"
            },
            "city": {
                "code": "NANP:628"
            }
        },
        "version": "1.1.0",
        "bap_id": "{{bap_id}}",
        "bap_uri": "{{bap_uri}}",
        "bpp_id": "{{bpp_id}}",
        "bpp_uri": "{{bpp_uri}}",
        "transaction_id": "{{transaction_id}}",
        "message_id": "{{message_id}}",
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "order": {
            "provider": {
                "id": "{{provider_id}}"
            },
            "items": [
                {
                    "id": "{{item_id}}"
                }
            ]
        }
    }
}
"""

CONFIRM_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:service",
        "action": "confirm",
        "location": {
            "country": {
                "code": "USA"
            },
            "city": {
                "code": "NANP:628"
            }
        },
        "version": "1.1.0",
        "bap_id": "{{bap_id}}",
        "bap_uri": "{{bap_uri}}",
        "bpp_id": "{{bpp_id}}",
        "bpp_uri": "{{bpp_uri}}",
        "transaction_id": "{{transaction_id}}",
        "message_id": "{{message_id}}",
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "order": {
            "provider": {
                "id": "{{provider_id}}"
            },
            "items": [
                {
                    "id": "{{item_id}}"
                }
            ],
            "fulfillments": [
                {
                    "id": "615",
                    "customer": {
                        "person": {
                            "name": "Lisa"
                        },
                        "contact": {
                            "phone": "876756454",
                            "email": "LisaS@mailinator.com"
                        }
                    }
                }
            ]
        }
    }
}
"""

STATUS_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:service",
        "action": "status",
        "location": {
            "country": {
                "code": "USA"
            },
            "city": {
                "code": "NANP:628"
            }
        },
        "version": "1.1.0",
        "bap_id": "{{bap_id}}",
        "bap_uri": "{{bap_uri}}",
        "bpp_id": "{{bpp_id}}",
        "bpp_uri": "{{bpp_uri}}",
        "transaction_id": "{{transaction_id}}",
        "message_id": "{{message_id}}",
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "order_id": "3779"
    }
}
"""

def search_connection_data(search_query: str) -> str:
    """
    Searches for connection data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all connection data.
    """
    try:
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        # ISO 8601 format timestamp with UTC timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        current_payload = SEARCH_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
                                     .replace("{{message_id}}", message_id) \
                                     .replace("{{timestamp}}", timestamp)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_SEARCH_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Try to get more specific error information from the response body if available
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass # Ignore if response.text is not available or causes an error
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err:
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass
        return f"Error decoding JSON response: {json_err} - Response was: {error_details}"
    
def select_connection_data(search_query: str) -> str:
    """
    Selects connection data based on a search query, parsing provider and item names.
    Prompts for missing information if the query is incomplete.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, or an error/prompt message.
    """
    try:
        found_provider_name = None
        found_item_name = None
        search_query_lower = search_query.lower()

        # Extract Provider Name
        for p_name in provider_name_to_id.keys():
            if p_name.lower() in search_query_lower:
                found_provider_name = p_name
                break
        
        # Extract Item Name
        # This simple extraction assumes item names are somewhat unique or the first match is acceptable.
        # For more complex scenarios, a more sophisticated NLP approach might be needed.
        for p_id_map, items_map in provider_id_to_items.items():
            for i_name in items_map.keys():
                if i_name.lower() in search_query_lower:
                    found_item_name = i_name
                    # If we also found a provider, check if this item belongs to it
                    if found_provider_name and provider_name_to_id.get(found_provider_name) == p_id_map:
                        break  # Item matches provider
                    elif not found_provider_name:
                         # If no provider yet, take this item and we might ask for provider later
                        break 
            if found_item_name and (not found_provider_name or provider_name_to_id.get(found_provider_name) == p_id_map):
                 break


        if not found_provider_name and not found_item_name:
            return "Error: Could not identify a provider or item from your query. Please specify a provider name (e.g., 'San Francisco Electric Authority') and an item name (e.g., 'Residential Electricity Connection')."

        if found_provider_name and not found_item_name:
            provider_id_for_items = provider_name_to_id[found_provider_name]
            available_items = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
            if not available_items:
                 return f"Error: No items found for provider '{found_provider_name}'. Please check the provider name or available services."
            return f"Error: Please specify the item for provider '{found_provider_name}'. Available items: {', '.join(available_items)}."

        if not found_provider_name and found_item_name:
            # Attempt to find which provider this item might belong to for a better prompt
            possible_providers = []
            for p_name, p_id_val in provider_name_to_id.items():
                if found_item_name in provider_id_to_items.get(p_id_val, {}):
                    possible_providers.append(p_name)
            if possible_providers:
                return f"Error: Please specify the provider for item '{found_item_name}'. This item is available from: {', '.join(possible_providers)}."
            else: # Should not happen if mappings are consistent
                return f"Error: Item '{found_item_name}' found, but no associated provider. Please also specify a provider name."


        # Both provider and item name are supposedly found
        provider_id = provider_name_to_id.get(found_provider_name)
        # Validate if the found item name actually belongs to the found provider
        item_id = provider_id_to_items.get(provider_id, {}).get(found_item_name)

        if not item_id:
            # This means the found_item_name does not belong to found_provider_name
            provider_id_for_items = provider_name_to_id[found_provider_name] # re-fetch to be sure
            actual_items_for_provider = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
            return (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                    f"Available items for this provider: {', '.join(actual_items_for_provider) if actual_items_for_provider else 'No items available'}.")

        # Proceed with API call if IDs are resolved
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        payload_dict = json.loads(SELECT_PAYLOAD_TEMPLATE)
        
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp
        
        payload_dict["message"]["order"]["provider"]["id"] = provider_id
        payload_dict["message"]["order"]["items"][0]["id"] = item_id
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_SELECT_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err: 
        error_details = ""
        try:
            error_details = response.text 
        except Exception:
            pass
        return f"Error processing JSON payload or response: {json_err} - Response was: {error_details}"

def initiate_connection_data(search_query: str) -> str:
    """
    Initiates connection data based on a search query, parsing provider and item names.
    Prompts for missing information if the query is incomplete.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, or an error/prompt message.
    """
    try:
        found_provider_name = None
        found_item_name = None
        search_query_lower = search_query.lower()

        for p_name in provider_name_to_id.keys():
            if p_name.lower() in search_query_lower:
                found_provider_name = p_name
                break
        
        for p_id_map, items_map in provider_id_to_items.items():
            for i_name in items_map.keys():
                if i_name.lower() in search_query_lower:
                    found_item_name = i_name
                    if found_provider_name and provider_name_to_id.get(found_provider_name) == p_id_map:
                        break
                    elif not found_provider_name:
                        break
            if found_item_name and (not found_provider_name or provider_name_to_id.get(found_provider_name) == p_id_map):
                 break

        if not found_provider_name and not found_item_name:
            return "Error: Could not identify a provider or item from your query. Please specify a provider name (e.g., 'San Francisco Electric Authority') and an item name (e.g., 'Residential Electricity Connection')."

        if found_provider_name and not found_item_name:
            provider_id_for_items = provider_name_to_id[found_provider_name]
            available_items = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
            if not available_items:
                 return f"Error: No items found for provider '{found_provider_name}'. Please check the provider name or available services."
            return f"Error: Please specify the item for provider '{found_provider_name}'. Available items: {', '.join(available_items)}."

        if not found_provider_name and found_item_name:
            possible_providers = []
            for p_name, p_id_val in provider_name_to_id.items():
                if found_item_name in provider_id_to_items.get(p_id_val, {}):
                    possible_providers.append(p_name)
            if possible_providers:
                return f"Error: Please specify the provider for item '{found_item_name}'. This item is available from: {', '.join(possible_providers)}."
            else:
                return f"Error: Item '{found_item_name}' found, but no associated provider. Please also specify a provider name."

        provider_id = provider_name_to_id.get(found_provider_name)
        item_id = provider_id_to_items.get(provider_id, {}).get(found_item_name)

        if not item_id:
            provider_id_for_items = provider_name_to_id[found_provider_name]
            actual_items_for_provider = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
            return (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                    f"Available items for this provider: {', '.join(actual_items_for_provider) if actual_items_for_provider else 'No items available'}.")

        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        payload_dict = json.loads(INITIATE_PAYLOAD_TEMPLATE)

        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp

        payload_dict["message"]["order"]["provider"]["id"] = provider_id
        payload_dict["message"]["order"]["items"][0]["id"] = item_id

        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_INITIATE_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err: 
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass
        return f"Error processing JSON payload or response: {json_err} - Response was: {error_details}"

def confirm_connection_data(search_query: str) -> str:
    """
    Confirms connection data based on a search query, parsing provider and multiple item names.
    Prompts for missing information if the query is incomplete.
    If confirmation is successful, it proceeds to call create_meter_data.
    If create_meter_data is successful, it proceeds to call create_er_house_hold.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the final successful API call or operation,
        or an error/prompt message string.
    """
    try:
        found_provider_name = None
        search_query_lower = search_query.lower()
            
        for p_name in provider_name_to_id.keys():
            if p_name.lower() in search_query_lower:
                found_provider_name = p_name
                break
        
        if not found_provider_name:
            return "Error: Could not identify a provider from your query. Please specify a provider name (e.g., 'San Francisco Electric Authority')."
        
        provider_id = provider_name_to_id[found_provider_name]

        # Parse Single Item for the found provider
        found_item_name = None
        single_item_id = None 

        provider_specific_items_map = provider_id_to_items.get(provider_id, {})
        if not provider_specific_items_map: # Should be rare if provider_id is valid and mappings are correct
             return f"Error: No items configured for provider '{found_provider_name}' (ID: {provider_id})."

        for i_name_key, i_id_val in provider_specific_items_map.items():
            if i_name_key.lower() in search_query_lower:
                # Found the first matching item for this provider
                found_item_name = i_name_key
                single_item_id = i_id_val
                break # Take the first match, similar to select/init and solar_retail logic
        
        if not single_item_id: # If no item was found for the provider
            available_items_names = list(provider_specific_items_map.keys())
            return (f"Error: No item specified or found for provider '{found_provider_name}' in your query. "
                    f"Available items for this provider: {', '.join(available_items_names) if available_items_names else 'No items available'}.")

        # item_ids_for_payload = [{"id": item["id"]} for item in found_items_details] # Old multi-item logic replaced
            
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        payload_dict = json.loads(CONFIRM_PAYLOAD_TEMPLATE)

        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp

        payload_dict["message"]["order"]["provider"]["id"] = provider_id
        # payload_dict["message"]["order"]["items"] = item_ids_for_payload # Old assignment
        if payload_dict["message"]["order"]["items"] and isinstance(payload_dict["message"]["order"]["items"], list) and len(payload_dict["message"]["order"]["items"]) > 0:
            payload_dict["message"]["order"]["items"][0]["id"] = single_item_id
        else:
            # Fallback or error if template structure is unexpected, though CONFIRM_PAYLOAD_TEMPLATE defines it.
            # This case should ideally not be hit if CONFIRM_PAYLOAD_TEMPLATE is as expected.
            payload_dict["message"]["order"]["items"] = [{"id": single_item_id}]
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_CONFIRM_ENDPOINT, data=current_payload, headers=headers)

        if response.status_code == 200:
            confirm_response_data = response.json()
            # Extract and store the order ID
            try:
                order_id = confirm_response_data['responses'][0]['message']['order']['id']
                order_ids.append(order_id)
            except (KeyError, IndexError, TypeError) as e:
                return f"Error extracting order_id from confirm response: {e} - Response was: {confirm_response_data}"
            
            # Call create_meter_data
            meter_data_output = create_meter_data(search_query) # Renamed variable

            if not isinstance(meter_data_output, dict):
                # If it's not a dict, it must be an error string from create_meter_data
                return meter_data_output 

            # Now, meter_data_output is confirmed to be a dictionary
            if "data" in meter_data_output and \
               isinstance(meter_data_output["data"], dict) and \
               "id" in meter_data_output["data"]:
                meter_id = meter_data_output["data"]["id"]
                print(f"A Meter with ID {meter_id} has been created")
            else:
                # The dict from create_meter_data didn't have the expected structure.
                print(f"Warning: Meter data response was a dictionary but ID could not be extracted or structure was unexpected. Response: {meter_data_output}")
                return f"Error: Meter creation response did not contain expected ID or had wrong structure. Response: {meter_data_output}"

            # If meter creation was successful (did not return an error string above), call create_er_house_hold
            er_household_output = create_er_house_hold(search_query) # Renamed variable

            if not isinstance(er_household_output, dict):
                # If it's not a dict, it must be an error string from create_er_house_hold
                return er_household_output
            
            # Now, er_household_output is confirmed to be a dictionary
            if "data" in er_household_output and \
               isinstance(er_household_output["data"], dict) and \
               "id" in er_household_output["data"]:
                er_id = er_household_output["data"]["id"]
                print(f"An ER Household with ID {er_id} has been created")
                # ER Household creation successful
                return "Connection was Successfull" # Final success
            else:
                print(f"Warning: ER household response was JSON but ID could not be extracted or structure was unexpected. Response: {er_household_output}")
                return f"Error: ER household creation response did not contain expected ID or had wrong structure. Response: {er_household_output}"
        else:
            # Handle non-200 status from the confirm API call itself
            error_details = ""
            try:
                error_details = response.text
            except Exception:
                pass
            return f"HTTP error from confirm API: {response.status_code} {response.reason} - {error_details}"

    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            if http_err.response: # Ensure response object exists
                 error_details = http_err.response.text
        except Exception:
            pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err: 
        error_details = ""
        # `response` might not be in scope if json.loads(CONFIRM_PAYLOAD_TEMPLATE) fails,
        # so we can't reliably use response.text here.
        return f"Error processing JSON payload or response: {json_err}"
    except Exception as e:
        # Catch any other unexpected errors
        return f"An unexpected error occurred in confirm_connection_data: {str(e)}"


def status_connection_data(search_query: str) -> str:
    """
    Searches for status data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all connection data.
    """
    try:
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        if not order_ids:
            return "Error: No order ID available to check status. Please confirm an order first."
        
        latest_order_id = order_ids[-1]

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        # ISO 8601 format timestamp with UTC timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        # Load the template as a dictionary to modify it
        payload_dict = json.loads(STATUS_PAYLOAD_TEMPLATE)

        # Update context
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = str(uuid.uuid4()) # Generate a new message_id for status request
        payload_dict["context"]["timestamp"] = timestamp
        
        # Update message with the latest order_id
        payload_dict["message"]["order_id"] = latest_order_id
        
        current_payload = json.dumps(payload_dict)


        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_STATUS_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Try to get more specific error information from the response body if available
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass # Ignore if response.text is not available or causes an error
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err:
        error_details = ""
        try:
            error_details = response.text
        except Exception:
            pass
        return f"Error decoding JSON response: {json_err} - Response was: {error_details}"
