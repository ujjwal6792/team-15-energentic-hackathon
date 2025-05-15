import requests
from google.adk.agents import Agent
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timezone
import json

# Vertex AI specific imports
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

load_dotenv()

# API_UTILITY_ENDPOINT = os.getenv("base_url") + "utility/detailed"
API_UTILITY_ENDPOINT = "http://world-engine-team7.becknprotocol.io/meter-data-simulator/utility/detailed"
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_PROJECT_REGION = os.getenv("GOOGLE_PROJECT_REGION")
VERTEX_AI_INDEX_ID = os.getenv("VERTEX_AI_INDEX_ID")
VERTEX_AI_INDEX_ENDPOINT_ID = os.getenv("VERTEX_AI_INDEX_ENDPOINT_ID")
EMBEDDING_MODEL_ID = "text-embedding-005"

# --- Vertex AI Initialization ---
# Ensure GOOGLE_PROJECT_ID and GOOGLE_PROJECT_REGION are set in your .env file
if GOOGLE_PROJECT_ID and GOOGLE_PROJECT_REGION:
    aiplatform.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_PROJECT_REGION)
else:
    print("Warning: GOOGLE_PROJECT_ID or GOOGLE_PROJECT_REGION not set. Vertex AI features may not work.")

# --- In-memory cache for demo purposes ---
# In a production environment, replace this with a persistent key-value store (e.g., Firestore, Redis)
# to map vector IDs to the actual text data. This cache will reset on script restart.
VECTOR_STORE_CACHE = {}
# Define a distance threshold for considering a match relevant (Euclidean distance for normalized embeddings)
# Lower is more similar. Adjust based on experimentation.
SIMILARITY_THRESHOLD = 0.5


def get_text_embedding(text: str) -> list[float] | None:
    """Generates embedding for a given text using Vertex AI."""
    try:
        model = aiplatform.TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_ID)
        embeddings = model.get_embeddings([text])
        if embeddings and embeddings[0].values:
            return embeddings[0].values
        return None
    except Exception as e:
        print(f"Error generating text embedding: {e}")
        return None

def get_utility_data(search_query: str) -> str:
    """
    Gets utility data. Tries to fetch from Vertex AI Vector Search first.
    If not found or not relevant, calls the external API, then caches the result.
    Args:
        search_query: The query string to search for utility data.
    Returns:
        A string representation of the JSON response, either from cache or fresh from API.
    """
    if not all([GOOGLE_PROJECT_ID, GOOGLE_PROJECT_REGION, VERTEX_AI_INDEX_ID, VERTEX_AI_INDEX_ENDPOINT_ID]):
        print("Warning: Vertex AI configuration missing. Falling back to direct API call.")
        return _fetch_from_api(search_query)

    print(f"Searching utility data for: {search_query}")

    # 1. Generate embedding for the search query
    query_embedding = get_text_embedding(search_query)

    if not query_embedding:
        print("Failed to generate query embedding. Falling back to direct API call.")
        return _fetch_from_api(search_query)

    # 2. Query Vertex AI Vector Search
    try:
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=VERTEX_AI_INDEX_ENDPOINT_ID
        )
        # Deployments can have multiple deployed indexes, usually one.
        # The deployed_index_id is often the same as the index_id if not specified otherwise during deployment.
        # You might need to fetch this dynamically or ensure it's set correctly.
        # For now, we assume the default or a known deployed index ID.
        # If your endpoint has a specific deployed_index_id, use it below.
        # If not specified, the client library might pick the default one.

        match_response = index_endpoint.match(
            queries=[query_embedding],
            num_neighbors=1,
        )

        if match_response and match_response[0]:
            neighbor = match_response[0][0]
            matched_id = neighbor.id
            distance = neighbor.distance
            print(f"Vector store potential match: ID={matched_id}, Distance={distance}")

            if distance < SIMILARITY_THRESHOLD:
                if matched_id in VECTOR_STORE_CACHE:
                    print(f"Cache hit! Returning data for ID: {matched_id} from local demo cache.")
                    return VECTOR_STORE_CACHE[matched_id]
                else:
                    print(f"ID {matched_id} found in vector store, but not in local demo cache. This might happen after a restart. Fetching fresh.")
            else:
                print(f"Match found (ID: {matched_id}) but distance {distance} exceeds threshold {SIMILARITY_THRESHOLD}.")

    except Exception as e:
        print(f"Error querying Vertex AI Vector Search: {e}. Falling back to API.")

    # 3. If not found in cache or not relevant, fetch from API and update vector store
    print("Cache miss or no relevant match. Fetching from API.")
    api_response_json = _fetch_from_api_json(search_query)

    if isinstance(api_response_json, str) and api_response_json.startswith("Error:"):
        return api_response_json

    try:
        api_response_text = json.dumps(api_response_json)
    except TypeError as e:
        print(f"Error serializing API response to JSON string: {e}")
        return f"Error: Could not serialize API response. {e}"

    # 4. Generate embedding for the API response
    response_embedding = get_text_embedding(api_response_text)

    if response_embedding:
        # 5. Upsert to Vertex AI Vector Search
        try:
            index = aiplatform.MatchingEngineIndex(index_name=VERTEX_AI_INDEX_ID)
            new_doc_id = uuid.uuid4().hex
            
            datapoint = aiplatform.MatchingEngineIndexDatapoint(
                datapoint_id=new_doc_id,
                feature_vector=response_embedding
            )
            index.upsert_datapoints(datapoints=[datapoint])

            VECTOR_STORE_CACHE[new_doc_id] = api_response_text
            print(f"Upserted to Vertex AI Vector Search with ID: {new_doc_id} and updated local demo cache.")
        except Exception as e:
            print(f"Error upserting to Vertex AI Vector Search: {e}")
            # Continue to return the API response even if upsert fails
    else:
        print("Failed to generate embedding for API response. Skipping vector store update.")

    return api_response_text

def _fetch_from_api_json(search_query: str) -> dict | str:
    """Helper function to fetch data from the API and return JSON object or error string."""
    try:
        params = {"q": search_query}
        response = requests.get(API_UTILITY_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return f"Error: API request failed. {e}"
    except json.JSONDecodeError as e:
        print(f"Failed to decode API JSON response: {e}")
        return f"Error: API response was not valid JSON. {e}"

# Keep a version that just returns string for cases where Vertex AI is not configured
def _fetch_from_api(search_query: str) -> str:
    """Directly fetches from API and returns string representation of JSON or error."""
    result = _fetch_from_api_json(search_query)
    if isinstance(result, str) and result.startswith("Error:"):
        return result
    try:
        return json.dumps(result)
    except TypeError as e:
        print(f"Error serializing API response to JSON string (fallback): {e}")
        return f"Error: Could not serialize API response (fallback). {e}"


        
