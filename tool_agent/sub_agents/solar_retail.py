import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json # Added for loading string templates as JSON
from .der import create_der

load_dotenv()

# --- Mappings for Solar Retail ---
provider_name_to_id = {
    "Bluebird Solar Panel": "27"
}
provider_id_to_items = {
    "27": {
        "5KW Solar Panel System – Polycrystalline & Mono PERC": "33"
    }
}

# Global list to store Solar Retail order IDs
solar_retail_order_ids = []
# --- End Mappings ---

API_CONFIRM_ENDPOINT = os.getenv("base_url") + "confirm"
API_SEARCH_ENDPOINT = os.getenv("base_url") + "search"
API_SELECT_ENDPOINT = os.getenv("base_url") + "select"
API_INITIATE_ENDPOINT = os.getenv("base_url") + "init"
API_STATUS_ENDPOINT = os.getenv("base_url") + "status"

SEARCH_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:retail",
        "action": "search",
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
        "intent": {
            "item": {
                "descriptor": {
                    "name": "solar"
                }
            }
        }
    }
}
"""

SELECT_PAYLOAD_TEMPLATE = """
{
  "context": {
    "domain": "deg:retail",
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

INIT_PAYLOAD_TEMPLATE = """
{
  "context": {
    "domain": "deg:retail",
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
    "domain": "deg:retail",
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
          "id": "3",
          "customer": {
            "person": {
              "name": "Mudit"
            },
            "contact": {
              "phone": "9714927300",
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
    "domain": "deg:retail",
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
    "order_id": "{{order_id}}"
  }
}
"""

def _extract_provider_and_item_solar_retail(search_query: str):
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
        return None, None, "Error: Could not identify provider or item. Please specify provider (e.g., 'Bluebird Solar Panel') and item (e.g., '5KW Solar Panel System – Polycrystalline & Mono PERC')."

    if found_provider_name and not found_item_name:
        provider_id_for_items = provider_name_to_id[found_provider_name]
        available_items = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
        if not available_items:
                return None, None, f"Error: No items found for provider '{found_provider_name}'."
        return None, None, f"Error: Please specify item for provider '{found_provider_name}'. Available items: {', '.join(available_items)}."

    if not found_provider_name and found_item_name:
        possible_providers = []
        for p_name, p_id_val in provider_name_to_id.items():
            if found_item_name in provider_id_to_items.get(p_id_val, {}):
                possible_providers.append(p_name)
        if possible_providers:
            return None, None, f"Error: Please specify provider for item '{found_item_name}'. Available from: {', '.join(possible_providers)}."
        else:
            return None, None, f"Error: Item '{found_item_name}' found, but no associated provider."

    provider_id = provider_name_to_id.get(found_provider_name)
    item_id = provider_id_to_items.get(provider_id, {}).get(found_item_name)

    if not item_id:
        actual_items = list(provider_id_to_items.get(provider_id, {}).keys())
        return None, None, (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                           f"Available items: {', '.join(actual_items) if actual_items else 'No items'}.")
    
    return provider_id, item_id, None


def search_solar_retail_data(search_query: str) -> str:
    """
    Searches for solar retail data based on a given search query.
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
        timestamp = datetime.now(timezone.utc).isoformat()
        
        payload_dict = json.loads(SEARCH_PAYLOAD_TEMPLATE)
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp
        # search_query is not used to modify descriptor.name for solar retail search
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_SEARCH_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try: error_details = response.text
        except Exception: pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err: # Catches json.loads or response.json() errors
        error_details = ""
        try: 
            if 'response' in locals() and hasattr(response, 'text'): error_details = response.text
        except Exception: pass
        return f"Error decoding JSON: {json_err} - Response: {error_details}"

    
def select_solar_retail_data(search_query: str) -> str:
    """
    Selects solar retail data based on provider and item names in search_query.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_retail(search_query)
        if error_msg:
            return error_msg

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
        try: error_details = response.text
        except Exception: pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err: 
        error_details = ""
        try: 
            if 'response' in locals() and hasattr(response, 'text'): error_details = response.text
        except Exception: pass
        return f"Error decoding JSON: {json_err} - Response: {error_details}"

    
def init_solar_retail_data(search_query: str) -> str:
    """
    Initializes solar retail order based on provider and item names in search_query.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_retail(search_query)
        if error_msg:
            return error_msg

        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        payload_dict = json.loads(INIT_PAYLOAD_TEMPLATE)
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
        try: error_details = response.text
        except Exception: pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err:
        error_details = ""
        try: 
            if 'response' in locals() and hasattr(response, 'text'): error_details = response.text
        except Exception: pass
        return f"Error decoding JSON: {json_err} - Response: {error_details}"

    
def confirm_solar_retail_data(search_query: str) -> str:
    """
    Confirms solar retail order based on provider and item names in search_query.
    Stores order ID on success.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_retail(search_query)
        if error_msg:
            return error_msg

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
        payload_dict["message"]["order"]["items"][0]["id"] = item_id
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_CONFIRM_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        
        confirm_response_data = response.json()
        try:
            order_id_val = confirm_response_data['responses'][0]['message']['order']['id']
            solar_retail_order_ids.append(order_id_val)
        except (KeyError, IndexError, TypeError) as e:
            print(f"Warning: Could not extract order_id from Solar Retail confirm response: {e} - Response: {confirm_response_data}")
            # Decide if this should be a critical error or just a warning
        
        # Call create_der if the API call was successful
        der_creation_response = create_der(search_query)
        
        # Attempt to parse der_creation_response and log the DER ID
        try:
            # Assuming der_creation_response is a JSON string from create_der
            der_response_data = json.loads(der_creation_response)
            if isinstance(der_response_data, dict) and "id" in der_response_data:
                der_id = der_response_data["id"]
                print(f"A DER with ID {der_id} has been created")
            elif isinstance(der_response_data, dict) and "data" in der_response_data and isinstance(der_response_data["data"], dict) and "id" in der_response_data["data"]: # Handling nested structure
                der_id = der_response_data["data"]["id"]
                print(f"A DER with ID {der_id} has been created")
            else:
                # This case handles when create_der returns an error string directly,
                # or if the JSON structure is not as expected.
                print(f"Warning: Could not extract DER ID. Response from create_der: {der_creation_response}")
        except json.JSONDecodeError:
            # This handles cases where der_creation_response is not a valid JSON string
            # (e.g., it's an error message like "Error: No energy resource IDs available...")
            print(f"Warning: der_creation_response was not valid JSON. Response: {der_creation_response}")
        except Exception as e:
            # Catch any other unexpected errors during parsing/id extraction
            print(f"Warning: An unexpected error occurred while processing der_creation_response: {e}. Response: {der_creation_response}")

        # Add der_creation_response to the main response
        # We need to ensure confirm_response_data is a dict. If it's a list (e.g. from some API structures), adapt accordingly.
        if isinstance(confirm_response_data, dict):
            confirm_response_data["der_creation_status"] = der_creation_response
        else:
            # If confirm_response_data is not a dict (e.g., a list or string),
            # we might need to structure this differently or log a warning.
            # For now, let's assume it's usually a dict, or we'll create a new dict.
            # This part might need adjustment based on actual API response structure.
            print(f"Warning: confirm_response_data is not a dict, der_creation_status will be added to a new dict wrapper.")
            confirm_response_data = {
                "original_confirm_response": confirm_response_data,
                "der_creation_status": der_creation_response
            }
            
        return confirm_response_data
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try: error_details = response.text
        except Exception: pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err:
        error_details = ""
        try: 
            if 'response' in locals() and hasattr(response, 'text'): error_details = response.text
        except Exception: pass
        return f"Error decoding JSON: {json_err} - Response: {error_details}"

    
def status_solar_retail_data(search_query: str) -> str: # search_query is not used here, but kept for consistency
    """
    Gets status for the latest confirmed solar retail order.
    """
    try:
        if not solar_retail_order_ids:
            return "Error: No Solar Retail order ID available for status. Please confirm an order first."
        latest_order_id = solar_retail_order_ids[-1]

        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        payload_dict = json.loads(STATUS_PAYLOAD_TEMPLATE)
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp
        payload_dict["message"]["order_id"] = latest_order_id
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_STATUS_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try: error_details = response.text
        except Exception: pass
        return f"HTTP error occurred: {http_err} - {error_details}"
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"
    except ValueError as json_err:
        error_details = ""
        try: 
            if 'response' in locals() and hasattr(response, 'text'): error_details = response.text
        except Exception: pass
        return f"Error decoding JSON: {json_err} - Response: {error_details}"