# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.

import os
import logging
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool


class ProjectPlanCreator(CodedTool):
    """Creates detailed project implementation plans with timelines and resource allocation."""

    def __init__(self):
        pass

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        try:
            project_name = args.get("project_name", "")
            
            if not project_name:
                return "Error: project_name parameter is required"

            logger = logging.getLogger(self.__class__.__name__)
            logger.info("Creating project plan for project: %s", project_name)
            
            # Create directory structure
            output_dir = f"output/{project_name}"
            docs_dir = os.path.join(output_dir, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            
            # Read design document if it exists
            design_content = ""
            design_path = os.path.join(docs_dir, "design.md")
            if os.path.exists(design_path):
                with open(design_path, 'r', encoding='utf-8') as f:
                    design_content = f.read()
            
            # Generate project plan
            plan_content = self._generate_project_plan(project_name, design_content)
            
            # Write to file
            plan_path = os.path.join(docs_dir, "project_plan.md")
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)
            
            return f"Project plan successfully created at {plan_path}"
            
        except Exception as e:
            return f"Error: Failed to create project plan - {str(e)}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)

    def _generate_project_plan(self, project_name: str, design_content: str = "") -> str:
        return f'''# Project Implementation Plan: {project_name}

**Document Version:** 1.0  
**Created:** {self._get_timestamp()}  
**Project Name:** {project_name}  
**Project Manager:** TBD  
**Technical Lead:** TBD  

## 1. Project Overview

### 1.1 Project Summary
This project plan is based on the design specifications for {project_name}.

{design_content[:500] + "..." if len(design_content) > 500 else design_content}

### 1.2 Project Objectives
Based on the design requirements, this project aims to implement a comprehensive infrastructure that meets all specified requirements for security, performance, and operational excellence.

## 2. Project Timeline

### Phase 1: Infrastructure Setup ({self._get_start_date()} - {self._get_date_offset(3)})
- Environment configuration
- Network setup
- Security baseline implementation

### Phase 2: Core Services ({self._get_date_offset(4)} - {self._get_date_offset(7)})
- Core infrastructure deployment
- Identity and access management
- Monitoring and logging setup

### Phase 3: Application Integration ({self._get_date_offset(8)} - {self._get_date_offset(10)})
- Application deployment
- Testing and validation
- Documentation finalization

## 3. Deliverables

1. **Infrastructure as Code (IaC)**
   - Terraform configurations
   - Ansible playbooks
   - Environment-specific variables

2. **Documentation**
   - Architecture diagrams
   - Deployment guides
   - Operations runbooks

3. **Testing Results**
   - Security validation
   - Performance benchmarks
   - Disaster recovery procedures

## 4. Success Criteria

- All infrastructure components deployed and functional
- Security requirements met and validated
- Performance targets achieved
- Documentation complete and reviewed
- Team trained on operations and maintenance

## 5. Risk Management

### High Priority Risks
- Network connectivity issues
- Security configuration gaps
- Resource quota limitations

### Mitigation Strategies
- Pre-deployment validation
- Incremental rollout approach
- Rollback procedures documented

## 6. Next Steps

1. Review and approve this project plan
2. Assign team members to specific tasks
3. Begin Phase 1 implementation
4. Schedule weekly progress reviews
'''

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_start_date(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_date_offset(self, days):
        from datetime import datetime, timedelta
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
