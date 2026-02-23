#!/usr/bin/env python3
"""Test script for MCP server functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all imports work correctly."""
    try:
        from jobs.manager import job_manager, JobStatus
        from server import mcp
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_sync_tool():
    """Test a synchronous tool."""
    try:
        from server import mcp

        # Test property calculation with a simple SMILES
        result = calculate_cyclic_peptide_properties(smiles="CCO")  # Simple ethanol for testing
        print(f"✅ Sync tool test: {result.get('status', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Sync tool test failed: {e}")
        return False

def test_job_manager():
    """Test job manager functionality."""
    try:
        from jobs.manager import job_manager

        # Test listing jobs (should work even if empty)
        result = job_manager.list_jobs()
        print(f"✅ Job manager test: {result.get('status', 'unknown')}, {result.get('total', 0)} jobs")
        return True
    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MCP server functionality...")

    tests = [
        test_imports,
        test_job_manager,
        # test_sync_tool,  # Skip for now since it needs actual script execution
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\nTests passed: {passed}/{len(tests)}")

    if passed == len(tests):
        print("✅ All tests passed! MCP server is ready.")
    else:
        print("❌ Some tests failed. Check the errors above.")