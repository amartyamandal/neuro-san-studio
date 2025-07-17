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
from datetime import datetime
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class DesignDocumentCreator(CodedTool):
    """
    Creates detailed infrastructure design documents based on architecture specifications.
    This tool implements the design template and creates structured documentation.
    """

    def __init__(self):
        """
        Initialize the DesignDocumentCreator.
        """
        self.template_path = os.path.join(
            os.path.dirname(__file__), 
            "template", 
            "design.md.template"
        )
        # Define required sections for completeness check
        self.required_sections = [
            "Business goal",
            "Regions",
            "Assumptions",
            "Architecture Diagram",
            "Directory layout",
            "State backend",
            "Module breakdown",
            "Ansible roles and purpose",
            "Host inventory plan",
            "Monitoring/logging strategy",
            "Alerting pipelines",
            "Network boundaries",
            "Identity & access",
            "Secrets mgmt",
            "High availability zones",
            "Backup & DR",
            "Resource SKUs",
            "Auto-scale plans",
            "Tagging conventions",
            "Budgeting alerts",
            "Known constraints",
            "Assumed defaults"
        ]

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Create a design document based on the provided project details, with completeness check and user clarification.
        
        :param args: Dictionary with keys:
                    - "project_details": Project requirements and specifications
                    - "timestamp": Session timestamp in MMDDYYYYHHMMSS format  
                    - "technology_stack" (optional): Detected technology stack (iac_tool, config_tool, etc.)
                    - "additional_sections" (optional): Additional sections to add to template
                    - "modified_sections" (optional): Sections to modify from template
                    - "skip_validation" (optional): Skip completeness validation if True
                    - "use_defaults" (optional): Use default values for missing sections if True
        """
        project_details = args.get("project_details", "")
        timestamp = args.get("timestamp", "")
        technology_stack = args.get("technology_stack", {})
        additional_sections = args.get("additional_sections", {})
        modified_sections = args.get("modified_sections", {})
        skip_validation = args.get("skip_validation", False)
        use_defaults = args.get("use_defaults", False)
        
        if not project_details:
            return {"status": "error", "error_message": "project_details parameter is required"}
        if not timestamp:
            return {"status": "error", "error_message": "timestamp parameter is required"}

        # Check completeness unless explicitly skipped or using defaults
        if not skip_validation and not use_defaults:
            missing_sections = self._check_completeness(project_details, technology_stack)
            if missing_sections:
                return {
                    "status": "clarification_required",
                    "missing_sections": missing_sections,
                    "clarification_prompts": self._generate_clarification_prompts(missing_sections, technology_stack),
                    "technology_stack": technology_stack,
                    "note": "You can respond with 'use defaults' to proceed with standard configurations"
                }

        try:
            print(f"========== Creating Design Document ==========")
            print(f"Project Details: {project_details[:100]}...")
            print(f"Timestamp: {timestamp}")

            # Create output directory structure
            output_dir = os.path.join("output", f"LZ_{timestamp}")
            docs_dir = os.path.join(output_dir, "docs")
            os.makedirs(docs_dir, exist_ok=True)

            # Read and process template
            template_content = self._load_template(technology_stack)
            design_content = self._process_template(
                template_content, timestamp, project_details, 
                additional_sections, modified_sections, technology_stack
            )

            # Create the design document path
            design_path = os.path.join(docs_dir, "design.md")
            file_exists = os.path.exists(design_path)

            # Write the design document with error handling
            try:
                with open(design_path, 'w', encoding='utf-8') as f:
                    f.write(design_content)
            except (IOError, OSError, PermissionError) as write_error:
                return {
                    "status": "error", 
                    "error_message": f"Failed to write design document: {str(write_error)}"
                }

            success_message = f"Design document created successfully at: {design_path}"
            if file_exists:
                success_message += " (overwritten existing file)"
            print(f"Result: {success_message}")

            # Store metadata in sly_data
            sly_data.update({
                "design_document_path": design_path,
                "project_timestamp": timestamp,
                "output_directory": output_dir,
                "design_created": True
            })

            return {"status": "success", "message": success_message, "path": design_path}

        except Exception as e:
            error_msg = f"Unexpected error creating design document: {str(e)}"
            print(f"Error: {error_msg}")
            return {"status": "error", "error_message": error_msg}

    def _check_completeness(self, project_details: str, technology_stack: dict = None) -> list:
        """Check which required sections are missing from project details based on technology stack."""
        missing_sections = []
        details_lower = project_details.lower()
        
        # Get technology-specific required sections
        required_sections = self._get_required_sections(technology_stack or {})
        
        for section in required_sections:
            # More sophisticated checking - look for key terms from each section
            if not self._section_present(section, details_lower, technology_stack or {}):
                missing_sections.append(section)
        
        return missing_sections

    def _get_required_sections(self, technology_stack: dict) -> list:
        """Get required sections based on technology stack."""
        iac_tool = technology_stack.get('iac_tool', 'terraform').lower()
        config_tool = technology_stack.get('config_tool', 'ansible').lower()
        
        # Base sections always required
        base_sections = [
            "Business goal",
            "Regions", 
            "Assumptions",
            "Architecture Diagram",
            "Network boundaries",
            "Identity & access",
            "Secrets mgmt",
            "High availability zones",
            "Backup & DR",
            "Resource SKUs",
            "Auto-scale plans",
            "Tagging conventions",
            "Budgeting alerts",
            "Known constraints",
            "Assumed defaults"
        ]
        
        # Technology-specific sections
        iac_sections = {
            'terraform': ["Directory layout", "State backend", "Module breakdown"],
            'cloudformation': ["Template structure", "Parameter files", "Nested stacks"],
            'arm': ["Template structure", "Parameter objects", "Linked templates"],
            'pulumi': ["Project structure", "Stack configs", "Component architecture"],
            'cdk': ["App structure", "Construct design", "Stack composition"],
            'bicep': ["Module structure", "Parameter files", "Template compilation"]
        }
        
        config_sections = {
            'ansible': ["Ansible roles and purpose", "Host inventory plan"],
            'chef': ["Cookbook structure", "Recipe organization", "Node configuration"],
            'puppet': ["Manifest structure", "Module organization", "Agent configuration"],
            'powershell_dsc': ["DSC configuration", "Node management", "Resource configuration"]
        }
        
        # Monitoring sections (always include but adapt keywords)
        monitoring_sections = ["Monitoring/logging strategy", "Alerting pipelines"]
        
        # Combine all sections
        all_sections = base_sections.copy()
        all_sections.extend(iac_sections.get(iac_tool, iac_sections['terraform']))
        all_sections.extend(config_sections.get(config_tool, config_sections['ansible']))
        all_sections.extend(monitoring_sections)
        
        return all_sections

    def _section_present(self, section: str, details: str, technology_stack: dict = None) -> bool:
        """Check if a section's content is present in the project details with technology-aware keywords."""
        tech_stack = technology_stack or {}
        iac_tool = tech_stack.get('iac_tool', 'terraform').lower()
        config_tool = tech_stack.get('config_tool', 'ansible').lower()
        
        # Technology-adaptive keywords
        section_keywords = {
            "Business goal": ["business", "goal", "objective", "purpose"],
            "Regions": ["region", "location", "zone", "geography"],
            "Assumptions": ["assume", "assumption", "constraint"],
            "Architecture Diagram": ["architecture", "diagram", "topology"],
            "Network boundaries": ["network", "boundary", "subnet", "vpc"],
            "Identity & access": ["identity", "access", "iam", "auth"],
            "Secrets mgmt": ["secret", "credential", "key management"],
            "High availability zones": ["availability", "ha", "redundancy"],
            "Backup & DR": ["backup", "disaster recovery", "dr"],
            "Resource SKUs": ["sku", "size", "instance type"],
            "Auto-scale plans": ["autoscale", "scaling", "elastic"],
            "Tagging conventions": ["tag", "label", "metadata"],
            "Budgeting alerts": ["budget", "cost", "billing"],
            "Known constraints": ["constraint", "limitation", "requirement"],
            "Assumed defaults": ["default", "standard", "baseline"],
            "Monitoring/logging strategy": ["monitor", "logging", "observability"],
            "Alerting pipelines": ["alert", "notification", "pipeline"],
            
            # Technology-specific IaC sections
            "Directory layout": ["directory", "folder", "structure", "layout"],
            "State backend": ["state", "backend", "remote state"] if iac_tool == 'terraform' else [],
            "Module breakdown": ["module", "component", "breakdown"],
            "Template structure": ["template", "structure", "organization"],
            "Parameter files": ["parameter", "config", "variable"],
            "Nested stacks": ["nested", "stack", "hierarchy"] if iac_tool == 'cloudformation' else [],
            "Parameter objects": ["parameter", "object", "variable"] if iac_tool == 'arm' else [],
            "Linked templates": ["linked", "template", "reference"] if iac_tool == 'arm' else [],
            "Project structure": ["project", "structure", "organization"] if iac_tool == 'pulumi' else [],
            "Stack configs": ["stack", "config", "environment"] if iac_tool == 'pulumi' else [],
            "Component architecture": ["component", "architecture", "design"] if iac_tool == 'pulumi' else [],
            "App structure": ["app", "structure", "organization"] if iac_tool == 'cdk' else [],
            "Construct design": ["construct", "design", "pattern"] if iac_tool == 'cdk' else [],
            "Stack composition": ["stack", "composition", "design"] if iac_tool == 'cdk' else [],
            "Module structure": ["module", "structure", "organization"] if iac_tool == 'bicep' else [],
            "Template compilation": ["compilation", "build", "generation"] if iac_tool == 'bicep' else [],
            
            # Technology-specific config sections  
            "Ansible roles and purpose": ["ansible", "role", "playbook"] if config_tool == 'ansible' else [],
            "Host inventory plan": ["inventory", "host", "server"] if config_tool == 'ansible' else [],
            "Cookbook structure": ["cookbook", "recipe", "structure"] if config_tool == 'chef' else [],
            "Recipe organization": ["recipe", "organization", "structure"] if config_tool == 'chef' else [],
            "Node configuration": ["node", "configuration", "management"],
            "Manifest structure": ["manifest", "structure", "organization"] if config_tool == 'puppet' else [],
            "Module organization": ["module", "organization", "structure"] if config_tool == 'puppet' else [],
            "Agent configuration": ["agent", "configuration", "setup"] if config_tool == 'puppet' else [],
            "DSC configuration": ["dsc", "configuration", "setup"] if config_tool == 'powershell_dsc' else [],
            "Node management": ["node", "management", "configuration"] if config_tool == 'powershell_dsc' else [],
            "Resource configuration": ["resource", "configuration", "management"]
        }
        
        keywords = section_keywords.get(section, [section.lower()])
        # Skip empty keyword lists (for sections not relevant to current tech stack)
        if not keywords:
            return True
            
        return any(keyword in details for keyword in keywords)

    def _generate_clarification_prompts(self, missing_sections: list, technology_stack: dict = None) -> list:
        """Generate technology-aware clarification prompts."""
        tech_stack = technology_stack or {}
        iac_tool = tech_stack.get('iac_tool', 'Terraform')
        config_tool = tech_stack.get('config_tool', 'Ansible')
        
        prompts = []
        for section in missing_sections:
            if section == "State backend" and iac_tool.lower() == 'terraform':
                prompts.append(f"Please specify Terraform state backend configuration (local, S3, Azure Storage, etc.)")
            elif section == "Parameter files" and iac_tool.lower() == 'cloudformation':
                prompts.append(f"Please specify CloudFormation parameter file organization and environment separation")
            elif section == "Ansible roles and purpose" and config_tool.lower() == 'ansible':
                prompts.append(f"Please specify Ansible roles needed and their purposes")
            elif section == "Cookbook structure" and config_tool.lower() == 'chef':
                prompts.append(f"Please specify Chef cookbook structure and recipe organization")
            elif section == "DSC configuration" and config_tool.lower() == 'powershell_dsc':
                prompts.append(f"Please specify PowerShell DSC configuration structure and node management")
            else:
                prompts.append(f"Please provide details for: '{section}'")
        
        return prompts

    def _load_template(self, technology_stack: dict = None) -> str:
        """Load the design template from file or return technology-specific fallback."""
        if os.path.exists(self.template_path):
            try:
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return self._get_fallback_template(technology_stack or {})

    def _process_template(self, template: str, timestamp: str, project_details: str, 
                         additional_sections: dict, modified_sections: dict, technology_stack: dict = None) -> str:
        """Process template with timestamp, project details, technology stack, and customizations."""
        tech_stack = technology_stack or {}
        
        # Replace timestamp placeholder
        content = template.replace("<MMDDYYYYHHMMSS>", timestamp)
        
        # Replace technology placeholders
        content = content.replace("<IaC_TOOL>", tech_stack.get('iac_tool', 'Terraform'))
        content = content.replace("<CONFIG_TOOL>", tech_stack.get('config_tool', 'Ansible'))
        content = content.replace("<CLOUD_PROVIDER>", tech_stack.get('cloud', 'Multi-Cloud'))
        
        # Apply section modifications
        for section_name, new_content in modified_sections.items():
            # Simple replacement - could be made more sophisticated
            content = content.replace(f"## {section_name}", f"## {section_name}\n{new_content}")
        
        # Add additional sections
        if additional_sections:
            content += "\n\n## Additional Sections\n"
            for section_name, section_content in additional_sections.items():
                content += f"\n### {section_name}\n{section_content}\n"
        
        # Add technology context
        if tech_stack:
            content += f"\n\n## Technology Stack\n"
            content += f"- **IaC Tool**: {tech_stack.get('iac_tool', 'Terraform')}\n"
            content += f"- **Config Tool**: {tech_stack.get('config_tool', 'Ansible')}\n" 
            content += f"- **Cloud Provider**: {tech_stack.get('cloud', 'Multi-Cloud')}\n"
            if tech_stack.get('orchestration'):
                content += f"- **Orchestration**: {tech_stack.get('orchestration')}\n"
            if tech_stack.get('ci_cd'):
                content += f"- **CI/CD**: {tech_stack.get('ci_cd')}\n"
        
        # Add project requirements
        content += f"\n\n## Project Requirements\n{project_details}"
        content += f"\n\n---\n*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content

    def _get_fallback_template(self, technology_stack: dict = None) -> str:
        """
        Provide a technology-specific fallback template if the template file is not found.
        """
        tech_stack = technology_stack or {}
        iac_tool = tech_stack.get('iac_tool', 'Terraform')
        config_tool = tech_stack.get('config_tool', 'Ansible')
        
        # Technology-specific section names
        iac_section = self._get_iac_section_title(iac_tool)
        config_section = self._get_config_section_title(config_tool)
        
        return f"""# Cloud Infrastructure Design: LZ_<MMDDYYYYHHMMSS>

## 1. Overview
- Business goal
- Regions  
- Assumptions

## 2. Architecture Diagram (textual if no image)

## 3. {iac_section}
{self._get_iac_subsections(iac_tool)}

## 4. {config_section}
{self._get_config_subsections(config_tool)}

## 5. Design Pillars

### Operational Excellence
- Monitoring/logging strategy
- Alerting pipelines

### Security
- Network boundaries
- Identity & access
- Secrets mgmt

### Reliability
- High availability zones
- Backup & DR

### Performance Efficiency
- Resource SKUs
- Auto-scale plans

### Cost Optimization
- Tagging conventions
- Budgeting alerts

## 6. Additional Notes
- Known constraints
- Assumed defaults"""

    def _get_iac_section_title(self, iac_tool: str) -> str:
        """Get technology-specific IaC section title."""
        titles = {
            'terraform': 'Terraform Repository Structure',
            'cloudformation': 'CloudFormation Template Structure', 
            'arm': 'ARM Template Structure',
            'pulumi': 'Pulumi Project Structure',
            'cdk': 'CDK Application Structure',
            'bicep': 'Bicep Module Structure'
        }
        return titles.get(iac_tool.lower(), 'Infrastructure as Code Structure')

    def _get_config_section_title(self, config_tool: str) -> str:
        """Get technology-specific configuration section title."""
        titles = {
            'ansible': 'Configuration Strategy (Ansible)',
            'chef': 'Configuration Strategy (Chef)',
            'puppet': 'Configuration Strategy (Puppet)', 
            'powershell_dsc': 'Configuration Strategy (PowerShell DSC)'
        }
        return titles.get(config_tool.lower(), 'Configuration Strategy')

    def _get_iac_subsections(self, iac_tool: str) -> str:
        """Get technology-specific IaC subsections."""
        subsections = {
            'terraform': "- Directory layout\n- State backend\n- Module breakdown",
            'cloudformation': "- Template structure\n- Parameter files\n- Nested stacks",
            'arm': "- Template structure\n- Parameter objects\n- Linked templates",
            'pulumi': "- Project structure\n- Stack configs\n- Component architecture",
            'cdk': "- App structure\n- Construct design\n- Stack composition",
            'bicep': "- Module structure\n- Parameter files\n- Template compilation"
        }
        return subsections.get(iac_tool.lower(), "- Directory layout\n- State management\n- Module breakdown")

    def _get_config_subsections(self, config_tool: str) -> str:
        """Get technology-specific configuration subsections."""
        subsections = {
            'ansible': "- Ansible roles and purpose\n- Host inventory plan",
            'chef': "- Cookbook structure\n- Recipe organization\n- Node configuration",
            'puppet': "- Manifest structure\n- Module organization\n- Agent configuration",
            'powershell_dsc': "- DSC configuration\n- Node management\n- Resource configuration"
        }
        return subsections.get(config_tool.lower(), "- Configuration roles and purpose\n- Host inventory plan")

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method.
        """
        return self.invoke(args, sly_data)
