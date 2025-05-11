from flask import Flask, request, jsonify 
import llama_cpp 

app = Flask(__name__) 
model = llama_cpp.Llama("llama-2-7b-chat.Q2_K.gguf") 

@app.route('/predict', methods=['POST']) 
def predict():
    data = request.json 
    prompt = f"""<s>[INST] <<SYS>>{data.get('sys_msg', '')}<</SYS>>{data.get('prompt', '')} [/INST]""" 
    response = model(prompt, max_tokens=1000) 
    return jsonify({'response': response}) 

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000) 
