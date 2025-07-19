import os
import torch
from transformers import LlamaTokenizerFast, LlamaForCausalLM, Trainer, TrainingArguments, BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
import json
from datetime import datetime
import boto3
    
def formatting_func(example):
    text = f"### Question: {example['prompt']}\n ### Answer: {example['response']}"
    return text

def tokenize_prompt(prompt):
    return tokenizer(formatting_func(prompt))

train_dataset_file = os.environ.get('TRAIN_DATASET_FILE')
eval_dataset_file = os.environ.get('EVAL_DATASET_FILE')

train_dataset = load_dataset('json', data_files=train_dataset_file, split='train')
eval_dataset = load_dataset('json', data_files=eval_dataset_file, split='train')

# Load model and tokenizer
base_model_id = "meta-llama/Meta-Llama-3-8B"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(base_model_id, quantization_config=bnb_config, device_map="auto")
base_model=model

print("Base Model:")
print(base_model)

tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,
    padding_side="left",
    add_eos_token=True,
    add_bos_token=True,
)
tokenizer.pad_token = tokenizer.eos_token
tokenized_train_dataset = train_dataset.map(tokenize_prompt)
tokenized_val_dataset = eval_dataset.map(tokenize_prompt)

eval_tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,
    add_bos_token=True,
)

def generate_text(user_prompt, max_new_tokens=100, repetition_penalty=1.15):
    # Tokenize the user prompt
    model_input = tokenizer(user_prompt, return_tensors="pt").to("cuda")

    # Set the model to evaluation mode
    model.eval()

    # Generate text without calculating gradients
    with torch.no_grad():
        # Generate the text
        generated_output = model.generate(
            **model_input,
            max_new_tokens=max_new_tokens,
            repetition_penalty=repetition_penalty
        )

        # Decode the generated output to text
        generated_text = tokenizer.decode(generated_output[0], skip_special_tokens=True)

    return generated_text

eval_prompt = "[MyElite Loyalty Program FAQ]:What is the maximum cashback I can earn?"
print("Before Fine tuning:")
print(generate_text(eval_prompt))

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

config = LoraConfig(
    r=32,
    lora_alpha=64,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
        "lm_head",
    ],
    bias="none",
    lora_dropout=0.05,  # Conventional
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, config)

print("PEFT Model!!")
print(model)

print(torch.cuda.device_count())
if torch.cuda.device_count() > 1: # If more than 1 GPU
    model.is_parallelizable = True
    model.model_parallel = True


run_name = "Llama_finetune_madmax"

trainer = Trainer(
    model=model,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_val_dataset,
    args=TrainingArguments(
        output_dir=run_name,
        warmup_steps=2,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=1,
        gradient_checkpointing=True,
        max_steps=200,
        learning_rate=2.5e-5, # Want a small lr for finetuning
        bf16=True,
        optim="paged_adamw_8bit",
        logging_steps=25,              # When to start reporting loss
        logging_dir="./logs",        # Directory for storing logs
        save_strategy="steps",       # Save the model checkpoint every logging step
        save_steps=25,                # Save checkpoints every 50 steps
        eval_strategy="steps", # Evaluate the model every logging step
        eval_steps=25,               # Evaluate and save checkpoints every 50 steps
        do_eval=True,                # Perform evaluation at the end of training
    ),
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

model.config.use_cache = False  # silence the warnings. Please re-enable for inference!
print("PEFT Training starting!")
trainer.train()

print("PEFT Training completed!")

def LLM_response(prompt):
    eval_prompt = "Please provide an answer for [MyElite Loyalty Program FAQ]: "+prompt
    print(generate_text(eval_prompt))
    
user_prompt = "Does the MyElite Loyalty Program offer any discount on purchases?"
LLM_response(user_prompt)

user_prompt = "Does the MyElite Loyalty Program offer any discount on purchases?"
LLM_response(user_prompt)

# Save the model
current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
fine_tuned_model_name = f"llama-{current_time}"
trainer.save_model(f"./{fine_tuned_model_name}")
tokenizer.save_pretrained(f"./{fine_tuned_model_name}")

model_assets_bucket = os.environ.get('MODEL_ASSETS_BUCKET')

def sync_folder_to_s3(local_folder, bucket_name, s3_folder):
    s3 = boto3.client('s3')
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_path = os.path.join(s3_folder, relative_path)

            try:
                s3.upload_file(local_path, bucket_name, s3_path)
                print(f'Uploaded {local_path} to s3://{bucket_name}/{s3_path}')
            except Exception as e:
                print(f'Error uploading {local_path}: {e}')

sync_folder_to_s3(f"./{fine_tuned_model_name}/", model_assets_bucket, fine_tuned_model_name)
