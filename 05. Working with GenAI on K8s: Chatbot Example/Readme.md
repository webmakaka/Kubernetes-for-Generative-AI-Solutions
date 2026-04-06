# Working with GenAI on K8s: Chatbot Example

<br/>

<img src="./img/chapter05-pic01.png" alt="Chatbot Example">

<br/>

### Experimentation using JupyterHub

<br/>

```bash
$ kubectl port-forward svc/proxy-public 8000:80 -n jupyterhub
```

<br/>

### Fine-tuning Llama 3 in K8s

<br/>

```bash
$ cd llama-finetuning
$ docker build -t my-llama-finetuned .
$ docker push XXXXXX
```

<br/>

```bash
$ kubectl apply -f llama-finetuning-job.yaml
$ kubectl logs -f job/my-llama-job
```

<br/>

### Deploying the fine-tuned model on K8s

<br/>

download

<br/>

```
s3://<<Your S3 Bucket Name>>/<<Your Model
directory>> model-assets/
```

<br/>

```bash
$ cd inference
$ docker build -t my-llama-finetuned:inf .
$ docker push XXXXXX
```

<br/>

```bash
$ kubectl apply -f finetuned-inf-deploy.yaml
```

<br/>

### Deploy a RAG application on K8s

<br/>

https://qdrant.github.io/qdrant-helm

<br/>

```bash
$ kubectl get pods -n qdrant
```

<br/>

```bash
$ kubectl port-forward service/qdrant 6333:6333 -n qdrant
```

<br/>

```bash
$ cd rag-app
$ docker build -t rag-app .
$ docker push XXXXXX
```

<br/>

```bash
$ kubectl apply -f rag-deploy.yaml
$ kubectl apply -f qdrant-restore-job.yaml
```

<br/>

### Deploying a chatbot on K8s

<br/>

```bash
$ cd chatbot
$ docker build
$ docker push XXXXXX
```

<br/>

```bash
$ kubectl apply -f chatbot-deploy.yaml
```

<br/>

```bash
$ export NLB_URL=$(kubectl get svc chatbot-ui-service -o
jsonpath='{.status.loadBalancer.ingress[0].hostname}')
$ echo $NLB_URL
```

<br/><br/>

---

<br/>

<a href="https://aiops.ru/">Предложить инженеру работу / подработку на проекте с kubernetes, microservices, machine learning, big data, golang</a>
