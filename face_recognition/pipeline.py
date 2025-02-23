import boto3
import json
from elasticsearch import Elasticsearch
import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup

# Initialize AWS clients
rekognition = boto3.client("rekognition", region_name="us-east-1")
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
ELASTIC_CLOUD_URL = "https://d055bd66cb6340cbaaf1e9955db841f7.us-central1.gcp.cloud.es.io:443"
USERNAME = "elastic"
PASSWORD = "uLko2QHYccbOJXVhUO1vq7f0"
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    basic_auth=(USERNAME, PASSWORD)
)

# Getting base64 image from database
def get_image_from_db():
    index_name = "missing_persons"
    
    query = {
        "query": {
            "term": {  # Use term for exact match
                "id.keyword": "person1"  
            }
        }
    }

    try:
        response = es.search(index=index_name, body=query)
        if response["hits"]["hits"]:
            document = response["hits"]["hits"][0]  # Get the first match
            base64 = document["_source"]["base64Image"]
            print("Document Found:", base64)
        else:
            print("No matching document found.")
    except Exception as e:
        print("Error fetching document:", e)

get_image_from_db()

print("\n")

def search_web_images(face_features):
    # Search across news sites and social media
    search_urls = [
        "https://news.google.com",
        "https://twitter.com/search",
        "https://www.instagram.com/explore"
    ]
    
    matches = []
    for url in search_urls:
        # Scrape images from each source
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')
        
        # Compare faces in found images
        for img in images:
            img_url = img.get('src')
            if img_url:
                img_data = requests.get(img_url).content
                comparison = rekognition.compare_faces(
                    SourceImage={"Bytes": face_features},
                    TargetImage={"Bytes": img_data}
                )
                if comparison['FaceMatches']:
                    matches.append({
                        "url": img_url,
                        "source": url,
                        "similarity": comparison['FaceMatches'][0]['Similarity']
                    })
    
    # Store results in Elasticsearch
    for match in matches:
        es.index(
            index="web_matches",
            body=match
        )
    
    return matches

def process_missing_person(image_path):
    # Extract face features including the multilingual embeddings that will enable searching across multiple languages so a larger data pool can be searched
    face_embedding = extract_face_features(image_path) 

    # Store embeddings in Elasticsearch 
    doc_id = store_embeddings(face_embedding)
    matches = search_web_images(image_path)
    insights = analyze_case(face_embedding, matches)
    
    return {
        "case_id": doc_id,
        "matches": matches,
        "insights": insights
    }

def extract_face_features(image_path):
    with open(image_path, "rb") as image:
        rekognition_features = rekognition.detect_faces(
            Image={"Bytes": image.read()},
            Attributes=["ALL"]
        )
    
    # Convert Rekognition features to a string (for Cohere)
    text_description = str(rekognition_features["FaceDetails"])
    
    # Use Cohere to get embeddings (multilingual support)
    response = bedrock.invoke_model(
        modelId='cohere.embed-multilingual-v3',
        body=json.dumps({
            'texts': [text_description]
        })
    )

    multilingual_embedding = json.loads(response['body'].read())['embeddings'][0]
    
    return {
        "rekognition": rekognition_features,
        "embedding": multilingual_embedding
    }

def store_embeddings(face_data):
    return es.index(
        index="missing_persons",
        body={
            "embedding": face_data["embedding"],
            "features": face_data["rekognition"]
        }
    )

def analyze_case(face_data, matches):
    prompt = f"""
    Analyze this missing person case:

    Face Data: {face_data}
    Potential Matches: {matches}

    Provide insights on whether these matches could potentially belong to the same individual.
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        })
    )
    
    return json.loads(response['body'].read())['completion']

def test_pipeline():
    print("Starting pipeline test...")
    
    # Test face detection and get face data
    print("Testing face detection...")
    face_data = extract_face_features("./missing_persons/missingperson1.jpg")  
    print("Face detection results:", json.dumps(face_data, indent=2))
    
    print("Testing storage...")
    test_results = store_embeddings(face_data)
    print("Storage results:", test_results)
    
    # Test search
    print("Testing search...")
    search_results = search_web_images("./missing_persons/missingperson1.jpg")
    print("Search results:", search_results)
    
    # Test insights
    print("Testing insights...")
    insights = analyze_case(face_data, search_results)
    print("Insights:", insights)

# if __name__ == "__main__":
#     test_pipeline()


