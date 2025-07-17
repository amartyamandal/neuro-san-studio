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
from unittest.mock import patch

from coded_tools.cloud_infrastructure_provider.design_document_creator import DesignDocumentCreator
from coded_tools.cloud_infrastructure_provider.project_plan_creator import ProjectPlanCreator
from coded_tools.cloud_infrastructure_provider.terraform_builder import TerraformBuilder
from coded_tools.cloud_infrastructure_provider.ansible_builder import AnsibleBuilder


class TestCloudInfrastructureProviderIntegration(unittest.TestCase):
    """
    Integration tests for the Cloud Infrastructure Provider system.
    Tests the complete workflow from design creation to code generation.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.test_timestamp = "07162025140200"
        self.test_project_details = """
        Project: Azure Landing Zone for E-commerce Platform
        
        Business Requirements:
        - Support 10,000 concurrent users
        - 99.9% availability SLA
        - PCI DSS compliance for payment processing
        - Global deployment (US East, US West, Europe)
        
        Technical Requirements:
        - 3-tier architecture (web, app, database)
        - Auto-scaling capabilities
        - Load balancing with SSL termination
        - Database clustering for high availability
        - Monitoring and alerting
        - Backup and disaster recovery
        
        Cloud Provider: Azure
        Primary Region: East US
        Secondary Region: West US
        
        Technologies:
        - Terraform for Infrastructure as Code
        - Ansible for configuration management
        - Docker containers for applications
        - Azure SQL Database for data persistence
        - Azure Application Gateway for load balancing
        """

    def test_complete_workflow(self):
        """
        Test the complete end-to-end workflow from design to code generation.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Step 1: Create design document
                design_creator = DesignDocumentCreator()
                design_args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                design_sly_data = {}
                
                design_result = design_creator.invoke(design_args, design_sly_data)
                
                # Verify design creation
                self.assertIn("Design document created successfully", design_result)
                self.assertIn("design_document_path", design_sly_data)
                
                design_path = design_sly_data["design_document_path"]
                self.assertTrue(os.path.exists(design_path))
                
                # Step 2: Create project plan
                plan_creator = ProjectPlanCreator()
                plan_args = {
                    "design_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                plan_sly_data = {}
                
                plan_result = plan_creator.invoke(plan_args, plan_sly_data)
                
                # Verify plan creation
                self.assertIn("Project plan created successfully", plan_result)
                self.assertIn("project_plan_path", plan_sly_data)
                
                plan_path = plan_sly_data["project_plan_path"]
                self.assertTrue(os.path.exists(plan_path))
                
                # Step 3: Generate Terraform code
                terraform_builder = TerraformBuilder()
                terraform_args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                terraform_sly_data = {}
                
                terraform_result = terraform_builder.invoke(terraform_args, terraform_sly_data)
                
                # Verify Terraform generation
                self.assertIn("Terraform code generated successfully", terraform_result)
                self.assertIn("terraform_directory", terraform_sly_data)
                
                terraform_dir = terraform_sly_data["terraform_directory"]
                self.assertTrue(os.path.exists(terraform_dir))
                
                # Step 4: Generate Ansible configuration
                ansible_builder = AnsibleBuilder()
                ansible_args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                ansible_sly_data = {}
                
                ansible_result = ansible_builder.invoke(ansible_args, ansible_sly_data)
                
                # Verify Ansible generation
                self.assertIn("Ansible configuration generated successfully", ansible_result)
                self.assertIn("ansible_directory", ansible_sly_data)
                
                ansible_dir = ansible_sly_data["ansible_directory"]
                self.assertTrue(os.path.exists(ansible_dir))
                
                # Step 5: Verify complete directory structure
                self._verify_complete_directory_structure(temp_dir)
                
                # Step 6: Verify content consistency
                self._verify_content_consistency(design_path, terraform_dir, ansible_dir)
                
            finally:
                os.chdir(original_cwd)

    def test_workflow_with_dependencies(self):
        """
        Test workflow where later steps depend on earlier outputs.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design first
                design_creator = DesignDocumentCreator()
                design_args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                design_sly_data = {}
                
                design_result = design_creator.invoke(design_args, design_sly_data)
                design_path = design_sly_data["design_document_path"]
                
                # Read the created design document
                with open(design_path, 'r') as f:
                    design_content = f.read()
                
                # Use design content for project plan
                plan_creator = ProjectPlanCreator()
                plan_args = {
                    "design_details": design_content,  # Use actual design content
                    "timestamp": self.test_timestamp
                }
                plan_sly_data = {}
                
                plan_result = plan_creator.invoke(plan_args, plan_sly_data)
                
                # Verify plan includes design context
                plan_path = plan_sly_data["project_plan_path"]
                with open(plan_path, 'r') as f:
                    plan_content = f.read()
                
                # Plan should reference the design content
                self.assertIn("Design Context", plan_content)
                self.assertIn(self.test_timestamp, plan_content)
                
                # Both Terraform and Ansible should reference the same design
                terraform_builder = TerraformBuilder()
                terraform_args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                terraform_sly_data = {}
                
                terraform_result = terraform_builder.invoke(terraform_args, terraform_sly_data)
                
                ansible_builder = AnsibleBuilder()
                ansible_args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                ansible_sly_data = {}
                
                ansible_result = ansible_builder.invoke(ansible_args, ansible_sly_data)
                
                # Verify consistency - both should reference same LZ timestamp directory
                terraform_parts = terraform_sly_data["terraform_directory"].split('/')
                ansible_parts = ansible_sly_data["ansible_directory"].split('/')
                
                # Find the LZ_timestamp directory in both paths
                terraform_lz_dir = None
                ansible_lz_dir = None
                
                for part in terraform_parts:
                    if part.startswith("LZ_"):
                        terraform_lz_dir = part
                        break
                        
                for part in ansible_parts:
                    if part.startswith("LZ_"):
                        ansible_lz_dir = part
                        break
                
                self.assertEqual(terraform_lz_dir, ansible_lz_dir)
                
            finally:
                os.chdir(original_cwd)

    def test_error_propagation(self):
        """
        Test that errors in one step don't break the entire workflow.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Test missing design file for Terraform
                terraform_builder = TerraformBuilder()
                terraform_args = {
                    "design_path": "/non/existent/design.md",
                    "timestamp": self.test_timestamp
                }
                terraform_sly_data = {}
                
                terraform_result = terraform_builder.invoke(terraform_args, terraform_sly_data)
                
                # Should return error message, not crash
                self.assertIn("Error: Design file not found", terraform_result)
                
                # Test missing timestamp
                design_creator = DesignDocumentCreator()
                design_args = {
                    "project_details": self.test_project_details,
                    "timestamp": ""  # Empty timestamp
                }
                design_sly_data = {}
                
                design_result = design_creator.invoke(design_args, design_sly_data)
                
                # Should return error message
                self.assertIn("Error: timestamp parameter is required", design_result)
                
            finally:
                os.chdir(original_cwd)

    def test_sly_data_consistency(self):
        """
        Test that sly_data is properly maintained across tools.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create design and check sly_data
                design_creator = DesignDocumentCreator()
                design_args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                design_sly_data = {}
                
                design_result = design_creator.invoke(design_args, design_sly_data)
                
                # Check sly_data structure
                expected_keys = ["design_document_path", "project_timestamp", "output_directory"]
                for key in expected_keys:
                    self.assertIn(key, design_sly_data)
                
                # Use design sly_data for subsequent tools
                terraform_builder = TerraformBuilder()
                terraform_args = {
                    "design_path": design_sly_data["design_document_path"],
                    "timestamp": design_sly_data["project_timestamp"]
                }
                terraform_sly_data = {}
                
                terraform_result = terraform_builder.invoke(terraform_args, terraform_sly_data)
                
                # Verify Terraform sly_data
                self.assertIn("terraform_directory", terraform_sly_data)
                self.assertIn("terraform_files", terraform_sly_data)
                
                # Check that directories are under the same output structure
                design_output_dir = design_sly_data["output_directory"]
                terraform_dir = terraform_sly_data["terraform_directory"]
                
                self.assertTrue(terraform_dir.startswith(design_output_dir))
                
            finally:
                os.chdir(original_cwd)

    def test_file_content_references(self):
        """
        Test that generated files reference each other correctly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create complete workflow
                design_creator = DesignDocumentCreator()
                design_args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                design_sly_data = {}
                
                design_result = design_creator.invoke(design_args, design_sly_data)
                design_path = design_sly_data["design_document_path"]
                
                terraform_builder = TerraformBuilder()
                terraform_args = {
                    "design_path": design_path,
                    "timestamp": self.test_timestamp
                }
                terraform_sly_data = {}
                
                terraform_result = terraform_builder.invoke(terraform_args, terraform_sly_data)
                terraform_dir = terraform_sly_data["terraform_directory"]
                
                # Check that Terraform README references the design
                terraform_readme_path = os.path.join(terraform_dir, "README.md")
                with open(terraform_readme_path, 'r') as f:
                    terraform_readme = f.read()
                
                self.assertIn("docs/design.md", terraform_readme)
                self.assertIn(self.test_timestamp, terraform_readme)
                
                # Check that Terraform main.tf uses module correctly
                main_tf_path = os.path.join(terraform_dir, "main.tf")
                with open(main_tf_path, 'r') as f:
                    main_tf_content = f.read()
                
                self.assertIn('source = "./modules/network"', main_tf_content)
                
            finally:
                os.chdir(original_cwd)

    def _verify_complete_directory_structure(self, base_dir):
        """
        Verify that the complete directory structure is created correctly.
        """
        expected_structure = {
            f"output/LZ_{self.test_timestamp}/docs": [
                "design.md",
                "project_plan.md"
            ],
            f"output/LZ_{self.test_timestamp}/iac/terraform": [
                "main.tf",
                "variables.tf",
                "outputs.tf",
                "provider.tf",
                "versions.tf",
                "README.md"
            ],
            f"output/LZ_{self.test_timestamp}/iac/terraform/modules/network": [
                "main.tf",
                "variables.tf",
                "outputs.tf"
            ],
            f"output/LZ_{self.test_timestamp}/iac/terraform/environments/dev": [
                "terraform.tfvars"
            ],
            f"output/LZ_{self.test_timestamp}/config/ansible": [
                "ansible.cfg",
                "requirements.yml",
                "README.md"
            ],
            f"output/LZ_{self.test_timestamp}/config/ansible/playbooks": [
                "site.yml",
                "webservers.yml",
                "databases.yml"
            ],
            f"output/LZ_{self.test_timestamp}/config/ansible/inventories": [
                "dev.yml",
                "prod.yml"
            ],
            f"output/LZ_{self.test_timestamp}/config/ansible/group_vars": [
                "all.yml",
                "webservers.yml",
                "databases.yml"
            ]
        }
        
        for dir_path, expected_files in expected_structure.items():
            full_dir_path = os.path.join(base_dir, dir_path)
            self.assertTrue(os.path.exists(full_dir_path), f"Directory missing: {dir_path}")
            
            for file_name in expected_files:
                file_path = os.path.join(full_dir_path, file_name)
                self.assertTrue(os.path.exists(file_path), f"File missing: {dir_path}/{file_name}")

    def _verify_content_consistency(self, design_path, terraform_dir, ansible_dir):
        """
        Verify that content is consistent across generated files.
        """
        # Read design document
        with open(design_path, 'r') as f:
            design_content = f.read()
        
        # Verify timestamp consistency
        self.assertIn(self.test_timestamp, design_content)
        
        # Check Terraform README references design
        terraform_readme_path = os.path.join(terraform_dir, "README.md")
        with open(terraform_readme_path, 'r') as f:
            terraform_readme = f.read()
        
        self.assertIn(self.test_timestamp, terraform_readme)
        
        # Check Ansible README references design
        ansible_readme_path = os.path.join(ansible_dir, "README.md")
        with open(ansible_readme_path, 'r') as f:
            ansible_readme = f.read()
        
        self.assertIn(self.test_timestamp, ansible_readme)
        
        # Verify Azure-specific content in Terraform
        terraform_main_path = os.path.join(terraform_dir, "main.tf")
        with open(terraform_main_path, 'r') as f:
            terraform_main = f.read()
        
        self.assertIn("azurerm", terraform_main)
        self.assertIn("resource_group", terraform_main)
        
        # Verify web server configuration in Ansible
        ansible_web_vars_path = os.path.join(ansible_dir, "group_vars", "webservers.yml")
        with open(ansible_web_vars_path, 'r') as f:
            ansible_web_vars = f.read()
        
        self.assertIn("web_service_name", ansible_web_vars)
        self.assertIn("nginx", ansible_web_vars)


if __name__ == '__main__':
    unittest.main()
