#!/usr/bin/env python3
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

"""
Test runner for Cloud Infrastructure Provider tests.

This script runs all tests for the cloud infrastructure provider coded tools,
including unit tests for individual components and integration tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --integration     # Run only integration tests
    python run_tests.py --verbose         # Run with verbose output
    python run_tests.py --coverage        # Run with coverage reporting
"""

import argparse
import os
import sys
import unittest
import subprocess
from pathlib import Path

# Add the project root to Python path so we can import coded_tools
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_command(command, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr if capture_output else str(e)}")
        return None


def discover_tests(test_dir, pattern="test_*.py"):
    """Discover test modules in the given directory."""
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    return suite


def run_tests(test_suite, verbosity=1):
    """Run the test suite with the specified verbosity level."""
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(test_suite)
    return result


def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Cloud Infrastructure Provider tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --integration     # Run only integration tests
    python run_tests.py --verbose         # Run with verbose output
    python run_tests.py --coverage        # Run with coverage reporting
        """
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests (individual component tests)"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests (end-to-end workflow tests)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests with verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting (requires coverage.py)"
    )
    
    parser.add_argument(
        "--module",
        type=str,
        help="Run tests for a specific module (e.g., design_document_creator)"
    )
    
    args = parser.parse_args()
    
    # Determine the test directory (current directory of this script)
    test_dir = Path(__file__).parent
    print(f"Running tests from: {test_dir}")
    print(f"Project root: {PROJECT_ROOT}")
    
    # Check if we can import the modules before running tests
    try:
        import coded_tools.cloud_infrastructure_provider
        print("✅ Successfully imported coded_tools module")
    except ImportError as e:
        print(f"❌ Failed to import coded_tools module: {e}")
        print("Make sure you're running this from the project root or the coded_tools directory exists")
        sys.exit(1)
    
    # Set verbosity level
    verbosity = 2 if args.verbose else 1
    
    # Determine which tests to run
    if args.unit and args.integration:
        print("Error: Cannot specify both --unit and --integration. Choose one or neither (for all tests).")
        sys.exit(1)
    
    if args.module:
        # Run tests for a specific module
        test_pattern = f"test_{args.module}.py"
        print(f"Running tests for module: {args.module}")
    elif args.unit:
        # Run only unit tests (exclude integration tests)
        test_pattern = "test_*.py"
        print("Running unit tests only...")
    elif args.integration:
        # Run only integration tests
        test_pattern = "test_integration.py"
        print("Running integration tests only...")
    else:
        # Run all tests
        test_pattern = "test_*.py"
        print("Running all tests...")
    
    # Check if coverage is requested and available
    coverage_cmd = None
    if args.coverage:
        try:
            coverage_version = run_command("coverage --version")
            if coverage_version:
                print(f"Coverage.py detected: {coverage_version.strip()}")
                coverage_cmd = "coverage"
            else:
                print("Warning: coverage.py not found. Install with: pip install coverage")
        except:
            print("Warning: coverage.py not available. Install with: pip install coverage")
    
    # Discover and run tests
    try:
        if args.unit:
            # Discover all test files except integration
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            for test_file in test_dir.glob("test_*.py"):
                if "integration" not in test_file.name:
                    module_name = test_file.stem
                    spec = unittest.util.spec_from_file_location(module_name, test_file)
                    module = unittest.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    suite.addTests(loader.loadTestsFromModule(module))
        else:
            # Use standard discovery
            suite = discover_tests(test_dir, test_pattern)
        
        if suite.countTestCases() == 0:
            print(f"No tests found matching pattern: {test_pattern}")
            sys.exit(1)
        
        print(f"Found {suite.countTestCases()} test cases")
        
        # Run tests with or without coverage
        if coverage_cmd:
            print("Running tests with coverage...")
            
            # Start coverage
            run_command(f"{coverage_cmd} erase", capture_output=False)
            
            # Run tests under coverage
            result = run_tests(suite, verbosity)
            
            # Generate coverage report
            print("\nGenerating coverage report...")
            run_command(f"{coverage_cmd} report", capture_output=False)
            run_command(f"{coverage_cmd} html", capture_output=False)
            print("HTML coverage report generated in htmlcov/")
            
        else:
            # Run tests normally
            result = run_tests(suite, verbosity)
        
        # Print summary
        print(f"\nTest Results Summary:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.failures:
            print(f"\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
        
        # Exit with appropriate code
        if result.wasSuccessful():
            print(f"\n✅ All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
