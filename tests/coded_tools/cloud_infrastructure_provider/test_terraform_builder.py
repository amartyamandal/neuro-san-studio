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
import tempfile
import unittest

from coded_tools.cloud_infrastructure_provider.terraform_builder import TerraformBuilder


class TestTerraformBuilder(unittest.TestCase):
    """
    Unit tests for the TerraformBuilder class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.builder = TerraformBuilder()
        self.test_timestamp = "07162025140200"
        self.test_design_content = """
        # Cloud Infrastructure Design: LZ_07162025140200
        
        ## Overview
        - Azure Landing Zone for e-commerce application
        - High availability architecture
        - Multi-tier design (web, app, data)
        
        ## Architecture
        - Virtual Network with subnets
        - Load balancers for HA
        - Storage accounts for diagnostics
        - Security groups for network control
        """

    def test_init(self):
        """
        Test the initialization of TerraformBuilder.
        """
        builder = TerraformBuilder()
        self.assertIsNotNone(builder)

    def test_invoke_success(self):
        """
        Test successful generation of Terraform code.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a design file first
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check result
                self.assertIn("Terraform code generated successfully", result)
                self.assertIn(f"LZ_{self.test_timestamp}", result)
                
                # Check sly_data was updated
                self.assertIn("terraform_directory", sly_data)
                self.assertIn("terraform_files", sly_data)
                
                # Check Terraform directory structure
                terraform_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform")
                self.assertTrue(os.path.exists(terraform_dir))
                
                # Check main files exist
                expected_files = [
                    "main.tf",
                    "variables.tf",
                    "outputs.tf",
                    "provider.tf",
                    "versions.tf",
                    "README.md"
                ]
                
                for file_name in expected_files:
                    file_path = os.path.join(terraform_dir, file_name)
                    self.assertTrue(os.path.exists(file_path), f"Missing file: {file_name}")
                
                # Check modules directory
                modules_dir = os.path.join(terraform_dir, "modules", "network")
                self.assertTrue(os.path.exists(modules_dir))
                
                # Check module files
                module_files = ["main.tf", "variables.tf", "outputs.tf"]
                for file_name in module_files:
                    file_path = os.path.join(modules_dir, file_name)
                    self.assertTrue(os.path.exists(file_path), f"Missing module file: {file_name}")
                
                # Check environments directory
                env_dir = os.path.join(terraform_dir, "environments", "dev")
                self.assertTrue(os.path.exists(env_dir))
                
                tfvars_path = os.path.join(env_dir, "terraform.tfvars")
                self.assertTrue(os.path.exists(tfvars_path))
                
            finally:
                os.chdir(original_cwd)

    def test_invoke_missing_design_path(self):
        """
        Test error handling when design_path parameter is missing.
        """
        args = {"timestamp": self.test_timestamp}
        sly_data = {}
        
        result = self.builder.invoke(args, sly_data)
        
        self.assertIn("Error: design_path parameter is required", result)

    def test_invoke_missing_timestamp(self):
        """
        Test error handling when timestamp parameter is missing.
        """
        args = {"design_path": "/some/path/design.md"}
        sly_data = {}
        
        result = self.builder.invoke(args, sly_data)
        
        self.assertIn("Error: timestamp parameter is required", result)

    def test_invoke_design_file_not_found(self):
        """
        Test error handling when design file doesn't exist.
        """
        args = {
            "design_path": "/non/existent/design.md",
            "timestamp": self.test_timestamp
        }
        sly_data = {}
        
        result = self.builder.invoke(args, sly_data)
        
        self.assertIn("Error: Design file not found", result)

    def test_main_tf_content(self):
        """
        Test that main.tf file has expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check main.tf content
                main_tf_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "main.tf")
                with open(main_tf_path, 'r') as f:
                    content = f.read()
                    
                    # Check required resources and modules
                    self.assertIn("terraform {", content)
                    self.assertIn("resource \"azurerm_resource_group\"", content)
                    self.assertIn("module \"network\"", content)
                    self.assertIn("resource \"azurerm_storage_account\"", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_variables_tf_content(self):
        """
        Test that variables.tf file has expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check variables.tf content
                vars_tf_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "variables.tf")
                with open(vars_tf_path, 'r') as f:
                    content = f.read()
                    
                    # Check required variables
                    expected_variables = [
                        "resource_group_name",
                        "location",
                        "environment",
                        "resource_prefix",
                        "common_tags",
                        "network_config"
                    ]
                    
                    for var in expected_variables:
                        self.assertIn(f'variable "{var}"', content)
                    
            finally:
                os.chdir(original_cwd)

    def test_outputs_tf_content(self):
        """
        Test that outputs.tf file has expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check outputs.tf content
                outputs_tf_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "outputs.tf")
                with open(outputs_tf_path, 'r') as f:
                    content = f.read()
                    
                    # Check required outputs
                    expected_outputs = [
                        "resource_group_name",
                        "resource_group_id",
                        "location",
                        "vnet_id",
                        "subnet_ids",
                        "storage_account_name"
                    ]
                    
                    for output in expected_outputs:
                        self.assertIn(f'output "{output}"', content)
                    
            finally:
                os.chdir(original_cwd)

    def test_provider_tf_content(self):
        """
        Test that provider.tf file has expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check provider.tf content
                provider_tf_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "provider.tf")
                with open(provider_tf_path, 'r') as f:
                    content = f.read()
                    
                    # Check provider configuration
                    self.assertIn("terraform {", content)
                    self.assertIn("required_providers {", content)
                    self.assertIn("azurerm", content)
                    self.assertIn("provider \"azurerm\"", content)
                    self.assertIn("features {", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_network_module_content(self):
        """
        Test that network module files have expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check network module main.tf
                network_main_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "modules", "network", "main.tf")
                with open(network_main_path, 'r') as f:
                    content = f.read()
                    
                    # Check network resources
                    self.assertIn("resource \"azurerm_virtual_network\"", content)
                    self.assertIn("resource \"azurerm_subnet\"", content)
                    self.assertIn("resource \"azurerm_network_security_group\"", content)
                    self.assertIn("for_each", content)  # Should use for_each for subnets
                    
            finally:
                os.chdir(original_cwd)

    def test_tfvars_content(self):
        """
        Test that terraform.tfvars file has expected content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check terraform.tfvars content
                tfvars_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "environments", "dev", "terraform.tfvars")
                with open(tfvars_path, 'r') as f:
                    content = f.read()
                    
                    # Check required variable assignments
                    self.assertIn("resource_group_name", content)
                    self.assertIn("location", content)
                    self.assertIn("environment", content)
                    self.assertIn("resource_prefix", content)
                    self.assertIn("common_tags", content)
                    self.assertIn("network_config", content)
                    
                    # Check values
                    self.assertIn('"dev"', content)
                    self.assertIn('"East US"', content)
                    
            finally:
                os.chdir(original_cwd)

    def test_readme_content(self):
        """
        Test that README.md file has expected content and timestamp.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.builder.invoke(args, sly_data)
                
                # Check README.md content
                readme_path = os.path.join("output", f"LZ_{self.test_timestamp}", "iac", "terraform", "README.md")
                with open(readme_path, 'r') as f:
                    content = f.read()
                    
                    # Check timestamp in title
                    self.assertIn(f"LZ_{self.test_timestamp}", content)
                    
                    # Check required sections
                    expected_sections = [
                        "## Directory Structure",
                        "## Prerequisites",
                        "## Setup Instructions",
                        "## Customization",
                        "## Security Considerations",
                        "## Troubleshooting"
                    ]
                    
                    for section in expected_sections:
                        self.assertIn(section, content)
                    
                    # Check Azure CLI commands
                    self.assertIn("az login", content)
                    self.assertIn("terraform init", content)
                    self.assertIn("terraform plan", content)
                    self.assertIn("terraform apply", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_async_invoke(self):
        """
        Test that async_invoke delegates to invoke.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design file
                design_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "docs")
                os.makedirs(design_dir, exist_ok=True)
                design_path = os.path.join(design_dir, "design.md")
                
                with open(design_path, 'w') as f:
                    f.write(self.test_design_content)
                
                args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                # Test async invoke
                import asyncio
                result = asyncio.run(self.builder.async_invoke(args, sly_data))
                
                self.assertIn("Terraform code generated successfully", result)
                
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
