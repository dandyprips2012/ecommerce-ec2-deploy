#!/usr/bin/env python3
"""
Main deployment script for EC2.
Copies all template files to their runtime locations,
installs dependencies, and starts the services.
"""

import os
import shutil
import subprocess
import sys
import json
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(ROOT_DIR, "templates")

def get_python_exe():
    python_exe = os.environ.get('DT_PYTHON')
    if python_exe:
        print(f"Using Python from DT_PYTHON: {python_exe}")
        return python_exe
    return sys.executable

def check_python_version(python_exe):
    try:
        output = subprocess.check_output([python_exe, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'], text=True).strip()
        print(f"Detected Python version: {output}")
        major, minor = map(int, output.split('.'))
        if major == 3 and minor >= 12:
            print("\n⚠️  WARNING: Python 3.12+ may have limited Dynatrace support on some platforms.")
    except Exception as e:
        print(f"Could not determine Python version: {e}")

def run_cmd(cmd, cwd=None, check=True, shell=True):
    print(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=shell, cwd=cwd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if check:
            raise

def copy_template(src_rel, dst_rel=None):
    src = os.path.join(TEMPLATE_DIR, src_rel)
    if dst_rel is None:
        dst_rel = src_rel
    dst = os.path.join(ROOT_DIR, dst_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"Copied {src_rel} -> {dst_rel}")

def stamp_file_path(service):
    return os.path.join(ROOT_DIR, 'backend', service, '.requirements_installed')

def are_requirements_installed(service):
    stamp = stamp_file_path(service)
    if not os.path.exists(stamp):
        return False
    req_path = os.path.join(ROOT_DIR, 'backend', service, 'requirements.txt')
    if os.path.getmtime(req_path) > os.path.getmtime(stamp):
        return False
    return True

def mark_requirements_installed(service):
    with open(stamp_file_path(service), 'w') as f:
        f.write('installed')

def main():
    # Load config if exists
    config = {}
    config_path = os.path.join(ROOT_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    else:
        print("No config.json found, using defaults.")

    # Determine Python interpreter
    PYTHON_EXE = get_python_exe()
    check_python_version(PYTHON_EXE)

    # 1. Copy backend files
    for service in ['product-service', 'order-service', 'inventory-service']:
        copy_template(f'backend/{service}/app.py', f'backend/{service}/app/app.py')
        copy_template(f'backend/{service}/requirements.txt', f'backend/{service}/requirements.txt')
    copy_template('backend/seed.py', 'backend/seed.py')

    # 2. Copy frontend files (recursively)
    frontend_template = os.path.join(TEMPLATE_DIR, 'frontend')
    for root, dirs, files in os.walk(frontend_template):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), TEMPLATE_DIR)
            copy_template(rel_path)

    # 3. Copy automation files
    automation_script = config.get('automation_script', 'traffic.js')
    if automation_script not in ['traffic.js', 'automate.js']:
        automation_script = 'traffic.js'
    copy_template(f'automation/{automation_script}', 'automation/automate.js')
    copy_template('automation/package.json', 'automation/package.json')

    # 4. Copy launch.sh
    copy_template('launch.sh', 'launch.sh')
    os.chmod(os.path.join(ROOT_DIR, 'launch.sh'), 0o755)

    # 5. Set up Python virtual environments and install dependencies
    print("\nSetting up Python virtual environments...")
    for service in ['product-service', 'order-service', 'inventory-service']:
        service_path = os.path.join(ROOT_DIR, 'backend', service)
        venv_path = os.path.join(service_path, 'venv')
        if not os.path.exists(venv_path):
            run_cmd(f'"{PYTHON_EXE}" -m venv venv', cwd=service_path)
            need_install = True
        else:
            need_install = not are_requirements_installed(service)

        if need_install:
            # Use '.' instead of 'source' for POSIX compatibility
            run_cmd(f'. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt',
                    cwd=service_path, shell=True)
            mark_requirements_installed(service)
        else:
            print(f"Requirements already installed for {service}, skipping.")

    # 6. Install automation dependencies
    print("\nInstalling automation dependencies...")
    auto_dir = os.path.join(ROOT_DIR, 'automation')
    if not os.path.exists(os.path.join(auto_dir, 'node_modules')):
        run_cmd('npm install', cwd=auto_dir)
    else:
        print("Automation node_modules found, skipping npm install.")

    # 7. Seed the database
    print("\nSeeding database...")
    seed_venv = os.path.join(ROOT_DIR, 'backend', 'product-service', 'venv', 'bin', 'activate')
    # Use '.' for activation
    run_cmd(f'. {seed_venv} && python seed.py', cwd=os.path.join(ROOT_DIR, 'backend'), shell=True)

    # 8. Start all services
    print("\nStarting all services...")
    run_cmd('./launch.sh', cwd=ROOT_DIR)

    print("\nAll done! The platform is now running in the background.")
    print("You can check logs in /tmp/product.log, /tmp/order.log, /tmp/inventory.log, /tmp/frontend.log, /tmp/automation.log")

if __name__ == "__main__":
    main()