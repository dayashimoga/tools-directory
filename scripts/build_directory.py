"""
Static Site Generator for the Programmatic SEO Directory.

Reads data/database.json, renders Jinja2 templates, and outputs
thousands of static HTML pages into dist/.
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path for Cloudflare Pages environment
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jinja2 import Environment, FileSystemLoader

from scripts.utils import (
    ADSENSE_PUBLISHER_ID,
    AMAZON_AFFILIATE_TAG,
    DIST_DIR,
    ENABLE_ADSENSE,
    ENABLE_AMAZON,
    ENABLE_PINTEREST,
    GA_MEASUREMENT_ID,
    PROJECT_ROOT,
    SITE_DESCRIPTION,
    SITE_NAME,
    SITE_URL,
    SRC_DIR,
    TEMPLATES_DIR,
    ensure_dir,
    get_categories,
    load_database,
    slugify,
    truncate,
)

# Amazon Affiliate tag
AMAZON_TAG = AMAZON_AFFILIATE_TAG

# Curated book recommendations per category (Amazon affiliate links)
BOOK_RECOMMENDATIONS = {
    "Development": [
        {"title": "Clean Code", "author": "Robert C. Martin", "asin": "0132350882"},
        {"title": "The Pragmatic Programmer", "author": "David Thomas & Andrew Hunt", "asin": "0135957052"},
    ],
    "Science": [
        {"title": "Python for Data Analysis", "author": "Wes McKinney", "asin": "109810403X"},
        {"title": "Automate the Boring Stuff with Python", "author": "Al Sweigart", "asin": "1593279922"},
    ],
    "Finance": [
        {"title": "Python for Finance", "author": "Yves Hilpisch", "asin": "1492024333"},
        {"title": "The Intelligent Investor", "author": "Benjamin Graham", "asin": "0060555661"},
    ],
    "Games": [
        {"title": "Game Programming Patterns", "author": "Robert Nystrom", "asin": "0990582906"},
        {"title": "Invent Your Own Computer Games with Python", "author": "Al Sweigart", "asin": "1593277954"},
    ],
    "Weather": [
        {"title": "Python Crash Course", "author": "Eric Matthes", "asin": "1718502702"},
        {"title": "Fluent Python", "author": "Luciano Ramalho", "asin": "1492056359"},
    ],
    "Music": [
        {"title": "Music and Technology", "author": "Julio d'Escrivan", "asin": "1501356860"},
    ],
    "Social": [
        {"title": "APIs: A Strategy Guide", "author": "Daniel Jacobson", "asin": "1449308929"},
    ],
    "Health": [
        {"title": "Python for Biologists", "author": "Martin Jones", "asin": "1492346136"},
        {"title": "Health Informatics", "author": "Ramona Nelson", "asin": "0323402313"},
    ],
    "Sports": [
        {"title": "Moneyball", "author": "Michael Lewis", "asin": "0393324818"},
        {"title": "Analyzing Baseball Data with R", "author": "Max Marchi", "asin": "0367233517"},
    ],
    "Transportation": [
        {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "asin": "1449373321"},
    ],
    "Photography": [
        {"title": "Understanding Exposure", "author": "Bryan Peterson", "asin": "1607748509"},
    ],
    "Movies & TV": [
        {"title": "Web Scraping with Python", "author": "Ryan Mitchell", "asin": "1491985577"},
    ],
    "Cloud & DevOps": [
        {"title": "The Phoenix Project", "author": "Gene Kim", "asin": "1942788290"},
        {"title": "Docker Deep Dive", "author": "Nigel Poulton", "asin": "1916585256"},
    ],
    "Machine Learning": [
        {"title": "Hands-On Machine Learning", "author": "Aurélien Géron", "asin": "1098125975"},
        {"title": "Deep Learning with Python", "author": "François Chollet", "asin": "1617296864"},
    ],
    "Cryptocurrency": [
        {"title": "Mastering Bitcoin", "author": "Andreas Antonopoulos", "asin": "1491954388"},
        {"title": "The Bitcoin Standard", "author": "Saifedean Ammous", "asin": "1119473861"},
    ],
    "Calendar & Time": [
        {"title": "Python Crash Course", "author": "Eric Matthes", "asin": "1718502702"},
    ],
    "Education": [
        {"title": "Learning Python", "author": "Mark Lutz", "asin": "1449355730"},
    ],
    "Email & Communication": [
        {"title": "APIs: A Strategy Guide", "author": "Daniel Jacobson", "asin": "1449308929"},
    ],
    "Security": [
        {"title": "Black Hat Python", "author": "Justin Seitz", "asin": "1718501129"},
        {"title": "The Web Application Hacker's Handbook", "author": "Dafydd Stuttard", "asin": "1118026470"},
    ],
    "Government": [
        {"title": "Open Data Now", "author": "Joel Gurin", "asin": "0071829776"},
    ],
    "Environment": [
        {"title": "Python for Data Analysis", "author": "Wes McKinney", "asin": "109810403X"},
    ],
    "Anime & Manga": [
        {"title": "The Anime Art Academy", "author": "Anime Art Academy", "asin": "B0C9ZPRW1C"},
    ],
    "Utilities": [
        {"title": "Designing Web APIs", "author": "Brenda Jin", "asin": "1492026921"},
    ],
    "Vehicles": [
        {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "asin": "1449373321"},
    ],
    "Open Data": [
        {"title": "Open Data Now", "author": "Joel Gurin", "asin": "0071829776"},
    ],
    "Online Courses": [
        {"title": "Ultralearning", "author": "Scott Young", "asin": "006285268X"},
        {"title": "Make It Stick", "author": "Peter C. Brown", "asin": "0674729013"},
    ],
    "Productivity": [
        {"title": "Getting Things Done", "author": "David Allen", "asin": "0143126563"},
        {"title": "Atomic Habits", "author": "James Clear", "asin": "0735211299"},
    ],
    "Student Essentials": [
        {"title": "A Mind for Numbers", "author": "Barbara Oakley", "asin": "039916524X"},
        {"title": "How to Become a Straight-A Student", "author": "Cal Newport", "asin": "0767922719"},
    ],
}

# Default books for categories without specific recommendations
DEFAULT_BOOKS = [
    {"title": "Designing Web APIs", "author": "Brenda Jin", "asin": "1492026921"},
    {"title": "RESTful Web APIs", "author": "Leonard Richardson", "asin": "1449358063"},
]

# Try HTML minification, but don't fail if not available
try:
    import htmlmin

    def minify_html(html: str) -> str:
        try:
            return htmlmin.minify(
                html,
                remove_comments=True,
                remove_empty_space=True,
                reduce_boolean_attributes=True,
            )
        except Exception as e:
            print(f"  ⚠️ Minification failed: {e}")
            return html
except ImportError:
    def minify_html(html: str) -> str:
        return html


def create_jinja_env() -> Environment:
    """Create and configure the Jinja2 template environment."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Register custom filters
    env.filters["slugify"] = slugify
    env.filters["truncate_text"] = truncate

    # Register global variables
    env.globals.update(
        {
            "site_name": SITE_NAME,
            "site_url": SITE_URL,
            "site_description": SITE_DESCRIPTION,
            "build_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "current_year": datetime.now(timezone.utc).year,
            "ga_measurement_id": GA_MEASUREMENT_ID,
            "adsense_publisher_id": ADSENSE_PUBLISHER_ID,
            "amazon_affiliate_tag": AMAZON_TAG,
            "enable_adsense": ENABLE_ADSENSE,
            "enable_amazon": ENABLE_AMAZON,
            "enable_pinterest": ENABLE_PINTEREST,
        }
    )

    return env


