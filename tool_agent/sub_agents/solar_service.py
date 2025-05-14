import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone

load_dotenv()

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
                "id": "329"
            },
            "items": [
                {
                    "id": "466"
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
                "id": "329"
            },
            "items": [
                {
                    "id": "466"
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
        "timestamp": "{{timestampp}}"
    },
    "message": {
        "order": {
            "provider": {
                "id": "329"
            },
            "items": [
                {
                    "id": "466"
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
        "order_id": "3774"
    }
}
"""

def search_solar_service_data(search_query: str) -> str:
    """
    Searches for solar service data based on a given search query.
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
    
def select_solar_service_data(search_query: str) -> str:
    """
    Selects for solar service data based on a given search query.
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

        current_payload = SELECT_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
                                     .replace("{{message_id}}", message_id) \
                                     .replace("{{timestamp}}", timestamp)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_SELECT_ENDPOINT, data=current_payload, headers=headers)
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
    
def init_solar_service_data(search_query: str) -> str:
    """
    Initializes for solar service data based on a given search query.
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

        current_payload = INIT_PAYLOAD_TEMPLATE.replace("{{bap_id}}", bap_id) \
                                     .replace("{{bap_uri}}", bap_uri) \
                                     .replace("{{bpp_id}}", bpp_id) \
                                     .replace("{{bpp_uri}}", bpp_uri) \
                                     .replace("{{transaction_id}}", transaction_id) \
                                     .replace("{{message_id}}", message_id) \
                                     .replace("{{timestamp}}", timestamp)

        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_INITIATE_ENDPOINT, data=current_payload, headers=headers)
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
    
def confirm_solar_service_data(search_query: str) -> str:
    """
    Confirms solar service data based on a given search query.
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
    
def status_solar_service_data(search_query: str) -> str:
    """
    Searches for status data for solar service based on a given search query.
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