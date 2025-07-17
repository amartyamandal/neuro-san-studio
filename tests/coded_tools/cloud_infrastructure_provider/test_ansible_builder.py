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

from coded_tools.cloud_infrastructure_provider.ansible_builder import AnsibleBuilder


class TestAnsibleBuilder(unittest.TestCase):
    """
    Unit tests for the AnsibleBuilder class.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.builder = AnsibleBuilder()
        self.test_timestamp = "07162025140200"
        self.test_design_content = """
        # Cloud Infrastructure Design: LZ_07162025140200
        
        ## Overview
        - Azure Landing Zone for e-commerce application
        - High availability architecture
        - Multi-tier design (web, app, data)
        
        ## Configuration Strategy
        - Ansible for server configuration
        - Web server configuration with Nginx
        - Database server setup with MySQL
        - Common security and monitoring setup
        """

    def test_init(self):
        """
        Test the initialization of AnsibleBuilder.
        """
        builder = AnsibleBuilder()
        self.assertIsNotNone(builder)

    def test_invoke_success(self):
        """
        Test successful generation of Ansible configuration.
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
                self.assertIn("Ansible configuration generated successfully", result)
                self.assertIn(f"LZ_{self.test_timestamp}", result)
                
                # Check sly_data was updated
                self.assertIn("ansible_directory", sly_data)
                self.assertIn("ansible_files", sly_data)
                
                # Check Ansible directory structure
                ansible_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible")
                self.assertTrue(os.path.exists(ansible_dir))
                
                # Check main directories exist
                expected_dirs = [
                    "playbooks",
                    "roles",
                    "inventories", 
                    "group_vars",
                    "host_vars"
                ]
                
                for dir_name in expected_dirs:
                    dir_path = os.path.join(ansible_dir, dir_name)
                    self.assertTrue(os.path.exists(dir_path), f"Missing directory: {dir_name}")
                
                # Check main files exist
                expected_files = [
                    "ansible.cfg",
                    "requirements.yml",
                    "README.md"
                ]
                
                for file_name in expected_files:
                    file_path = os.path.join(ansible_dir, file_name)
                    self.assertTrue(os.path.exists(file_path), f"Missing file: {file_name}")
                
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

    def test_playbooks_generation(self):
        """
        Test that playbook files are generated with correct content.
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
                
                # Check playbook files
                playbooks_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "playbooks")
                
                expected_playbooks = [
                    "site.yml",
                    "webservers.yml",
                    "databases.yml"
                ]
                
                for playbook in expected_playbooks:
                    playbook_path = os.path.join(playbooks_dir, playbook)
                    self.assertTrue(os.path.exists(playbook_path), f"Missing playbook: {playbook}")
                    
                    # Check content
                    with open(playbook_path, 'r') as f:
                        content = f.read()
                        self.assertIn("---", content)  # YAML header
                        self.assertIn("name:", content)  # Ansible task name
                
                # Check main site.yml content
                site_yml_path = os.path.join(playbooks_dir, "site.yml")
                with open(site_yml_path, 'r') as f:
                    content = f.read()
                    self.assertIn("import_playbook:", content)
                    self.assertIn("webservers.yml", content)
                    self.assertIn("databases.yml", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_inventory_generation(self):
        """
        Test that inventory files are generated with correct structure.
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
                
                # Check inventory files
                inventories_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "inventories")
                
                expected_inventories = ["dev.yml", "prod.yml"]
                
                for inventory in expected_inventories:
                    inventory_path = os.path.join(inventories_dir, inventory)
                    self.assertTrue(os.path.exists(inventory_path), f"Missing inventory: {inventory}")
                    
                    # Check content structure
                    with open(inventory_path, 'r') as f:
                        content = f.read()
                        self.assertIn("---", content)  # YAML header
                        self.assertIn("all:", content)
                        self.assertIn("children:", content)
                        self.assertIn("webservers:", content)
                        self.assertIn("databases:", content)
                        self.assertIn("ansible_host:", content)
                        
            finally:
                os.chdir(original_cwd)

    def test_group_vars_generation(self):
        """
        Test that group variables files are generated with correct content.
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
                
                # Check group_vars files
                group_vars_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "group_vars")
                
                expected_group_vars = [
                    "all.yml",
                    "webservers.yml", 
                    "databases.yml"
                ]
                
                for group_var in expected_group_vars:
                    group_var_path = os.path.join(group_vars_dir, group_var)
                    self.assertTrue(os.path.exists(group_var_path), f"Missing group var: {group_var}")
                    
                    # Check content
                    with open(group_var_path, 'r') as f:
                        content = f.read()
                        self.assertIn("---", content)  # YAML header
                
                # Check specific content in all.yml
                all_yml_path = os.path.join(group_vars_dir, "all.yml")
                with open(all_yml_path, 'r') as f:
                    content = f.read()
                    self.assertIn("common_packages:", content)
                    self.assertIn("timezone:", content)
                    self.assertIn("admin_users:", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_roles_generation(self):
        """
        Test that Ansible roles are generated with correct structure.
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
                
                # Check roles directory structure
                roles_dir = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "roles")
                
                expected_roles = ["common", "webserver", "database"]
                
                for role in expected_roles:
                    role_dir = os.path.join(roles_dir, role)
                    self.assertTrue(os.path.exists(role_dir), f"Missing role directory: {role}")
                    
                    # Check role subdirectories
                    expected_subdirs = [
                        "tasks",
                        "handlers", 
                        "templates",
                        "files",
                        "vars",
                        "defaults",
                        "meta"
                    ]
                    
                    for subdir in expected_subdirs:
                        subdir_path = os.path.join(role_dir, subdir)
                        self.assertTrue(os.path.exists(subdir_path), f"Missing role subdir: {role}/{subdir}")
                    
                    # Check main.yml files exist
                    for subdir in ["tasks", "handlers", "vars", "defaults", "meta"]:
                        main_yml_path = os.path.join(role_dir, subdir, "main.yml")
                        self.assertTrue(os.path.exists(main_yml_path), f"Missing main.yml in {role}/{subdir}")
                        
            finally:
                os.chdir(original_cwd)

    def test_role_tasks_content(self):
        """
        Test that role tasks have appropriate content.
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
                
                # Check common role tasks
                common_tasks_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "roles", "common", "tasks", "main.yml")
                with open(common_tasks_path, 'r') as f:
                    content = f.read()
                    self.assertIn("Update system packages", content)
                    self.assertIn("Install common packages", content)
                    self.assertIn("Configure timezone", content)
                    self.assertIn("Configure SSH", content)
                
                # Check webserver role tasks
                webserver_tasks_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "roles", "webserver", "tasks", "main.yml")
                with open(webserver_tasks_path, 'r') as f:
                    content = f.read()
                    self.assertIn("Install web server", content)
                    self.assertIn("Configure web server", content)
                    self.assertIn("Start and enable web server", content)
                
                # Check database role tasks
                database_tasks_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "roles", "database", "tasks", "main.yml")
                with open(database_tasks_path, 'r') as f:
                    content = f.read()
                    self.assertIn("Install database server", content)
                    self.assertIn("Secure database installation", content)
                    self.assertIn("Configure database", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_ansible_config_generation(self):
        """
        Test that ansible.cfg file is generated with correct settings.
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
                
                # Check ansible.cfg content
                ansible_cfg_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "ansible.cfg")
                with open(ansible_cfg_path, 'r') as f:
                    content = f.read()
                    
                    # Check configuration sections
                    self.assertIn("[defaults]", content)
                    self.assertIn("[inventory]", content)
                    self.assertIn("[ssh_connection]", content)
                    self.assertIn("[privilege_escalation]", content)
                    
                    # Check specific settings
                    self.assertIn("inventory = inventories/", content)
                    self.assertIn("host_key_checking = False", content)
                    self.assertIn("gathering = smart", content)
                    
            finally:
                os.chdir(original_cwd)

    def test_requirements_generation(self):
        """
        Test that requirements.yml file is generated with necessary roles and collections.
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
                
                # Check requirements.yml content
                requirements_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "requirements.yml")
                with open(requirements_path, 'r') as f:
                    content = f.read()
                    
                    # Check sections exist
                    self.assertIn("roles:", content)
                    self.assertIn("collections:", content)
                    
                    # Check specific requirements
                    self.assertIn("geerlingguy.nginx", content)
                    self.assertIn("geerlingguy.mysql", content)
                    self.assertIn("community.general", content)
                    self.assertIn("ansible.posix", content)
                    
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
                readme_path = os.path.join("output", f"LZ_{self.test_timestamp}", "config", "ansible", "README.md")
                with open(readme_path, 'r') as f:
                    content = f.read()
                    
                    # Check timestamp in title
                    self.assertIn(f"LZ_{self.test_timestamp}", content)
                    
                    # Check required sections
                    expected_sections = [
                        "## Directory Structure",
                        "## Prerequisites", 
                        "## Setup Instructions",
                        "## Usage",
                        "## Customization",
                        "## Security Considerations",
                        "## Troubleshooting"
                    ]
                    
                    for section in expected_sections:
                        self.assertIn(section, content)
                    
                    # Check Ansible commands
                    self.assertIn("ansible-galaxy install", content)
                    self.assertIn("ansible-playbook", content)
                    self.assertIn("ansible all -i inventories/dev.yml -m ping", content)
                    
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
                
                self.assertIn("Ansible configuration generated successfully", result)
                
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
