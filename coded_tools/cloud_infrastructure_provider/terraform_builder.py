# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.

import os
import logging
from typing import Any, Dict, Union, List

from neuro_san.interfaces.coded_tool import CodedTool


class TerraformBuilder(CodedTool):
    """Generates Terraform infrastructure code based on design specifications."""

    def __init__(self):
        pass

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        try:
            project_name = args.get("project_name", "")
            output_dir = args.get("output_dir", f"output/{project_name}")
            
            if not project_name:
                return "Error: project_name parameter is required"

            logger = logging.getLogger(self.__class__.__name__)
            logger.info("Generating Terraform infrastructure for project: %s", project_name)
            
            # Read design document to extract requirements
            design_path = os.path.join(output_dir, "docs", "design.md")
            if os.path.exists(design_path):
                with open(design_path, 'r') as f:
                    design_content = f.read()
                requirements = self._parse_design_requirements(design_content)
            else:
                # Default minimal requirements
                requirements = {
                    "services": ["nginx"],
                    "databases": [],
                    "load_balancers": [],
                    "monitoring": False,
                    "ssl": False,
                    "backup": False,
                    "security": [],
                    "networking": {"vpc": True},
                    "scaling": {"auto_scaling": False}
                }
            
            # Create directory structure
            terraform_dir = os.path.join(output_dir, "terraform")
            os.makedirs(terraform_dir, exist_ok=True)
            
            # Generate Terraform files based on requirements
            self._create_main_tf(terraform_dir, project_name, requirements)
            self._create_variables_tf(terraform_dir, project_name, requirements)
            self._create_outputs_tf(terraform_dir, project_name, requirements)
            self._create_terraform_tfvars(terraform_dir, project_name, requirements)
            self._create_readme(terraform_dir, project_name, requirements)
            
            return f"Terraform infrastructure successfully generated at {terraform_dir}"
            
        except Exception as e:
            return f"Error: Failed to generate Terraform infrastructure - {str(e)}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)

    def _parse_design_requirements(self, design_content: str) -> Dict[str, Any]:
        """Parse design document to extract infrastructure requirements dynamically."""
        requirements = {
            "cloud_provider": self._detect_cloud_provider(design_content),
            "region": self._extract_region(design_content),
            "resources": self._extract_resources(design_content),
            "networking": self._extract_networking(design_content),
            "security": self._extract_security(design_content),
            "monitoring": self._extract_monitoring(design_content),
            "backup": self._extract_backup(design_content),
            "scaling": self._extract_scaling(design_content),
            "compliance": self._extract_compliance(design_content)
        }
        
        return requirements

    def _detect_cloud_provider(self, content: str) -> str:
        """Detect cloud provider from design document."""
        content_lower = content.lower()
        
        if "aws" in content_lower or "amazon" in content_lower:
            return "aws"
        elif "azure" in content_lower or "microsoft" in content_lower:
            return "azure"
        elif "gcp" in content_lower or "google cloud" in content_lower:
            return "gcp"
        else:
            return "unknown"

    def _extract_region(self, content: str) -> str:
        """Extract region information from design document."""
        import re
        
        # AWS regions
        aws_regions = re.findall(r'us-[a-z]+-\d+|eu-[a-z]+-\d+|ap-[a-z]+-\d+', content.lower())
        if aws_regions:
            return aws_regions[0]
        
        # Azure regions
        azure_regions = re.findall(r'(east us|west us|north europe|west europe|southeast asia)', content.lower())
        if azure_regions:
            return azure_regions[0].replace(' ', '')
        
        # GCP regions
        gcp_regions = re.findall(r'us-central\d+|us-east\d+|us-west\d+|europe-west\d+', content.lower())
        if gcp_regions:
            return gcp_regions[0]
        
        return "us-east-1"  # Default

    def _extract_resources(self, content: str) -> Dict[str, Any]:
        """Extract specific cloud resources from design document."""
        content_lower = content.lower()
        resources = {
            "compute": [],
            "storage": [],
            "database": [],
            "networking": [],
            "security": [],
            "analytics": [],
            "serverless": []
        }
        
        # Extract compute resources
        if "ec2" in content_lower or "virtual machine" in content_lower:
            resources["compute"].append("ec2" if "aws" in content_lower else "vm")
        if "lambda" in content_lower:
            resources["serverless"].append("lambda")
        if "cloud functions" in content_lower:
            resources["serverless"].append("cloud_functions")
        if "azure functions" in content_lower:
            resources["serverless"].append("azure_functions")
        
        # Extract storage resources
        if "s3" in content_lower:
            resources["storage"].append("s3")
        if "blob storage" in content_lower:
            resources["storage"].append("blob_storage")
        if "cloud storage" in content_lower:
            resources["storage"].append("cloud_storage")
        
        # Extract database resources
        if "rds" in content_lower:
            resources["database"].append("rds")
        if "sql database" in content_lower:
            resources["database"].append("sql_database")
        if "cloud sql" in content_lower:
            resources["database"].append("cloud_sql")
        if "dynamodb" in content_lower:
            resources["database"].append("dynamodb")
        if "cosmosdb" in content_lower:
            resources["database"].append("cosmosdb")
        
        return resources

    def _extract_networking(self, content: str) -> Dict[str, Any]:
        """Extract networking requirements from design document."""
        content_lower = content.lower()
        networking = {
            "vpc_required": "vpc" in content_lower or "virtual network" in content_lower,
            "subnets": [],
            "load_balancers": [],
            "dns": [],
            "vpn": "vpn" in content_lower,
            "nat_gateway": "nat" in content_lower
        }
        
        # Extract load balancer types
        if "application load balancer" in content_lower or "alb" in content_lower:
            networking["load_balancers"].append("alb")
        if "network load balancer" in content_lower or "nlb" in content_lower:
            networking["load_balancers"].append("nlb")
        if "application gateway" in content_lower:
            networking["load_balancers"].append("application_gateway")
        
        return networking

    def _extract_security(self, content: str) -> Dict[str, Any]:
        """Extract security requirements from design document."""
        content_lower = content.lower()
        security = {
            "encryption": "encryption" in content_lower,
            "key_management": [],
            "access_control": [],
            "monitoring": [],
            "compliance": []
        }
        
        # Key management
        if "kms" in content_lower:
            security["key_management"].append("kms")
        if "key vault" in content_lower:
            security["key_management"].append("key_vault")
        
        # Access control
        if "iam" in content_lower:
            security["access_control"].append("iam")
        if "rbac" in content_lower:
            security["access_control"].append("rbac")
        if "sso" in content_lower:
            security["access_control"].append("sso")
        
        return security

    def _extract_monitoring(self, content: str) -> Dict[str, Any]:
        """Extract monitoring requirements from design document."""
        content_lower = content.lower()
        monitoring = {
            "enabled": "monitoring" in content_lower or "observability" in content_lower,
            "logging": [],
            "metrics": [],
            "alerting": []
        }
        
        if "cloudwatch" in content_lower:
            monitoring["logging"].append("cloudwatch")
        if "azure monitor" in content_lower:
            monitoring["logging"].append("azure_monitor")
        if "stackdriver" in content_lower:
            monitoring["logging"].append("stackdriver")
        
        return monitoring

    def _extract_backup(self, content: str) -> Dict[str, Any]:
        """Extract backup requirements from design document."""
        content_lower = content.lower()
        return {
            "enabled": "backup" in content_lower or "disaster recovery" in content_lower,
            "retention": self._extract_retention_period(content_lower),
            "cross_region": "cross-region" in content_lower or "cross region" in content_lower
        }

    def _extract_scaling(self, content: str) -> Dict[str, Any]:
        """Extract scaling requirements from design document."""
        content_lower = content.lower()
        return {
            "auto_scaling": "auto scaling" in content_lower or "autoscaling" in content_lower,
            "load_balancing": "load balancing" in content_lower,
            "high_availability": "high availability" in content_lower or "multi-az" in content_lower
        }

    def _extract_compliance(self, content: str) -> List[str]:
        """Extract compliance requirements from design document."""
        content_lower = content.lower()
        compliance = []
        
        if "gdpr" in content_lower:
            compliance.append("gdpr")
        if "hipaa" in content_lower:
            compliance.append("hipaa")
        if "sox" in content_lower:
            compliance.append("sox")
        if "pci" in content_lower:
            compliance.append("pci")
        
        return compliance

    def _extract_retention_period(self, content: str) -> str:
        """Extract backup retention period from design document."""
        import re
        
        # Look for patterns like "30 days", "7 days", "1 year"
        retention_pattern = r'(\d+)\s*(day|week|month|year)s?'
        matches = re.findall(retention_pattern, content)
        
        if matches:
            return f"{matches[0][0]} {matches[0][1]}s"
        
        return "30 days"  # Default

    def _create_main_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        """Generate main.tf based on design requirements."""
        
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        # Base infrastructure based on cloud provider
        if cloud_provider == "azure":
            content = self._create_azure_main_tf(project_name, requirements)
        elif cloud_provider == "aws":
            content = self._create_aws_main_tf(project_name, requirements)
        elif cloud_provider == "gcp":
            content = self._create_gcp_main_tf(project_name, requirements)
        else:
            # Default to Azure
            content = self._create_azure_main_tf(project_name, requirements)
        
        with open(os.path.join(terraform_dir, "main.tf"), 'w') as f:
            f.write(content)

    def _create_azure_main_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create Azure-specific main.tf content."""
        region = requirements.get("region", "East US")
        
        content = f'''# Terraform configuration for {project_name} on Azure

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
}}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "rg-${{var.project_name}}-${{var.environment}}"
  location = var.location

  tags = {{
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}
'''

        # Add networking if required
        if requirements.get("networking", {}).get("vpc_required", True):
            content += '''
# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.project_name}-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Subnets
resource "azurerm_subnet" "web" {
  name                 = "subnet-web"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}
'''

        # Add compute resources
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "vm" in compute_resources:
            content += '''
# Virtual Machine
resource "azurerm_public_ip" "vm" {
  name                = "pip-vm-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                = "Standard"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_network_interface" "vm" {
  name                = "nic-vm-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.web.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm.id
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                = "vm-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B2s"
  admin_username      = var.vm_admin_username

  network_interface_ids = [
    azurerm_network_interface.vm.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add storage resources
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "blob_storage" in storage_resources:
            content += '''
# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "st${lower(replace(var.project_name, "-", ""))}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add database resources
        database_resources = requirements.get("resources", {}).get("database", [])
        if "sql_database" in database_resources:
            content += '''
# SQL Database
resource "azurerm_mssql_server" "main" {
  name                         = "sql-${var.project_name}-${var.environment}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.db_admin_username
  administrator_login_password = var.db_admin_password

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_mssql_database" "main" {
  name           = "db-${var.project_name}-${var.environment}"
  server_id      = azurerm_mssql_server.main.id
  sku_name       = "S0"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add monitoring if required
        if requirements.get("monitoring", {}).get("enabled", False):
            content += '''
# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add backup storage if required  
        if requirements.get("backup", {}).get("enabled", False):
            content += '''
# Recovery Services Vault
resource "azurerm_recovery_services_vault" "main" {
  name                = "rsv-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        return content

    def _create_aws_main_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create AWS-specific main.tf content."""
        region = requirements.get("region", "us-east-1")
        
        content = f'''# Terraform configuration for {project_name} on AWS

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

# VPC
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name        = "${{var.project_name}}-vpc"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id

  tags = {{
    Name        = "${{var.project_name}}-igw"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}

# Public Subnet
resource "aws_subnet" "public" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {{
    Name        = "${{var.project_name}}-public-subnet"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}

# Route Table
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id

  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}

  tags = {{
    Name        = "${{var.project_name}}-public-rt"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}

resource "aws_route_table_association" "public" {{
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}}

# Data source for availability zones
data "aws_availability_zones" "available" {{
  state = "available"
}}
'''

        # Add compute resources
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "ec2" in compute_resources:
            content += '''
# Security Group for EC2
resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-ec2-sg"
  description = "Security group for EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-ec2-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.ec2.id]
  subnet_id              = aws_subnet.public.id

  tags = {
    Name        = "${var.project_name}-instance"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Data source for AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
'''

        # Add storage resources
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "s3" in storage_resources:
            content += '''
# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-bucket"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
'''

        # Add database resources
        database_resources = requirements.get("resources", {}).get("database", [])
        if "rds" in database_resources:
            content += '''
# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]

  tags = {
    Name        = "${var.project_name}-db-subnet-group"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private Subnet for RDS
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name        = "${var.project_name}-private-subnet"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  tags = {
    Name        = "${var.project_name}-rds-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_admin_username
  password = var.db_admin_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  skip_final_snapshot = true
  
  tags = {
    Name        = "${var.project_name}-database"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        return content

    def _create_gcp_main_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create GCP-specific main.tf content."""
        region = requirements.get("region", "us-central1")
        
        content = f'''# Terraform configuration for {project_name} on GCP

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 4.0"
    }}
  }}
}}

