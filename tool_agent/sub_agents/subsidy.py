import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json # Added for loading string templates as JSON

load_dotenv()

# Global list to store subsidy order IDs
subsidy_order_ids = []

# Provided Mappings
provider_name_to_id = {
    "SF Department of Energy Support": "335"
}
provider_id_to_items = {
    "335": [
        {
            "name": "Smart EV Charger Load-Balancing Incentive",
            "id": "474"
        }
    ]
}

API_CONFIRM_ENDPOINT = os.getenv("base_url") + "confirm"
API_SEARCH_ENDPOINT = os.getenv("base_url") + "search"
API_STATUS_ENDPOINT = os.getenv("base_url") + "status"


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
SEARCH_PAYLOAD_TEMPLATE = """{
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
        
        "timestamp": "{{timestamp}}"
    },
    "message": {
        "intent": {
            "item": {
                "descriptor": {
                    "name": "incentive"
                }
            }
        }
    }
} """

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

def confirm_subsidies_data(search_query: str) -> str:
    """
    Confirms a specific subsidy item from a provider based on a search query.
    Parses provider and item names from the query, prompts for missing info if necessary.
    This function will be used as a tool by the agent.

    Args:
        search_query: A string containing the provider and/or item name.

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
        for p_id_map, item_list in provider_id_to_items.items():
            for item_dict in item_list:
                if item_dict["name"].lower() in search_query_lower:
                    found_item_name = item_dict["name"]
                    # If we also found a provider, check if this item belongs to it
                    if found_provider_name and provider_name_to_id.get(found_provider_name) == p_id_map:
                        break  # Item matches provider
                    elif not found_provider_name:
                        # If no provider yet, take this item
                        break
            if found_item_name and (not found_provider_name or provider_name_to_id.get(found_provider_name) == p_id_map):
                 break

        if not found_provider_name and not found_item_name:
            return "Error: Could not identify a provider or item from your query. Please specify a provider name (e.g., 'SF Department of Energy Support') and an item name (e.g., 'Smart EV Charger Load-Balancing Incentive')."

        if found_provider_name and not found_item_name:
            provider_id_for_items = provider_name_to_id[found_provider_name]
            available_items_list = provider_id_to_items.get(provider_id_for_items, [])
            available_items_names = [item["name"] for item in available_items_list]
            if not available_items_names:
                 return f"Error: No items found for provider '{found_provider_name}'. Please check the provider name or available services."
            return f"Error: Please specify the item for provider '{found_provider_name}'. Available items: {', '.join(available_items_names)}."

        if not found_provider_name and found_item_name:
            possible_providers = []
            for p_name_map, p_id_val_map in provider_name_to_id.items():
                items_for_this_provider = provider_id_to_items.get(p_id_val_map, [])
                for item_dict in items_for_this_provider:
                    if item_dict["name"] == found_item_name: # Exact match as found_item_name is from mapping
                        possible_providers.append(p_name_map)
                        break 
            if possible_providers:
                return f"Error: Please specify the provider for item '{found_item_name}'. This item is available from: {', '.join(list(set(possible_providers)))}."
            else: 
                return f"Error: Item '{found_item_name}' found, but no associated provider. Please also specify a provider name."

        # Both provider and item name are supposedly found
        provider_id = provider_name_to_id.get(found_provider_name)
        item_id = None
        
        # Validate if the found item name actually belongs to the found provider and get its ID
        if provider_id and provider_id in provider_id_to_items:
            for item_detail in provider_id_to_items[provider_id]:
                if item_detail["name"] == found_item_name: # Compare with the exact name from mapping
                    item_id = item_detail["id"]
                    break
        
        if not item_id:
            provider_id_for_items = provider_name_to_id[found_provider_name] # re-fetch to be sure
            actual_items_for_provider_list = provider_id_to_items.get(provider_id_for_items, [])
            actual_items_names = [item["name"] for item in actual_items_for_provider_list]
            return (f"Error: Item '{found_item_name}' is not valid for provider '{found_provider_name}'. "
                    f"Available items for this provider: {', '.join(actual_items_names) if actual_items_names else 'No items available'}.")

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

        payload_dict = json.loads(CONFIRM_PAYLOAD_TEMPLATE)
        
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
        payload_dict["context"]["timestamp"] = timestamp
        
        payload_dict["message"]["order"]["provider"]["id"] = provider_id
        payload_dict["message"]["order"]["items"][0]["id"] = item_id # Assumes one item in template
        
        current_payload = json.dumps(payload_dict)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_CONFIRM_ENDPOINT, data=current_payload, headers=headers)
        response.raise_for_status()
        confirm_response_data = response.json()
        # Extract and store the order ID
        try:
            order_id = confirm_response_data['responses'][0]['message']['order']['id']
            subsidy_order_ids.append(order_id)
        except (KeyError, IndexError, TypeError) as e:
            # Log the error and the response for debugging, but proceed as confirm might be successful otherwise
            print(f"Warning: Could not extract order_id from subsidy confirm response: {e} - Response: {confirm_response_data}")
            # Depending on requirements, you might want to return an error here or just log
        
        return confirm_response_data # Return the full response
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
        # This can happen from json.loads or if response.json() fails
        error_details = ""
        # Avoid NameError if 'response' is not defined (e.g. json.loads(CONFIRM_PAYLOAD_TEMPLATE) fails)
        try:
            if 'response' in locals() and hasattr(response, 'text'):
                error_details = response.text 
        except Exception:
            pass
        return f"Error processing JSON payload or response: {json_err} - Details: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def search_subsidies_data(search_query: str) -> str:
    """
    Searches for subsidies data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all subsidies.
    """
    try:
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        transaction_id = str(uuid.uuid4())

        # ISO 8601 format timestamp with UTC timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        current_payload = SEARCH_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
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
    

def status_subsidies_data(search_query: str) -> str:
    """
    Searches for status data based on a given search query.
    This function will be used as a tool by the agent.

     Returns:
        A string representation of the JSON response from the API, containing all subsidies status data.
    """
    try:
        bap_id = os.getenv("bap_id")
        bap_uri = os.getenv("bap_uri")
        bpp_id = os.getenv("bpp_id")
        bpp_uri = os.getenv("bpp_uri")

        if not all([bap_id, bap_uri, bpp_id, bpp_uri]):
            return "Error: BAP_ID, BAP_URI, BPP_ID, or BPP_URI environment variables are not set."

        if not subsidy_order_ids:
            return "Error: No order ID available to check status. Please confirm a subsidy order first."
        
        latest_order_id = subsidy_order_ids[-1]

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4()) # New message_id for status request
        timestamp = datetime.now(timezone.utc).isoformat()

        # Load the template as a dictionary to modify it
        payload_dict = json.loads(STATUS_PAYLOAD_TEMPLATE)

        # Update context
        payload_dict["context"]["bap_id"] = bap_id
        payload_dict["context"]["bap_uri"] = bap_uri
        payload_dict["context"]["bpp_id"] = bpp_id
        payload_dict["context"]["bpp_uri"] = bpp_uri
        payload_dict["context"]["transaction_id"] = transaction_id
        payload_dict["context"]["message_id"] = message_id
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

