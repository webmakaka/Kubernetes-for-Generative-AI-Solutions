import torch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
import json

app = FastAPI()

logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger("uvicorn")

app.logger.info(torch.cuda.is_available())  # Should return True
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B", torch_dtype=torch.float16)

app.logger.info("Model loaded!!")
app.logger.info(model)

# Make sure the model is in evaluation mode
model.to(device)
model.eval()

# Ensure pad_token_id is set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

@app.post("/generate")
async def generate(request: Request):
    
    app.logger.info(f"Request received: {request}")
    
    data = await request.json()
    
    prompt = data.get('prompt', '')
    
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "No input text provided"})

    # Tokenize the input and generate a response
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=256,  # Adjust max length as needed
        )
    
    # Decode the response and return it
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    app.logger.info("Response::")
    app.logger.info(response)
    
    return {"response": response}

