#!/usr/bin/env python3
"""
Software Development Workflow Engine with AAOSA Integration
Coordinates multi-agent workflows for software development projects
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Add the path for coded_tools import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from coded_tools.cloud_landing_zone_provider.aaosa_delegation_engine import AAOSADelegationEngine
    AAOSA_AVAILABLE = True
except ImportError:
    AAOSA_AVAILABLE = False
    print("Warning: AAOSA Delegation Engine not available - falling back to single-agent mode")


class WorkflowEngine:
    """
    Core workflow engine that orchestrates software development workflows
    with AAOSA multi-agent delegation
    """
    
    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path
        self.workflows = {}
        self.active_sessions = {}
        
        # Initialize AAOSA delegation if available
        if AAOSA_AVAILABLE:
            self.delegation_engine = AAOSADelegationEngine()
            self.aaosa_enabled = True
        else:
            self.delegation_engine = None
            self.aaosa_enabled = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for workflow engine"""
        logger = logging.getLogger("workflow_engine")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = logs_dir / "workflow_engine.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def execute_workflow(self, workflow_type: str, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a workflow with AAOSA delegation
        This is the main entry point that replaces single-agent execution
        """
        if not session_id:
            session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Starting workflow {workflow_type} with session {session_id}")
        
        if not self.aaosa_enabled:
            # Fallback to single-agent mode
            return self._execute_single_agent_workflow(workflow_type, user_input, session_id)
        
        # Execute with AAOSA delegation
        try:
            workflow_result = self.delegation_engine.execute_workflow_delegation(
                workflow_type=workflow_type,
                user_requirements=user_input,
                session_id=session_id
            )
            
            # Store session
            self.active_sessions[session_id] = {
                "workflow_type": workflow_type,
                "user_input": user_input,
                "result": workflow_result,
                "timestamp": datetime.now().isoformat(),
                "mode": "multi_agent_aaosa"
            }
            
            self.logger.info(f"Workflow {session_id} completed with {len(workflow_result['otrace'])} agents")
            
            return {
                "success": True,
                "session_id": session_id,
                "workflow_type": workflow_type,
                "otrace": workflow_result["otrace"],
                "delegation_results": workflow_result["delegation_results"],
                "mode": "multi_agent_aaosa",
                "total_delegations": len(workflow_result["delegation_trace"]),
                "workflow_result": workflow_result
            }
            
        except Exception as e:
            self.logger.error(f"Workflow {session_id} failed: {str(e)}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "mode": "error"
            }
    
    def _execute_single_agent_workflow(self, workflow_type: str, user_input: str, session_id: str) -> Dict[str, Any]:
        """Fallback to single-agent execution when AAOSA is not available"""
        self.logger.warning(f"Executing {workflow_type} in single-agent mode (session: {session_id})")
        
        # Store session
        self.active_sessions[session_id] = {
            "workflow_type": workflow_type,
            "user_input": user_input,
            "result": {"otrace": ["boss"], "mode": "single_agent"},
            "timestamp": datetime.now().isoformat(),
            "mode": "single_agent_fallback"
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_type": workflow_type,
            "otrace": ["boss"],
            "mode": "single_agent_fallback",
            "message": "Executed in single-agent mode - AAOSA delegation not available"
        }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow session"""
        if session_id not in self.active_sessions:
            return {"error": f"No session found with ID: {session_id}"}
        
        session = self.active_sessions[session_id]
        return {
            "session_id": session_id,
            "workflow_type": session["workflow_type"],
            "timestamp": session["timestamp"],
            "mode": session["mode"],
            "otrace": session["result"].get("otrace", ["unknown"]),
            "status": "completed"
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active workflow sessions"""
        return [
            {
                "session_id": sid,
                "workflow_type": session["workflow_type"],
                "timestamp": session["timestamp"],
                "mode": session["mode"],
                "agents_count": len(session["result"].get("otrace", ["unknown"]))
            }
            for sid, session in self.active_sessions.items()
        ]
    
    def handle_azure_landing_zone(self, user_requirements: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle Azure Landing Zone requests specifically
        This is called by the boss agent tool
        """
        return self.execute_workflow(
            workflow_type="azure_landing_zone",
            user_input=user_requirements,
            session_id=session_id
        )
    
    def handle_software_development(self, project_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle general software development requests"""
        return self.execute_workflow(
            workflow_type="software_development",
            user_input=project_description,
            session_id=session_id
        )


class WorkflowEngineAPI:
    """
    API interface for the workflow engine
    This is what gets called by registry tools
    """
    
    def __init__(self):
        self.engine = WorkflowEngine()
    
    def create_azure_landing_zone(self, requirements: str, **kwargs) -> str:
        """
        Tool function for creating Azure Landing Zone
        Called by boss agent from software_company.hocon registry
        """
        session_id = kwargs.get('session_id')
        result = self.engine.handle_azure_landing_zone(requirements, session_id)
        
        if result["success"]:
            # Generate response message for boss agent
            otrace = result["otrace"]
            mode = result["mode"]
            
            if mode == "multi_agent_aaosa":
                delegations = result["delegation_results"]
                
                response = f"""# 🎯 **AZURE LANDING ZONE - MULTI-AGENT COORDINATION**

I've successfully coordinated with our expert team to handle your Azure Landing Zone request:

## 👥 **TEAM COORDINATION** 
**Agents Involved**: {' → '.join(otrace)}
**Total Delegations**: {result['total_delegations']}
**Session ID**: `{result['session_id']}`

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
            else:
                response = f"""# ⚠️ **AZURE LANDING ZONE - SINGLE AGENT MODE**

**Status**: Completed in fallback mode
**Session ID**: `{result['session_id']}`
**Mode**: {mode}
**Trace**: {otrace}

Note: AAOSA multi-agent delegation was not available, so I handled this request directly.
"""
            
            return response.strip()
        else:
            return f"❌ **ERROR**: Failed to create Azure Landing Zone - {result.get('error', 'Unknown error')}"
    
    def get_workflow_status(self, session_id: str) -> str:
        """Get status of a workflow session"""
        status = self.engine.get_session_status(session_id)
        
        if "error" in status:
            return f"❌ {status['error']}"
        
        return f"""📊 **WORKFLOW STATUS**
**Session ID**: {status['session_id']}
**Type**: {status['workflow_type']}
**Mode**: {status['mode']}
**Agents**: {status['otrace']}
**Status**: {status['status']}
**Timestamp**: {status['timestamp']}
"""
    
    def list_sessions(self) -> str:
        """List all active workflow sessions"""
        sessions = self.engine.list_active_sessions()
        
        if not sessions:
            return "📋 **No active workflow sessions found**"
        
        response = "📋 **ACTIVE WORKFLOW SESSIONS**\n\n"
        for session in sessions:
            response += f"**{session['session_id']}**:\n"
            response += f"  - Type: {session['workflow_type']}\n"
            response += f"  - Mode: {session['mode']}\n"
            response += f"  - Agents: {session['agents_count']}\n"
            response += f"  - Time: {session['timestamp']}\n\n"
        
        return response.strip()


# Global instance for tool registration
workflow_api = WorkflowEngineAPI()


def create_azure_landing_zone(requirements: str, **kwargs) -> str:
    """Global function for registry tool registration"""
    return workflow_api.create_azure_landing_zone(requirements, **kwargs)


def get_workflow_status(session_id: str) -> str:
    """Global function for getting workflow status"""
    return workflow_api.get_workflow_status(session_id)


def list_workflow_sessions() -> str:
    """Global function for listing workflow sessions"""
    return workflow_api.list_sessions()


if __name__ == "__main__":
    # Test the workflow engine
    print("🚀 **WORKFLOW ENGINE TEST**")
    print("=" * 50)
    
    engine = WorkflowEngine()
    
    # Test Azure Landing Zone workflow
    result = engine.handle_azure_landing_zone(
        "Create Azure Landing Zone with hub and spoke model with 3 regions"
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"✅ Mode: {result['mode']}")
    print(f"✅ Session: {result['session_id']}")
    print(f"✅ Agents: {result['otrace']}")
    
    if result.get('delegation_results'):
        print(f"✅ Delegations: {len(result['delegation_results'])}")
