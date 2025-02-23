import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up AWS credentials from environment variables
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-southeast-2"
)

# AWS Bedrock Configuration
AWS_REGION = "ap-southeast-2"
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Initialize AWS Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def extract_fields(text):
    """
    Uses AWS Bedrock (Claude) to extract timestamp & location.
    Returns None if no relevant data is found.
    """
    if not text:
        return None

    # Correct Bedrock AI prompt with structured messaging
    prompt_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "temperature": 0.5,
        "top_k": 250,
        "messages": [
            {
                "role": "user",
                "content": f"""
                Extract the following structured fields from the given text:
                - Timestamp (Date or Time Mentioned strictly in DD-MM-YYYY format)
                - Location (City, State, or Address)
                - City (if applicable)
                - State (if applicable)
                - Address (if applicable)
                - Town (if applicable)
                - Summary (A readable summary of the text, no more than two lines)
                - Persons (a list of names found in the text in array format, ["...", "...", "..."])
                If no timestamp or location or city or state or address or town or persons is found, return null.

                Text: "{text}"
                Response format (strictly JSON): {{"timestamp": "...", "location": "...", "city" : "...", "state" : "...", "address" : "...", "summary": "...", "persons" : ["...", "...", "..."]}}
                """
            }
        ]
    }

    try:
        # Send request to AWS Bedrock
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(prompt_payload)
        )

        # Read and parse the response correctly
        response_body = json.loads(response["body"].read().decode("utf-8"))

        # 🔹 Debugging: Print the full Claude response
        print("🔹 Claude Raw Response:", response_body)

        # Extract content from the response (handles lists correctly)
        extracted_data = response_body.get("content", [{}])[0].get("text", "").strip()
        print("🔹 Claude Extracted Response:", extracted_data)

        # Try parsing JSON response
        try:
            extracted_data_json = json.loads(extracted_data)
        except json.JSONDecodeError:
            print("⚠️ Claude's response is NOT valid JSON. Raw output:", extracted_data)
            return None  # If response is not valid JSON, return None

        # Ensure both timestamp & location exist, otherwise return None
        if "timestamp" in extracted_data_json and "location" in extracted_data_json:
            return extracted_data_json

        return None  # If no timestamp or location, discard the result

    except Exception as e:
        print(f"⚠️ AWS Bedrock API Error: {e}")
        return None


#print(extract_fields("A MAN named John Ruckus WAS FOUND IN OHIO, at 32 Gundam Street, police officer James Hawking caught him on 15th Febraury 2025. "))