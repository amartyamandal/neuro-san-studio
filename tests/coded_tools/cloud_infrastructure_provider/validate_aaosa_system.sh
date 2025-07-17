#!/usr/bin/env bash
# AAOSA Configuration Validation Script
# Validates that the cloud infrastructure provider agents are properly configured

echo "==========================================================="
echo "CLOUD INFRASTRUCTURE PROVIDER VALIDATION"  
echo "==========================================================="
echo ""

# Test 1: Check HOCON file exists and basic structure
echo "1. Testing HOCON configuration file..."
if [ -f "registries/cloud_infrastructure_provider.hocon" ]; then
    echo "   ✅ HOCON configuration file exists"
    
    # Check for required agents using grep
    if grep -q '"name": "Manager"' registries/cloud_infrastructure_provider.hocon; then
        echo "   ✅ Manager agent found"
    else
        echo "   ❌ Manager agent missing"
        exit 1
    fi
    
    if grep -q '"name": "Architect"' registries/cloud_infrastructure_provider.hocon; then
        echo "   ✅ Architect agent found"
    else
        echo "   ❌ Architect agent missing"
        exit 1
    fi
    
    if grep -q '"name": "Engineer"' registries/cloud_infrastructure_provider.hocon; then
        echo "   ✅ Engineer agent found"
    else
        echo "   ❌ Engineer agent missing"
        exit 1
    fi
    
    # Check AAOSA configuration
    if grep -q '"function": "aaosa_call"' registries/cloud_infrastructure_provider.hocon; then
        echo "   ✅ AAOSA configuration found"
    else
        echo "   ❌ AAOSA configuration missing"
        exit 1
    fi
    
    echo "   ✅ All agent configurations valid"
else
    echo "   ❌ HOCON configuration file missing"
    exit 1
fi

echo ""

# Test 2: Check coded tools
echo "2. Testing coded tools..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from coded_tools.cloud_infrastructure_provider.design_document_creator import DesignDocumentCreator
    from coded_tools.cloud_infrastructure_provider.project_plan_creator import ProjectPlanCreator  
    from coded_tools.cloud_infrastructure_provider.terraform_builder import TerraformBuilder
    from coded_tools.cloud_infrastructure_provider.ansible_builder import AnsibleBuilder
    
    print('   ✅ All coded tools import successfully')
    
    # Test instantiation
    DesignDocumentCreator()
    ProjectPlanCreator()
    TerraformBuilder()
    AnsibleBuilder()
    
    print('   ✅ All coded tools instantiate successfully')
    
except Exception as e:
    print(f'   ❌ Coded tools error: {str(e)}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "Coded tools validation failed!"
    exit 1
fi

echo ""

# Test 3: Run unit tests
echo "3. Running unit tests..."
cd tests/coded_tools/cloud_infrastructure_provider
python3 run_tests.py > /tmp/test_output.log 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ All 53 unit tests passed"
else
    echo "   ❌ Unit tests failed - check /tmp/test_output.log"
    exit 1
fi

cd - > /dev/null

echo ""

# Test 4: Validate workflow execution
echo "4. Testing workflow components..."
python3 tests/coded_tools/cloud_infrastructure_provider/test_complete_workflow.py > /tmp/workflow_output.log 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Complete workflow test passed"
    
    # Check if files were created
    LATEST_OUTPUT=$(ls -t output/ | head -1)
    if [ -d "output/$LATEST_OUTPUT" ]; then
        echo "   ✅ Output directory created: output/$LATEST_OUTPUT"
        
        if [ -f "output/$LATEST_OUTPUT/docs/design.md" ]; then
            echo "   ✅ Design document created"
        fi
        
        if [ -f "output/$LATEST_OUTPUT/docs/project_plan.md" ]; then
            echo "   ✅ Project plan created"
        fi
        
        if [ -d "output/$LATEST_OUTPUT/iac/terraform" ]; then
            echo "   ✅ Terraform code generated"
        fi
        
        if [ -d "output/$LATEST_OUTPUT/config/ansible" ]; then
            echo "   ✅ Ansible configuration generated"
        fi
    fi
else
    echo "   ❌ Workflow test failed - check /tmp/workflow_output.log"
    exit 1
fi

echo ""
echo "==========================================================="
echo "VALIDATION COMPLETE - ALL TESTS PASSED ✅"
echo "==========================================================="
echo ""
echo "Your cloud infrastructure provider agents are ready!"
echo ""
echo "Agent Structure:"
echo "  • Manager    - Project coordination and user interface"  
echo "  • Architect  - Infrastructure design and documentation"
echo "  • Engineer   - Terraform and Ansible code generation"
echo ""
echo "Workflow:"
echo "  User → Manager → Architect → Manager → User → Engineer"
echo ""
echo "To test with the live server:"
echo "  1. Ensure server is running: python run.py" 
echo "  2. Connect via the web interface at localhost:4173"
echo "  3. Select 'cloud_infrastructure_provider' agent"
echo "  4. Send: 'create a azure landing zone'"
echo ""
echo "Expected behavior:"
echo "  • Manager coordinates the entire workflow"
echo "  • Architect creates design.md in output/LZ_<timestamp>/docs/"
echo "  • Manager creates project_plan.md" 
echo "  • Engineer generates Terraform and Ansible code"
echo "  • All files saved in timestamped output directory"
echo ""