def copy_static_assets():
    """Copy static assets (CSS, JS, images, ads.txt, robots.txt) to dist/."""
    asset_dirs = ["css", "js", "images"]

    for asset_dir in asset_dirs:
        src = SRC_DIR / asset_dir
        dst = DIST_DIR / asset_dir
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # Copy root-level files
    for filename in ["ads.txt", "robots.txt", "_headers", "_redirects"]:
        src_file = SRC_DIR / filename
        if src_file.exists():
            shutil.copy2(src_file, DIST_DIR / filename)



def optimize_images():
    """Optimize images in the dist/images directory using Pillow."""
    images_dir = DIST_DIR / "images"
    if not images_dir.exists():
        return

    try:
        from PIL import Image
    except ImportError:
        print("  ⚠️ Pillow not installed. Skipping image optimization.")
        return

    print("  🖼 Optimizing images...")
    processed_count = 0
    total_saved = 0

    for img_path in images_dir.glob("*"):
        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                original_size = img_path.stat().st_size
                with Image.open(img_path) as img:
                    # Keep original format
                    fmt = img.format
                    
                    if fmt == "PNG":
                        # Optimize PNG
                        img.save(img_path, format=fmt, optimize=True)
                    elif fmt in ["JPEG", "JPG"]:
                        # Optimize JPEG/JPG
                        img.save(img_path, format=fmt, quality=85, optimize=True)
                    else:
                        # Other formats (WebP, etc.)
                        img.save(img_path, format=fmt, optimize=True)
                
                new_size = img_path.stat().st_size
                saved = original_size - new_size
                if saved > 0:
                    total_saved += saved
                    processed_count += 1
            except Exception as e:
                print(f"    ✗ Failed to optimize {img_path.name}: {e}")

    if processed_count > 0:
        print(f"    ✓ Optimized {processed_count} images (Saved {total_saved / 1024:.1f} KB)")
