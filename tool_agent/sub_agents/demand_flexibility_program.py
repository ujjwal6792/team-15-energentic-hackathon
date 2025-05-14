import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone

load_dotenv()

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
                "id": "323"
            },
            "items": [
                {
                    "id": "458"
                  
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
"order_id": "3776"

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
    Confirms demand flexibility program data based on a given search query.
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

        current_payload = CONFIRM_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
                                     .replace("{{message_id}}", message_id) \
                                     .replace("{{timestamp}}", timestamp)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_CONFIRM_ENDPOINT, data=current_payload, headers=headers)
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

        transaction_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        # ISO 8601 format timestamp with UTC timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        current_payload = STATUS_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
                                     .replace("{{message_id}}", message_id) \
                                     .replace("{{timestamp}}", timestamp)

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
    


