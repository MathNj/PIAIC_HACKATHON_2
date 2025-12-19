# =========================================
# Todo App - Terraform Infrastructure
# =========================================
# Cloud-Native Infrastructure as Code for DigitalOcean
#
# Components:
# - DigitalOcean Kubernetes (DOKS) cluster
# - Container Registry
# - Managed PostgreSQL Database
# - Managed Redis
# - Load Balancer
# - Domain & DNS configuration
#
# Usage:
#   terraform init
#   terraform plan
#   terraform apply
# =========================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  # Optional: Store state in DigitalOcean Spaces (S3-compatible)
  # backend "s3" {
  #   bucket                      = "terraform-state-bucket"
  #   key                         = "todo-app/terraform.tfstate"
  #   endpoint                    = "https://nyc3.digitaloceanspaces.com"
  #   region                      = "us-east-1"  # Dummy value required by AWS provider
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  # }
}

# =========================================
# Variables
# =========================================

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "todo-app"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

variable "k8s_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31.1-do.4"
}

variable "node_size" {
  description = "Droplet size for Kubernetes nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "node_count" {
  description = "Number of Kubernetes nodes"
  type        = number
  default     = 2
}

variable "db_size" {
  description = "Database instance size"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

variable "redis_size" {
  description = "Redis instance size"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

# =========================================
# Provider Configuration
# =========================================

provider "digitalocean" {
  token = var.do_token
}

# =========================================
# DigitalOcean Kubernetes Cluster (DOKS)
# =========================================

resource "digitalocean_kubernetes_cluster" "app_cluster" {
  name    = "${var.project_name}-${var.environment}-cluster"
  region  = var.region
  version = var.k8s_version

  node_pool {
    name       = "${var.project_name}-worker-pool"
    size       = var.node_size
    node_count = var.node_count
    auto_scale = true
    min_nodes  = 2
    max_nodes  = 5

    labels = {
      environment = var.environment
      project     = var.project_name
    }

    tags = [
      "${var.project_name}-${var.environment}",
      "kubernetes",
      "managed"
    ]
  }

  tags = [
    "${var.project_name}-${var.environment}",
    "kubernetes"
  ]

  maintenance_policy {
    day        = "sunday"
    start_time = "04:00"
  }
}

# =========================================
# Container Registry
# =========================================

resource "digitalocean_container_registry" "app_registry" {
  name                   = "${var.project_name}-registry"
  subscription_tier_slug = "basic"
  region                 = var.region
}

resource "digitalocean_container_registry_docker_credentials" "app_registry_creds" {
  registry_name = digitalocean_container_registry.app_registry.name
}

# =========================================
# Managed PostgreSQL Database
# =========================================

resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-${var.environment}-postgres"
  engine     = "pg"
  version    = "16"
  size       = var.db_size
  region     = var.region
  node_count = 1

  tags = [
    "${var.project_name}-${var.environment}",
    "database",
    "postgres"
  ]

  maintenance_window {
    day  = "sunday"
    hour = "04:00:00"
  }
}

resource "digitalocean_database_db" "app_database" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "${var.project_name}_db"
}

resource "digitalocean_database_user" "app_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "${var.project_name}_user"
}

# =========================================
# Managed Redis (Valkey)
# =========================================

resource "digitalocean_database_cluster" "redis" {
  name       = "${var.project_name}-${var.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = var.redis_size
  region     = var.region
  node_count = 1

  tags = [
    "${var.project_name}-${var.environment}",
    "database",
    "redis",
    "cache"
  ]

  maintenance_window {
    day  = "sunday"
    hour = "05:00:00"
  }
}

# =========================================
# VPC (Virtual Private Cloud)
# =========================================

resource "digitalocean_vpc" "app_vpc" {
  name   = "${var.project_name}-${var.environment}-vpc"
  region = var.region

  description = "VPC for ${var.project_name} ${var.environment} environment"
}

# =========================================
# Kubernetes Provider Configuration
# =========================================

provider "kubernetes" {
  host  = digitalocean_kubernetes_cluster.app_cluster.endpoint
  token = digitalocean_kubernetes_cluster.app_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.app_cluster.kube_config[0].cluster_ca_certificate
  )
}

provider "helm" {
  kubernetes {
    host  = digitalocean_kubernetes_cluster.app_cluster.endpoint
    token = digitalocean_kubernetes_cluster.app_cluster.kube_config[0].token
    cluster_ca_certificate = base64decode(
      digitalocean_kubernetes_cluster.app_cluster.kube_config[0].cluster_ca_certificate
    )
  }
}

# =========================================
# Kubernetes Namespace
# =========================================

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.project_name

    labels = {
      environment = var.environment
      project     = var.project_name
    }
  }

  depends_on = [digitalocean_kubernetes_cluster.app_cluster]
}

# =========================================
# Kubernetes Secrets
# =========================================

resource "kubernetes_secret" "database_credentials" {
  metadata {
    name      = "database-credentials"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    host     = digitalocean_database_cluster.postgres.private_host
    port     = digitalocean_database_cluster.postgres.port
    database = digitalocean_database_db.app_database.name
    username = digitalocean_database_user.app_user.name
    password = digitalocean_database_user.app_user.password
    uri      = digitalocean_database_cluster.postgres.private_uri
  }

  type = "Opaque"
}

resource "kubernetes_secret" "redis_credentials" {
  metadata {
    name      = "redis-credentials"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    host     = digitalocean_database_cluster.redis.private_host
    port     = digitalocean_database_cluster.redis.port
    password = digitalocean_database_cluster.redis.password
    uri      = digitalocean_database_cluster.redis.private_uri
  }

  type = "Opaque"
}

resource "kubernetes_secret" "registry_credentials" {
  metadata {
    name      = "registry-credentials"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    ".dockerconfigjson" = digitalocean_container_registry_docker_credentials.app_registry_creds.docker_credentials
  }

  type = "kubernetes.io/dockerconfigjson"
}

# =========================================
# Outputs
# =========================================

output "cluster_id" {
  description = "Kubernetes cluster ID"
  value       = digitalocean_kubernetes_cluster.app_cluster.id
}

output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = digitalocean_kubernetes_cluster.app_cluster.endpoint
  sensitive   = true
}

output "cluster_kubeconfig" {
  description = "Kubernetes cluster kubeconfig"
  value       = digitalocean_kubernetes_cluster.app_cluster.kube_config[0].raw_config
  sensitive   = true
}

output "registry_endpoint" {
  description = "Container registry endpoint"
  value       = digitalocean_container_registry.app_registry.endpoint
}

output "database_host" {
  description = "PostgreSQL database host"
  value       = digitalocean_database_cluster.postgres.host
}

output "database_uri" {
  description = "PostgreSQL database connection URI"
  value       = digitalocean_database_cluster.postgres.uri
  sensitive   = true
}

output "redis_host" {
  description = "Redis cache host"
  value       = digitalocean_database_cluster.redis.host
}

output "redis_uri" {
  description = "Redis connection URI"
  value       = digitalocean_database_cluster.redis.uri
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = digitalocean_vpc.app_vpc.id
}
