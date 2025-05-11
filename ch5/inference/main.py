import torch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import LlamaTokenizerFast, LlamaForCausalLM, BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import logging
import json

app = FastAPI()

logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger("uvicorn")

app.logger.info(torch.cuda.is_available())  # Should return True
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('./model-assets')

# Define the quantization configuration for 8-bit
base_model_id = "meta-llama/Meta-Llama-3-8B"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

base_model = AutoModelForCausalLM.from_pretrained(base_model_id, torch_dtype=torch.float16, quantization_config=bnb_config,  device_map='auto')
app.logger.info("Base model loaded!!")
app.logger.info(base_model)

model = PeftModel.from_pretrained(base_model, './model-assets')
app.logger.info("PEFT model loaded!!")
app.logger.info(model)

# Make sure the model is in evaluation mode
model.eval()

# Ensure pad_token_id is set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

@app.post("/generate")
async def generate(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        app.logger.error(f"Failed to parse JSON: {str(e)}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    app.logger.info("Request received - " + json.dumps(data))
    
    prompt = data.get('prompt', '')
    
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "No input text provided"})

    # Tokenize the input and generate a response
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            # max_length=256,  # Adjust max length as needed
            max_new_tokens=100,
            repetition_penalty=1.15
        )
    
    # Decode the response and return it
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    app.logger.info("Response::")
    app.logger.info(response)
    
    return {"response": response}
