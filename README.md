# ProjectPartner

## Student Project Discovery, Planning & Guidance Platform

ProjectPartner is a 100% offline-capable, student-owned software engineering project discovery, architectural planning, team management, and documentation platform built with Flask, SQLAlchemy, AST code inspection engines, local TF-IDF recommendation algorithms, and ReportLab PDF document generation.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- **Python 3.10+** (Python 3.10, 3.11, or 3.12 recommended)
- **Pip package manager**
- **Git**

### 2. Environment Setup
Clone the repository and create a local Python virtual environment:

```bash
# Clone repository
git clone https://github.com/rockychandu/ProjectPartner.git
cd ProjectPartner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages from `requirements.txt` and verify `requirements.lock`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the development server using either `app.py` or `run.py`:

```bash
# Option 1: Run via app.py
python app.py

# Option 2: Run via run.py
python run.py
```

Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the automated Pytest suite:

```bash
python -m pytest tests/ -v
```

---

## 🐳 Running with Docker

Build and run using Docker:

```bash
# Build Docker image
docker build -t projectpartner:latest .

# Run Docker container
docker run -d -p 5000:5000 --name projectpartner_app projectpartner:latest
```

---

## 📦 Dependency Manifest & Lockfile

- **Manifest**: `requirements.txt`
- **Lockfile**: `requirements.lock` / `poetry.lock`
- **Primary Dependencies**:
  - `Flask>=3.0.0`
  - `Flask-SQLAlchemy>=3.1.0`
  - `Flask-Login>=0.6.3`
  - `Werkzeug>=3.0.0`
  - `reportlab>=4.0.0`
  - `scikit-learn>=1.4.0`
  - `pytest>=8.0.0`

---

## 📄 License & Proprietary Notice

Proprietary Software — All rights reserved. Registered student engineering platform.
