#!/usr/bin/env python
"""
Test runner script for Swim Data Project.

This script provides a convenient way to run tests with different configurations.
It also supports generating coverage reports.
"""

import os
import sys
import argparse
import subprocess


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for Swim Data Project")
    
    parser.add_argument(
        "--unit", action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--slow", action="store_true",
        help="Include slow tests"
    )
    parser.add_argument(
        "--selenium", action="store_true",
        help="Include tests that require a real browser"
    )
    parser.add_argument(
        "--coverage", action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--html", action="store_true",
        help="Generate HTML test report"
    )
    parser.add_argument(
        "--source", type=str, default=None,
        help="Run tests for a specific scraper source (e.g., usa_swimming)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()


def build_pytest_command(args):
    """Build the pytest command based on arguments."""
    command = ["python", "-m", "pytest"]
    
    # Test selection
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.source:
        markers.append(args.source)
    
    # Combine markers
    if markers:
        command.append("-m")
        command.append(" and ".join(markers))
    
    # Exclude markers
    exclude_markers = []
    if not args.slow:
        exclude_markers.append("slow")
    if not args.selenium:
        exclude_markers.append("selenium")
    
    if exclude_markers:
        command.append("-k")
        command.append(" and ".join([f"not {marker}" for marker in exclude_markers]))
    
    # Coverage
    if args.coverage:
        command.append("--cov=SwimDataProject")
        command.append("--cov-report=term")
        if args.html:
            command.append("--cov-report=html:coverage_html")
    
    # HTML report
    if args.html:
        command.append("--html=test_report.html")
        command.append("--self-contained-html")
    
    # Verbosity
    if args.verbose:
        command.append("-v")
    
    return command


def main():
    """Main function to run tests."""
    args = parse_args()
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Build the pytest command
    command = build_pytest_command(args)
    
    # Print the command for reference
    print(f"Running: {' '.join(command)}")
    
    # Run the tests
    try:
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with code {e.returncode}")
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
