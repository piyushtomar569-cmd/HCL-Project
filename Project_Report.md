# Project 14 — File-Integrity Verification
## Practical Project Report

### Aim
To verify the integrity of selected files by generating and comparing SHA-256 hashes.

### Tools
- Python 3.9+
- Python standard library (`hashlib`, `json`, `argparse`, `pathlib`)
- No external packages

### Procedure
1. Select an authorized test directory containing sample files.
2. Generate a baseline using the `baseline` command.
3. Modify, add, or remove a test file.
4. Run the `verify` command against the same baseline.
5. Record the detected differences and determine whether they were expected.

### Result
The program reports unchanged files as a successful verification. It identifies
changed, missing, and newly added files for review.

### Conclusion
A SHA-256 baseline provides a simple way to detect file-content changes. The
baseline should be stored securely and updated only after authorized changes
have been reviewed.