def build_item_pages(env: Environment, items: list, categories: dict):
    """Generate individual item pages.

    Args:
        env: Jinja2 environment.
        items: All items from the database.
        categories: Items grouped by category.
    """
    template = env.get_template("item.html")
    items_dir = DIST_DIR / "item"
    ensure_dir(items_dir)

    for item in items:
        if "auth" not in item:
            item["auth"] = "None"
        # Get related items from the same category (up to 6, excluding self)
        related = [
            i
            for i in categories.get(item["category"], [])
            if i["slug"] != item["slug"]
        ][:6]

        # Get book recommendations for this category
        raw_books = BOOK_RECOMMENDATIONS.get(item["category"], DEFAULT_BOOKS)
        books = [
            {
                "title": b["title"],
                "author": b["author"],
                "url": f"https://www.amazon.com/dp/{b['asin']}?tag={AMAZON_TAG}",
            }
            for b in raw_books
        ]

        html = template.render(
            item=item,
            related_items=related,
            recommended_books=books,
            page_title=f"{item['title']} - Free API | {SITE_NAME}",
            page_description=truncate(item["description"]),
            page_url=f"{SITE_URL}/item/{item['slug']}.html",
            canonical_url=f"{SITE_URL}/item/{item['slug']}.html",
        )

        output_path = items_dir / f"{item['slug']}.html"
        output_path.write_text(minify_html(html), encoding="utf-8")

    print(f"  ✓ Generated {len(items)} item pages → dist/item/")


def build_category_pages(env: Environment, categories: dict):
    """Generate category listing pages.

    Args:
        env: Jinja2 environment.
        categories: Items grouped by category.
    """
    template = env.get_template("category.html")
    cat_dir = DIST_DIR / "category"
    ensure_dir(cat_dir)

    all_categories = [
        {"name": name, "slug": slugify(name), "count": len(items)}
        for name, items in categories.items()
    ]

    for name, items in categories.items():
        cat_slug = slugify(name)

        html = template.render(
            category_name=name,
            category_slug=cat_slug,
            items=items,
            item_count=len(items),
            all_categories=all_categories,
            page_title=f"{name} APIs - Free & Open | {SITE_NAME}",
            page_description=f"Browse {len(items)} free {name} APIs. Find the best open APIs for {name.lower()} development.",
            page_url=f"{SITE_URL}/category/{cat_slug}.html",
            canonical_url=f"{SITE_URL}/category/{cat_slug}.html",
        )

        output_path = cat_dir / f"{cat_slug}.html"
        output_path.write_text(minify_html(html), encoding="utf-8")

    print(f"  ✓ Generated {len(categories)} category pages → dist/category/")


