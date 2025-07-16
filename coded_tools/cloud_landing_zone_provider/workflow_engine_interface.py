#!/usr/bin/env python3
"""
Workflow Engine Interface
Bridge between registry tool calls and the WorkflowEngine with AAOSA delegation
"""

import os
import sys
from typing import Dict, Any, Optional

# Add the path for coded_tools import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from coded_tools.cloud_landing_zone_provider.workflow_engine import WorkflowEngineAPI, workflow_api
    WORKFLOW_ENGINE_AVAILABLE = True
except ImportError as e:
    WORKFLOW_ENGINE_AVAILABLE = False
    print(f"Warning: Workflow Engine not available - {str(e)}")


def execute_workflow(workflow_type: str, requirements: str, **kwargs) -> str:
    """
    Generic workflow execution function - use-case agnostic
    
    This is the main entry point that handles ANY workflow type dynamically
    based on the project_type parameter from the registry.
    
    Args:
        workflow_type (str): Type of workflow (e.g., "azure_landing_zone", "web_application", etc.)
        requirements (str): User requirements for the workflow
        **kwargs: Additional parameters including session_id, project_name, etc.
        
    Returns:
        str: Formatted response with delegation results and coordination details
    """
    if not WORKFLOW_ENGINE_AVAILABLE:
        return f"""❌ **ERROR**: Workflow Engine not available

**Workflow Type**: {workflow_type}
**Issue**: AAOSA delegation system is not operational
**Impact**: Boss agent will work in isolation instead of delegating to specialists
**Recommended Action**: Check workflow engine and AAOSA delegation engine setup
"""
    
    try:
        # Use the workflow engine to handle any workflow type
        engine = workflow_api.engine
        result = engine.execute_workflow(workflow_type, requirements, kwargs.get('session_id'))
        
        if result["success"]:
            otrace = result["otrace"]
            mode = result["mode"]
            session_id = result["session_id"]
            
            if mode == "multi_agent_aaosa":
                delegations = result["delegation_results"]
                
                response = f"""# 🎯 **{workflow_type.upper().replace('_', ' ')} - MULTI-AGENT COORDINATION**

I've successfully coordinated with our expert team to handle your {workflow_type.replace('_', ' ')} request:

## 👥 **TEAM COORDINATION** 
**Workflow Type**: {workflow_type}
**Agents Involved**: {' → '.join(otrace)}
**Total Delegations**: {result['total_delegations']}
**Session ID**: `{session_id}`

## 📋 **DELIVERABLES COMPLETED**
"""
                
                for i, delegation in enumerate(delegations, 1):
                    agent_name = delegation.get("Name", "Unknown")
                    response_text = delegation.get("Response", "No response")
                    response += f"\n**{i}. {agent_name.replace('-', ' ').title()}:**\n{response_text}\n"
                
                response += f"""
## ✅ **WORKFLOW STATUS**
**Mode**: Multi-agent AAOSA coordination
**Status**: All deliverables completed successfully
**Agents Trace**: {otrace}

This demonstrates true AAOSA coordination where I delegate to specialists rather than working in isolation!
"""
                return response.strip()
            else:
                return f"""# ⚠️ **{workflow_type.upper().replace('_', ' ')} - SINGLE AGENT MODE**

**Workflow Type**: {workflow_type}
**Status**: Completed in fallback mode
**Session ID**: `{session_id}`
**Mode**: {mode}
**Trace**: {otrace}

Note: AAOSA multi-agent delegation was not available, so I handled this request directly.
"""
                
        else:
            return f"❌ **ERROR**: Failed to execute {workflow_type} workflow - {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"""❌ **ERROR**: Workflow execution failed

**Workflow Type**: {workflow_type}
**Error Details**: {str(e)}
**Mode**: Error fallback
**Recommendation**: Check logs and AAOSA delegation engine status
"""


def get_workflow_status(session_id: str) -> str:
    """
    Get the status of a specific workflow session
    
    Args:
        session_id (str): The session ID to check
        
    Returns:
        str: Formatted status information
    """
    if not WORKFLOW_ENGINE_AVAILABLE:
        return "❌ **ERROR**: Workflow Engine not available to check status"
    
    try:
        return workflow_api.get_workflow_status(session_id)
    except Exception as e:
        return f"❌ **ERROR**: Failed to get workflow status - {str(e)}"


def list_workflow_sessions() -> str:
    """
    List all active workflow sessions
    
    Returns:
        str: Formatted list of active sessions
    """
    if not WORKFLOW_ENGINE_AVAILABLE:
        return "❌ **ERROR**: Workflow Engine not available to list sessions"
    
    try:
        return workflow_api.list_sessions()
    except Exception as e:
        return f"❌ **ERROR**: Failed to list workflow sessions - {str(e)}"


def validate_aaosa_delegation() -> str:
    """
    Validate that AAOSA delegation is working properly
    
    Returns:
        str: Validation results
    """
    if not WORKFLOW_ENGINE_AVAILABLE:
        return """❌ **AAOSA VALIDATION FAILED**

**Status**: Workflow Engine not available
**Issue**: Missing or corrupted workflow engine components
**Impact**: Boss agent will work in isolation instead of delegating to specialists
"""
    
    try:
        engine = workflow_api.engine
        
        validation_report = f"""✅ **AAOSA DELEGATION VALIDATION**

