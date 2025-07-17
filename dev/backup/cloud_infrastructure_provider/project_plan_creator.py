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
import re
from datetime import datetime
from typing import Any, Dict, Union, List, Tuple

from neuro_san.interfaces.coded_tool import CodedTool


class ProjectPlanCreator(CodedTool):
    """
    Creates project plans with task breakdowns and timelines for infrastructure projects.
    This tool analyzes design requirements and creates structured project plans.
    """

    def __init__(self):
        """
        Initialize the ProjectPlanCreator.
        """
        pass

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Create a project plan based on the provided design details or by reading the design document.

        :param args: A dictionary with the following keys:
                    "design_details": (optional) The design details to create a project plan for
                    "design_path": (optional) Path to design.md file to read
                    "timestamp": Project timestamp in MMDDYYYYHHMMSS format
                    "technology_stack": (optional) Detected technology stack for adaptive planning

        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.

        :return: The path to the created project plan or error message.
        """
        try:
            design_details = args.get("design_details", "")
            design_path = args.get("design_path", "")
            timestamp = args.get("timestamp", "")
            technology_stack = args.get("technology_stack", {})
            
            if not timestamp:
                return "Error: timestamp parameter is required"
            
            # If design_path not provided, construct it from timestamp
            if not design_path:
                design_path = os.path.join("output", f"LZ_{timestamp}", "docs", "design.md")
            
            # If design_details not provided, read from design file
            if not design_details:
                if os.path.exists(design_path):
                    try:
                        with open(design_path, 'r', encoding='utf-8') as f:
                            design_details = f.read()
                        print(f"========== Creating Project Plan ==========")
                        print(f"    Reading design from: {design_path}")
                        print(f"    Timestamp: {timestamp}")
                    except Exception as e:
                        return f"Error: Failed to read design document from {design_path}: {str(e)}"
                else:
                    error_message = f"Error: Design document not found at {design_path}."
                    error_message += "\n\nWORKFLOW ISSUE DETECTED:"
                    error_message += "\nThe ProjectPlanCreator requires a design document to be created first."
                    error_message += "\nCorrect workflow sequence:"
                    error_message += "\n1. Manager → Architect: Create design document"
                    error_message += "\n2. Architect → DesignDocumentCreator: Generate design.md"
                    error_message += "\n3. Architect → Manager: Report design completion"
                    error_message += "\n4. Manager → ProjectPlanCreator: Generate project plan (auto-reads design.md)"
                    error_message += f"\n\nPlease ensure the Architect has completed step 2 and created the design document at {design_path} before calling ProjectPlanCreator."
                    return error_message
            else:
                print(f"========== Creating Project Plan ==========")
                print(f"    Design Details: {design_details[:100]}...")
                print(f"    Timestamp: {timestamp}")

            # Create output directory structure
            output_dir = os.path.join("output", f"LZ_{timestamp}")
            docs_dir = os.path.join(output_dir, "docs")
            os.makedirs(docs_dir, exist_ok=True)

            # Create the project plan content with technology awareness
            plan_content = self._generate_project_plan_content(timestamp, design_details, technology_stack)
            
            # Create the project plan path
            plan_path = os.path.join(docs_dir, "project_plan.md")
            
            # Write the project plan document
            with open(plan_path, 'w') as f:
                f.write(plan_content)

            success_message = f"Project plan created successfully at: {plan_path}"
            print(f"    Result: {success_message}")
            
            # Store the plan path in sly_data for other tools to use
            sly_data["project_plan_path"] = plan_path
            sly_data["design_path"] = design_path
            
            return success_message

        except Exception as e:
            error_msg = f"Error creating project plan: {str(e)}"
            print(f"    Error: {error_msg}")
            return f"Error: {error_msg}"

    def _generate_project_plan_content(self, timestamp: str, design_details: str, technology_stack: dict = None) -> str:
        """
        Generate the project plan content based on design details and technology stack.
        """
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Analyze design details to extract requirements and incorporate technology stack
        requirements = self._analyze_design_requirements(design_details)
        
        # Merge technology stack if provided
        if technology_stack:
            requirements.update(technology_stack)
        
        # Generate dynamic tasks based on requirements
        tasks = self._generate_tasks_from_requirements(requirements)
        
        # Calculate timeline and dependencies
        timeline_info = self._calculate_timeline(tasks)
        
        # Generate deliverables based on requirements
        deliverables = self._generate_deliverables(requirements)
        
        # Generate risk assessment based on complexity
        risks = self._assess_risks(requirements)
        
        return f"""# Project Plan: LZ_{timestamp}

