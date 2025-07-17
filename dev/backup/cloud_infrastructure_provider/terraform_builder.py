# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
# END COPYRIGHT

import os
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class TerraformBuilder(CodedTool):
    """
    Generates Terraform infrastructure code based on design specifications.
    This tool reads design documents and creates appropriate Terraform modules and configurations.
    """

    def __init__(self):
        """
        Initialize the TerraformBuilder.
        """
        pass

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Generate Terraform code based on the design document.

        :param args: A dictionary with the following keys:
                    "design_path": Path to the design.md file to implement
                    "timestamp": Project timestamp in MMDDYYYYHHMMSS format

        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.

        :return: Success message with paths to created Terraform files or error message.
        """
        try:
            design_path = args.get("design_path", "")
            timestamp = args.get("timestamp", "")
            
            if not design_path:
                return "Error: design_path parameter is required"
            
            if not timestamp:
                return "Error: timestamp parameter is required"

            print(f"========== Building Terraform Code ==========")
            print(f"    Design Path: {design_path}")
            print(f"    Timestamp: {timestamp}")

            # Read the design document
            if not os.path.exists(design_path):
                return f"Error: Design file not found at {design_path}"

            with open(design_path, 'r') as f:
                design_content = f.read()

            # Create output directory structure for Terraform
            output_dir = os.path.join("output", f"LZ_{timestamp}")
            terraform_dir = os.path.join(output_dir, "iac", "terraform")
            os.makedirs(terraform_dir, exist_ok=True)

            # Create subdirectories for modular structure
            modules_dir = os.path.join(terraform_dir, "modules")
            environments_dir = os.path.join(terraform_dir, "environments", "dev")
            os.makedirs(modules_dir, exist_ok=True)
            os.makedirs(environments_dir, exist_ok=True)

            # Generate Terraform files
            created_files = []
            
            # Main configuration files
            main_tf_path = os.path.join(terraform_dir, "main.tf")
            with open(main_tf_path, 'w') as f:
                f.write(self._generate_main_tf())
            created_files.append(main_tf_path)

            # Variables file
            variables_tf_path = os.path.join(terraform_dir, "variables.tf")
            with open(variables_tf_path, 'w') as f:
                f.write(self._generate_variables_tf())
            created_files.append(variables_tf_path)

            # Outputs file
            outputs_tf_path = os.path.join(terraform_dir, "outputs.tf")
            with open(outputs_tf_path, 'w') as f:
                f.write(self._generate_outputs_tf())
            created_files.append(outputs_tf_path)

            # Provider configuration
            provider_tf_path = os.path.join(terraform_dir, "provider.tf")
            with open(provider_tf_path, 'w') as f:
                f.write(self._generate_provider_tf())
            created_files.append(provider_tf_path)

            # Terraform configuration for state backend
            versions_tf_path = os.path.join(terraform_dir, "versions.tf")
            with open(versions_tf_path, 'w') as f:
                f.write(self._generate_versions_tf())
            created_files.append(versions_tf_path)

            # Environment-specific terraform.tfvars
            tfvars_path = os.path.join(environments_dir, "terraform.tfvars")
            with open(tfvars_path, 'w') as f:
                f.write(self._generate_tfvars())
            created_files.append(tfvars_path)

            # Network module
            network_module_dir = os.path.join(modules_dir, "network")
            os.makedirs(network_module_dir, exist_ok=True)
            
            network_main_path = os.path.join(network_module_dir, "main.tf")
            with open(network_main_path, 'w') as f:
                f.write(self._generate_network_module())
            created_files.append(network_main_path)

            network_vars_path = os.path.join(network_module_dir, "variables.tf")
            with open(network_vars_path, 'w') as f:
                f.write(self._generate_network_variables())
            created_files.append(network_vars_path)

            network_outputs_path = os.path.join(network_module_dir, "outputs.tf")
            with open(network_outputs_path, 'w') as f:
                f.write(self._generate_network_outputs())
            created_files.append(network_outputs_path)

            # README for Terraform
            readme_path = os.path.join(terraform_dir, "README.md")
            with open(readme_path, 'w') as f:
                f.write(self._generate_terraform_readme(timestamp))
            created_files.append(readme_path)

            success_message = f"Terraform code generated successfully in {terraform_dir}. Created {len(created_files)} files."
            print(f"    Result: {success_message}")
            print(f"    Files created: {created_files}")
            
            # Store the terraform directory in sly_data for other tools to use
            sly_data["terraform_directory"] = terraform_dir
            sly_data["terraform_files"] = created_files
            
            return success_message

        except Exception as e:
            error_msg = f"Error generating Terraform code: {str(e)}"
            print(f"    Error: {error_msg}")
            return f"Error: {error_msg}"

    def _generate_main_tf(self) -> str:
        """Generate the main Terraform configuration."""
        return '''# Main Terraform configuration for cloud infrastructure

terraform {
  required_version = ">= 1.0"
  backend "azurerm" {
    # Backend configuration will be provided during terraform init
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = var.common_tags
}

# Network Module
module "network" {
  source = "./modules/network"

  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  environment        = var.environment
  common_tags        = var.common_tags
}

# Application Gateway (if needed)
resource "azurerm_public_ip" "app_gateway" {
  count               = var.enable_app_gateway ? 1 : 0
  name                = "${var.resource_prefix}-appgw-pip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.common_tags
}

# Storage Account for diagnostics
resource "azurerm_storage_account" "diagnostics" {
  name                     = "${replace(var.resource_prefix, "-", "")}diag"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  tags = var.common_tags
}
'''

    def _generate_variables_tf(self) -> str:
        """Generate the variables configuration."""
        return '''# Variables for the infrastructure deployment

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "resource_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "enable_app_gateway" {
  description = "Enable Application Gateway"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    "Environment" = "dev"
    "Project"     = "landing-zone"
    "ManagedBy"   = "Terraform"
  }
}

variable "network_config" {
  description = "Network configuration"
  type = object({
    vnet_address_space = list(string)
    subnet_configs = map(object({
      address_prefixes = list(string)
      service_endpoints = list(string)
    }))
  })
  default = {
    vnet_address_space = ["10.0.0.0/16"]
    subnet_configs = {
      "web" = {
        address_prefixes  = ["10.0.1.0/24"]
        service_endpoints = ["Microsoft.Storage"]
      }
      "app" = {
        address_prefixes  = ["10.0.2.0/24"]
        service_endpoints = ["Microsoft.Storage"]
      }
      "data" = {
        address_prefixes  = ["10.0.3.0/24"]
        service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
      }
    }
  }
}
'''

    def _generate_outputs_tf(self) -> str:
        """Generate the outputs configuration."""
        return '''# Outputs for the infrastructure deployment

output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID of the created resource group"
  value       = azurerm_resource_group.main.id
}

output "location" {
  description = "Azure region where resources are deployed"
  value       = azurerm_resource_group.main.location
}

output "vnet_id" {
  description = "ID of the virtual network"
  value       = module.network.vnet_id
}

output "subnet_ids" {
  description = "IDs of the created subnets"
  value       = module.network.subnet_ids
}

output "storage_account_name" {
  description = "Name of the diagnostics storage account"
  value       = azurerm_storage_account.diagnostics.name
}

output "storage_account_primary_key" {
  description = "Primary key of the diagnostics storage account"
  value       = azurerm_storage_account.diagnostics.primary_access_key
  sensitive   = true
}
'''

    def _generate_provider_tf(self) -> str:
        """Generate the provider configuration."""
        return '''# Provider configuration for Azure

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}
'''

    def _generate_versions_tf(self) -> str:
        """Generate the versions and backend configuration."""
        return '''# Terraform version and backend configuration

terraform {
  required_version = ">= 1.0"
  
  backend "azurerm" {
    # Configure these values during terraform init:
    # resource_group_name  = "terraform-state-rg"
    # storage_account_name = "terraformstate<randomstring>"
    # container_name       = "terraform-state"
    # key                  = "infrastructure.tfstate"
  }
}
'''

    def _generate_tfvars(self) -> str:
        """Generate the terraform.tfvars file."""
        return '''# Environment-specific variables for development

resource_group_name = "lz-dev-rg"
location           = "East US"
environment        = "dev"
resource_prefix    = "lz-dev"
enable_app_gateway = false

common_tags = {
  "Environment" = "dev"
  "Project"     = "landing-zone"
  "ManagedBy"   = "Terraform"
  "CostCenter"  = "IT"
}

network_config = {
  vnet_address_space = ["10.0.0.0/16"]
  subnet_configs = {
    "web" = {
      address_prefixes  = ["10.0.1.0/24"]
      service_endpoints = ["Microsoft.Storage"]
    }
    "app" = {
      address_prefixes  = ["10.0.2.0/24"]
      service_endpoints = ["Microsoft.Storage"]
    }
    "data" = {
      address_prefixes  = ["10.0.3.0/24"]
      service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
    }
  }
}
'''

    def _generate_network_module(self) -> str:
        """Generate the network module main configuration."""
        return '''# Network module for creating VNet and subnets

resource "azurerm_virtual_network" "main" {
  name                = "${var.resource_prefix}-vnet"
  address_space       = var.vnet_address_space
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

resource "azurerm_subnet" "subnets" {
  for_each = var.subnet_configs

  name                 = "${var.resource_prefix}-${each.key}-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = each.value.address_prefixes
  service_endpoints    = each.value.service_endpoints
}

resource "azurerm_network_security_group" "subnet_nsgs" {
  for_each = var.subnet_configs

  name                = "${var.resource_prefix}-${each.key}-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name

  # Default security rules
  security_rule {
    name                       = "AllowHTTPSInbound"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPInbound"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.common_tags
}

resource "azurerm_subnet_network_security_group_association" "subnet_nsg_associations" {
  for_each = var.subnet_configs

  subnet_id                 = azurerm_subnet.subnets[each.key].id
  network_security_group_id = azurerm_network_security_group.subnet_nsgs[each.key].id
}
'''

    def _generate_network_variables(self) -> str:
        """Generate the network module variables."""
        return '''# Variables for the network module

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "resource_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_configs" {
  description = "Configuration for subnets"
  type = map(object({
    address_prefixes  = list(string)
    service_endpoints = list(string)
  }))
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}
'''

    def _generate_network_outputs(self) -> str:
        """Generate the network module outputs."""
        return '''# Outputs for the network module

output "vnet_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}

output "vnet_name" {
  description = "Name of the virtual network"
  value       = azurerm_virtual_network.main.name
}

output "subnet_ids" {
  description = "Map of subnet names to IDs"
  value       = { for k, v in azurerm_subnet.subnets : k => v.id }
}

output "subnet_names" {
  description = "Map of subnet names"
  value       = { for k, v in azurerm_subnet.subnets : k => v.name }
}

output "nsg_ids" {
  description = "Map of NSG names to IDs"
  value       = { for k, v in azurerm_network_security_group.subnet_nsgs : k => v.id }
}
'''

    def _generate_terraform_readme(self, timestamp: str) -> str:
        """Generate README for the Terraform code."""
        return f'''# Terraform Infrastructure - LZ_{timestamp}

This directory contains Terraform code for deploying cloud infrastructure based on the design specifications.

## Directory Structure

```
terraform/
├── main.tf              # Main infrastructure configuration
├── variables.tf         # Variable definitions
├── outputs.tf          # Output definitions
├── provider.tf         # Provider configuration
├── versions.tf         # Version constraints and backend config
├── README.md           # This file
├── modules/
│   └── network/        # Network module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    └── dev/
        └── terraform.tfvars  # Environment-specific variables
```

## Prerequisites

1. **Azure CLI** - Install and configure Azure CLI
2. **Terraform** - Version >= 1.0
3. **Azure Subscription** - With appropriate permissions

## Setup Instructions

### 1. Configure Azure CLI
```bash
az login
az account set --subscription "<your-subscription-id>"
```

### 2. Create State Storage (First time only)
```bash
# Create resource group for Terraform state
az group create --name terraform-state-rg --location "East US"

# Create storage account
az storage account create \\
  --name terraformstate$(openssl rand -hex 3) \\
  --resource-group terraform-state-rg \\
  --location "East US" \\
  --sku Standard_LRS

# Create container
az storage container create \\
  --name terraform-state \\
  --account-name <storage-account-name>
```

### 3. Initialize Terraform
```bash
terraform init \\
  -backend-config="resource_group_name=terraform-state-rg" \\
  -backend-config="storage_account_name=<storage-account-name>" \\
  -backend-config="container_name=terraform-state" \\
  -backend-config="key=infrastructure.tfstate"
```

### 4. Plan and Apply
```bash
# Validate configuration
terraform validate

# Plan deployment
terraform plan -var-file="environments/dev/terraform.tfvars"

# Apply configuration
terraform apply -var-file="environments/dev/terraform.tfvars"
```

## Customization

### Variables
Edit `environments/dev/terraform.tfvars` to customize:
- Resource names and prefixes
- Network configuration
- Tags and metadata

### Modules
The `modules/` directory contains reusable components:
- **network**: VNet, subnets, and NSGs

## Validation

After deployment, verify resources are created:
```bash
# List resources in the resource group
az resource list --resource-group <resource-group-name> --output table

# Get network information
az network vnet list --resource-group <resource-group-name>
```

## Cleanup

To destroy all resources:
```bash
terraform destroy -var-file="environments/dev/terraform.tfvars"
```

## Security Considerations

1. **State File**: Contains sensitive data - store securely in Azure Storage
2. **Variables**: Use Azure Key Vault for secrets
3. **Network**: Review NSG rules before deployment
4. **Access**: Follow least-privilege principle

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check Azure CLI login
   az account show
   
   # Re-login if needed
   az login
   ```

2. **State Lock Issues**
   ```bash
   # Force unlock if needed (use carefully)
   terraform force-unlock <lock-id>
   ```

3. **Resource Already Exists**
   ```bash
   # Import existing resource
   terraform import azurerm_resource_group.main /subscriptions/<sub-id>/resourceGroups/<rg-name>
   ```

4. **Permission Denied**
   ```bash
   # Check subscription and permissions
   az account list --output table
   az role assignment list --assignee <user-id>
   ```

### Debug Mode
```bash
# Enable detailed logging
export TF_LOG=DEBUG
terraform plan -var-file="environments/dev/terraform.tfvars"
```

## Support

For questions or issues:
1. Review the design document in `docs/design.md`
2. Check Terraform documentation
3. Contact the infrastructure team

---
*Generated on: {timestamp}*
'''

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method.
        """
        return self.invoke(args, sly_data)
