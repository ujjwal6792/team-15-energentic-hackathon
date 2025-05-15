import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json # Added for loading string templates as JSON

load_dotenv()

# Mappings for Demand Flexibility Program
provider_name_to_id = {
    "Pacific Gas and Electric Company (PG&E)": "323"
}
provider_id_to_items = {
    "323": [
        {
            "name": "Home Battery Discharge Program",
            "id": "458"
        }
    ]
}

# Global list to store DFP order IDs
dfp_order_ids = []

API_SEARCH_ENDPOINT = os.getenv("base_url") + "search"
API_CONFIRM_ENDPOINT = os.getenv("base_url") + "confirm"
API_STATUS_ENDPOINT = os.getenv("base_url") + "status"

# mapping for dfp provider -> id

SEARCH_PAYLOAD_TEMPLATE = """
{
    "context": {
        "domain": "deg:schemes",
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
                    "name": "Program"
                }
            }
        }
    }
}
"""

CONFIRM_PAYLOAD_TEMPLATE = """
{
  "context": {
    "domain": "deg:schemes",
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
          "id": "616",
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
    "domain": "deg:schemes",
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

def search_demand_flexibility_program_data(search_query: str) -> str:
    """
    Searches for demand flexibility program data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all demand flexibility program data.
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


def confirm_demand_flexibility_program_data(search_query: str) -> str:
    """
    Confirms demand flexibility program data based on a given search query,
    parsing provider and item names and using mappings to find IDs.
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
        
        for p_id_map, item_list in provider_id_to_items.items():
            for item_dict in item_list:
                if item_dict["name"].lower() in search_query_lower:
                    found_item_name = item_dict["name"]
                    if found_provider_name and provider_name_to_id.get(found_provider_name) == p_id_map:
                        break
                    elif not found_provider_name:
                        break
            if found_item_name and (not found_provider_name or provider_name_to_id.get(found_provider_name) == p_id_map):
                 break

        if not found_provider_name and not found_item_name:
            return "Error: Could not identify a provider or item. Please specify provider (e.g., 'Pacific Gas and Electric Company (PG&E)') and item (e.g., 'Home Battery Discharge Program')."

        if found_provider_name and not found_item_name:
            provider_id_for_items = provider_name_to_id[found_provider_name]
            available_items_list = provider_id_to_items.get(provider_id_for_items, [])
            available_items_names = [item["name"] for item in available_items_list]
            if not available_items_names:
                 return f"Error: No items found for provider '{found_provider_name}'."
            return f"Error: Please specify item for '{found_provider_name}'. Available: {', '.join(available_items_names)}."

        if not found_provider_name and found_item_name:
            possible_providers = []
            for p_name_map, p_id_val_map in provider_name_to_id.items():
                items_for_this_provider = provider_id_to_items.get(p_id_val_map, [])
                if any(item_dict["name"] == found_item_name for item_dict in items_for_this_provider):
                    possible_providers.append(p_name_map)
            if possible_providers:
                return f"Error: Please specify provider for '{found_item_name}'. Available from: {', '.join(list(set(possible_providers)))}."
            else: 
                return f"Error: Item '{found_item_name}' found, but no associated provider."

        provider_id = provider_name_to_id.get(found_provider_name)
        item_id = None
        if provider_id and provider_id in provider_id_to_items:
            for item_detail in provider_id_to_items[provider_id]:
                if item_detail["name"] == found_item_name:
                    item_id = item_detail["id"]
                    break
        
        if not item_id:
            actual_items_list = provider_id_to_items.get(provider_id, [])
            actual_items_names = [item["name"] for item in actual_items_list]
            return (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                    f"Available items: {', '.join(actual_items_names) if actual_items_names else 'No items'}.")

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
            dfp_order_ids.append(order_id_val)
        except (KeyError, IndexError, TypeError) as e:
            print(f"Warning: Could not extract order_id from DFP confirm response: {e} - Response: {confirm_response_data}")
        
        return confirm_response_data
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


def status_demand_flexibility_program_data(search_query: str) -> str:
    """
    Searches for status data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all demand flexibility program data.
    """
    try:
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        if not dfp_order_ids:
            return "Error: No DFP order ID available for status. Please confirm a DFP order first."
        
        latest_order_id = dfp_order_ids[-1]

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
    


