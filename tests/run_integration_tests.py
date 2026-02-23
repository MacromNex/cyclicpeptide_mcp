#!/usr/bin/env python3
"""Automated integration test runner for Cyclic Peptide MCP server."""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MCPTestRunner:
    def __init__(self, server_path: str, env_path: str):
        self.server_path = Path(server_path).resolve()
        self.env_path = Path(env_path).resolve()
        self.python_path = self.env_path / "bin" / "python"
        self.results = {
            "test_date": datetime.now().isoformat(),
            "server_path": str(self.server_path),
            "env_path": str(self.env_path),
            "tests": {},
            "issues": [],
            "summary": {},
            "test_data": {}
        }

    def run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run a command and capture output."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }

    def test_server_startup(self) -> bool:
        """Test that server starts without errors."""
        print("Testing server startup...")
        cmd = [str(self.python_path), "-c", "from src.server import mcp; print('Server import OK')"]
        result = self.run_command(cmd)

        self.results["tests"]["server_startup"] = {
            "status": "passed" if result["success"] else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "command": " ".join(cmd)
        }
        return result["success"]

    def test_rdkit_import(self) -> bool:
        """Test that RDKit is available."""
        print("Testing RDKit import...")
        cmd = [str(self.python_path), "-c", "from rdkit import Chem; print('RDKit OK')"]
        result = self.run_command(cmd)

        self.results["tests"]["rdkit_import"] = {
            "status": "passed" if result["success"] else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "command": " ".join(cmd)
        }
        return result["success"]

    def test_tool_count(self) -> bool:
        """Test that expected number of tools are available."""
        print("Testing tool count...")
        cmd = [str(self.python_path), "-c", "import sys; sys.path.insert(0, 'src'); exec(open('src/server.py').read()); print('Tools loaded')"]
        result = self.run_command(cmd)

        # Count tools by searching for @mcp.tool() decorators
        try:
            with open(self.server_path, 'r') as f:
                content = f.read()
                tool_count = content.count('@mcp.tool()')
        except Exception as e:
            tool_count = 0

        self.results["tests"]["tool_count"] = {
            "status": "passed" if result["success"] else "failed",
            "expected_tools": 13,
            "found_tools": tool_count,
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "tools_match": tool_count == 13
        }
        return result["success"] and tool_count == 13

    def test_fastmcp_dev(self) -> bool:
        """Test that server starts in dev mode."""
        print("Testing FastMCP dev mode...")
        fastmcp_path = self.env_path / "bin" / "fastmcp"

        # Use timeout to test server startup
        cmd = ["timeout", "5", str(fastmcp_path), "dev", str(self.server_path)]
        result = self.run_command(cmd, timeout=10)

        # Exit code 124 means timeout (expected), any other error is bad
        success = result["returncode"] in [124, 0] or "MCP inspector" in result.get("stderr", "")

        self.results["tests"]["fastmcp_dev"] = {
            "status": "passed" if success else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "returncode": result["returncode"],
            "note": "Exit code 124 (timeout) is expected"
        }
        return success

    def test_claude_mcp_connection(self) -> bool:
        """Test that Claude CLI can connect to the server."""
        print("Testing Claude CLI MCP connection...")
        cmd = ["claude", "mcp", "list"]
        result = self.run_command(cmd)

        success = result["success"] and "cycpep-tools" in result.get("stdout", "")

        self.results["tests"]["claude_mcp_connection"] = {
            "status": "passed" if success else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "found_server": "cycpep-tools" in result.get("stdout", "")
        }
        return success

    def test_sync_tool_execution(self) -> bool:
        """Test direct execution of sync tools."""
        print("Testing sync tool execution...")

        # Test property calculation with valid SMILES
        cmd = [
            str(self.python_path), "-c",
            """
import sys
sys.path.insert(0, 'src')
from server import calculate_cyclic_peptide_properties
result = calculate_cyclic_peptide_properties(smiles='CC(=O)NC1CCCC1C(=O)O')
print(f'Status: {result.get("status", "unknown")}')
if 'molecular_weight' in str(result):
    print('Properties calculated successfully')
else:
    print('Properties not found in result')
"""
        ]

        result = self.run_command(cmd, timeout=60)  # Longer timeout for calculations

        success = result["success"] and "Properties calculated successfully" in result.get("stdout", "")

        self.results["tests"]["sync_tool_execution"] = {
            "status": "passed" if success else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "test_smiles": "CC(=O)NC1CCCC1C(=O)O"
        }
        return success

    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs."""
        print("Testing error handling...")

        cmd = [
            str(self.python_path), "-c",
            """
