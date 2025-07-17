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
from unittest.mock import patch, mock_open

from coded_tools.cloud_infrastructure_provider.design_document_creator import DesignDocumentCreator


class TestDesignDocumentCreator(unittest.TestCase):
    """
    Unit tests for the DesignDocumentCreator class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.creator = DesignDocumentCreator()
        self.test_timestamp = "07162025140200"
        self.test_project_details = """
        Project: Azure Landing Zone for E-commerce Application
        
        Requirements:
        - High availability web application
        - Secure database layer
        - Load balancing capability
        - Auto-scaling support
        - Development and production environments
        
        Cloud Provider: Azure
        Regions: East US (primary), West US (secondary)
        """

    def test_init(self):
        """
        Test the initialization of DesignDocumentCreator.
        """
        creator = DesignDocumentCreator()
        self.assertIsNotNone(creator)
        self.assertTrue(creator.template_path.endswith('design.md.template'))

    def test_invoke_success(self):
        """
        Test successful creation of a design document.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory for testing
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                # Check result
                self.assertIn("Design document created successfully", result)
                self.assertIn(f"LZ_{self.test_timestamp}", result)
                
                # Check sly_data was updated
                self.assertIn("design_document_path", sly_data)
                self.assertIn("project_timestamp", sly_data)
                self.assertIn("output_directory", sly_data)
                self.assertEqual(sly_data["project_timestamp"], self.test_timestamp)
                
                # Check file was created
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "design.md")
                self.assertTrue(os.path.exists(expected_path))
                
                # Check file content
                with open(expected_path, 'r') as f:
                    content = f.read()
                    self.assertIn(f"LZ_{self.test_timestamp}", content)
                    self.assertIn(self.test_project_details, content)
                    self.assertIn("Project Requirements", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_invoke_missing_project_details(self):
        """
        Test error handling when project_details parameter is missing.
        """
        args = {"timestamp": self.test_timestamp}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: project_details parameter is required", result)

    def test_invoke_missing_timestamp(self):
        """
        Test error handling when timestamp parameter is missing.
        """
        args = {"project_details": self.test_project_details}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: timestamp parameter is required", result)

    def test_invoke_empty_parameters(self):
        """
        Test error handling with empty parameters.
        """
        args = {"project_details": "", "timestamp": ""}
        sly_data = {}
        
        result = self.creator.invoke(args, sly_data)
        
        self.assertIn("Error: project_details parameter is required", result)

    def test_fallback_template(self):
        """
        Test that fallback template is used when template file doesn't exist.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create creator with non-existent template path
                creator = DesignDocumentCreator()
                creator.template_path = "/non/existent/path/template.md"
                
                args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = creator.invoke(args, sly_data)
                
                # Should still succeed with fallback template
                self.assertIn("Design document created successfully", result)
                
                # Check file was created with fallback content
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "design.md")
                self.assertTrue(os.path.exists(expected_path))
                
                with open(expected_path, 'r') as f:
                    content = f.read()
                    self.assertIn("Cloud Infrastructure Design", content)
                    self.assertIn("Design Pillars", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_template_content_replacement(self):
        """
        Test that timestamp placeholder is correctly replaced in template.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a real template file
                template_dir = os.path.join("coded_tools", "cloud_infrastructure_provider", "template")
                os.makedirs(template_dir, exist_ok=True)
                template_path = os.path.join(template_dir, "design.md.template")
                
                template_content = "# Design: LZ_<MMDDYYYYHHMMSS>\n\nTimestamp: <MMDDYYYYHHMMSS>"
                with open(template_path, 'w') as f:
                    f.write(template_content)
                
                args = {
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                result = self.creator.invoke(args, sly_data)
                
                # Check that timestamp was replaced
                expected_path = os.path.join("output", f"LZ_{self.test_timestamp}", "docs", "design.md")
                if os.path.exists(expected_path):
                    with open(expected_path, 'r') as f:
                        content = f.read()
                        self.assertNotIn("<MMDDYYYYHHMMSS>", content)
                        self.assertIn(self.test_timestamp, content)
                    
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
                    "project_details": self.test_project_details,
                    "timestamp": self.test_timestamp
                }
                sly_data = {}
                
                # Test async invoke
                import asyncio
                result = asyncio.run(self.creator.async_invoke(args, sly_data))
                
                self.assertIn("Design document created successfully", result)
                
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
                    "project_details": self.test_project_details,
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


if __name__ == '__main__':
    unittest.main()
