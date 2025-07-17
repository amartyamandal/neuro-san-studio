#!/usr/bin/env python3
"""
Test script to validate memory integration in cloud infrastructure provider agents.
Tests the integration of CommitToMemory and RecallMemory tools.
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

def test_memory_tools_integration():
    """Test that memory tools can be imported and work with cloud infrastructure provider."""
    
    print("Testing memory tools integration...")
    
    try:
        # Test CommitToMemory import
        from coded_tools.kwik_agents.commit_to_memory import CommitToMemory
        commit_tool = CommitToMemory()
        print("✅ CommitToMemory imported and instantiated successfully")
        
        # Test RecallMemory import  
        from coded_tools.kwik_agents.recall_memory import RecallMemory
        recall_tool = RecallMemory()
        print("✅ RecallMemory imported and instantiated successfully")
        
        # Test memory operations
        test_sly_data = {}
        test_topic = "test_project_requirements"
        test_content = "Azure landing zone with App Service, SQL, and Storage for 500 users"
        
        # Test commit to memory
        commit_args = {
            "topic": test_topic,
            "new_fact": test_content
        }
        
        result = commit_tool.invoke(commit_args, test_sly_data)
        print(f"✅ CommitToMemory result: {result[:100]}...")
        
        # Test recall from memory
        recall_args = {
            "topic": test_topic
        }
        
        recall_result = recall_tool.invoke(recall_args, test_sly_data)
        print(f"✅ RecallMemory result: {recall_result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory tools integration test failed: {e}")
        return False

def test_hocon_configuration():
    """Test that HOCON configuration includes memory tools correctly."""
    
    print("\nTesting HOCON configuration with memory tools...")
    
    try:
        hocon_path = os.path.join(os.path.dirname(__file__), '../../../registries/cloud_infrastructure_provider.hocon')
        
        with open(hocon_path, 'r') as f:
            content = f.read()
        
        # Check for memory tool configurations
        memory_checks = [
            'CommitToMemory',
            'RecallMemory',
            'coded_tools.kwik_agents.commit_to_memory.CommitToMemory',
            'coded_tools.kwik_agents.recall_memory.RecallMemory',
            'Store project information',
            'Retrieve stored project information'
        ]
        
        for check in memory_checks:
            if check in content:
                print(f"✅ Found: {check}")
            else:
                print(f"❌ Missing: {check}")
                return False
        
        # Check that all agents have memory tools
        agent_memory_checks = [
            '"tools": ["Architect", "Engineer", "ProjectPlanCreator", "CommitToMemory", "RecallMemory"]',
            '"tools": ["DesignDocumentCreator", "CommitToMemory", "RecallMemory"]',
            '"tools": ["TerraformBuilder", "AnsibleBuilder", "CommitToMemory", "RecallMemory"]'
        ]
        
        for check in agent_memory_checks:
            if check in content:
                print(f"✅ Found agent memory tools: {check.split('[')[1].split(']')[0]}")
            else:
                print(f"❌ Missing agent memory tools configuration")
                return False
        
        print("✅ HOCON configuration includes memory tools correctly")
        return True
        
    except Exception as e:
        print(f"❌ HOCON configuration test failed: {e}")
        return False

def test_memory_topics():
    """Test the recommended memory topics for infrastructure projects."""
    
    print("\nTesting memory topics structure...")
    
    recommended_topics = [
        "session_07162025140200",  # Session state
        "project_requirements",    # User requirements
        "design_decisions",        # Architectural choices
        "project_context",         # Overall project info
        "implementation_details",  # Technical implementation
        "deployment_notes",        # Deployment information
        "technical_decisions"      # Engineering decisions
    ]
    
    try:
        from coded_tools.kwik_agents.commit_to_memory import CommitToMemory
        commit_tool = CommitToMemory()
        
        test_sly_data = {}
        
        for topic in recommended_topics:
            test_content = f"Test content for {topic} - timestamp: {datetime.now().isoformat()}"
            args = {
                "topic": topic,
                "new_fact": test_content
            }
            
            result = commit_tool.invoke(args, test_sly_data)
            print(f"✅ Successfully stored memory for topic: {topic}")
        
        print("✅ All recommended memory topics work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Memory topics test failed: {e}")
        return False

def main():
    """Run all memory integration tests."""
    
    print("=" * 70)
    print("CLOUD INFRASTRUCTURE PROVIDER MEMORY INTEGRATION TESTS")
    print("=" * 70)
    
    tests = [
        test_memory_tools_integration,
        test_hocon_configuration,
        test_memory_topics
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✅ ALL MEMORY INTEGRATION TESTS PASSED")
        print("\nMemory-enhanced cloud infrastructure provider is ready!")
        print("\nMemory Features:")
        print("• Project requirements and context persistence")
        print("• Design decisions and architectural choices tracking") 
        print("• Implementation details and deployment notes storage")
        print("• Session state management across workflow steps")
        print("• Long-term project knowledge retention")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failing tests above.")
    print("=" * 70)

if __name__ == "__main__":
    main()