import sys
sys.path.insert(0, 'src')
from server import calculate_cyclic_peptide_properties
result = calculate_cyclic_peptide_properties(smiles='invalid_smiles_123')
print(f'Status: {result.get("status", "unknown")}')
if result.get("status") == "error":
    print('Error handling works correctly')
else:
    print('Error handling failed')
"""
        ]

        result = self.run_command(cmd)

        success = result["success"] and "Error handling works correctly" in result.get("stdout", "")

        self.results["tests"]["error_handling"] = {
            "status": "passed" if success else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "test_invalid_smiles": "invalid_smiles_123"
        }
        return success

    def test_job_manager(self) -> bool:
        """Test job management functionality."""
        print("Testing job manager...")

        cmd = [
            str(self.python_path), "-c",
            """
import sys
sys.path.insert(0, 'src')
from server import list_jobs
result = list_jobs()
print(f'Job list result: {type(result)}')
if isinstance(result, dict):
    print('Job manager functional')
else:
    print('Job manager issue')
"""
        ]

        result = self.run_command(cmd)

        success = result["success"] and "Job manager functional" in result.get("stdout", "")

        self.results["tests"]["job_manager"] = {
            "status": "passed" if success else "failed",
            "output": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
        return success

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate report."""
        print(f"Starting integration tests for {self.server_path}")
        print(f"Using Python environment: {self.python_path}")
        print("=" * 60)

        # Track test results
        test_methods = [
            self.test_server_startup,
            self.test_rdkit_import,
            self.test_tool_count,
            self.test_fastmcp_dev,
            self.test_claude_mcp_connection,
            self.test_sync_tool_execution,
            self.test_error_handling,
            self.test_job_manager
        ]

        passed_tests = 0
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
                    print("✓ PASSED")
                else:
                    print("✗ FAILED")
            except Exception as e:
                print(f"✗ ERROR: {e}")
            print("-" * 40)

        # Generate summary
        total_tests = len(test_methods)
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A",
            "all_tests_passed": passed_tests == total_tests
        }

        # Add test environment info
        self.results["test_data"] = {
            "valid_smiles": [
                "CC(=O)NC1CCCC1C(=O)O",
                "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O"
            ],
            "invalid_smiles": ["invalid_smiles_123", "not_a_smiles"],
            "test_sequences": ["GRGDSP", "RGDFV", "YIGSR"],
            "invalid_sequences": ["XYZABC123"]
        }

        return self.results

    def save_report(self, output_path: str = "reports/integration_test_results.json"):
        """Save test results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Test results saved to: {output_file}")

    def print_summary(self):
        """Print test summary to console."""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']}")
        print(f"Overall: {'✓ ALL TESTS PASSED' if summary['all_tests_passed'] else '✗ SOME TESTS FAILED'}")

        if summary['failed'] > 0:
            print("\nFailed Tests:")
            for test_name, test_result in self.results["tests"].items():
                if test_result.get("status") == "failed":
                    print(f"  ✗ {test_name}: {test_result.get('error', 'Unknown error')}")


def main():
    """Main test runner function."""
    if len(sys.argv) < 3:
        print("Usage: python run_integration_tests.py <server_path> <env_path>")
        print("Example: python run_integration_tests.py src/server.py ./env")
        sys.exit(1)

    server_path = sys.argv[1]
    env_path = sys.argv[2]

    runner = MCPTestRunner(server_path, env_path)
    runner.run_all_tests()
    runner.print_summary()
    runner.save_report()

    # Exit with error code if tests failed
    if not runner.results["summary"]["all_tests_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()