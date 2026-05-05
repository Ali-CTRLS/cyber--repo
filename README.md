# InjuryAssist

**A Secure Patient-Doctor Injury Management Platform**

This project is a cybersecurity-focused medical platform built with **Python Flask**, demonstrating secure data handling, robust authentication, and file encryption at rest.

## 🔐 Cybersecurity Highlights

This platform was built to demonstrate core security concepts for a college project:

- **Authentication & Secure Storage**: Passwords are cryptographically hashed and salted using Werkzeug's `PBKDF2` algorithm, protecting against rainbow table and timing attacks.
- **Session Security**: Managed via `Flask-Login` using secure, HTTP-only session cookies.
- **CSRF Protection**: All POST forms are strictly protected against Cross-Site Request Forgery using `Flask-WTF` validation tokens.
- **Data-at-Rest Encryption**: Sensitive medical reports are encrypted using **AES-256-GCM** via the `cryptography` library. This ensures both confidentiality and data integrity (tamper-detection via MAC tags) of medical records stored on disk. Encryption keys are managed separately in the SQLite database.
- **Role-based Access Control (RBAC)**: Distinct separation between `Patient` and `Doctor` blueprints prevents privilege escalation.

## 💻 Technology Stack

- **Backend:** Python 3.9+, Flask
- **Database:** SQLite + Flask-SQLAlchemy (zero configuration)
- **Frontend:** Jinja2 Templates + Tailwind CSS (via CDN)
- **Security:** `werkzeug.security`, `flask-login`, `flask-wtf`, `cryptography`

## 🚀 Setup & Installation

**1. Prerequisites**
- Python 3.9 or higher

**2. Install dependencies**
Open your terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

**3. Run the Application**
```bash
python app.py
```
*Note: The application runs on port `5001` to avoid common Windows permission conflicts on port 5000.*

**4. Access the Platform**
Open your browser and navigate to: `http://127.0.0.1:5001`

### 🩺 Default Credentials

On the very first run, the database automatically initializes and seeds with 5 sample doctors. You can log in to the doctor dashboard using:
- **Username:** `dr.ahmed` (or `dr.sara`, `dr.omar`)
- **Password:** `doctor123`

Patients can dynamically create their own secure accounts via the `/auth/register` page.

## 📂 Project Documentation

- **Development Guide:** Read `instructions.md` for the full project roadmap, implementation rules, and component structures.
- **Security Architecture:** Check the `.puml` files in the `explination-diagram/` directory for detailed PlantUML sequence diagrams mapping out the exact authentication and AES-256-GCM encryption mechanics.
