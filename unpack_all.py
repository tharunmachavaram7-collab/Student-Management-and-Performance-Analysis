"""
unpack_all.py
Utility script to extract and restore all individual files from ALL_CODE.md
Run: python unpack_all.py
"""

import os
import re

def unpack():
    all_code_file = "ALL_CODE.md"
    if not os.path.exists(all_code_file):
        print(f"Error: {all_code_file} not found in the current directory.")
        return

    with open(all_code_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Pattern matches: ## File: `path` ... ```lang\ncode\n```
    pattern = re.compile(r"## File: `([^`]+)`.*?\n\*\*Relative Path:\*\* `([^`]+)`.*?\n```[a-zA-Z0-9_\-]*\r?\n(.*?)```", re.DOTALL)
    matches = pattern.findall(content)

    if not matches:
        print("No file sections detected with the primary pattern, attempting fallback pattern...")
        pattern_fallback = re.compile(r"## File: `([^`]+)`.*?\n```[a-zA-Z0-9_\-]*\r?\n(.*?)```", re.DOTALL)
        matches_fallback = pattern_fallback.findall(content)
        matches = [(m[0], m[0], m[1]) for m in matches_fallback]

    if not matches:
        print("No files could be parsed from ALL_CODE.md.")
        return

    print(f"Found {len(matches)} files to extract...\n")
    for display_path, rel_path, file_code in matches:
        target_path = rel_path.replace("/", os.sep).replace("\\", os.sep)
        parent_dir = os.path.dirname(target_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as out:
            out.write(file_code)
        print(f"  [CREATED] {target_path} ({len(file_code):,} chars)")

    print(f"\nSuccessfully extracted all {len(matches)} files from {all_code_file}!")

if __name__ == "__main__":
    unpack()

