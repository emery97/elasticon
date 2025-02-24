import boto3
import json
from elasticsearch import Elasticsearch
import numpy as np
import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io

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

def search_web_images(face_features):
    """Search news websites, extract images, and compare facial features."""
    print("Starting web search...")
    search_urls = [
        "https://www.cnn.com/world",
        # "https://www.reuters.com/world",
        # "https://www.bbc.com/news",
        # "https://www.aljazeera.com/news",
        # "https://www.straitstimes.com/world"
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
                    # Clean the URL by removing query parameters
                    base_url = img_url.split('?')[0]
                    
                    try:
                        response = requests.get(base_url, headers={
                            'User-Agent': 'Mozilla/5.0',
                            'Accept': 'image/jpeg,image/png'
                        }, stream=True)
                        
                        # Process image with explicit format handling
                        img = Image.open(response.raw)
                        rgb_img = img.convert('RGB')
                        
                        # Save as fresh JPEG
                        buffer = io.BytesIO()
                        rgb_img.save(buffer, format='JPEG', quality=95)
                        img_bytes = buffer.getvalue()
                        
                        comparison = rekognition.compare_faces(
                            SourceImage={"Bytes": face_features},
                            TargetImage={"Bytes": img_bytes},
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

def process_image(img_bytes):
    """Convert WebP (or any format) to JPEG for Rekognition processing."""
    temp_buffer = io.BytesIO(img_bytes)
    img = Image.open(temp_buffer)

    # Convert to RGB (removes transparency)
    img = img.convert('RGB')

    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG', quality=95)
    
    return output_buffer.getvalue()

def extract_face_features(base64_image):
    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_image)
    
    # Process with Rekognition
    rekognition_features = rekognition.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]
    )
    
    # Convert Rekognition features to string
    text_description = str(rekognition_features["FaceDetails"])
    
    return {
        "rekognition": rekognition_features
    }

def store_embeddings(face_data):
    return es.index(
        index="missing_persons",
        body={
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
    
    return json.loads(response['body'].read())['completion']

# Base 64 encoding function
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# Test functions
def test_pipeline():
    print("Starting pipeline test...")
    
    # Test face detection and get face data
    print("Testing face detection...")
    image_path = "./missing_persons/missingperson1.jpg"
    base64_image = image_to_base64(image_path)
    face_data = extract_face_features(base64_image)  
    print("Face detection results:", json.dumps(face_data, indent=2))
    
    # print("Testing storage...")
    # test_results = store_embeddings(face_data)
    # print("Storage results:", test_results)
    
    # Test search
    print("Testing search...")
    search_results = search_web_images("./missing_persons/missingperson1.jpg")
    print("Search results:", search_results)
    
    # Test insights
    print("Testing insights...")
    insights = analyze_case(face_data, search_results)
    print("Insights:", insights)

if __name__ == "__main__":
    test_pipeline()