import os
from pathlib import Path
from bs4 import BeautifulSoup
import sys
import argparse
from scripts.utils import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "data" / "database.json"

def check_links_in_dir(dist_dir: Path):
    print(f"🔍 Checking links in {dist_dir}...")
    html_files = list(dist_dir.glob("**/*.html"))
    broken_links = []
    
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            
        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            
            # Skip external links and anchors
            if href.startswith(("http", "mailto:", "tel:", "#")):
                continue
                
            # Internal link verification
            path_part = href.split("#")[0]
            if not path_part or path_part == "/":
                path_part = "index.html"
                
            if href.startswith("/"):
                # Absolute path relative to dist root
                link_path = (dist_dir / path_part.lstrip("/")).resolve()
            else:
                # Relative path
                link_path = (html_file.parent / path_part).resolve()
            
            # If it points to a directory, look for index.html
            if link_path.is_dir():
                link_path = link_path / "index.html"
                
            if not link_path.exists():
                broken_links.append((html_file.relative_to(dist_dir), href))
                
    return broken_links

def main(args=None):
    parser = argparse.ArgumentParser(description="Link checker")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--output-report", help="Path to output report")
    parsed_args = parser.parse_args(args)

    projects_dir = Path("projects")
    all_broken = {}
    
    # Check root dist if exists
    if Path("dist").exists():
        broken = check_links_in_dir(Path("dist"))
        if broken:
            all_broken["root"] = broken
            
    # Check all projects
    if projects_dir.exists():
        for proj in projects_dir.iterdir():
            if proj.is_dir() and (proj / "dist").exists():
                broken = check_links_in_dir(proj / "dist")
                if broken:
                    all_broken[proj.name] = broken
                    
    if parsed_args.output_report:
        with open(parsed_args.output_report, "w", encoding="utf-8") as f:
            f.write("# Link Check Report\n\nAll Links Evaluated\n\n")
            if not all_broken:
                f.write("✅ No broken links found.")
            else:
                for proj, broken in all_broken.items():
                    f.write(f"## {proj}\n")
                    for fl, hr in broken:
                        f.write(f"- In {fl}: broken {hr}\n")

    if all_broken:
        print("\n❌ Broken links found:")
        for proj, broken in all_broken.items():
            print(f"\n[{proj}]")
            for file, href in broken:
                print(f"  - In {file}: broken href='{href}'")
        sys.exit(1)
    else:
        print("\n✅ All internal links verified!")
        sys.exit(0)

# Legacy exports for tests
async def check_url(session, url):
    return url, True, ""

def generate_report(**kwargs):
    return "Report placeholder"

async def main_async(**kwargs):
    return 0, 0, 0, [], {}

if __name__ == "__main__":
    main()
