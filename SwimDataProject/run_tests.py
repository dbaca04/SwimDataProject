#!/usr/bin/env python3
"""
Test runner for Swim Data Project.

This script runs all unit and integration tests and generates coverage reports.
"""
import os
import sys
import subprocess
import argparse


def run_tests(test_type='all', verbose=False, coverage=False):
    """
    Run the specified type of tests.
    
    Args:
        test_type (str): Type of tests to run ('unit', 'integration', 'all')
        verbose (bool): Whether to run in verbose mode
        coverage (bool): Whether to generate coverage report
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    # Determine test markers based on test type
    if test_type == 'unit':
        markers = 'unit'
    elif test_type == 'integration':
        markers = 'integration'
    elif test_type == 'functional':
        markers = 'functional'
    else:  # all
        markers = None
    
    # Build command
    cmd = ['pytest']
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    
    # Add markers if specified
    if markers:
        cmd.append(f'-m {markers}')
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=scrapers', '--cov=database', '--cov=web', 
                    '--cov-report', 'term', '--cov-report', 'html'])
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode == 0


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run tests for Swim Data Project')
    parser.add_argument('--type', choices=['unit', 'integration', 'functional', 'all'], 
                      default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                      help='Run tests in verbose mode')
    parser.add_argument('--coverage', '-c', action='store_true',
                      help='Generate coverage report')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Make sure we're in the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Running {args.type} tests...")
    success = run_tests(args.type, args.verbose, args.coverage)
    
    if success:
        print("All tests passed successfully.")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)
