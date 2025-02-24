import boto3
import json
from elasticsearch import Elasticsearch
import numpy as np
import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io
import time
import botocore

# Initialize AWS clients
rekognition = boto3.client("rekognition", region_name="ap-southeast-2")
bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-2')
ELASTIC_CLOUD_URL = "https://d055bd66cb6340cbaaf1e9955db841f7.us-central1.gcp.cloud.es.io:443"
USERNAME = "elastic"
PASSWORD = "uLko2QHYccbOJXVhUO1vq7f0"
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    basic_auth=(USERNAME, PASSWORD)
)

def process_image(img_bytes):
    """Convert WebP (or any format) to JPEG for Rekognition processing."""
    temp_buffer = io.BytesIO(img_bytes)
    img = Image.open(temp_buffer)

    # Convert to RGB (removes transparency)
    img = img.convert('RGB')

    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG', quality=95)
    
    return output_buffer.getvalue()


def store_embeddings(face_data):
    return es.index(
        index="missing_persons",
        body={
            "features": face_data["rekognition"]
        }
    )

def search_web_images(image):
    """Search news websites, extract images, and compare facial features."""
    print("Starting web search...")
    
    # Use the face_features directly as bytes for comparison
    source_bytes = base64.b64decode(image) if isinstance(image, str) else image
    
    search_urls = [
        'https://www.independent.ie/irish-news/missing-person-case-files-rise-by-38-to-reach-almost-900-active-garda-investigations/a1538496733.html',
        "https://www.cnn.com/world",
        "https://www.reuters.com/world",
        "https://www.straitstimes.com",
        "https://www.channelnewsasia.com",
        "https://www.todayonline.com",
        "https://www.asiaone.com",
        "https://news.google.com",
        "https://www.instagram.com/explore"
    ]

    
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for base_url in search_urls:
        print(f"Searching: {base_url}")
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            images = soup.find_all('img', src=True)
            
            for img in images:
                img_url = img.get('src')
                if img_url:
                    try:
                        img_response = requests.get(img_url, headers=headers)
                        web_image_bytes = process_image(img_response.content)
                        
                        comparison = rekognition.compare_faces(
                            SourceImage={"Bytes": source_bytes},
                            TargetImage={"Bytes": web_image_bytes},
                            SimilarityThreshold=70
                        )

                        if comparison.get('FaceMatches'):
                            match = {
                                "url": img_url,
                                "source": base_url,
                                "similarity": comparison['FaceMatches'][0]['Similarity']
                            }
                            matches.append(match)
                            print(f"✅ Match found! {img_url} (Similarity: {match['similarity']}%)")
                        else:
                            print(f"❌ No match for {img_url}")

                    except Exception as e:
                        print(f"Error comparing {img_url}: {str(e)}")

        except Exception as e:
            print(f"Error fetching {base_url}: {str(e)}")
            
    return matches

def analyze_case(face_data, matches):
    """Analyze case with improved rate limiting"""
    wait_time = 2  
    max_attempts = 1
    
    for attempt in range(max_attempts):
        try:
            prompt = f"""
            Analyze this missing person case:
            Face Data: {face_data}
            Potential Matches: {matches}
            Provide insights on whether these matches could potentially belong to the same individual.
            """
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                })
            )
            return json.loads(response['body'].read())['content']
            
        except botocore.exceptions.ClientError as e:
            if attempt < max_attempts - 1:
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                raise
    
    return "Analysis unavailable due to rate limiting"

# Base 64 encoding function
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# Test functions
def test_pipeline():
    print("Starting pipeline test...")
    
    # Test face detection and get face data
    # print("Testing face detection...")
    image_path = "./missing_persons/missingperson1.jpg"
    base64_image = image_to_base64(image_path)
    # print("Face detection results:", json.dumps(face_data, indent=2))
    
    # print("Testing storage...")
    # test_results = store_embeddings(face_data)
    # print("Storage results:", test_results)
    
    # Test search
    print("Testing search...")
    search_results = search_web_images(base64_image)
    print("Search results:", search_results)
    
    # Test insights
    print("Testing insights...")
    insights = analyze_case(base64_image, search_results)
    print("Insights:", insights)

if __name__ == "__main__":
    test_pipeline()