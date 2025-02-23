import scrapy
import urllib.parse  # ✅ Decodes escaped characters
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from elasticsearch import Elasticsearch
import hashlib
import os
from dotenv import load_dotenv
from summariser import extract_fields  # Import AWS Bedrock AI function

# Load environment variables from .env file
load_dotenv()

# Elasticsearch Credentials
ELASTICSEARCH_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTIC_CLOUD_USERNAME")  
ELASTICSEARCH_PASSWORD = os.getenv("ELASTIC_CLOUD_PASSWORD")  

def test():
    es = Elasticsearch(
        ELASTICSEARCH_URL,
        basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
    )
    if es.ping():
        print("✅ Connected to Elasticsearch successfully!")
    else:
        print("❌ Failed to connect to Elasticsearch")
class NewsCrawlerSpider(scrapy.Spider):
    name = "news_crawler"
    allowed_domains = ["mothership.sg"]  
    start_urls = ["https://mothership.sg/"]  
    custom_settings = {
        "DEPTH_LIMIT": 2,
        "CLOSESPIDER_PAGECOUNT": 10,
    }

    # Initialize Elasticsearch Connection
    try:
        es = Elasticsearch(
            ELASTICSEARCH_URL,
            basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
        )
        es.cluster.put_settings(body={
            "persistent": {
                "search.max_async_search_response_size": "50mb"
            }
        })
        if es.ping():
            print("✅ Connected to Elasticsearch successfully!")
        else:
            print("❌ Failed to connect to Elasticsearch")
    except Exception as e:
        print(f"⚠️ Elasticsearch connection error: {e}")

    def clean_text(self, text):
        """ Cleans extracted text by decoding escape characters and removing noise. """
        if not text:
            return ""

        # Decode URL-encoded characters (e.g., %20 -> space)
        text = urllib.parse.unquote(text)

        # Remove excessive whitespace, newlines, tabs
        text = re.sub(r"\s+", " ", text).strip()

        # Remove unwanted special characters
        text = re.sub(r"[^\w\s.,!?;:()'-]", "", text)  # Keeps punctuation

        return text

    def parse(self, response):
        # Extract all text content
        raw_text = " ".join(response.xpath("//body//text()").getall()).strip()
        text_data = self.clean_text(raw_text)

        if text_data:
            # Process text using AWS Bedrock AI
            extracted_data = extract_fields(text_data)

            # If no timestamp & location, discard the result
            if extracted_data:
                doc_id = hashlib.sha256(response.url.encode()).hexdigest()

                # Store in Elasticsearch
                try:
                    self.es.index(
                        index="news_articles_data",
                        id=doc_id,
                        document={
                            "url": response.url,
                            "text": text_data,
                            "title": response.xpath("//title/text()").get(),
                            "timestamp": extracted_data.get("timestamp"),
                            "location": extracted_data.get("location"),
                            "city": extracted_data.get("city"),
                            "state": extracted_data.get("state"),
                            "address": extracted_data.get("address"),
                            "summary": extracted_data.get("summary"),
                            "persons": extracted_data.get("persons")
                        }
                    )
                    print(f"✅ Stored in Elasticsearch: {response.url}")
                except Exception as e:
                    print(f"❌ Error storing data in Elasticsearch: {e}")
            else:
                print(f"⚠️ No valid timestamp or location found in: {response.url}")
        else:
            print(f"⚠️ No text extracted from {response.url}")

        # Follow all links on the page
        for link in response.xpath("//a/@href").getall():
            yield response.follow(link, callback=self.parse)


# Run the spider programmatically
if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(NewsCrawlerSpider)
    process.start()