## Project Overview
This project plan outlines the tasks, timelines, and responsibilities for implementing the cloud infrastructure design.

**Generated on:** {current_date}
**Project Type:** {requirements.get('project_type', 'Cloud Infrastructure')}
**Cloud Provider:** {requirements.get('cloud_provider', requirements.get('cloud', 'Multi-Cloud'))}
**Complexity Level:** {requirements.get('complexity', 'Medium')}
**IaC Tool:** {requirements.get('iac_tool', 'Terraform')}
**Config Tool:** {requirements.get('config_tool', 'Ansible')}

## Requirements Summary
{self._format_requirements_summary(requirements)}

## Task Breakdown

| Phase | Task | Owner | Duration | Dependencies | Status |
|-------|------|-------|----------|--------------|--------|
{self._format_tasks_table(tasks)}

## Timeline Summary
- **Total Estimated Duration:** {timeline_info['total_duration']} days
- **Critical Path:** {timeline_info['critical_path']}
- **Parallel Opportunities:** {timeline_info['parallel_tasks']}

## Deliverables
{self._format_deliverables(deliverables)}

## Risk Assessment
{self._format_risks(risks)}

## Design Document Reference
- **Design Document**: `output/LZ_{timestamp}/docs/design.md`
- **Architecture**: Based on {requirements.get('iac_tool', 'Terraform')} + {requirements.get('config_tool', 'Ansible')} stack

## Next Steps
{self._generate_next_steps(requirements, tasks)}