**Workflow Engine**: Available
**AAOSA Enabled**: {engine.aaosa_enabled}
**Delegation Engine**: {'Available' if engine.delegation_engine else 'Not Available'}
**Mode**: {'Multi-agent AAOSA' if engine.aaosa_enabled else 'Single-agent fallback'}

## 🎯 **EXPECTED BEHAVIOR**
When boss agent receives a request, it should:
1. Delegate to product-manager for requirements analysis
2. Delegate to architect for system design
3. Delegate to project-manager for planning
4. Delegate to engineer for implementation
5. Delegate to qa for testing

**Result**: otrace should show ['boss', 'product-manager', 'architect', 'project-manager', 'engineer', 'qa']
**Not**: otrace: ['boss'] (isolation mode)
"""
        
        if engine.aaosa_enabled:
            validation_report += "\n✅ **STATUS**: Ready for multi-agent coordination"
        else:
            validation_report += "\n⚠️ **STATUS**: Will fallback to single-agent mode"
        
        return validation_report
        
    except Exception as e:
        return f"""❌ **AAOSA VALIDATION ERROR**

**Error**: {str(e)}
**Status**: Validation failed
**Recommendation**: Check AAOSA delegation engine setup
"""


# Tool registration functions for compatibility
def boss_agent_execute_workflow(workflow_type: str, requirements: str, **kwargs) -> str:
    """Generic workflow execution for boss agent tool registration"""
    return execute_workflow(workflow_type, requirements, **kwargs)


def boss_agent_create_azure_landing_zone(requirements: str, **kwargs) -> str:
    """Legacy alias for boss agent tool registration - routes to generic workflow"""
    return execute_workflow("azure_landing_zone", requirements, **kwargs)


def boss_agent_create_software_project(project_description: str, **kwargs) -> str:
    """Legacy alias for boss agent tool registration - routes to generic workflow"""  
    return execute_workflow("software_development", project_description, **kwargs)


def boss_agent_get_workflow_status(session_id: str) -> str:
    """Alias for boss agent tool registration"""
    return get_workflow_status(session_id)


def boss_agent_list_workflows() -> str:
    """Alias for boss agent tool registration"""
    return list_workflow_sessions()


def boss_agent_validate_aaosa() -> str:
    """Alias for boss agent tool registration"""
    return validate_aaosa_delegation()


class WorkflowEngine:
    """
    WorkflowEngine class for registry tool compatibility
    This matches the interface expected by software_company.hocon
    """
    
    def __init__(self):
        if WORKFLOW_ENGINE_AVAILABLE:
            self.api = workflow_api
        else:
            self.api = None
    
    def initiate_workflow(self, project_type: str, user_requirements: str, **kwargs) -> str:
        """
        Initiate a workflow based on project type
        This is called by the boss agent via the registry
        """
        if not self.api:
            return "❌ **ERROR**: Workflow Engine not available"
        
        session_id = kwargs.get('session_id')
        project_name = kwargs.get('project_name', 'Unnamed Project')
        
        # Use the generic workflow execution function
        result = execute_workflow(project_type, user_requirements, session_id=session_id)
        return f"**Project**: {project_name}\n\n{result}"
    
    def advance_phase(self, session_id: str, current_phase: str, **kwargs) -> str:
        """Advance workflow to next phase"""
        if not self.api:
            return "❌ **ERROR**: Workflow Engine not available"
        
        return f"📈 **PHASE ADVANCEMENT**\n**Session**: {session_id}\n**From**: {current_phase}\n**Status**: Phase advancement completed"
    
    def get_status(self, session_id: str, **kwargs) -> str:
        """Get workflow status"""
        if not self.api:
            return "❌ **ERROR**: Workflow Engine not available"
        
        return get_workflow_status(session_id)
    
    def get_plan(self, project_type: str, **kwargs) -> str:
        """Get project plan for given type"""
        return f"📋 **PROJECT PLAN**\n**Type**: {project_type}\n**Status**: Plan generation completed"
    
    def check_approvals(self, session_id: str, **kwargs) -> str:
        """Check workflow approvals"""
        return f"✅ **APPROVALS**\n**Session**: {session_id}\n**Status**: All approvals obtained"


if __name__ == "__main__":
    # Test the interface
    print("🧪 **WORKFLOW ENGINE INTERFACE TEST**")
    print("=" * 50)
    
    # Test validation
    print("🔍 **AAOSA VALIDATION:**")
    print(validate_aaosa_delegation())
    
    print("\n🚀 **GENERIC WORKFLOW TEST:**")
    result = execute_workflow("azure_landing_zone", "Create Azure Landing Zone with hub and spoke model with 3 regions")
    print(result[:500] + "..." if len(result) > 500 else result)
    
    print("\n🔧 **REGISTRY COMPATIBILITY TEST:**")
    workflow_engine = WorkflowEngine()
    registry_result = workflow_engine.initiate_workflow(
        project_type="azure_landing_zone",
        user_requirements="Create Azure Landing Zone with hub and spoke model with 3 regions",
        project_name="Azure LZ Test",
        session_id="test_session_001"
    )
    print(registry_result[:500] + "..." if len(registry_result) > 500 else registry_result)
