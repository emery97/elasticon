from fastapi import FastAPI, UploadFile
from .pipeline import process_missing_person

app = FastAPI()

@app.post("/missing-person")
async def report_missing_person(image: UploadFile):
    # Process uploaded image
    results = process_missing_person(image.file)
    return results

@app.get("/search")
async def search_cases(query: str):
    # Search existing cases
    results = es.search(
        index="missing_persons",
        body={
            "query": {
                "match": {"features": query}
            }
        }
    )
    return results
