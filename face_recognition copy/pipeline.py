import boto3
import json
import os
from elasticsearch import Elasticsearch
import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up AWS credentials from environment variables
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-southeast-2"
)

# Initialize AWS clients
rekognition = boto3.client("rekognition")
bedrock = boto3.client('bedrock-runtime')

# Elasticsearch credentials
ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
USERNAME = os.getenv("ELASTIC_CLOUD_USERNAME")
PASSWORD = os.getenv("ELASTIC_CLOUD_PASSWORD")
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    basic_auth=(USERNAME, PASSWORD)
)

def search_web_images(face_features):
    search_urls = ["https://www.cnn.com/world"]
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for base_url in search_urls:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=True)

        for img in images:
            img_url = img.get('src').split('?')[0]
            try:
                response = requests.get(img_url, headers=headers, stream=True)
                img = Image.open(response.raw).convert('RGB')
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                img_bytes = buffer.getvalue()

                comparison = rekognition.compare_faces(
                    SourceImage={"Bytes": face_features},
                    TargetImage={"Bytes": img_bytes},
                    SimilarityThreshold=70
                )

                if comparison.get('FaceMatches'):
                    matches.append({
                        "url": img_url,
                        "similarity": comparison['FaceMatches'][0]['Similarity']
                    })
            except:
                continue

    return matches

def extract_face_features(base64_image):
    image_bytes = base64.b64decode(base64_image)
    rekognition_features = rekognition.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]
    )
    return rekognition_features["FaceDetails"]

def store_embeddings(face_data):
    return es.index(index="missing_persons", body={"features": face_data})

def analyze_case(face_data, matches):
    prompt = f"""
    Analyze this missing person case:

    Face Data: {face_data}
    Potential Matches: {matches}

    Provide insights on potential identity matches.
    """

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        })
    )

    result = json.loads(response['body'].read())

    # Corrected parsing based on your provided structure
    insights = result["content"][0]["text"]
    
    return insights


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_pipeline():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "missing_persons", "missingperson1.jpg")

    base64_image = image_to_base64(image_path)
    face_data = extract_face_features(base64_image)
    print(face_data)
    search_results = search_web_images(base64.b64decode(base64_image))
    insights = analyze_case(face_data, search_results)

    #print("Insights:", insights)

if __name__ == "__main__":
    test_pipeline()