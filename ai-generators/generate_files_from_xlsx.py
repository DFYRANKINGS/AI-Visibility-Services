import os
import pandas as pd
import yaml
import json
import re

def slugify(text):
    """Generate clean filename from text"""
    if not text:
        return "untitled"
    # Keep only alphanumeric + hyphens
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text))
    # Replace spaces with hyphens
    text = re.sub(r'[\s]+', '-', text.strip().lower())
    return text or "untitled"

# ... [your existing code above] ...

# ➤ FIND AND REPLACE THE "help-articles" SECTION

if 'help-articles' in xls.sheet_names:
    print("📄 Processing help-articles sheet...")
    df_help = xls.parse('help-articles')
    output_dir = "schemas/help-articles"
    os.makedirs(output_dir, exist_ok=True)

    for idx, row in df_help.iterrows():
        # Get title and slug — fallback to index if missing
        title = str(row.get('title', '')).strip()
        slug = str(row.get('slug', '')).strip()

        # Generate unique filename
        if not slug:
            slug = slugify(title) if title else f"article-{idx+1}"

        # Ensure unique filename (in case slugs collide)
        base_slug = slug
        counter = 1
        filename = f"{slug}.md"
        filepath = os.path.join(output_dir, filename)

        while os.path.exists(filepath):
            filename = f"{base_slug}-{counter}.md"
            filepath = os.path.join(output_dir, filename)
            counter += 1

        # Get content
        content = str(row.get('content', '')).strip()

        # Write .md file
        with open(filepath, 'w', encoding='utf-8') as f:
            # Optional: Add YAML frontmatter
            f.write(f"---\n")
            f.write(f"title: {title}\n")
            if slug:
                f.write(f"slug: {slug}\n")
            f.write(f"---\n\n")
            f.write(content)

        print(f"✅ Generated: {filepath}")
