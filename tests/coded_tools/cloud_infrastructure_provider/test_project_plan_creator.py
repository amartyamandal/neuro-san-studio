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

from coded_tools.cloud_infrastructure_provider.project_plan_creator import ProjectPlanCreator


class TestProjectPlanCreator(unittest.TestCase):
    """
    Unit tests for the ProjectPlanCreator class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.creator = ProjectPlanCreator()
        self.test_timestamp = "07162025140200"
        self.test_design_details = """
        Azure Landing Zone Design Summary:
        
        - 3-tier architecture (web, app, data)
        - High availability with load balancers
        - Azure Virtual Network with multiple subnets
        - Network security groups for traffic control
        - Storage accounts for diagnostics
        - Terraform for IaC implementation
        - Ansible for configuration management
        
        Estimated complexity: Medium
        Expected deployment time: 2-3 weeks
        """

    def test_init(self):
        """
        Test the initialization of ProjectPlanCreator.
        """
        creator = ProjectPlanCreator()
        self.assertIsNotNone(creator)

    def test_invoke_success(self):
        """
        Test successful creation of a project plan.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                # Check result
                self.assertIn("Project plan created successfully", result)
                self.assertIn(f"LZ_{self.test_timestamp}", result)
                
                # Check sly_data was updated
                self.assertIn("project_plan_path", sly_data)
                
                # Check file was created
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                self.assertTrue(os.path.exists(expected_path))
                
                # Check file content
                with open(expected_path, 'r') as f:
                    content = f.read()
                    self.assertIn(f"Project Plan: LZ_{self.test_timestamp}", content)
                    self.assertIn("Task Breakdown", content)
                    self.assertIn("Timeline Summary", content)
                    self.assertIn("Deliverables", content)
                    self.assertIn("Risk Assessment", content)
                    self.assertIn(self.test_design_details, content)
                    
            finally:
                os.chdir(original_cwd)

    def test_invoke_missing_design_details(self):
        """
        Test error handling when design_details parameter is missing.
        """
        args = {"timestamp": self.test_timestamp}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: design_details parameter is required", result)

    def test_invoke_missing_timestamp(self):
        """
        Test error handling when timestamp parameter is missing.
        """
        args = {"design_details": self.test_design_details}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: timestamp parameter is required", result)

    def test_invoke_empty_parameters(self):
        """
        Test error handling with empty parameters.
        """
        args = {"design_details": "", "timestamp": ""}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: design_details parameter is required", result)

    def test_project_plan_content_structure(self):
        """
        Test that the generated project plan has the expected structure.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                with open(expected_path, 'r') as f:
                    content = f.read()
                    
                    # Check required sections exist
                    required_sections = [
                        "## Project Overview",
                        "## Task Breakdown",
                        "## Timeline Summary",
                        "## Deliverables",
                        "## Risk Assessment",
                        "## Design Context",
                        "## Next Steps"
                    ]
                    
                    for section in required_sections:
                        self.assertIn(section, content)
                    
                    # Check task table headers
                    self.assertIn("| Phase | Task | Owner | Duration | Dependencies | Status |", content)
                    
                    # Check specific tasks are mentioned
                    expected_tasks = [
                        "Requirements Analysis",
                        "Terraform Module Setup",
                        "Network Infrastructure",
                        "Security Implementation",
                        "Ansible Role Development",
                        "Testing & Validation"
                    ]
                    
                    for task in expected_tasks:
                        self.assertIn(task, content)
                    
                    # Check owner assignments
                    self.assertIn("Architect", content)
                    self.assertIn("Engineer", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_timeline_calculations(self):
        """
        Test that timeline calculations are present in the plan.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                with open(expected_path, 'r') as f:
                    content = f.read()
                    
                    # Check timeline summary exists
                    self.assertIn("**Total Estimated Duration:**", content)
                    self.assertIn("days", content)
                    self.assertIn("**Critical Path:**", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_deliverables_section(self):
        """
        Test that deliverables are properly listed.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                with open(expected_path, 'r') as f:
                    content = f.read()
                    
                    # Check expected deliverables
                    expected_deliverables = [
                        "Design Document",
                        "Terraform Code",
                        "Ansible Playbooks",
                        "Testing Documentation",
                        "Deployment Guide"
                    ]
                    
                    for deliverable in expected_deliverables:
                        self.assertIn(deliverable, content)
                    
            finally:
                os.chdir(original_cwd)

    def test_risk_assessment_section(self):
        """
        Test that risk assessment is included.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                with open(expected_path, 'r') as f:
                    content = f.read()
                    
                    # Check risk levels are mentioned
                    self.assertIn("**High:**", content)
                    self.assertIn("**Medium:**", content)
                    self.assertIn("**Low:**", content)
                    
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
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                # Test async invoke
                import asyncio
                result = asyncio.run(self.creator.async_invoke(args, sly_data))
                
                self.assertIn("Project plan created successfully", result)
                
            finally:
                os.chdir(original_cwd)

    def test_directory_creation(self):
        """
        Test that necessary directories are created.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                # Check directories were created
                output_dir = os.path.join("output", f"LZ_{self.test_timestamp}")
                docs_dir = os.path.join(output_dir, "docs")
                
                self.assertTrue(os.path.exists(output_dir))
                self.assertTrue(os.path.exists(docs_dir))
                self.assertTrue(os.path.isdir(output_dir))
                self.assertTrue(os.path.isdir(docs_dir))
                
            finally:
                os.chdir(original_cwd)

    def test_timestamp_in_content(self):
        """
        Test that timestamp is properly embedded in the content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "design_details": self.test_design_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "project_plan.md")
                with open(expected_path, 'r') as f:
                    content = f.read()
                    
                    # Check timestamp is in title and content
                    self.assertIn(f"LZ_{self.test_timestamp}", content)
                    # Should appear at least twice (title and references)
                    self.assertGreater(content.count(self.test_timestamp), 0)
                    
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
