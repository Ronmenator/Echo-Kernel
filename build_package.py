#!/usr/bin/env python3
"""
Build script for EchoKernel package.
This script automates the process of building and distributing the package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    
    return result


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed: {path}")


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Install build dependencies
    run_command("pip install build twine")
    
    # Build the package
    run_command("python -m build")


def check_package():
    """Check the built package."""
    print("Checking package...")
    
    # Check the built package
    run_command("twine check dist/*")


def upload_to_test_pypi():
    """Upload to TestPyPI."""
    print("Uploading to TestPyPI...")
    
    # Upload to TestPyPI
    run_command("twine upload --repository testpypi dist/*")


def upload_to_pypi():
    """Upload to PyPI."""
    print("Uploading to PyPI...")
    
    # Upload to PyPI
    run_command("twine upload dist/*")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and distribute EchoKernel package")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--build", action="store_true", help="Build the package")
    parser.add_argument("--check", action="store_true", help="Check the built package")
    parser.add_argument("--upload-test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--upload", action="store_true", help="Upload to PyPI")
    parser.add_argument("--all", action="store_true", help="Clean, build, check, and upload to TestPyPI")
    
    args = parser.parse_args()
    
    try:
        if args.clean or args.all:
            clean_build()
        
        if args.build or args.all:
            build_package()
        
        if args.check or args.all:
            check_package()
        
        if args.upload_test or args.all:
            upload_to_test_pypi()
        
        if args.upload:
            upload_to_pypi()
        
        if not any([args.clean, args.build, args.check, args.upload_test, args.upload, args.all]):
            print("No action specified. Use --help for options.")
            print("Recommended: python build_package.py --all")
    
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 