# Security Stages for a Web System

This document covers two independent views:
1) The security lifecycle of a website (from idea to operations).
2) The security flow of a single web request (from browser to database and back).

---

## 1) Security Lifecycle Stages (End-to-End)

### Stage 1: Strategy and Risk Framing
- **Goal**: Decide what must be protected and why.
- **Key outputs**: Data classification, threat model scope, compliance needs.
- **Typical evidence**: Asset inventory, data flow map, risk register.

### Stage 2: Secure Design and Architecture
- **Goal**: Build security into the blueprint before code exists.
- **Key controls**: Least privilege, zero trust boundaries, segmentation, defense-in-depth.
- **Typical evidence**: Architecture diagrams, trust boundaries, threat model notes.

### Stage 3: Secure Build and Dependency Hygiene
- **Goal**: Keep the code and dependencies safe.
- **Key controls**: SAST, linting, dependency scanning, secret detection.
- **Typical evidence**: CI pipeline reports, SBOM, dependency lockfiles.

### Stage 4: Verification and Testing
- **Goal**: Prove the system resists realistic misuse.
- **Key controls**: DAST, unit tests for access control, abuse cases.
- **Typical evidence**: Test results, vuln tickets, retest outcomes.

### Stage 5: Hardening and Release
- **Goal**: Ship a hardened, minimal attack surface build.
- **Key controls**: Secure headers, least-privileged configs, safe defaults.
- **Typical evidence**: Deployment checklist, hardened config diffs.

### Stage 6: Monitoring and Detection
- **Goal**: Detect threats quickly and reduce dwell time.
- **Key controls**: Centralized logs, alerting, anomaly detection.
- **Typical evidence**: SIEM rules, dashboards, alert playbooks.

### Stage 7: Incident Response and Recovery
- **Goal**: Respond fast, limit damage, recover safely.
- **Key controls**: Incident runbooks, backups, key rotation.
- **Typical evidence**: Post-incident reviews, recovery timelines.

### Stage 8: Continuous Improvement
- **Goal**: Feed lessons back into the design and build stages.
- **Key controls**: Security backlog, regular audits, training.
- **Typical evidence**: Remediation roadmap, updated policies.

---

## 2) Security Flow of a Single Web Request

### A) Client and Transport Layer
1. **Browser Request**
   - User action triggers an HTTP request.
   - Client-side input validation can reduce accidental errors.

2. **TLS Handshake**
   - Encrypts traffic in transit.
   - Certificate validation prevents man-in-the-middle attacks.

3. **DNS and CDN/WAF (Edge)**
   - CDN caches safe responses; WAF blocks known threats.
   - Rate limiting prevents abuse and brute force.

### B) Application Entry
4. **Load Balancer and Reverse Proxy**
   - Normalizes headers and routes to the correct service.
   - Enforces request size limits and timeouts.

5. **Authentication**
   - Verifies identity (login session, token).
   - Failures should return generic messages to avoid user enumeration.

6. **Authorization (RBAC/ABAC)**
   - Checks role and ownership for every sensitive action.
   - Denies early and logs access decisions.

7. **Input Validation and Sanitization**
   - Validates types, ranges, and formats.
   - Protects against injection and malformed data.

### C) Business Logic and Data Access
8. **Business Rules Enforcement**
   - Enforces application rules (status transitions, time windows).
   - Prevents unauthorized state changes.

9. **Data Access Layer**
   - Uses parameterized queries via ORM.
   - Enforces least privilege at the database.

10. **Sensitive Data Handling**
    - Encrypts at rest (files, keys).
    - Protects secrets and limits exposure.

### D) Response and Observability
11. **Response Construction**
    - Strips sensitive fields, returns minimal data.
    - Uses secure headers (CSP, HSTS, etc.).

12. **Audit and Logging**
    - Logs key security events (login, access denied, file download).
    - Ties events to user and request IDs for traceability.

13. **Monitoring and Alerting**
    - Detects spikes, repeated failures, or policy violations.
    - Triggers incident response workflows.

---

## Summary: Why This Shocks People
- Security is not a single feature, it is a full lifecycle.
- Every request crosses multiple layers of enforcement.
- The weakest layer decides the outcome, so every layer must be strong.

---

## Quick Verification (Network Tab)

Use this when demoing the system to prove RBAC and data protection.

1) **RBAC denial**
   - Open DevTools -> Network.
   - Try a report URL for another patient (`/patient/report/<id>`).
   - Expect: `403` status and no file payload in response.

2) **Download header check**
   - Download a valid report.
   - Click the network request for the download.
   - Expect headers:
     - `Content-Disposition` includes the original filename.
     - `Content-Type` matches the original file type.

3) **Auth hygiene**
   - Attempt an invalid login.
   - Expect a generic error message with no user enumeration clues.
