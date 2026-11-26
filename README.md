# Project 14 — File-Integrity Verification

## Objective
Use SHA-256 hashes to record a baseline for selected lab files, then compare the
current files against that baseline to identify changed, missing, or added files.

## Requirements
- Python 3.9 or newer
- No third-party packages required

## Quick start
1. Extract this folder.
2. Create a folder named `sample_files` and place a few test files inside it.
3. Open a terminal in this project folder.
4. Create a baseline:

   ```bash
   python integrity_check.py baseline ./sample_files --manifest ./baseline.json
   ```

5. Verify the files:

   ```bash
   python integrity_check.py verify ./sample_files --manifest ./baseline.json
   ```

If no changes occurred, the program prints `PASS`. If files were modified,
removed, or added, it reports `CHANGED`, `MISSING`, or `ADDED`.

## Demonstration
- Run `baseline` on the sample directory.
- Edit one file, delete another, and add a new file.
- Run `verify` again and capture the output for your practical report.

## Method
The program reads each file in chunks and calculates its SHA-256 digest.
The baseline JSON stores each relative path, digest, and file size. Verification
recalculates the digests and compares the current file set with the baseline.

## Limitations
- A hash comparison detects differences; it does not prove whether a change is malicious.
- The baseline must be protected. If an attacker can alter both the files and
  the baseline, the comparison can be defeated.
- File metadata such as permissions and timestamps is not evaluated.
- Use only on files you own or are authorized to assess.

## Expected result
An unchanged directory returns exit code `0`; differences return `1`; operational
errors return `2`.
