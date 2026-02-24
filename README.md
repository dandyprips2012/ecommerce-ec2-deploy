# E‑Commerce Platform Deployment on EC2

This project automates the deployment of a full‑stack Python/React e‑commerce application on an AWS EC2 instance. It includes three backend microservices (Product, Order, Inventory), a React frontend, and an automated traffic generator.

## Files Overview

- `deploy.py` – Main script to copy templates, install dependencies, and start services.
- `config.json` – Configuration for AWS credentials and deployment options (optional).
- `cleanup_ec2.py` – Terminates the EC2 instance and deletes resources (use after testing).
- `templates/` – All application source files (backend, frontend, automation).

## Usage

1. **Launch an EC2 instance** (Ubuntu 20.04/22.04 recommended) with appropriate security groups (open ports 3006, 5001‑5003 for internal access; optionally open 22 for SSH).
2. **Upload this project** to the instance (e.g., via `scp` or `git clone`).
3. **SSH into the instance** and run:
   ```bash
   cd project-root
   python3 deploy.py