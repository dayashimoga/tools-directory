import os
from pathlib import Path

def update_utils_py(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Original load_database:
    # def load_database(path: Path = None) -> list:
    #     if path is None:
    #         path = DATA_DIR / "database.json"
    #     with open(path, "r", encoding="utf-8") as f:
    #         data = json.load(f)
    #     if not isinstance(data, list):
    #         raise ValueError("database.json must contain a JSON array")
    #     return data
    
    # New load_database with slug injection:
    new_load_db = """def load_database(path: Path = None) -> list:
    \"\"\"Load the database JSON file and return a list of items with slugs generated if missing.\"\"\"
    if path is None:
        path = DATA_DIR / "database.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("database.json must contain a JSON array")

    # Inject slugs and titles if missing
    for item in data:
        # Title can be 'name' or 'title'
        if "title" not in item:
            item["title"] = item.get("name", "Unknown Item")
        
        # Slug can be 'slug' or 'id' or slugified title
        if "slug" not in item:
            if "id" in item:
                item["slug"] = slugify(str(item["id"]))
            else:
                item["slug"] = slugify(item["title"])
                
    return data"""

    # Look for the old function and replace it
    import re
    # Match the function definition until the return statement
    pattern = r"def load_database\(path: Path = None\) -> list:.*?\n    return data"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_load_db, content, flags=re.DOTALL)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {path}")
    else:
        print(f"Could not find load_database pattern in {path}")

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

for d in directories:
    utils_path = os.path.join(d, "scripts", "utils.py")
    if os.path.exists(utils_path):
        update_utils_py(utils_path)

print("Global utils.py update complete.")
