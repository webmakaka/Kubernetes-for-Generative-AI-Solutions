# Getting Started with Kubernetes in the Cloud

<br/>

Minikube + Metal LB

<br/>

```bash
$ kubectl create deploy my-llama --image webmakaka/my-llama
```

<br/>

```bash
$ kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
my-llama-8649ff89c6-djdvd   1/1     Running   0          5m35s
```

<br/>

```yaml
$ cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  labels:
    app: my-llama-svc
  name: my-llama-svc
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 5000
  type: LoadBalancer
  selector:
    app: my-llama
EOF
```

<br/>

```bash
$ export NLB_URL=$(kubectl get svc my-llama-svc -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
$ echo ${NLB_URL}
```

<br/>

```bash
// OK!
$ curl -X POST http://${NLB_URL}/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a poem about humanity?","sys_msg":"You are a helpful, respectful, and honest assistant. Always provide safe, unbiased, and positive responses. Avoid harmful, unethical, or illegal content. If a question is unclear or incorrect, explain why. If unsure, do not provide false information."}' \
  | jq .
```

<br/><br/>

---

<br/>

<a href="https://aiops.ru/">Предложить инженеру работу / подработку на проекте с kubernetes, microservices, machine learning, big data, golang</a>
