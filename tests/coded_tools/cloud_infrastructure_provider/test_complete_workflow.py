#!/usr/bin/env python3
"""
Complete workflow test for Cloud Infrastructure Provider Agents
Tests the full end-to-end workflow: User → Manager → Architect → Engineer

This test simulates the complete AAOSA workflow:
1. User submits infrastructure request to Manager
2. Manager delegates design to Architect  
3. Architect creates design.md
4. Manager creates project_plan.md
5. Manager gets user approval (simulated)
6. Engineer builds Terraform and Ansible code

Expected output structure:
output/LZ_<TIMESTAMP>/
├── docs/
│   ├── design.md          ← Architect-created
│   └── project_plan.md    ← Manager-created
├── iac/
│   └── terraform/         ← Engineer-created
└── config/
    └── ansible/           ← Engineer-created
"""

import os
import sys
import shutil
import json
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from coded_tools.cloud_infrastructure_provider.design_document_creator import DesignDocumentCreator
from coded_tools.cloud_infrastructure_provider.project_plan_creator import ProjectPlanCreator
from coded_tools.cloud_infrastructure_provider.terraform_builder import TerraformBuilder
from coded_tools.cloud_infrastructure_provider.ansible_builder import AnsibleBuilder


class WorkflowTester:
    """Test class that simulates the complete agent workflow"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%m%d%Y%H%M%S")
        self.output_dir = f"output/LZ_{self.timestamp}"
        self.results = {
            "timestamp": self.timestamp,
            "workflow_steps": [],
            "files_created": [],
            "errors": []
        }
    
    def log_step(self, agent: str, action: str, status: str, details: str = ""):
        """Log each workflow step"""
        step = {
            "agent": agent,
            "action": action,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.results["workflow_steps"].append(step)
        print(f"[{step['timestamp']}] {agent}: {action} - {status}")
        if details:
            print(f"    → {details}")
    
    def simulate_user_request(self) -> str:
        """Simulate a user infrastructure request"""
        request = """
I need a landing zone in Azure for my e-commerce application. 

Requirements:
- Web application with load balancer
- SQL database backend
- Development and production environments
- Security best practices
- Auto-scaling capability
- Monitoring and logging

