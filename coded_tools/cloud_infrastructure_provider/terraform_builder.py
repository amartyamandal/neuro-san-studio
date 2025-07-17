# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.

import os
import logging
from typing import Any, Dict, Union

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
            self._create_readme(terraform_dir, project_name)
            
            return f"Terraform infrastructure successfully generated at {terraform_dir}"
            
        except Exception as e:
            return f"Error: Failed to generate Terraform infrastructure - {str(e)}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)

    def _parse_design_requirements(self, design_content: str) -> Dict[str, Any]:
        """Parse design document to extract infrastructure requirements."""
        requirements = {
            "services": [],
            "databases": [],
            "load_balancers": [],
            "monitoring": False,
            "ssl": False,
            "backup": False,
            "security": [],
            "networking": {"vpc": True},
            "scaling": {"auto_scaling": False}
        }
        
        content_lower = design_content.lower()
        
        # Parse services from design
        if "nginx" in content_lower or "web server" in content_lower:
            requirements["services"].append("nginx")
        if "apache" in content_lower:
            requirements["services"].append("apache")
        if "docker" in content_lower or "container" in content_lower:
            requirements["services"].append("docker")
        if "redis" in content_lower:
            requirements["services"].append("redis")
        if "elasticsearch" in content_lower:
            requirements["services"].append("elasticsearch")
            
        # Parse databases
        if "postgresql" in content_lower or "postgres" in content_lower:
            requirements["databases"].append("postgresql")
        if "mysql" in content_lower:
            requirements["databases"].append("mysql")
        if "mongodb" in content_lower:
            requirements["databases"].append("mongodb")
            
        # Parse infrastructure components
        if "load balancer" in content_lower or "load balancing" in content_lower:
            requirements["load_balancers"].append("alb")
            
        # Parse monitoring requirements
        requirements["monitoring"] = "monitoring" in content_lower or "metrics" in content_lower
        
        # Parse security requirements
        if "ssl" in content_lower or "tls" in content_lower or "https" in content_lower:
            requirements["ssl"] = True
        if "firewall" in content_lower or "security group" in content_lower:
            requirements["security"].append("security_groups")
        if "waf" in content_lower or "web application firewall" in content_lower:
            requirements["security"].append("waf")
            
        # Parse backup requirements
        requirements["backup"] = "backup" in content_lower or "disaster recovery" in content_lower
        
        # Parse scaling requirements
        requirements["scaling"]["auto_scaling"] = "auto scaling" in content_lower or "autoscaling" in content_lower
        
        return requirements

    def _create_main_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        """Generate main.tf based on design requirements."""
        
        # Base infrastructure
        content = f'''# Terraform configuration for {project_name}

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
        if requirements.get("networking", {}).get("vpc", True):
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

        # Add security groups if security is required
        if "security_groups" in requirements.get("security", []):
            content += '''
# Network Security Groups
resource "azurerm_network_security_group" "web" {
  name                = "nsg-web-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "HTTP"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
'''
            
            # Add HTTPS rule if SSL is enabled
            if requirements.get("ssl", False):
                content += '''
  security_rule {
    name                       = "HTTPS"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
'''
            
            content += '''
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add databases based on requirements
        for db in requirements.get("databases", []):
            if db == "postgresql":
                content += '''
# PostgreSQL Database
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "psql-${var.project_name}-${var.environment}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  
  sku_name   = "B_Standard_B1ms"
  storage_mb = 32768
  version    = "13"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''
            elif db == "mysql":
                content += '''
# MySQL Database
resource "azurerm_mysql_flexible_server" "main" {
  name                = "mysql-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  
  sku_name = "B_Standard_B1ms"
  version  = "8.0.21"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add load balancer if required
        if requirements.get("load_balancers"):
            content += '''
# Application Gateway (Load Balancer)
resource "azurerm_public_ip" "gateway" {
  name                = "pip-gateway-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                = "Standard"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''

        # Add monitoring if required
        if requirements.get("monitoring", False):
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
        if requirements.get("backup", False):
            content += '''
# Storage Account for Backups
resource "azurerm_storage_account" "backup" {
  name                     = "stbackup${lower(replace(var.project_name, "-", ""))}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
'''
        
        with open(os.path.join(terraform_dir, "main.tf"), 'w') as f:
            f.write(content)

    def _create_variables_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        content = f'''# Variables for {project_name} Terraform configuration

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
  default     = "East US"
}}

variable "admin_username" {{
  description = "Administrator username for VMs"
  type        = string
  default     = "azureuser"
}}

variable "vm_size" {{
  description = "Size of the virtual machines"
  type        = string
  default     = "Standard_B2s"
}}

variable "enable_monitoring" {{
  description = "Enable monitoring and diagnostics"
  type        = bool
  default     = true
}}

variable "backup_retention_days" {{
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}}

variable "allowed_ip_ranges" {{
  description = "List of IP ranges allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}}
'''
        
        with open(os.path.join(terraform_dir, "variables.tf"), 'w') as f:
            f.write(content)

    def _create_outputs_tf(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        content = f'''# Outputs for {project_name} Terraform configuration

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

output "subnet_ids" {{
  description = "IDs of the created subnets"
  value = {{
    web  = azurerm_subnet.web.id
    app  = azurerm_subnet.app.id
    data = azurerm_subnet.data.id
  }}
}}

output "storage_account_name" {{
  description = "Name of the created storage account"
  value       = azurerm_storage_account.main.name
}}

output "storage_account_primary_endpoint" {{
  description = "Primary endpoint of the storage account"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}}

output "key_vault_name" {{
  description = "Name of the created Key Vault"
  value       = azurerm_key_vault.main.name
}}

output "key_vault_uri" {{
  description = "URI of the created Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}}

output "log_analytics_workspace_id" {{
  description = "ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}}

output "log_analytics_workspace_name" {{
  description = "Name of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.name
}}
'''
        
        with open(os.path.join(terraform_dir, "outputs.tf"), 'w') as f:
            f.write(content)

    def _create_terraform_tfvars(self, terraform_dir: str, project_name: str, requirements: Dict[str, Any]):
        content = f'''# Terraform variables for {project_name}

project_name = "{project_name.lower()}"
environment  = "dev"
location     = "East US"

# VM Configuration
admin_username = "azureuser"
vm_size       = "Standard_B2s"

# Monitoring
enable_monitoring = true

# Backup Configuration
backup_retention_days = 30

# Network Security
allowed_ip_ranges = [
  "0.0.0.0/0"  # Update with your actual IP ranges
]

# Additional configuration can be added here
'''
        
        with open(os.path.join(terraform_dir, "terraform.tfvars"), 'w') as f:
            f.write(content)

    def _create_readme(self, terraform_dir: str, project_name: str):
        content = f'''# Terraform Infrastructure for {project_name}

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
        
        with open(os.path.join(terraform_dir, "README.md"), 'w') as f:
            f.write(content)
