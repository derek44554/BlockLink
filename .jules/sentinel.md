## 2025-05-15 - [Path Traversal in Node BID]
**Vulnerability:** User-controlled `bid` identifiers were used directly in file paths, allowing arbitrary file writes (Path Traversal) during node registration and connection saving.
**Learning:** Common identifier fields in distributed protocols (like `bid`) can be manipulated to include path traversal sequences like `../`.
**Prevention:** Always sanitize user-provided identifiers using `os.path.basename()` before using them in filesystem operations.
