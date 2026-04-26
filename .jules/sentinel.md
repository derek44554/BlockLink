## 2025-05-20 - [Path Traversal in Node Identification]
**Vulnerability:** User-controlled node identifier (`bid`) was used to construct file paths for saving signatures and connection data without sanitization, allowing arbitrary file writes via path traversal (e.g., `../../../etc/passwd`).
**Learning:** In a distributed system where nodes identify themselves, identifiers must be treated as untrusted input when used in filesystem operations.
**Prevention:** Always use `os.path.basename()` or a similar sanitization function when including user-provided identifiers in file paths.
