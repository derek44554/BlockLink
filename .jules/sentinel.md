## 2026-04-25 - [Hardcoded Credentials in IPFS Adapter]
**Vulnerability:** Hardcoded password for IPFS upload endpoint.
**Learning:** Credentials were hardcoded in `blocklink/adapters/ipfs/tools.py` for ease of use during development but exposed a significant security risk.
**Prevention:** Always use environment variables or a secure secret management system for credentials. Add linting or static analysis checks to catch hardcoded secrets.
