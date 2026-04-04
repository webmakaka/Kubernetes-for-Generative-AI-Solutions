# Kubernetes – Introduction and Integration with GenAI

<br/>

// HuggingFace  
https://huggingface.co/docs/huggingface_hub/en/installation

<br/>

```bash
$ pip install --upgrade huggingface_hub
```

<br/>

```bash
// https://huggingface.co/docs/huggingface_hub/en/guides/cli
$ curl -LsSf https://hf.co/cli/install.sh | bash


// GENERATE TOKEN
https://huggingface.co/settings/tokens

$ hf auth login
```

<br/>

### Run inside docker

<br/>

```bash
$ hf download TheBloke/Llama-2-7B-Chat-GGUF llama-2-7b-chat.Q2_K.gguf --local-dir .
```

<br/>

```bash
$ docker build -t my-llama .
```

<br/>

```bash
$ docker tag my-llama webmakaka/my-llama
$ docker push webmakaka/my-llama
```

<br/>

```bash
$ docker run -p 8000:5000 webmakaka/my-llama
```

<br/>

```bash
// OK!
$ curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a poem about humanity?","sys_msg":"You are a helpful, respectful, and honest assistant. Always provide safe, unbiased, and positive responses. Avoid harmful, unethical, or illegal content. If a question is unclear or incorrect, explain why. If unsure, do not provide false information."}' \
  | jq .
```

<br/><br/>

---

<br/>

<a href="https://aiops.ru/">Предложить инженеру работу / подработку на проекте с kubernetes, microservices, machine learning, big data, golang</a>
