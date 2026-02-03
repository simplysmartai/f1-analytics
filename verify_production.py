#!/usr/bin/env python
"""
F1 Analytics Dashboard - Pre-Deployment Verification Script
Verifies all systems are go for production deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_item(description, passed):
    """Print check result"""
    status = "[OK]" if passed else "[FAIL]"
    symbol = "[+]" if passed else "[-]"
    print(f"  {symbol} {status} {description}")
    return passed

def main():
    """Run verification checks"""
    print_header("F1 ANALYTICS DASHBOARD - PRE-DEPLOYMENT VERIFICATION")
    
    all_passed = True
    
    # 1. Check Python version
    print("\n1. Environment Checks")
    python_version = sys.version_info
    py_ok = check_item(
        f"Python version ({python_version.major}.{python_version.minor})",
        python_version >= (3, 13)
    )
    all_passed = all_passed and py_ok
    
    # 2. Check required files
    print("\n2. Project Structure")
    required_files = {
        "app.py": "Main application file",
        "requirements.txt": "Dependencies",
        "config/settings.py": "Configuration",
        "services/f1_data_service.py": "Data service",
        "services/telemetry_service.py": "Telemetry service",
        "services/ai_service.py": "AI service",
        "utils/logger.py": "Logger",
        "utils/validators.py": "Validators",
        "ui/styles.py": "Styles",
    }
    
    for filepath, description in required_files.items():
        exists = Path(filepath).exists()
        check_item(f"{description} ({filepath})", exists)
        all_passed = all_passed and exists
    
    # 3. Check documentation
    print("\n3. Documentation")
    docs = {
        "README.md": "Main README",
        "START.md": "Quick start guide",
        "ARCHITECTURE.md": "Architecture documentation",
        "DEPLOYMENT.md": "Deployment guide",
        "API.md": "API reference",
        "PRODUCTION_READINESS.md": "Production readiness report",
    }
    
    for filepath, description in docs.items():
        exists = Path(filepath).exists()
        check_item(f"{description} ({filepath})", exists)
        all_passed = all_passed and exists
    
    # 4. Check tests
    print("\n4. Test Suite")
    test_dirs = {
        "tests/test_services.py": "Service tests",
        "tests/test_validation.py": "Validation tests",
        "tests/test_performance.py": "Performance tests",
    }
    
    for filepath, description in test_dirs.items():
        exists = Path(filepath).exists()
        check_item(f"{description} ({filepath})", exists)
        all_passed = all_passed and exists
    
    # 5. Check imports
    print("\n5. Import Verification")
    try:
        from config.settings import settings
        check_item("config.settings", True)
    except Exception as e:
        check_item(f"config.settings ({e})", False)
        all_passed = False
    
    try:
        from services.f1_data_service import data_service
        check_item("services.f1_data_service", True)
    except Exception as e:
        check_item(f"services.f1_data_service ({e})", False)
        all_passed = False
    
    try:
        from utils.logger import logger
        check_item("utils.logger", True)
    except Exception as e:
        check_item(f"utils.logger ({e})", False)
        all_passed = False
    
    # 6. Check configuration
    print("\n6. Configuration")
    try:
        from config.settings import settings
        settings.validate()
        check_item("Configuration validation", True)
    except Exception as e:
        check_item(f"Configuration validation ({e})", False)
        all_passed = False
    
    # 7. Summary
    print("\n" + "="*60)
    if all_passed:
        print("  [+] ALL CHECKS PASSED - READY FOR DEPLOYMENT")
        print("="*60)
        print("\nNext steps:")
        print("  1. Read DEPLOYMENT.md")
        print("  2. Choose deployment option (Streamlit Cloud recommended)")
        print("  3. Follow deployment instructions")
        print("  4. Run 'streamlit run app.py' to test locally")
        print("\n[+] Good to go!")
        return 0
    else:
        print("  [-] SOME CHECKS FAILED - REVIEW ABOVE")
        print("="*60)
        print("\nPlease fix the issues before deployment.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