def build_index_page(env: Environment, items: list, categories: dict):
    """Generate the homepage.

    Args:
        env: Jinja2 environment.
        items: All items from the database.
        categories: Items grouped by category.
    """
    template = env.get_template("index.html")

    category_cards = [
        {"name": name, "slug": slugify(name), "count": len(cat_items)}
        for name, cat_items in categories.items()
    ]

    # Pick featured items (first 8 from the database)
    featured = items[:8]

    # Categories context
    html = template.render(
        categories=category_cards,
        featured_items=featured,
        total_apis=len(items),
        total_categories=len(categories),
        page_title=f"{SITE_NAME} — Discover Free & Open APIs",
        page_description=SITE_DESCRIPTION,
        page_url=SITE_URL,
        canonical_url=SITE_URL,
    )

    output_path = DIST_DIR / "index.html"
    output_path.write_text(minify_html(html), encoding="utf-8")
    print("  ✓ Generated homepage → dist/index.html")


def build_404_page(env: Environment):
    """Generate a custom 404 page."""
    template = env.get_template("404.html")

    html = template.render(
        page_title=f"Page Not Found | {SITE_NAME}",
        page_description="The page you're looking for doesn't exist.",
        page_url=f"{SITE_URL}/404.html",
        canonical_url=SITE_URL,
    )

    output_path = DIST_DIR / "404.html"
    output_path.write_text(minify_html(html), encoding="utf-8")
    print("  ✓ Generated 404 page → dist/404.html")


def build_site(database_path: Path = None):
    """Main build pipeline.

    Args:
        database_path: Optional path to database.json. Defaults to data/database.json.
    """
    print("🔨 Building static directory site...")

    # Load data
    items = load_database(database_path)
    if not items:
        print("  ✗ No items in database. Aborting build.")
        return

    categories = get_categories(items)

    # Clean and create dist directory
    if DIST_DIR.exists():
        # Clear contents inside dist (but don't remove the dir itself,
        # as it may be a Docker bind-mount)
        for child in DIST_DIR.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    ensure_dir(DIST_DIR)

    # Set up Jinja2
    env = create_jinja_env()

    # Build pages
    build_item_pages(env, items, categories)
    build_category_pages(env, categories)
    build_index_page(env, items, categories)
    build_404_page(env)

    # Copy static assets
    copy_static_assets()
    

    # Optimize images
    optimize_images()
    # Search Index Generation
    search_items = []
    for item in items:
        title = item.get('name', item.get('title', 'Unknown'))
        desc = item.get('description', '')
        cat = item.get('category', '')
        link = f"/item/{item['slug']}.html"
        search_items.append({'title': title, 'description': desc, 'category': cat, 'url': link})
        
    import json
    (DIST_DIR / "search.json").write_text(json.dumps(search_items), encoding="utf-8")

    # RSS Feed Generation
    rss_items = []
    for item in items[:20]:
        title = item.get('name', item.get('title', 'Unknown'))
        desc = item.get('description', '')
        link = f"{SITE_URL}/item/{item['slug']}.html"
        rss_items.append({'title': title, 'description': desc, 'link': link})
        
    rss_content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>{SITE_NAME}</title>
  <link>{SITE_URL}</link>
  <description>{SITE_DESCRIPTION}</description>
'''
    for item in rss_items:
        rss_content += f'''  <item>
    <title>{item['title']}</title>
    <link>{item['link']}</link>
    <description>{item['description']}</description>
    <guid>{item['link']}</guid>
  </item>
'''
    rss_content += '''</channel>
</rss>'''
    (DIST_DIR / "feed.xml").write_text(rss_content, encoding="utf-8")

    print("  ✓ Copied static assets (CSS, JS, images)")

    print(
        f"✅ Build complete: {len(items)} items, {len(categories)} categories, "
        f"{len(items) + len(categories) + 2} total pages."
    )


def main():
    build_site()


if __name__ == "__main__":
    main()
