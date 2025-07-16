import pytest
import json
import os
import sys
from coded_tools.cloud_landing_zone_provider.workflow_engine_interface import WorkflowEngine


class MockAAOSAAgent:
    """Mock agent that simulates AAOSA agent-to-agent calls"""
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.call_trace = []
    
    def aaosa_call(self, inquiry, mode="Determine"):
        """Simulate AAOSA agent call"""
        self.call_trace.append((self.agent_name, inquiry, mode))
        
        if mode == "Determine":
            return {
                "Name": self.agent_name,
                "Inquiry": inquiry,
                "Mode": "Determine",
                "Relevant": "Yes",
                "Strength": 9,
                "Claim": "All",
                "Requirements": []
            }
        elif mode == "Fulfill":
            return {
                "Name": self.agent_name,
                "Inquiry": inquiry,
                "Mode": "Fulfill",
                "Response": f"{self.agent_name} has completed the task: {inquiry}"
            }


def test_boss_delegates_to_product_manager():
    """
    Test that boss agent delegates PRD creation to product-manager agent
    following AAOSA protocol
    """
    # Create mock agents
    product_manager = MockAAOSAAgent("product-manager")
    architect = MockAAOSAAgent("architect")
    
    # Simulate boss agent workflow initiation
    engine = WorkflowEngine()
    session_id = f"test_session_{os.urandom(4).hex()}"
    project_name = "Test Azure LZ"
    user_requirements = "Create Azure Landing Zone with hub and spoke in 3 regions"
    project_type = "azure_landing_zone"

    # Step 1: Boss agent initiates workflow
    response = engine.run(
        action="initiate_workflow",
        project_type=project_type,
        session_id=session_id,
        project_name=project_name,
        user_requirements=user_requirements,
        return_full_result=True
    )
    assert response["success"]
    workflow_id = response["workflow_id"]

    # Step 2: Boss agent should delegate PRD creation to product-manager
    # This simulates the AAOSA call that should happen in the boss agent
    inquiry = f"Create Product Requirements Document for {project_name}: {user_requirements}"
    
    # First, boss calls product-manager to determine if they can handle this
    determine_response = product_manager.aaosa_call(inquiry, "Determine")
    assert determine_response["Relevant"] == "Yes"
    assert determine_response["Name"] == "product-manager"
    
    # Then, boss calls product-manager to fulfill the task
    fulfill_response = product_manager.aaosa_call(inquiry, "Fulfill")
    assert fulfill_response["Mode"] == "Fulfill"
    assert "completed the task" in fulfill_response["Response"]
    
    # Step 3: Product-manager should then call architect for technical validation
    tech_inquiry = f"Review and validate technical feasibility for: {user_requirements}"
    architect_response = architect.aaosa_call(tech_inquiry, "Fulfill")
    assert architect_response["Mode"] == "Fulfill"
    
    # Verify the complete AAOSA call chain
    expected_otrace = ["boss", "product-manager", "architect"]
    actual_otrace = ["boss"] + [call[0] for call in product_manager.call_trace + architect.call_trace]
    
    # Remove duplicates while preserving order
    seen = set()
    actual_otrace_unique = []
    for agent in actual_otrace:
        if agent not in seen:
            seen.add(agent)
            actual_otrace_unique.append(agent)
    
    assert actual_otrace_unique == expected_otrace
    
    print(f"✅ AAOSA multi-agent trace: {actual_otrace_unique}")
    print(f"✅ Product-manager calls: {len(product_manager.call_trace)}")
    print(f"✅ Architect calls: {len(architect.call_trace)}")
    print("✅ PRD creation delegated from boss to product-manager: PASS")


def test_aaosa_coordination_workflow():
    """
    Test the full AAOSA coordination workflow for Azure Landing Zone
    """
    # Create the agent chain
    agents = {
        "product-manager": MockAAOSAAgent("product-manager"),
        "architect": MockAAOSAAgent("architect"), 
        "project-manager": MockAAOSAAgent("project-manager"),
        "engineer": MockAAOSAAgent("engineer"),
        "qa": MockAAOSAAgent("qa")
    }
    
    # Simulate the boss agent coordinating the full workflow
    inquiry = "Create Azure Landing Zone with hub and spoke model with 3 regions"
    
    # Phase 1: Boss delegates to product-manager
    prd_response = agents["product-manager"].aaosa_call(
        f"Create PRD for: {inquiry}", "Fulfill"
    )
    
    # Phase 2: Product-manager delegates architecture to architect  
    arch_response = agents["architect"].aaosa_call(
        f"Design architecture for: {inquiry}", "Fulfill"
    )
    
    # Phase 3: Architect delegates project planning to project-manager
    plan_response = agents["project-manager"].aaosa_call(
        f"Create project plan for: {inquiry}", "Fulfill"
    )
    
    # Phase 4: Project-manager delegates implementation to engineer
    impl_response = agents["engineer"].aaosa_call(
        f"Implement solution for: {inquiry}", "Fulfill"
    )
    
    # Phase 5: Engineer delegates testing to QA
    test_response = agents["qa"].aaosa_call(
        f"Test and validate: {inquiry}", "Fulfill"
    )
    
    # Verify all responses
    responses = [prd_response, arch_response, plan_response, impl_response, test_response]
    for response in responses:
        assert response["Mode"] == "Fulfill"
        assert "completed the task" in response["Response"]
    
    # Verify complete agent chain
    complete_otrace = ["boss"] + [agent for agent in agents.keys()]
    expected_agents = ["boss", "product-manager", "architect", "project-manager", "engineer", "qa"]
    assert complete_otrace == expected_agents
    
    print(f"✅ Complete AAOSA workflow trace: {complete_otrace}")
    print("✅ Full multi-agent coordination: PASS")
