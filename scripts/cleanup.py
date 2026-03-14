import os
import shutil
import glob

directories = [
    r"h:\boring",
    r"h:\boring\projects\datasets-directory",
    r"h:\boring\projects\opensource-directory",
    r"h:\boring\projects\tools-directory",
    r"h:\boring\projects\prompts-directory",
    r"h:\boring\projects\cheatsheets-directory",
    r"h:\boring\projects\boilerplates-directory",
    r"h:\boring\projects\jobs-directory",
    r"h:\boring\projects\apistatus-directory"
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
