# Scaling GenAI Applications on Kubernetes

**In this chapter, we’re going to cover the following main topics:**

• Scaling metrics  
• HorizontalPodAutoscaler (HPA)  
• VerticalPodAutoscaler (VPA)  
• Kubernetes Event-Driven Autoscaler (KEDA)  
• Cluster Autoscaler (CA)  
• Karpenter  

<br/>

### VerticalPodAutoscaler (VPA)

Unlike HPA, VPA is not included with K8s by default; it is a separate project available on GitHub at https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler. Install the VPA add-on by following the instructions provided at https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/installation.md.

<br/>

It is recommended not to combine HPA and VPA in the same cluster (unless VPA is set to “off ”), as it can result in potential conflicts.

<br/><br/>

---

<br/>

<a href="https://aiops.ru/">Предложить инженеру работу / подработку на проекте с kubernetes, microservices, machine learning, big data, golang</a>