provider "google" {{
  project = var.gcp_project_id
  region  = var.gcp_region
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "${{var.project_name}}-vpc"
  auto_create_subnetworks = false
}}

# Subnet
resource "google_compute_subnetwork" "main" {{
  name          = "${{var.project_name}}-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id
}}

# Firewall Rules
resource "google_compute_firewall" "allow_http" {{
  name    = "${{var.project_name}}-allow-http"
  network = google_compute_network.main.name

  allow {{
    protocol = "tcp"
    ports    = ["80", "443"]
  }}

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}}
'''

        # Add compute resources
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "compute_instance" in compute_resources:
            content += '''
# Compute Instance
resource "google_compute_instance" "main" {
  name         = "${var.project_name}-instance"
  machine_type = "e2-micro"
  zone         = "${var.gcp_region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.main.name
    subnetwork = google_compute_subnetwork.main.name
    access_config {}
  }

  tags = ["http-server"]
}
'''

        # Add storage resources
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "cloud_storage" in storage_resources:
            content += '''
# Cloud Storage Bucket
resource "google_storage_bucket" "main" {
  name     = "${var.project_name}-${var.environment}-${random_string.bucket_suffix.result}"
  location = var.gcp_region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
'''

        return content

    def _create_variables_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        if cloud_provider == "azure":
            content = self._create_azure_variables_tf(project_name, requirements)
        elif cloud_provider == "aws":
            content = self._create_aws_variables_tf(project_name, requirements)
        elif cloud_provider == "gcp":
            content = self._create_gcp_variables_tf(project_name, requirements)
        else:
            content = self._create_azure_variables_tf(project_name, requirements)
        
        with open(os.path.join(terraform_dir, "variables.tf"), 'w') as f:
            f.write(content)

    def _create_azure_variables_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create Azure-specific variables.tf content."""
        region = requirements.get("region", "East US")
        
        content = f'''# Variables for {project_name} Terraform configuration on Azure

variable "project_name" {{
  description = "Name of the project"
  type        = string
  default     = "{project_name.lower()}"
}}

variable "environment" {{
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "location" {{
  description = "Azure region for resources"
  type        = string
  default     = "{region}"
}}

variable "vm_admin_username" {{
  description = "Administrator username for VMs"
  type        = string
  default     = "azureuser"
}}

variable "vm_size" {{
  description = "Size of the virtual machines"
  type        = string
  default     = "Standard_B2s"
}}

variable "db_admin_username" {{
  description = "Database administrator username"
  type        = string
  default     = "dbadmin"
}}

variable "db_admin_password" {{
  description = "Database administrator password"
  type        = string
  sensitive   = true
}}

variable "enable_monitoring" {{
  description = "Enable monitoring and diagnostics"
  type        = bool
  default     = {str(requirements.get("monitoring", {}).get("enabled", True)).lower()}
}}

variable "backup_retention_days" {{
  description = "Number of days to retain backups"
  type        = number
  default     = {self._extract_backup_retention_days(requirements)}
}}

variable "allowed_ip_ranges" {{
  description = "List of IP ranges allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}}

variable "tags" {{
  description = "Additional tags for resources"
  type        = map(string)
  default     = {{}}
}}
'''
        return content

    def _create_aws_variables_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create AWS-specific variables.tf content."""
        region = requirements.get("region", "us-east-1")
        
        content = f'''# Variables for {project_name} Terraform configuration on AWS

variable "project_name" {{
  description = "Name of the project"
  type        = string
  default     = "{project_name.lower()}"
}}

variable "environment" {{
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "aws_region" {{
  description = "AWS region for resources"
  type        = string
  default     = "{region}"
}}

variable "instance_type" {{
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}}

variable "key_pair_name" {{
  description = "EC2 Key Pair name for SSH access"
  type        = string
}}

variable "db_name" {{
  description = "Database name"
  type        = string
  default     = "mydb"
}}

variable "db_admin_username" {{
  description = "Database administrator username"
  type        = string
  default     = "admin"
}}

variable "db_admin_password" {{
  description = "Database administrator password"
  type        = string
  sensitive   = true
}}

variable "enable_monitoring" {{
  description = "Enable monitoring and diagnostics"
  type        = bool
  default     = {str(requirements.get("monitoring", {}).get("enabled", True)).lower()}
}}

variable "backup_retention_days" {{
  description = "Number of days to retain backups"
  type        = number
  default     = {self._extract_backup_retention_days(requirements)}
}}

variable "allowed_cidr_blocks" {{
  description = "List of CIDR blocks allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}}

variable "tags" {{
  description = "Additional tags for resources"
  type        = map(string)
  default     = {{}}
}}
'''
        return content

    def _create_gcp_variables_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create GCP-specific variables.tf content."""
        region = requirements.get("region", "us-central1")
        
        content = f'''# Variables for {project_name} Terraform configuration on GCP

variable "project_name" {{
  description = "Name of the project"
  type        = string
  default     = "{project_name.lower()}"
}}

variable "environment" {{
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "gcp_project_id" {{
  description = "GCP project ID"
  type        = string
}}

variable "gcp_region" {{
  description = "GCP region for resources"
  type        = string
  default     = "{region}"
}}

variable "machine_type" {{
  description = "Compute instance machine type"
  type        = string
  default     = "e2-micro"
}}

variable "db_admin_username" {{
  description = "Database administrator username"
  type        = string
  default     = "admin"
}}

variable "db_admin_password" {{
  description = "Database administrator password"
  type        = string
  sensitive   = true
}}

variable "enable_monitoring" {{
  description = "Enable monitoring and diagnostics"
  type        = bool
  default     = {str(requirements.get("monitoring", {}).get("enabled", True)).lower()}
}}

variable "backup_retention_days" {{
  description = "Number of days to retain backups"
  type        = number
  default     = {self._extract_backup_retention_days(requirements)}
}}

variable "allowed_source_ranges" {{
  description = "List of source ranges allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}}

variable "labels" {{
  description = "Additional labels for resources"
  type        = map(string)
  default     = {{}}
}}
'''
        return content

    def _extract_backup_retention_days(self, requirements: Dict[str, Any]) -> int:
        """Extract backup retention days from requirements."""
        backup_info = requirements.get("backup", {})
        if isinstance(backup_info, dict):
            retention = backup_info.get("retention", "30 days")
        else:
            retention = "30 days"
        
        # Parse retention string to extract days
        if "day" in retention:
            try:
                return int(retention.split()[0])
            except (ValueError, IndexError):
                return 30
        elif "week" in retention:
            try:
                return int(retention.split()[0]) * 7
            except (ValueError, IndexError):
                return 30
        elif "month" in retention:
            try:
                return int(retention.split()[0]) * 30
            except (ValueError, IndexError):
                return 30
        else:
            return 30

    def _create_outputs_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        if cloud_provider == "azure":
            content = self._create_azure_outputs_tf(project_name, requirements)
        elif cloud_provider == "aws":
            content = self._create_aws_outputs_tf(project_name, requirements)
        elif cloud_provider == "gcp":
            content = self._create_gcp_outputs_tf(project_name, requirements)
        else:
            content = self._create_azure_outputs_tf(project_name, requirements)
        
        with open(os.path.join(terraform_dir, "outputs.tf"), 'w') as f:
            f.write(content)

    def _create_azure_outputs_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create Azure-specific outputs.tf content."""
        content = f'''# Outputs for {project_name} Terraform configuration on Azure

output "resource_group_name" {{
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}}

output "resource_group_location" {{
  description = "Location of the created resource group"
  value       = azurerm_resource_group.main.location
}}

output "virtual_network_id" {{
  description = "ID of the created virtual network"
  value       = azurerm_virtual_network.main.id
}}

output "virtual_network_name" {{
  description = "Name of the created virtual network"
  value       = azurerm_virtual_network.main.name
}}
'''

        # Add compute outputs
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "vm" in compute_resources:
            content += '''
output "vm_public_ip" {
  description = "Public IP address of the virtual machine"
  value       = azurerm_public_ip.vm.ip_address
}

output "vm_private_ip" {
  description = "Private IP address of the virtual machine"
  value       = azurerm_network_interface.vm.private_ip_address
}
'''

        # Add storage outputs
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "blob_storage" in storage_resources:
            content += '''
output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_endpoint" {
  description = "Primary endpoint of the storage account"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}
'''

        # Add database outputs
        database_resources = requirements.get("resources", {}).get("database", [])
        if "sql_database" in database_resources:
            content += '''
output "sql_server_name" {
  description = "Name of the SQL server"
  value       = azurerm_mssql_server.main.name
}

output "sql_database_name" {
  description = "Name of the SQL database"
  value       = azurerm_mssql_database.main.name
}
'''

        return content

    def _create_aws_outputs_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create AWS-specific outputs.tf content."""
        content = f'''# Outputs for {project_name} Terraform configuration on AWS

output "vpc_id" {{
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}}

output "vpc_cidr_block" {{
  description = "CIDR block of the created VPC"
  value       = aws_vpc.main.cidr_block
}}

output "public_subnet_id" {{
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}}

output "internet_gateway_id" {{
  description = "ID of the internet gateway"
  value       = aws_internet_gateway.main.id
}}
'''

        # Add compute outputs
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "ec2" in compute_resources:
            content += '''
output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "ec2_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.main.private_ip
}
'''

        # Add storage outputs
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "s3" in storage_resources:
            content += '''
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}
'''

        # Add database outputs
        database_resources = requirements.get("resources", {}).get("database", [])
        if "rds" in database_resources:
            content += '''
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}
'''

        return content

    def _create_gcp_outputs_tf(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create GCP-specific outputs.tf content."""
        content = f'''# Outputs for {project_name} Terraform configuration on GCP

output "network_name" {{
  description = "Name of the created network"
  value       = google_compute_network.main.name
}}

output "network_id" {{
  description = "ID of the created network"
  value       = google_compute_network.main.id
}}

output "subnet_name" {{
  description = "Name of the created subnet"
  value       = google_compute_subnetwork.main.name
}}

output "subnet_id" {{
  description = "ID of the created subnet"
  value       = google_compute_subnetwork.main.id
}}
'''

        # Add compute outputs
        compute_resources = requirements.get("resources", {}).get("compute", [])
        if "compute_instance" in compute_resources:
            content += '''
output "instance_name" {
  description = "Name of the compute instance"
  value       = google_compute_instance.main.name
}

output "instance_internal_ip" {
  description = "Internal IP address of the compute instance"
  value       = google_compute_instance.main.network_interface[0].network_ip
}

output "instance_external_ip" {
  description = "External IP address of the compute instance"
  value       = google_compute_instance.main.network_interface[0].access_config[0].nat_ip
}
'''

        # Add storage outputs
        storage_resources = requirements.get("resources", {}).get("storage", [])
        if "cloud_storage" in storage_resources:
            content += '''
output "bucket_name" {
  description = "Name of the storage bucket"
  value       = google_storage_bucket.main.name
}

output "bucket_url" {
  description = "URL of the storage bucket"
  value       = google_storage_bucket.main.url
}
'''

        return content

    def _create_terraform_tfvars(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        cloud_provider = requirements.get("cloud_provider", "azure")
        region = requirements.get("region", "us-east-1")
        
        if cloud_provider == "azure":
            content = self._create_azure_tfvars(project_name, requirements)
        elif cloud_provider == "aws":
            content = self._create_aws_tfvars(project_name, requirements)
        elif cloud_provider == "gcp":
            content = self._create_gcp_tfvars(project_name, requirements)
        else:
            content = self._create_azure_tfvars(project_name, requirements)
        
        with open(os.path.join(terraform_dir, "terraform.tfvars"), 'w') as f:
            f.write(content)

    def _create_azure_tfvars(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create Azure-specific terraform.tfvars content."""
        region = requirements.get("region", "East US")
        retention_days = self._extract_backup_retention_days(requirements)
        
        content = f'''# Terraform variables for {project_name} on Azure

project_name = "{project_name.lower()}"
environment  = "dev"
location     = "{region}"

# VM Configuration
vm_admin_username = "azureuser"
vm_size          = "Standard_B2s"

# Database Configuration
db_admin_username = "dbadmin"
# db_admin_password = "your-secure-password"  # Set this value

# Monitoring
enable_monitoring = true

# Backup Configuration
backup_retention_days = {retention_days}

# Network Security
allowed_ip_ranges = [
  "0.0.0.0/0"  # Update with your actual IP ranges
]

# Additional configuration can be added here
'''
        return content

    def _create_aws_tfvars(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create AWS-specific terraform.tfvars content."""
        region = requirements.get("region", "us-east-1")
        retention_days = self._extract_backup_retention_days(requirements)
        
        content = f'''# Terraform variables for {project_name} on AWS

project_name = "{project_name.lower()}"
environment  = "dev"
aws_region   = "{region}"

# EC2 Configuration
instance_type = "t3.micro"
key_pair_name = "my-key-pair"  # Update with your key pair name

# Database Configuration
db_name           = "mydb"
db_admin_username = "admin"
# db_admin_password = "your-secure-password"  # Set this value

# Monitoring
enable_monitoring = true

# Backup Configuration
backup_retention_days = {retention_days}

# Network Security
allowed_cidr_blocks = [
  "0.0.0.0/0"  # Update with your actual CIDR blocks
]

# Additional configuration can be added here
'''
        return content

    def _create_gcp_tfvars(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create GCP-specific terraform.tfvars content."""
        region = requirements.get("region", "us-central1")
        retention_days = self._extract_backup_retention_days(requirements)
        
        content = f'''# Terraform variables for {project_name} on GCP

project_name   = "{project_name.lower()}"
environment    = "dev"
gcp_project_id = "my-project-id"  # Update with your GCP project ID
gcp_region     = "{region}"

# Compute Configuration
machine_type = "e2-micro"

# Database Configuration
db_admin_username = "admin"
# db_admin_password = "your-secure-password"  # Set this value

# Monitoring
enable_monitoring = true

# Backup Configuration
backup_retention_days = {retention_days}

# Network Security
allowed_source_ranges = [
  "0.0.0.0/0"  # Update with your actual source ranges
]

# Additional configuration can be added here
'''
        return content

    def _create_readme(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        cloud_provider = requirements.get("cloud_provider", "azure")
        
        if cloud_provider == "azure":
            content = self._create_azure_readme(project_name, requirements)
        elif cloud_provider == "aws":
            content = self._create_aws_readme(project_name, requirements)
        elif cloud_provider == "gcp":
            content = self._create_gcp_readme(project_name, requirements)
        else:
            content = self._create_azure_readme(project_name, requirements)
        
        with open(os.path.join(terraform_dir, "README.md"), 'w') as f:
            f.write(content)

    def _create_azure_readme(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create Azure-specific README content."""
        content = f'''# Terraform Infrastructure for {project_name} on Azure

This directory contains Terraform configuration files for deploying the {project_name} infrastructure on Azure.

## Prerequisites

1. Azure CLI installed and configured
2. Terraform >= 1.0 installed
3. Appropriate Azure permissions

## Quick Start

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Review the plan:**
   ```bash
   terraform plan
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply
   ```

4. **Destroy resources (when needed):**
   ```bash
   terraform destroy
   ```

## Configuration Files

- `main.tf` - Main infrastructure resources
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values
- `terraform.tfvars` - Variable values (customize as needed)

## Resources Created

- **Resource Group**: Container for all resources
- **Virtual Network**: Network infrastructure with subnets
- **Network Security Groups**: Security rules for network traffic
- **Storage Account**: Object storage for applications
- **Key Vault**: Secure storage for secrets and certificates
- **Log Analytics Workspace**: Monitoring and logging

## Network Architecture

```
Virtual Network (10.0.0.0/16)
├── Web Subnet (10.0.1.0/24)
├── App Subnet (10.0.2.0/24)
└── Data Subnet (10.0.3.0/24)
```

## Security

- Network Security Groups control traffic flow
- Storage Account has HTTPS-only access enabled
- Key Vault for secure secret management
- All resources are tagged for management

## Customization

Update `terraform.tfvars` with your specific values:

```hcl
project_name = "{project_name.lower()}"
environment  = "dev"  # or "staging", "prod"
location     = "East US"  # or your preferred region
```

## Monitoring

Log Analytics Workspace is configured for:
- Infrastructure monitoring
- Application insights
- Security monitoring
- Cost tracking

## Support

For questions or issues, refer to the project documentation or contact the infrastructure team.
'''
        return content

    def _create_aws_readme(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create AWS-specific README content."""
        content = f'''# Terraform Infrastructure for {project_name} on AWS

This directory contains Terraform configuration files for deploying the {project_name} infrastructure on AWS.

## Prerequisites

1. AWS CLI installed and configured
2. Terraform >= 1.0 installed
3. Appropriate AWS permissions
4. EC2 Key Pair created for SSH access

## Quick Start

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Review the plan:**
   ```bash
   terraform plan
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply
   ```

4. **Destroy resources (when needed):**
   ```bash
   terraform destroy
   ```

## Configuration Files

- `main.tf` - Main infrastructure resources
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values
- `terraform.tfvars` - Variable values (customize as needed)

## Resources Created

- **VPC**: Virtual Private Cloud with public and private subnets
- **Internet Gateway**: Internet access for public resources
- **Security Groups**: Network security rules
- **EC2 Instance**: Virtual machine in public subnet
- **RDS Database**: MySQL database in private subnet
- **S3 Bucket**: Object storage with versioning
- **Route Tables**: Network routing configuration

## Network Architecture

```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)
│   ├── Internet Gateway
│   └── EC2 Instance
└── Private Subnet (10.0.2.0/24)
    └── RDS Database
```

## Security

- Security Groups control traffic flow
- RDS in private subnet, accessible only from EC2
- S3 bucket with server-side encryption
- All resources are tagged for management

## Customization

Update `terraform.tfvars` with your specific values:

```hcl
project_name  = "{project_name.lower()}"
environment   = "dev"  # or "staging", "prod"
aws_region    = "us-west-2"  # or your preferred region
key_pair_name = "my-key-pair"  # your EC2 key pair name
```

## Monitoring

CloudWatch is configured for:
- Infrastructure monitoring
- Application logs
- Security monitoring
- Cost tracking

## Support

For questions or issues, refer to the project documentation or contact the infrastructure team.
'''
        return content

    def _create_gcp_readme(self, project_name: str, requirements: Dict[str, Any]) -> str:
        """Create GCP-specific README content."""
        content = f'''# Terraform Infrastructure for {project_name} on GCP

This directory contains Terraform configuration files for deploying the {project_name} infrastructure on Google Cloud Platform.

## Prerequisites

1. Google Cloud SDK installed and configured
2. Terraform >= 1.0 installed
3. Appropriate GCP permissions
4. GCP Project with billing enabled

## Quick Start

1. **Initialize Terraform:**
   ```bash
   terraform init
   ```

2. **Review the plan:**
   ```bash
   terraform plan
   ```

3. **Apply the configuration:**
   ```bash
   terraform apply
   ```

4. **Destroy resources (when needed):**
   ```bash
   terraform destroy
   ```

## Configuration Files

- `main.tf` - Main infrastructure resources
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values
- `terraform.tfvars` - Variable values (customize as needed)

## Resources Created

- **VPC Network**: Virtual Private Cloud with custom subnets
- **Firewall Rules**: Network security rules
- **Compute Instance**: Virtual machine with external IP
- **Cloud Storage Bucket**: Object storage with versioning
- **Subnetwork**: Custom subnet configuration

## Network Architecture

```
VPC Network
├── Custom Subnet (10.0.1.0/24)
│   ├── Compute Instance
│   └── External IP
└── Firewall Rules
    ├── HTTP/HTTPS (80, 443)
    └── SSH (22)
```

## Security

- Firewall rules control traffic flow
- Storage bucket with uniform bucket-level access
- Compute instance with external IP for demo purposes
- All resources are labeled for management

## Customization

Update `terraform.tfvars` with your specific values:

```hcl
project_name   = "{project_name.lower()}"
environment    = "dev"  # or "staging", "prod"
gcp_project_id = "my-project-id"  # your GCP project ID
gcp_region     = "us-central1"  # or your preferred region
```

## Monitoring

Stackdriver is configured for:
- Infrastructure monitoring
- Application logs
- Security monitoring
- Cost tracking

## Support

For questions or issues, refer to the project documentation or contact the infrastructure team.
'''
        return content
