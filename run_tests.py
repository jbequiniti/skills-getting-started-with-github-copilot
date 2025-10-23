#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API.
"""

import subprocess
import sys


def run_tests():
    """Run the test suite with coverage reporting."""
    print("🧪 Running FastAPI tests with pytest...")
    print("=" * 60)
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "--cov=src", 
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v"
        ], check=True)
        
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)