variable "region" {
  description = "AWS region to create EKS cluster in"
  type        = string
  default     = "us-west-1"
}

variable "cluster_name" {
  description = "EKS Cluster name"
  type        = string
  default     = "my-eks-cluster"
}
