import requests
import os
import base64
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from pipeline import extract_face_features
# Load environment variables from .env file
load_dotenv()

# Google Custom Search API Key & Search Engine ID
API_KEY = os.getenv("API_KEY") 
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Load credentials from environment variables or define directly
ELASTICSEARCH_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTIC_CLOUD_USERNAME")  # Replace with actual username
ELASTICSEARCH_PASSWORD = os.getenv("ELASTIC_CLOUD_PASSWORD")  # Replace with actual password

# Connect to Elasticsearch with authentication
es = Elasticsearch(
    ELASTICSEARCH_URL,
    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
)

# Test connection
if es.ping():
    print("Connected to Elasticsearch successfully!")
else:
    print("Failed to connect to Elasticsearch")


def google_image_search(query, num_images=5, index_name="image_index_facefeatures"):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": SEARCH_ENGINE_ID,
        "key": API_KEY,
        "searchType": "image",
        "num": num_images
    }

    response = requests.get(url, params=params).json()

    for item in response.get("items", []):
        image_url = item["link"]
        source_page = item["image"]["contextLink"]

        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            # Encode image in base64 for extraction
            img_base64 = base64.b64encode(img_response.content).decode('utf-8')

            # Extract face features
            face_features = extract_face_features(img_base64)
            print(face_features)

            doc = {
                "query": query,
                "image_url": image_url,
                "source_page": source_page,
                "status": "success",
                "number_faces_found" : len(face_features),
                "face_features": face_features,
            }

            es.index(index=index_name, body=doc)
            print(f"Stored in Elasticsearch: {image_url}")

        except Exception as e:
            print(f"Failed to process {image_url}: {e}")

def store_images_in_elasticsearch(image_data, index_name="image_index_facefeatures"):
    """Store image metadata in Elasticsearch"""
    if not image_data:
        print("No images found.")
        return

    for doc in image_data:
        es.index(index=index_name, body=doc)
        print(f"Stored in Elasticsearch: {doc}")

# Example Usage == CHANGE QUERY TO SEARCH FOR DIFFERENT IMAGES
query = "Wu Enjia"
image_data = google_image_search(query, num_images=5)
store_images_in_elasticsearch(image_data)
