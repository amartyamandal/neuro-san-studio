# Cloud Infrastructure Provider Agents

A comprehensive multi-agent system for designing, planning, and building cloud infrastructure using Infrastructure as Code (IaC) and configuration management.

## Overview

This system implements the cloud infrastructure provider workflow with specialized agents that handle different aspects of infrastructure deployment:

- **Manager**: Coordinates workflow and interfaces with users
- **Architect**: Designs infrastructure and creates detailed specifications  
- **Engineer**: Builds Terraform and Ansible code from designs
- **Project Planner**: Creates project plans with task breakdowns and timelines

## Agents & Expertise

| Agent | Role Summary | Expertise Tags |
|-------|-------------|----------------|
| **Manager** | Interfaces with user, coordinates workflow, builds project plan | `communication`, `project planning` |
| **Architect** | Designs infra using cloud + IaC best practices | `terraform`, `ansible`, `git`, `cloud (Azure, AWS, GCP)` |
| **Engineer** | Builds code from design; clarifies build gaps with architect | `terraform`, `ansible`, `git` |

## End-to-End Workflow

### 1. User → Manager
User submits a request: "I need a landing zone in Azure for my app…"
(Could be vague or detailed.)

### 2. Manager → Architect
"Please create design.md based on the user request. Use Terraform for infra, Ansible for config."

### 3. Architect ↔ User (via Manager)
Architect asks clarifying questions only if needed.
Once all info is collected or user says "use defaults," Architect generates:
```
output/LZ_<MMDDYYYYHHMMSS>/docs/design.md
```

### 4. Manager creates Project Plan
Writes project_plan.md with estimated task durations (1–2 days granularity).
```
output/LZ_<MMDDYYYYHHMMSS>/docs/project_plan.md
```

### 5. Manager → User
"Design and project plan are ready for approval."

### 6. User Approves
When user gives the green light…

### 7. Engineer → Architect (if needed)
Engineer reviews design.md, and if unclear, asks clarifying questions only to the Architect.

### 8. Engineer Builds & Stores Code
Code stored under:
```
output/LZ_<TS>/iac/terraform/
output/LZ_<TS>/config/ansible/
```

### 9. Final Status
Manager confirms project is in build or completed phase.

## Directory Structure (Session-based)

```
output/
  LZ_<MMDDYYYYHHMMSS>/
    docs/
      design.md          ← Architect-created
      project_plan.md    ← Manager-created
    iac/
      terraform/         ← Engineer-created
        main.tf
        variables.tf
        outputs.tf
        provider.tf
        versions.tf
        modules/
          network/
        environments/
          dev/
            terraform.tfvars
    config/
      ansible/           ← Engineer-created
        ansible.cfg
        requirements.yml
        playbooks/
          site.yml
          webservers.yml
          databases.yml
        roles/
          common/
          webserver/
          database/
        inventories/
          dev.yml
          prod.yml
        group_vars/
          all.yml
          webservers.yml
          databases.yml
```

## Implementation Details

### Registry Configuration
- **File**: `registries/cloud_infrastructure_provider.hocon`
- **Structure**: AAOSA (Agent-Agent-Orchestrated Service Architecture) pattern
- **Tools**: Multi-agent coordination with specialized coded tools

### Coded Tools
Located in `coded_tools/cloud_infrastructure_provider/`:

- **DesignDocumentCreator**: Creates detailed infrastructure design documents
- **ProjectPlanCreator**: Generates project plans with task breakdowns
- **TerraformBuilder**: Generates complete Terraform infrastructure code
- **AnsibleBuilder**: Creates comprehensive Ansible configuration

### Templates
- **Design Template**: `coded_tools/cloud_infrastructure_provider/template/design.md.template`
- Provides structured approach following Well-Architected Framework pillars

## Testing

Comprehensive test suite located in `tests/coded_tools/cloud_infrastructure_provider/`:

### Test Files
- `test_design_document_creator.py` - Unit tests for design document creation
- `test_project_plan_creator.py` - Unit tests for project planning
- `test_terraform_builder.py` - Unit tests for Terraform code generation
- `test_ansible_builder.py` - Unit tests for Ansible configuration generation
- `test_integration.py` - End-to-end integration tests
- `run_tests.py` - Test runner script with coverage support

### Running Tests

```bash
# Run all tests
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py

# Run only unit tests
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py --unit

# Run only integration tests
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py --integration

# Run with verbose output
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py --verbose

# Run with coverage reporting
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py --coverage

# Run tests for specific module
python tests/coded_tools/cloud_infrastructure_provider/run_tests.py --module design_document_creator
```

## Features

### Design Document Creation
- Uses structured template following Well-Architected Framework
- Includes business requirements, technical specifications, and architecture details
- Automatically generates timestamped documentation

### Project Planning
- Breaks down infrastructure projects into manageable tasks
- Provides realistic timeline estimates (1-2 day granularity)
- Identifies dependencies and assigns ownership (Architect vs Engineer)
- Includes risk assessment and deliverables tracking

### Terraform Code Generation
- Complete infrastructure-as-code implementation
- Modular design with reusable components
- Azure-focused with best practices
- Includes state management, variables, outputs, and documentation
- Environment-specific configurations (dev, prod)

### Ansible Configuration
- Comprehensive server configuration management
- Role-based architecture (common, webserver, database)
- Multi-environment inventory management
- Security hardening and monitoring setup
- Complete documentation and setup instructions

## Security Considerations

1. **Infrastructure Security**
   - Network segmentation with security groups
   - Least-privilege access patterns
   - SSL/TLS configuration
   - Backup and disaster recovery

2. **Configuration Security**
   - SSH key-based authentication
   - Firewall configuration
   - Security headers and hardening
   - Ansible Vault for secrets management

3. **Operational Security**
   - Monitoring and alerting
   - Log management
   - Regular security updates
   - Access control and auditing

## Best Practices

### Well-Architected Framework
All designs follow the five pillars:
1. **Operational Excellence** - Monitoring, logging, alerting
2. **Security** - Network boundaries, identity, secrets management
3. **Reliability** - High availability, backup, disaster recovery
4. **Performance Efficiency** - Resource optimization, auto-scaling
5. **Cost Optimization** - Tagging, budgeting, resource optimization

### Infrastructure as Code
- Version-controlled infrastructure definitions
- Automated deployment and configuration
- Consistent environments across dev/staging/prod
- Documentation integrated with code

### Configuration Management
- Idempotent operations
- Role-based organization
- Environment-specific variables
- Comprehensive testing and validation

## Usage Examples

### Basic Landing Zone Request
```
"I need a basic Azure landing zone for a web application with a database."
```

### Complex Multi-Region Setup
```
"I need a highly available e-commerce platform on Azure with:
- Multi-region deployment (East US, West US, Europe)
- Auto-scaling web tier
- Database clustering
- CDN integration
- PCI DSS compliance requirements"
```

### Development Environment
```
"Set up a development environment in Azure with:
- Single region (East US)
- Basic networking
- Development-grade resources
- Cost optimization focus"
```

## Support

For questions or issues:
1. Review the generated design documents and project plans
2. Check the comprehensive README files in generated output
3. Run the test suite to validate functionality
4. Contact the infrastructure team for specialized assistance

---

*This system provides a complete solution for cloud infrastructure design, planning, and implementation using industry best practices and proven patterns.*
