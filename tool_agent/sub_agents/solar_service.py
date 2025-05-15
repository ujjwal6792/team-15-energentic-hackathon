import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json

load_dotenv()

# --- Mappings for Solar Service ---
provider_name_to_id = {
    "Luminalt": "329",
    "Sunrun": "330",
    "Infinity Energy": "331",
    "SolarUnion": "332",
    "Horizon Solar Power": "333",
    "San Francisco Electric Authority": "334", # Note: This provider might be duplicated if also in connection.py
}
provider_id_to_items = {
    "329": {
        "sp-resi-001": "466"
    },
    "330": {
        "sp-resi-002": "467"
    },
    "331": {
        "sp-resi-003": "468"
    },
    "332": {
        "sp-resi-004": "469"
    },
    "333": {
        "sp-resi-005": "470"
    },
    "334": {
        "Residential Electricity Connection6": "471" # Item name might need review for uniqueness/clarity
    },
}

# Global list to store Solar Service order IDs
solar_service_order_ids = []
# --- End Mappings ---

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
            "descriptor": {
                "name": "resi" 
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

INIT_PAYLOAD_TEMPLATE = """
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
                    "id": "617",
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
        "order_id": "{{order_id}}"
    }
}
"""

def _extract_provider_and_item_solar_service(search_query: str):
    found_provider_name = None
    found_item_name = None
    search_query_lower = search_query.lower()

    for p_name in provider_name_to_id.keys():
        if p_name.lower() in search_query_lower:
            found_provider_name = p_name
            break
    
    # Adjusted item search for solar_service structure
    for p_id_map, items_map in provider_id_to_items.items():
        for i_name in items_map.keys(): # i_name is like "sp-resi-001"
            if i_name.lower() in search_query_lower:
                found_item_name = i_name
                if found_provider_name and provider_name_to_id.get(found_provider_name) == p_id_map:
                    break 
                elif not found_provider_name:
                    break 
        if found_item_name and (not found_provider_name or provider_name_to_id.get(found_provider_name) == p_id_map):
            break
            
    if not found_provider_name and not found_item_name:
        return None, None, "Error: Could not identify a provider or item. Please specify provider (e.g., 'Luminalt') and item (e.g., 'sp-resi-001')."

    if found_provider_name and not found_item_name:
        provider_id_for_items = provider_name_to_id[found_provider_name]
        available_items = list(provider_id_to_items.get(provider_id_for_items, {}).keys())
        if not available_items:
            return None, None, f"Error: No items found for provider '{found_provider_name}'."
        return None, None, f"Error: Please specify the item for provider '{found_provider_name}'. Available items: {', '.join(available_items)}."

    if not found_provider_name and found_item_name:
        possible_providers = []
        for p_name, p_id_val in provider_name_to_id.items():
            if found_item_name in provider_id_to_items.get(p_id_val, {}):
                possible_providers.append(p_name)
        if possible_providers:
            return None, None, f"Error: Please specify the provider for item '{found_item_name}'. This item is available from: {', '.join(possible_providers)}."
        else: 
            return None, None, f"Error: Item '{found_item_name}' found, but no associated provider. Please also specify a provider name."

    provider_id = provider_name_to_id.get(found_provider_name)
    item_id = provider_id_to_items.get(provider_id, {}).get(found_item_name)

    if not item_id:
        actual_items = list(provider_id_to_items.get(provider_id, {}).keys())
        return None, None, (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                           f"Available items for this provider: {', '.join(actual_items) if actual_items else 'No items available'}.")
    
    return provider_id, item_id, None


def search_solar_service_data(search_query: str) -> str:
    """
    Searches for solar service data based on a given search query.
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
        # search_query can be used to modify payload_dict["message"]["intent"]["descriptor"]["name"] if needed
        # For now, it uses the default "resi"
        
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

    
def select_solar_service_data(search_query: str) -> str:
    """
    Selects solar service data based on provider and item names in search_query.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_service(search_query)
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

    
def init_solar_service_data(search_query: str) -> str:
    """
    Initializes solar service order based on provider and item names in search_query.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_service(search_query)
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

    
def confirm_solar_service_data(search_query: str) -> str:
    """
    Confirms solar service order based on provider and item names in search_query.
    Stores order ID on success.
    """
    try:
        provider_id, item_id, error_msg = _extract_provider_and_item_solar_service(search_query)
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
            solar_service_order_ids.append(order_id_val)
        except (KeyError, IndexError, TypeError) as e:
            print(f"Warning: Could not extract order_id from Solar Service confirm response: {e} - Response: {confirm_response_data}")

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

    
def status_solar_service_data(search_query: str) -> str: # search_query is not used here
    """
    Gets status for the latest confirmed solar service order.
    """
    try:
        if not solar_service_order_ids:
            return "Error: No Solar Service order ID available. Please confirm an order first."
        latest_order_id = solar_service_order_ids[-1]

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