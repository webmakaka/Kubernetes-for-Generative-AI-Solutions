import os
import json
import io
import csv

# FastAPI and Pydantic imports
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging
import httpx
import boto3
import random
import string
from urllib.parse import urlparse

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# FastAPI app instance
app = FastAPI()

# Read Qdrant endpoint from an environment variable
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT", "http://localhost:6333")  # Default to localhost if not set

# Initialize Qdrant client with the endpoint from the environment variable
client = QdrantClient(QDRANT_ENDPOINT)

# Specify the collection name
collection_name = "catalog"

bedrock = boto3.client('bedrock-runtime')

# Define the request body schema
class PromptModel(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class VectorDataModel(BaseModel):
    catalog_name: Optional[str] = None
    url: Optional[str] = None
    

@app.post("/create_collection")
async def create_collection(request: VectorDataModel):
    try:
        if 'catalog_name' not in request:
            raise HTTPException(status_code=400, detail="No collection provided in the request.")
    
        collection = request.catalog_name
        
        logger.info(collection)
        
        client.recreate_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)  # Vector size set to 256
        )
        
    except httpx.HTTPStatusError as e:
        logger.error("HTTP Error occurred while downloading the file: %s", e)
        raise HTTPException(status_code=500, detail="Failed to download the file")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while loading data")


def generate_embedding(text):
    try:
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            contentType='application/json',
            body=json.dumps({"inputText": text, "dimensions": 1024, "normalize": True})  # Pass the batch of texts
        )
        model_response = json.loads(response["body"].read())

        embedding = model_response['embedding']
        app.logger.debug(embedding)
        return embedding
    except Exception as e:
        app.logger.error(f"An error occurred while generating embeddings: {e}")
        return None

def perform_similarity_search(prompt, top_k=5):
    
    prompt_embedding = generate_embedding(prompt)
    
    app.logger.info("Response from Prompt Embedding:")
    app.logger.info(prompt_embedding)
    
    # Perform similarity search in Qdrant
    search_result = client.search(
        collection_name=collection_name,
        query_vector=prompt_embedding,
        # top=top_k
    )
    app.logger.info("Response from Qdrant Search:")
    app.logger.info(search_result)
    
    return search_result
    
def generate_bedrock_response(prompt, context):
    # Combine the prompt with the context retrieved from Qdrant
    context_text = "\n".join(context)
    combined_prompt = f"Context:\n{context_text}\n\nPrompt:\n{prompt}"
    
    app.logger.info("Bedrock Prompt:")
    app.logger.info(combined_prompt)
    
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": combined_prompt}],
            }
        ],
    }
    
    # Call the Bedrock API
    response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(native_request)  # Pass the batch of texts
        )
    
    model_response = json.loads(response["body"].read())
    
    app.logger.info(model_response)
    
    return model_response["content"][0]["text"]
    

@app.post("/generate")
async def generate_answer(prompt_model: PromptModel):
    try:
        prompt = prompt_model.prompt

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
    
        logger.info(prompt)
        
        search_results = perform_similarity_search(prompt)
    
        context = [json.dumps(hit.payload) for hit in search_results if hit.payload]
        
        # Generate a response from Bedrock based on the context and user prompt
        response = generate_bedrock_response(prompt, context)
        
        return JSONResponse({"response": response}, status_code=200)
        
    except httpx.HTTPStatusError as e:
        logger.error("HTTP Error occurred while downloading the file: %s", e)
        raise HTTPException(status_code=500, detail="Failed to download the file")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while loading data")



@app.post("/load_data")
async def load_data(request: VectorDataModel):
    try:
        
        if 'url' not in request:
            raise HTTPException(status_code=400, detail="No URL provided in the request")
    
        logger.info(request.url)
    
        # Fetch the file from the input URL using async HTTP client
        async with httpx.AsyncClient() as client:
            response = await client.get(request.url)
        
        # Handle non-200 status codes
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to download file from the URL")
        
        # Convert the content of the response to a BytesIO object and then a string
        file_content = io.StringIO(response.text)

        # Load the CSV file using the built-in csv module
        reader = csv.DictReader(file_content)
            
        # Prepare points to be inserted into Qdrant
        points = []
        for item in reader:
            logger.debug(item)
            embeddings = generate_embedding(item["Description"])
            point = models.PointStruct(
                    id=item.get("ProductID"),  # Ensure your JSON data has an 'id' field
                    payload=item,
                    vector=embeddings
                )
            points.append(point)
    
        # Insert the batch into Qdrant
        client.upsert(collection_name=collection_name, points=points)
        app.logger.info(f"Batch inserted, total points: {len(points)}")
        
        return JSONResponse({"message": "Document ingested successfully!"}, status_code=200)

    except httpx.HTTPStatusError as e:
        logger.error("HTTP Error occurred while downloading the file: %s", e)
        raise HTTPException(status_code=500, detail="Failed to download the file")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while loading data")
        