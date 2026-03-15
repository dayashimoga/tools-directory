import os
import shutil
import glob
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

directories = [
    str(PROJECT_ROOT),
    str(PROJECT_ROOT / "projects" / "datasets-directory"),
    str(PROJECT_ROOT / "projects" / "opensource-directory"),
    str(PROJECT_ROOT / "projects" / "tools-directory"),
    str(PROJECT_ROOT / "projects" / "prompts-directory"),
    str(PROJECT_ROOT / "projects" / "cheatsheets-directory"),
    str(PROJECT_ROOT / "projects" / "boilerplates-directory"),
    str(PROJECT_ROOT / "projects" / "jobs-directory"),
    str(PROJECT_ROOT / "projects" / "apistatus-directory")
]

patterns = [
    "test_*.txt",
    "*.log",
    "final_test_report.txt",
    "link_report.md",
    "tests_report.txt",
    "pytest_debug.txt",
    "pytest_report.txt",
    "venv_pytest_out.txt",
    "test_output.txt",
    "test_output_utf8.txt",
    "tests_output.txt",
    ".coverage"
]

dirs_to_remove = [
    ".pytest_cache",
    "htmlcov"
]

for d in directories:
    if not os.path.exists(d):
        continue
    
    print(f"Cleaning {d}...")
    
    # Remove file patterns
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(d, pattern)):
            try:
                os.remove(file_path)
                print(f"  Removed file: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  Error removing {file_path}: {e}")
                
    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = os.path.join(d, dir_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"  Removed directory: {dir_name}")
            except Exception as e:
                print(f"  Error removing directory {dir_path}: {e}")

print("Cleanup complete.")
