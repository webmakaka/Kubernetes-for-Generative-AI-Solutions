# EKS Cluster for GenAI Models

This Terraform configuration creates an Amazon EKS cluster optimized for running generative AI models.

## Architecture

The infrastructure includes:

- Amazon EKS cluster (v1.32) named "eks-genai-demo" in us-west-2 region
- Dedicated VPC (CIDR 10.0.0.0/16) with public and private subnets across 3 AZs
- Single NAT gateway for internet access from private subnets
- Standard EKS managed add-ons (Amazon VPC CNI, CoreDNS, kube-proxy)
- EKS managed node group with m5.large instances

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform v1.0.0 or newer
- kubectl (for interacting with the cluster after deployment)

## Usage

1. Initialize Terraform:
   ```
   terraform init
   ```

2. Review the execution plan:
   ```
   terraform plan
   ```

3. Apply the configuration:
   ```
   terraform apply
   ```

4. Configure kubectl to connect to your cluster:
   ```
   aws eks update-kubeconfig --region us-west-2 --name eks-genai-demo
   ```

5. Verify the connection:
   ```
   kubectl get nodes
   ```

## Customization

You can customize the deployment by modifying the variables in `variables.tf` or by providing a `.tfvars` file.

## Clean Up

To destroy all resources created by this configuration:
```
terraform destroy
```

## Notes

- The configuration uses a single NAT gateway to reduce costs, but for production environments, consider using one NAT gateway per AZ for higher availability.
- The node group uses m5.large instances by default. For running large GenAI models, consider using GPU-enabled instance types like g4dn or p3 series.