Please use defaults for anything not specified.
        """.strip()
        
        self.log_step("User", "Submit Request", "SUCCESS", 
                     "Submitted e-commerce landing zone request")
        return request
    
    def simulate_manager_coordination(self, user_request: str) -> Dict[str, Any]:
        """Simulate Manager agent coordinating the workflow"""
        self.log_step("Manager", "Receive Request", "SUCCESS", 
                     "Processing user infrastructure request")
        
        # Manager would delegate to Architect
        self.log_step("Manager", "Delegate to Architect", "SUCCESS", 
                     "Requesting design.md creation")
        
        return {
            "delegation": "architect",
            "instructions": "Create design.md based on user request. Use Terraform for infra, Ansible for config.",
            "user_request": user_request
        }
    
    def simulate_architect_design(self, manager_delegation: Dict[str, Any]) -> str:
        """Simulate Architect agent creating design"""
        self.log_step("Architect", "Start Design", "IN_PROGRESS", 
                     "Creating infrastructure design document")
        
        try:
            # Use the actual DesignDocumentCreator
            creator = DesignDocumentCreator()
            args = {
                "project_details": manager_delegation["user_request"],
                "timestamp": self.timestamp
            }
            sly_data = {}
            
            result = creator.invoke(args, sly_data)
            
            if "successfully" in result:
                design_path = f"{self.output_dir}/docs/design.md"
                self.results["files_created"].append(design_path)
                self.log_step("Architect", "Create Design", "SUCCESS", 
                             f"Design document created: {design_path}")
                return design_path
            else:
                self.log_step("Architect", "Create Design", "FAILED", result)
                return ""
                
        except Exception as e:
            error_msg = f"Design creation failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.log_step("Architect", "Create Design", "ERROR", error_msg)
            return ""
    
    def simulate_manager_project_plan(self, design_path: str) -> str:
        """Simulate Manager creating project plan after design completion"""
        self.log_step("Manager", "Receive Design", "SUCCESS", 
                     "Design completed by Architect")
        
        self.log_step("Manager", "Create Project Plan", "IN_PROGRESS", 
                     "Generating project plan with task breakdown")
        
        try:
            # Read the design to create project plan
            with open(design_path, 'r') as f:
                design_content = f.read()
            
            creator = ProjectPlanCreator()
            args = {
                "design_details": f"Design complete for Azure e-commerce landing zone: {design_content[:200]}...",
                "timestamp": self.timestamp
            }
            sly_data = {}
            
            result = creator.invoke(args, sly_data)
            
            if "successfully" in result:
                plan_path = f"{self.output_dir}/docs/project_plan.md"
                self.results["files_created"].append(plan_path)
                self.log_step("Manager", "Create Project Plan", "SUCCESS", 
                             f"Project plan created: {plan_path}")
                return plan_path
            else:
                self.log_step("Manager", "Create Project Plan", "FAILED", result)
                return ""
                
        except Exception as e:
            error_msg = f"Project plan creation failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.log_step("Manager", "Create Project Plan", "ERROR", error_msg)
            return ""
    
    def simulate_user_approval(self) -> bool:
        """Simulate user approving the design and project plan"""
        self.log_step("Manager", "Request Approval", "SUCCESS", 
                     "Presenting design and project plan to user")
        
        # Simulate user approval (always approve in test)
        self.log_step("User", "Approve Project", "SUCCESS", 
                     "Design and project plan approved - proceed with implementation")
        return True
    
    def simulate_engineer_implementation(self, design_path: str) -> Dict[str, str]:
        """Simulate Engineer building Terraform and Ansible code"""
        self.log_step("Engineer", "Start Implementation", "IN_PROGRESS", 
                     "Building infrastructure code from design")
        
        results = {"terraform": "", "ansible": ""}
        
        # Build Terraform code
        try:
            terraform_builder = TerraformBuilder()
            args = {
                "design_path": design_path,
                "timestamp": self.timestamp
            }
            sly_data = {}
            
            terraform_result = terraform_builder.invoke(args, sly_data)
            
            if "successfully" in terraform_result:
                terraform_path = f"{self.output_dir}/iac/terraform"
                results["terraform"] = terraform_path
                self.results["files_created"].append(terraform_path)
                self.log_step("Engineer", "Build Terraform", "SUCCESS", 
                             f"Terraform code created in: {terraform_path}")
            else:
                self.log_step("Engineer", "Build Terraform", "FAILED", terraform_result)
                
        except Exception as e:
            error_msg = f"Terraform build failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.log_step("Engineer", "Build Terraform", "ERROR", error_msg)
        
        # Build Ansible code
        try:
            ansible_builder = AnsibleBuilder()
            args = {
                "design_path": design_path,
                "timestamp": self.timestamp
            }
            sly_data = {}
            
            ansible_result = ansible_builder.invoke(args, sly_data)
            
            if "successfully" in ansible_result:
                ansible_path = f"{self.output_dir}/config/ansible"
                results["ansible"] = ansible_path
                self.results["files_created"].append(ansible_path)
                self.log_step("Engineer", "Build Ansible", "SUCCESS", 
                             f"Ansible code created in: {ansible_path}")
            else:
                self.log_step("Engineer", "Build Ansible", "FAILED", ansible_result)
                
        except Exception as e:
            error_msg = f"Ansible build failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.log_step("Engineer", "Build Ansible", "ERROR", error_msg)
        
        return results
    
    def verify_output_structure(self) -> bool:
        """Verify the complete output directory structure"""
        self.log_step("System", "Verify Structure", "IN_PROGRESS", 
                     "Checking complete directory structure")
        
        expected_structure = {
            f"{self.output_dir}/docs/design.md": "Architect design document",
            f"{self.output_dir}/docs/project_plan.md": "Manager project plan",
            f"{self.output_dir}/iac/terraform/main.tf": "Terraform main configuration",
            f"{self.output_dir}/iac/terraform/variables.tf": "Terraform variables",
            f"{self.output_dir}/config/ansible/playbooks/site.yml": "Ansible main playbook",
            f"{self.output_dir}/config/ansible/inventories/dev.yml": "Ansible dev inventory"
        }
        
        all_exist = True
        for file_path, description in expected_structure.items():
            if os.path.exists(file_path):
                self.log_step("System", f"Verify {description}", "SUCCESS", 
                             f"File exists: {file_path}")
            else:
                self.log_step("System", f"Verify {description}", "FAILED", 
                             f"Missing file: {file_path}")
                all_exist = False
        
        return all_exist
    
    def count_created_files(self) -> Dict[str, int]:
        """Count all files created in the output directory"""
        counts = {"total": 0, "terraform": 0, "ansible": 0, "docs": 0}
        
        if os.path.exists(self.output_dir):
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    counts["total"] += 1
                    if "terraform" in root:
                        counts["terraform"] += 1
                    elif "ansible" in root:
                        counts["ansible"] += 1
                    elif "docs" in root:
                        counts["docs"] += 1
        
        return counts
    
    def run_complete_workflow(self) -> Dict[str, Any]:
        """Execute the complete workflow simulation"""
        print("=" * 60)
        print("CLOUD INFRASTRUCTURE PROVIDER - COMPLETE WORKFLOW TEST")
        print("=" * 60)
        print(f"Test Timestamp: {self.timestamp}")
        print(f"Output Directory: {self.output_dir}")
        print("")
        
        try:
            # 1. User submits request
            user_request = self.simulate_user_request()
            
            # 2. Manager coordinates
            manager_delegation = self.simulate_manager_coordination(user_request)
            
            # 3. Architect creates design
            design_path = self.simulate_architect_design(manager_delegation)
            if not design_path:
                raise Exception("Design creation failed")
            
            # 4. Manager creates project plan
            plan_path = self.simulate_manager_project_plan(design_path)
            if not plan_path:
                raise Exception("Project plan creation failed")
            
            # 5. User approves (simulated)
            approval = self.simulate_user_approval()
            if not approval:
                raise Exception("User approval failed")
            
            # 6. Engineer implements
            implementation = self.simulate_engineer_implementation(design_path)
            
            # 7. Verify complete structure
            structure_valid = self.verify_output_structure()
            
            # 8. Count files
            file_counts = self.count_created_files()
            
            # Final status
            success = (design_path and plan_path and 
                      implementation["terraform"] and implementation["ansible"] and
                      structure_valid)
            
            if success:
                self.log_step("Manager", "Project Complete", "SUCCESS", 
                             f"All deliverables created successfully in {self.output_dir}")
            else:
                self.log_step("Manager", "Project Complete", "PARTIAL", 
                             "Some components failed - check logs")
            
            # Update results
            self.results.update({
                "success": success,
                "output_directory": self.output_dir,
                "file_counts": file_counts,
                "structure_valid": structure_valid
            })
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.results["success"] = False
            self.log_step("System", "Workflow", "FAILED", error_msg)
        
        return self.results
    
    def print_summary(self):
        """Print a comprehensive test summary"""
        print("\n" + "=" * 60)
        print("WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Success: {'✅ YES' if self.results.get('success') else '❌ NO'}")
        print(f"Output Directory: {self.results.get('output_directory', 'N/A')}")
        
        if self.results.get("file_counts"):
            counts = self.results["file_counts"]
            print(f"\nFiles Created:")
            print(f"  Total: {counts['total']}")
            print(f"  Documentation: {counts['docs']}")
            print(f"  Terraform: {counts['terraform']}")
            print(f"  Ansible: {counts['ansible']}")
        
        print(f"\nWorkflow Steps: {len(self.results['workflow_steps'])}")
        success_steps = sum(1 for step in self.results['workflow_steps'] 
                           if step['status'] == 'SUCCESS')
        print(f"Successful Steps: {success_steps}")
        
        if self.results.get("errors"):
            print(f"\nErrors: {len(self.results['errors'])}")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        print(f"\nStructure Valid: {'✅ YES' if self.results.get('structure_valid') else '❌ NO'}")
        
        print("\nAgent Coordination Test:")
        agents = set(step['agent'] for step in self.results['workflow_steps'])
        for agent in ['User', 'Manager', 'Architect', 'Engineer', 'System']:
            if agent in agents:
                agent_steps = [s for s in self.results['workflow_steps'] if s['agent'] == agent]
                successful = sum(1 for s in agent_steps if s['status'] == 'SUCCESS')
                print(f"  {agent}: {successful}/{len(agent_steps)} steps successful")


def main():
    """Main test execution"""
    tester = WorkflowTester()
    results = tester.run_complete_workflow()
    tester.print_summary()
    
    # Return exit code based on success
    return 0 if results.get("success") else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
