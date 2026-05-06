#!/usr/bin/env python3
"""Pre-commit check script: runs ruff and pytest."""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode == 0:
        print(f"✓ {description} passed")
        return True
    else:
        print(f"✗ {description} failed (exit code: {result.returncode})")
        return False


def main():
    """Run all pre-commit checks."""
    project_root = Path(__file__).parent.parent
    
    # Detect pytest path
    import shutil
    pytest_cmd = shutil.which('pytest')
    if not pytest_cmd:
        # Try virtual environment
        venv_pytest = project_root / '.venv' / 'Scripts' / 'pytest.exe'
        if venv_pytest.exists():
            pytest_cmd = str(venv_pytest)
        else:
            print("Warning: pytest not found, skipping tests")
            pytest_cmd = None
    
    checks = [
        {
            'cmd': ['ruff', 'check', 'src/'],
            'description': 'Ruff linting check'
        },
        {
            'cmd': ['ruff', 'format', '--check', 'src/'],
            'description': 'Ruff format check'
        },
    ]
    
    if pytest_cmd:
        checks.append({
            'cmd': [pytest_cmd, 'tests/', '-v'],
            'description': 'Pytest unit tests'
        })
    
    print("\n" + "="*60)
    print("Starting pre-commit checks...")
    print("="*60)
    
    all_passed = True
    for check in checks:
        if not run_command(check['cmd'], check['description']):
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All checks passed!")
        print("="*60)
        return 0
    else:
        print("✗ Some checks failed!")
        print("="*60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