---
*This project plan was dynamically generated based on the design document and follows infrastructure development best practices.*
"""

    def _analyze_design_requirements(self, design_details: str) -> Dict[str, Any]:
        """
        Analyze design details to extract key requirements and characteristics.
        """
        requirements = {
            'project_type': 'Cloud Infrastructure',
            'cloud_provider': 'Multi-Cloud',
            'complexity': 'Medium',
            'components': [],
            'technologies': [],
            'features': [],
            'scale': 'Medium',
            'security_level': 'Standard',
            'automation_level': 'Standard'
        }
        
        # Extract cloud provider
        if re.search(r'\b(?:aws|amazon)\b', design_details, re.IGNORECASE):
            requirements['cloud_provider'] = 'AWS'
        elif re.search(r'\b(?:azure|microsoft)\b', design_details, re.IGNORECASE):
            requirements['cloud_provider'] = 'Azure'
        elif re.search(r'\b(?:gcp|google)\b', design_details, re.IGNORECASE):
            requirements['cloud_provider'] = 'GCP'
        elif re.search(r'\bmulti.?cloud\b', design_details, re.IGNORECASE):
            requirements['cloud_provider'] = 'Multi-Cloud'
        
        # Extract technologies
        tech_patterns = {
            'terraform': r'\bterraform\b',
            'ansible': r'\bansible\b',
            'kubernetes': r'\b(?:kubernetes|k8s)\b',
            'docker': r'\bdocker\b',
            'jenkins': r'\bjenkins\b',
            'monitoring': r'\b(?:monitoring|prometheus|grafana)\b',
            'logging': r'\b(?:logging|elk|splunk)\b',
            'database': r'\b(?:database|db|mysql|postgres|mongo)\b',
            'load_balancer': r'\b(?:load.?balancer|alb|nlb)\b',
            'storage': r'\b(?:storage|s3|blob|volume)\b',
            'networking': r'\b(?:vpc|vnet|subnet|security.?group)\b',
            'ci_cd': r'\b(?:ci/cd|pipeline|deployment)\b'
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, design_details, re.IGNORECASE):
                requirements['technologies'].append(tech)
        
        # Determine complexity based on content analysis
        complexity_indicators = {
            'high': ['enterprise', 'scalable', 'distributed', 'microservices', 'multi-region', 'compliance'],
            'medium': ['application', 'production', 'staging', 'monitoring', 'backup'],
            'low': ['simple', 'basic', 'single', 'development', 'test']
        }
        
        for level, indicators in complexity_indicators.items():
            if any(re.search(f'\\b{indicator}\\b', design_details, re.IGNORECASE) for indicator in indicators):
                requirements['complexity'] = level.capitalize()
                break
        
        # Extract project scale
        if re.search(r'\b(?:large|enterprise|scale|thousands|millions)\b', design_details, re.IGNORECASE):
            requirements['scale'] = 'Large'
        elif re.search(r'\b(?:small|simple|basic|single)\b', design_details, re.IGNORECASE):
            requirements['scale'] = 'Small'
        
        # Extract security requirements
        if re.search(r'\b(?:security|compliance|audit|encryption|pci|hipaa|sox)\b', design_details, re.IGNORECASE):
            requirements['security_level'] = 'High'
        
        # Extract automation level
        if re.search(r'\b(?:automation|devops|ci/cd|pipeline|automated)\b', design_details, re.IGNORECASE):
            requirements['automation_level'] = 'High'
        
        return requirements

    def _generate_tasks_from_requirements(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate dynamic tasks based on analyzed requirements.
        """
        base_tasks = [
            {'name': 'Requirements Analysis', 'owner': 'Architect', 'base_duration': 1, 'phase': 1},
            {'name': 'Infrastructure Design Review', 'owner': 'Architect', 'base_duration': 1, 'phase': 2}
        ]
        
        # Add technology-specific tasks
        tech_tasks = {
            'terraform': [
                {'name': 'Terraform Module Setup', 'owner': 'Engineer', 'base_duration': 2, 'phase': 3},
                {'name': 'Terraform State Management', 'owner': 'Engineer', 'base_duration': 1, 'phase': 4}
            ],
            'ansible': [
                {'name': 'Ansible Role Development', 'owner': 'Engineer', 'base_duration': 2, 'phase': 7},
                {'name': 'Configuration Management', 'owner': 'Engineer', 'base_duration': 1, 'phase': 8}
            ],
            'kubernetes': [
                {'name': 'Kubernetes Cluster Setup', 'owner': 'Engineer', 'base_duration': 3, 'phase': 5},
                {'name': 'Container Orchestration', 'owner': 'Engineer', 'base_duration': 2, 'phase': 6}
            ],
            'networking': [
                {'name': 'Network Infrastructure', 'owner': 'Engineer', 'base_duration': 2, 'phase': 4},
                {'name': 'Security Groups & Firewall', 'owner': 'Engineer', 'base_duration': 1, 'phase': 5}
            ],
            'database': [
                {'name': 'Database Configuration', 'owner': 'Engineer', 'base_duration': 2, 'phase': 6},
                {'name': 'Data Migration Setup', 'owner': 'Engineer', 'base_duration': 1, 'phase': 7}
            ],
            'monitoring': [
                {'name': 'Monitoring Setup', 'owner': 'Engineer', 'base_duration': 2, 'phase': 8},
                {'name': 'Alerting Configuration', 'owner': 'Engineer', 'base_duration': 1, 'phase': 9}
            ],
            'storage': [
                {'name': 'Storage Configuration', 'owner': 'Engineer', 'base_duration': 1, 'phase': 5}
            ],
            'load_balancer': [
                {'name': 'Load Balancer Setup', 'owner': 'Engineer', 'base_duration': 1, 'phase': 6}
            ],
            'ci_cd': [
                {'name': 'CI/CD Pipeline Setup', 'owner': 'Engineer', 'base_duration': 3, 'phase': 9},
                {'name': 'Deployment Automation', 'owner': 'Engineer', 'base_duration': 2, 'phase': 10}
            ]
        }
        
        tasks = base_tasks.copy()
        
        # Add tasks based on detected technologies
        for tech in requirements.get('technologies', []):
            if tech in tech_tasks:
                tasks.extend(tech_tasks[tech])
        
        # Add standard infrastructure tasks if not covered by technology-specific tasks
        standard_tasks = [
            {'name': 'Compute Resources', 'owner': 'Engineer', 'base_duration': 2, 'phase': 5},
            {'name': 'Security Implementation', 'owner': 'Engineer', 'base_duration': 2, 'phase': 8}
        ]
        
        # Only add standard tasks if similar tech-specific tasks weren't added
        existing_task_names = [task['name'].lower() for task in tasks]
        for task in standard_tasks:
            if not any(keyword in existing_task_names for keyword in task['name'].lower().split()):
                tasks.append(task)
        
        # Add final tasks
        final_tasks = [
            {'name': 'Testing & Validation', 'owner': 'Architect', 'base_duration': 2, 'phase': 98},
            {'name': 'Documentation Update', 'owner': 'Architect', 'base_duration': 1, 'phase': 99},
            {'name': 'Deployment & Handover', 'owner': 'Engineer', 'base_duration': 1, 'phase': 100}
        ]
        
        tasks.extend(final_tasks)
        
        # Adjust durations based on complexity
        complexity_multiplier = {
            'Low': 0.8,
            'Medium': 1.0,
            'High': 1.5
        }
        
        multiplier = complexity_multiplier.get(requirements.get('complexity', 'Medium'), 1.0)
        
        # Sort tasks by phase and assign task numbers and dependencies
        tasks.sort(key=lambda x: x['phase'])
        
        for i, task in enumerate(tasks):
            task['task_number'] = i + 1
            task['duration'] = max(1, int(task['base_duration'] * multiplier))
            task['dependencies'] = f"Task {i}" if i > 0 else "None"
            task['status'] = 'Planned'
        
        return tasks

    def _calculate_timeline(self, tasks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Calculate timeline information based on tasks.
        """
        total_duration = sum(task['duration'] for task in tasks)
        
        # Calculate critical path (sequential tasks)
        critical_path_tasks = [f"Task {task['task_number']}" for task in tasks[:5]]  # First 5 as critical
        critical_path = " → ".join(critical_path_tasks)
        
        # Identify parallel opportunities
        parallel_tasks = []
        tech_tasks = [task for task in tasks if task['owner'] == 'Engineer' and 5 <= task['task_number'] <= len(tasks) - 3]
        if len(tech_tasks) >= 2:
            parallel_tasks.append(f"{tech_tasks[0]['name']} and {tech_tasks[1]['name']}")
        
        parallel_opportunities = "; ".join(parallel_tasks) if parallel_tasks else "Limited parallel opportunities"
        
        return {
            'total_duration': str(total_duration),
            'critical_path': critical_path,
            'parallel_tasks': parallel_opportunities
        }

    def _generate_deliverables(self, requirements: Dict[str, Any]) -> List[str]:
        """
        Generate deliverables based on requirements.
        """
        base_deliverables = [
            "**Design Document** - Comprehensive architecture documentation",
            "**Infrastructure Code** - Infrastructure as Code implementation"
        ]
        
        tech_deliverables = {
            'terraform': "**Terraform Modules** - Reusable infrastructure modules",
            'ansible': "**Ansible Playbooks** - Configuration management scripts",
            'kubernetes': "**Kubernetes Manifests** - Container orchestration configurations",
            'monitoring': "**Monitoring Setup** - Monitoring and alerting configurations",
            'ci_cd': "**CI/CD Pipelines** - Automated deployment pipelines",
            'database': "**Database Schemas** - Database setup and migration scripts"
        }
        
        deliverables = base_deliverables.copy()
        
        for tech in requirements.get('technologies', []):
            if tech in tech_deliverables:
                deliverables.append(tech_deliverables[tech])
        
        # Add standard deliverables
        standard_deliverables = [
            "**Testing Documentation** - Validation and testing results",
            "**Deployment Guide** - Step-by-step deployment instructions",
            "**Operations Manual** - Ongoing maintenance and support documentation"
        ]
        
        deliverables.extend(standard_deliverables)
        
        return deliverables

    def _assess_risks(self, requirements: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Assess risks based on requirements complexity.
        """
        risks = {
            'High': [],
            'Medium': [],
            'Low': []
        }
        
        # Complexity-based risks
        if requirements.get('complexity') == 'High':
            risks['High'].extend([
                "Complex architecture may require extensive testing",
                "Integration challenges between multiple components"
            ])
        
        # Technology-specific risks
        if 'kubernetes' in requirements.get('technologies', []):
            risks['Medium'].append("Kubernetes cluster management complexity")
        
        if 'ci_cd' in requirements.get('technologies', []):
            risks['Medium'].append("CI/CD pipeline reliability and security")
        
        if requirements.get('security_level') == 'High':
            risks['High'].append("Security compliance requirements")
        
        # Default risks
        risks['Medium'].extend([
            "Resource availability and scaling requirements",
            "Third-party service dependencies"
        ])
        
        risks['Low'].extend([
            "Documentation and knowledge transfer",
            "Minor configuration adjustments"
        ])
        
        return risks

    def _format_requirements_summary(self, requirements: Dict[str, Any]) -> str:
        """Format requirements summary."""
        technologies = ", ".join(requirements.get('technologies', []))
        return f"""- **Technologies:** {technologies or 'Standard Infrastructure'}
- **Scale:** {requirements.get('scale', 'Medium')} scale deployment
- **Security Level:** {requirements.get('security_level', 'Standard')}
- **Automation Level:** {requirements.get('automation_level', 'Standard')}"""

    def _format_tasks_table(self, tasks: List[Dict[str, Any]]) -> str:
        """Format tasks as table rows."""
        rows = []
        for task in tasks:
            row = f"| {task['task_number']} | {task['name']} | {task['owner']} | {task['duration']} day{'s' if task['duration'] > 1 else ''} | {task['dependencies']} | {task['status']} |"
            rows.append(row)
        return "\n".join(rows)

    def _format_deliverables(self, deliverables: List[str]) -> str:
        """Format deliverables as numbered list."""
        return "\n".join(f"{i+1}. {deliverable}" for i, deliverable in enumerate(deliverables))

    def _format_risks(self, risks: Dict[str, List[str]]) -> str:
        """Format risks by level."""
        sections = []
        for level, risk_list in risks.items():
            if risk_list:
                formatted_risks = "\n".join(f"  - {risk}" for risk in risk_list)
                sections.append(f"- **{level}:**\n{formatted_risks}")
        return "\n".join(sections)

    def _generate_next_steps(self, requirements: Dict[str, Any], tasks: List[Dict[str, Any]]) -> str:
        """Generate next steps based on requirements and tasks."""
        steps = []
        
        if tasks:
            first_task = tasks[0]
            steps.append(f"1. {first_task['owner']} to begin {first_task['name'].lower()}")
        
        if 'terraform' in requirements.get('technologies', []):
            steps.append("2. Set up Terraform workspace and state management")
        else:
            steps.append("2. Prepare infrastructure provisioning tools")
        
        if requirements.get('complexity') == 'High':
            steps.append("3. Schedule detailed technical review meetings")
        else:
            steps.append("3. Regular progress check-ins every 2-3 days")
        
        steps.append("4. Establish testing and validation procedures")
        
        return "\n".join(steps)

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method.
        """
        return self.invoke(args, sly_data)
