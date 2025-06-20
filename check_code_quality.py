#!/usr/bin/env python3
"""
Code Quality Checker for OMEGA6
Runs various linting and formatting tools
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PASSED")
            return True, result.stdout
        else:
            print("❌ FAILED")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False, result.stdout + "\n" + result.stderr
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)


def main():
    """Run all code quality checks"""
    print("OMEGA6 Code Quality Check")
    print("=" * 80)

    # Change to OMEGA6 directory
    omega6_dir = Path(__file__).parent
    os.chdir(omega6_dir)

    # Ensure we're in virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️  Not in virtual environment. Please run: source venv/bin/activate")
        return 1

    # Define Python files to check
    python_files = []
    for pattern in ["*.py", "src/*.py", "plugins/*/*.py", "tests/*.py"]:
        python_files.extend(Path(".").glob(pattern))

    python_files = [str(f) for f in python_files if f.is_file()]

    print(f"Found {len(python_files)} Python files to check")

    # Run checks
    results = []

    # 1. Black formatting (auto-fix)
    print("\n1. Running Black formatter...")
    success, _ = run_command(["black", "--check", "--diff"] + python_files, "Black (checking)")

    if not success:
        print("   Applying Black formatting...")
        run_command(["black"] + python_files, "Black (fixing)")
        results.append(("Black", True, "Formatted"))
    else:
        results.append(("Black", True, "Already formatted"))

    # 2. isort import sorting (auto-fix)
    print("\n2. Running isort...")
    success, _ = run_command(["isort", "--check-only", "--diff"] + python_files, "isort (checking)")

    if not success:
        print("   Applying isort fixes...")
        run_command(["isort"] + python_files, "isort (fixing)")
        results.append(("isort", True, "Fixed imports"))
    else:
        results.append(("isort", True, "Imports already sorted"))

    # 3. Flake8 linting
    print("\n3. Running Flake8...")
    success, output = run_command(["flake8", "--statistics", "--count"] + python_files, "Flake8")
    results.append(("Flake8", success, output.strip() if not success else "No issues"))

    # 4. MyPy type checking
    print("\n4. Running MyPy...")
    success, output = run_command(["mypy", "--no-error-summary"] + python_files, "MyPy")
    results.append(("MyPy", success, "Type checking passed" if success else output.strip()))

    # 5. Pylint (informational only)
    print("\n5. Running Pylint...")
    success, output = run_command(["pylint", "--score=no", "--reports=no"] + python_files, "Pylint")
    # Pylint is very strict, so we don't fail on it
    results.append(("Pylint", True, "Informational only"))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_passed = True
    for tool, passed, message in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{tool:15} {status}")
        if not passed and message:
            print(f"{'':15} {message[:60]}...")
            all_passed = False

    if all_passed:
        print("\n✅ All code quality checks passed!")
    else:
        print("\n❌ Some checks failed. Please review the output above.")

    # Generate report
    report_path = Path("code_quality_report.txt")
    with open(report_path, "w") as f:
        f.write("OMEGA6 Code Quality Report\n")
        f.write("=" * 80 + "\n\n")

        for tool, passed, message in results:
            f.write(f"{tool}:\n")
            f.write(f"Status: {'PASSED' if passed else 'FAILED'}\n")
            f.write(f"Details: {message}\n")
            f.write("-" * 40 + "\n\n")

    print(f"\nDetailed report saved to: {report_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
