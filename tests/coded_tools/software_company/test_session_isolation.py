#!/usr/bin/env python3
"""
Test script to validate session-based isolation in the software company network.
This simulates multiple concurrent sessions to ensure no file conflicts.
"""

import json
import os
import shutil
import sys
from typing import Dict, Any

# Add the project root to the path (going up 3 levels from tests/coded_tools/software_company)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from coded_tools.cloud_landing_zone_provider.document_manager import DocumentManager
from coded_tools.cloud_landing_zone_provider.code_repository import CodeRepository
from coded_tools.cloud_landing_zone_provider.task_manager import TaskManager


def test_session_isolation():
    """Test that multiple sessions create isolated outputs"""
    
    # Clean up any existing test outputs
    if os.path.exists("output/software_company"):
        shutil.rmtree("output/software_company")
    
    print("🧪 Testing Session-Based Isolation...")
    print("=" * 60)
    
    # Create test scenarios for different sessions
    sessions = [
        {
            "session_id": "session_alpha",
            "project_name": "azure_migration",
            "scenario": "Azure Cloud Migration Project"
        },
        {
            "session_id": "session_beta", 
            "project_name": "ecommerce_platform",
            "scenario": "E-commerce Platform Development"
        },
        {
            "session_id": "session_gamma",
            "project_name": "ai_chatbot",
            "scenario": "AI Chatbot Implementation"
        }
    ]
    
    all_paths = []
    
    for session in sessions:
        print(f"\n🎯 Testing {session['scenario']}")
        print(f"   Session: {session['session_id']}")
        print(f"   Project: {session['project_name']}")
        
        # Create sly_data context for this session
        sly_data = {
            "session_id": session["session_id"],
            "project_name": session["project_name"],
            "scenario": session["scenario"]
        }
        
        # Test DocumentManager
        doc_manager = DocumentManager()
        doc_result = doc_manager.invoke({
            "action": "create_document",
            "doc_type": "technical_specification",
            "title": f"{session['scenario']} - Technical Specs",
            "content": f"This is the technical specification for {session['scenario']}",
            "metadata": {
                "author": "Test Engineer",
                "project": session["project_name"]
            }
        }, sly_data)
        
        if doc_result.get("file_path"):
            all_paths.append(doc_result["file_path"])
            print(f"   ✅ Document: {doc_result['file_path']}")
        
        # Test CodeRepository
        code_repo = CodeRepository()
        code_result = code_repo.invoke({
            "action": "create_file",
            "filename": "main.py",
            "content": f"# {session['scenario']} Main Application\nprint('Hello from {session['project_name']}')",
            "language": "python",
            "metadata": {
                "component": "main_application",
                "version": "1.0.0"
            }
        }, sly_data)
        
        if code_result.get("file_path"):
            all_paths.append(code_result["file_path"])
            print(f"   ✅ Code File: {code_result['file_path']}")
        
        # Test TaskManager
        task_manager = TaskManager()
        task_result = task_manager.invoke({
            "action": "create",
            "title": f"{session['scenario']} - Implementation Task",
            "description": f"Main implementation task for {session['scenario']}",
            "task_type": "development",
            "priority": "high",
            "estimated_effort": 40,
            "assigned_to": "Development Team",
            "project_type": "enterprise"
        }, sly_data)
        
        if task_result.get("artifact_paths"):
            all_paths.extend(task_result["artifact_paths"])
            print(f"   ✅ Task Artifacts: {len(task_result['artifact_paths'])} files")
    
    print(f"\n📊 Session Isolation Test Results:")
    print(f"   Total files created: {len(all_paths)}")
    
    # Verify directory structure
    print(f"\n📁 Directory Structure Verification:")
    for session in sessions:
        session_dir = f"output/software_company/{session['session_id']}/{session['project_name']}"
        if os.path.exists(session_dir):
            print(f"   ✅ {session_dir}")
            
            # Check subdirectories
            subdirs = ["documents", "scripts", "project_management"]
            for subdir in subdirs:
                subdir_path = os.path.join(session_dir, subdir)
                if os.path.exists(subdir_path):
                    file_count = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
                    print(f"      ✅ {subdir}/ ({file_count} files)")
                else:
                    print(f"      ❌ {subdir}/ (missing)")
        else:
            print(f"   ❌ {session_dir} (missing)")
    
    # Verify no file conflicts
    print(f"\n🔍 File Conflict Check:")
    unique_paths = set(all_paths)
    if len(unique_paths) == len(all_paths):
        print(f"   ✅ No file conflicts detected ({len(all_paths)} unique paths)")
    else:
        print(f"   ❌ File conflicts detected! {len(all_paths)} total vs {len(unique_paths)} unique")
        
        # Show duplicates
        from collections import Counter
        path_counts = Counter(all_paths)
        duplicates = [path for path, count in path_counts.items() if count > 1]
        for dup in duplicates:
            print(f"      ⚠️ Duplicate: {dup}")
    
    # Show sample files
    print(f"\n📋 Sample File Contents:")
    for i, path in enumerate(all_paths[:3]):  # Show first 3 files
        if os.path.exists(path):
            print(f"\n   File {i+1}: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]  # First 200 chars
                    print(f"   Content: {content}...")
            except:
                print(f"   Content: [Binary or unreadable file]")
    
    return len(all_paths), len(unique_paths) == len(all_paths)


def test_concurrent_scenarios():
    """Test running the same scenario with different session IDs"""
    print(f"\n🔄 Testing Concurrent Scenario Execution...")
    print("=" * 60)
    
    # Same project type, different sessions
    concurrent_sessions = [
        {"session_id": "morning_team", "project_name": "web_portal"},
        {"session_id": "afternoon_team", "project_name": "web_portal"}, 
        {"session_id": "evening_team", "project_name": "web_portal"}
    ]
    
    paths_by_session = {}
    
    for session in concurrent_sessions:
        print(f"\n👥 Team: {session['session_id']}")
        
        sly_data = {
            "session_id": session["session_id"],
            "project_name": session["project_name"]
        }
        
        # Create identical tasks
        task_manager = TaskManager()
        result = task_manager.invoke({
            "action": "create",
            "title": "Web Portal Development",
            "description": "Build customer web portal",
            "task_type": "development",
            "priority": "high"
        }, sly_data)
        
        paths_by_session[session["session_id"]] = result.get("artifact_paths", [])
        print(f"   Files: {len(paths_by_session[session['session_id']])}")
    
    # Verify each team has their own files
    all_concurrent_paths = []
    for session_id, paths in paths_by_session.items():
        all_concurrent_paths.extend(paths)
        print(f"   {session_id}: {paths[0] if paths else 'No files'}")
    
    unique_concurrent = set(all_concurrent_paths)
    conflict_free = len(unique_concurrent) == len(all_concurrent_paths)
    
    print(f"\n🎯 Concurrent Test Result:")
    print(f"   Total files: {len(all_concurrent_paths)}")
    print(f"   Unique files: {len(unique_concurrent)}")
    print(f"   Conflict-free: {'✅ Yes' if conflict_free else '❌ No'}")
    
    return conflict_free


if __name__ == "__main__":
    print("🚀 Neuro-San Studio: Session Isolation Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Session isolation
        total_files, isolation_success = test_session_isolation()
        
        # Test 2: Concurrent scenarios
        concurrent_success = test_concurrent_scenarios()
        
        # Final results
        print(f"\n🏆 FINAL TEST RESULTS:")
        print("=" * 40)
        print(f"Session Isolation: {'✅ PASS' if isolation_success else '❌ FAIL'}")
        print(f"Concurrent Safety: {'✅ PASS' if concurrent_success else '❌ FAIL'}")
        print(f"Total Files Generated: {total_files}")
        
        if isolation_success and concurrent_success:
            print(f"\n🎉 Session-based isolation is working perfectly!")
            print(f"   Multiple teams can now work simultaneously without conflicts.")
            print(f"   Each session creates its own organized output structure.")
        else:
            print(f"\n⚠️ Session isolation needs attention!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
