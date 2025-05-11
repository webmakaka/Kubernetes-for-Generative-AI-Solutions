import gradio as gr
import os
import requests
import logging
import sys

# Get the API endpoint from the environment variable
API_1_ENDPOINT = os.getenv("RAG_API_ENDPOINT", "http://localhost:5000/generate")
API_2_ENDPOINT = os.getenv("FINETUNE_API_ENDPOINT", "http://localhost:5000/generate")

# Set up logging
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()

# Function to send the prompt to the model and get the response
def chat_with_model(user_input, model_choice, history=None, session_id=None):
    
    if history is None:
        history = []  # Initialize history as an empty list if it's None

    headers = {"Content-Type": "application/json"}
    data = {"prompt": user_input}
    
    # Include session_id in the request if available
    if session_id:
        data["session_id"] = session_id
        
    if model_choice == "Shopping":
        api_endpoint = API_1_ENDPOINT
    elif model_choice == "Loyalty Program":
        api_endpoint = API_2_ENDPOINT
    else:
        return history, "Error: Invalid model choice.", session_id

    try:
        response = requests.post(api_endpoint, headers=headers, json=data)
        response.raise_for_status()  # Check for HTTP request errors
        response_data = response.json()
        
        logger.info(f"API Response: {response_data}")
        
        model_response = response_data.get("response", "No response from model.")
        session_id = response_data.get("session_id", session_id)  # Capture or update the session_id
        
        history.append((user_input, model_response))
        return history, history, session_id  # Return session_id to the UI
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred: {e}")
        return history, f"Error: {e}", session_id
        
        
def clear_chat():
    return [], "", None  # Return empty history, input, and session_id
    

# Create a Gradio Chat Interface
with gr.Blocks() as demo:
    gr.Markdown("# MyRetail ecommerce assistant")
    # chatbot = gr.Chatbot(height=600)
    chatbot = gr.Chatbot()
    model_choice = gr.Radio(choices=["Shopping", "Loyalty Program"], label="Choose an assistant")
    
    user_input = gr.Textbox(show_label=False, label="Type your question")
    clear_btn = gr.Button("Clear")

    state = gr.State()
    session_id = gr.State()  # Store the session_id in Gradio's State component
    
    submit_button = gr.Button("Submit")
    
    submit_button.click(
        chat_with_model, 
        inputs=[user_input, model_choice, state, session_id],  # Pass session_id in the input
        outputs=[chatbot, chatbot, session_id]  # Update session_id in the state
    )
    
    clear_btn.click(clear_chat, None, [chatbot, user_input, session_id])


demo.launch(server_name="0.0.0.0", server_port=7860)
