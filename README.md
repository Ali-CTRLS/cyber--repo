<div align="center">
  <img src="https://img.icons8.com/color/96/000000/medical-doctor.png" alt="InjuryAssist Logo" width="80" height="80">
  
  # 🏥 InjuryAssist

  **A Secure Patient-Doctor Injury Management Platform**

  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
  [![Flask](https://img.shields.io/badge/Flask-3.1.1-lightgrey.svg?logo=flask&logoColor=black)](https://flask.palletsprojects.com/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![Security](https://img.shields.io/badge/Security-AES--256--GCM-red.svg)](https://cryptography.io/en/latest/)
</div>

<br />

> **InjuryAssist** is a lightweight, cybersecurity-focused medical web application built to connect injured patients with specialized doctors. It emphasizes secure data handling, robust authentication, and file encryption at rest, making it an excellent demonstration of applied cybersecurity in healthcare software.

---

## ✨ Key Features

- **🧑‍⚕️ Role-Based Access Control (RBAC)**: Distinct patient and doctor workflows to prevent privilege escalation.
- **📅 Appointment Management**: Intelligent doctor matching based on injury types and seamless appointment booking.
- **📄 Encrypted Medical Reports**: Secure generation, storage, and retrieval of medical reports.
- **🎨 Modern UI**: Clean, responsive, and accessible interface built with Tailwind CSS.

## 🔐 Cybersecurity Highlights

This platform implements critical security measures to protect sensitive medical data:

- **Authentication & Secure Storage**: Passwords are cryptographically hashed and salted using Werkzeug's `PBKDF2` algorithm, protecting against rainbow table and timing attacks.
- **Session Security**: Managed via `Flask-Login` using secure, HTTP-only session cookies to prevent session hijacking.
- **CSRF Protection**: All state-changing POST forms are strictly protected against Cross-Site Request Forgery using `Flask-WTF` validation tokens.
- **Data-at-Rest Encryption**: Sensitive medical reports are encrypted using **AES-256-GCM** via the `cryptography` library. This ensures both confidentiality and data integrity (tamper-detection via MAC tags) of medical records stored on disk. Encryption keys are securely managed.
- **Input Sanitization**: Extensive use of SQLAlchemy ORM prevents SQL Injection attacks by parameterizing database queries.

## 💻 Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Backend** | Python 3.9+, Flask | Lightweight, scalable server-side framework. |
| **Database** | SQLite + Flask-SQLAlchemy | Zero-configuration database with robust ORM. |
| **Frontend** | Jinja2 + Tailwind CSS | Server-side rendered templates with utility-first styling. |
| **Security** | `cryptography`, `werkzeug.security` | Industry-standard cryptographic primitives and hashing. |

## 🚀 Setup & Installation

Follow these steps to get a local development environment running:

### 1. Prerequisites
- Python 3.9 or higher installed on your system.

### 2. Clone and Install Dependencies
Open your terminal, navigate to the project directory, and run:

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Run the Application

You can easily launch the application using the provided batch script on Windows:
```bash
run.bat
```

Or start the Flask development server manually:
```bash
python app.py
```
> *Note: The application runs on port `5001` (`http://127.0.0.1:5001`) to avoid common permission conflicts on port 5000.*

## 🩺 Default Credentials & Demo Data

On the very first run, the SQLite database is automatically initialized and seeded with 5 sample doctors to help you test the platform immediately. 

**Doctor Login:**
- **Username:** `dr.ahmed` (or `dr.sara`, `dr.omar`, `dr.nora`, `dr.khaled`)
- **Password:** `doctor123`

**Patient Access:**
Patients can dynamically create their own secure accounts via the Register page (`/auth/register`). Alternatively, run `python seed_demo.py` to populate additional demo patients and records.

## 📂 Project Architecture

```text
injury-assist/
├── app.py                # Flask application factory and entry point
├── config.py             # App configuration (Secret keys, DB URI)
├── models.py             # SQLAlchemy database schemas
├── forms.py              # Flask-WTF form definitions
├── encryption.py         # AES-256-GCM cryptographic functions
├── requirements.txt      # Python dependencies
├── blueprints/           # Modular route definitions (auth, patient, doctor)
├── templates/            # Jinja2 HTML templates
└── storage/reports/      # Directory for AES-encrypted medical reports
```

## 📖 Additional Documentation

- **Development Guide:** Refer to `instructions.md` for a comprehensive roadmap, implementation rules, and component structures.
- **Security Architecture:** Check the `.puml` files in the `explination-diagram/` directory for detailed PlantUML sequence diagrams mapping out authentication and AES-256-GCM encryption mechanics.
- **Workflow Overview:** See `task/security-stages.md` for request-flow breakdowns.

---
<div align="center">
  <i>Developed for academic demonstration of secure software engineering principles.</i>
</div>
