import os
import pandas as pd
import yaml
import json
import re
import sys

def slugify(text):
    """Generate clean, URL-friendly slug from text"""
    if not text:
        return "untitled"
    # Remove invalid characters
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text))
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[\s]+', '-', text.strip().lower())
    return text or "untitled"

def main(input_file="templates/client-data.xlsx"):
    print(f"📂 Opening Excel file: {input_file}")
    
    try:
        xls = pd.ExcelFile(input_file)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        sys.exit(1)

    # Process each sheet
    for sheet_name in xls.sheet_names:
        print(f"\n📄 Processing sheet: {sheet_name}")
        df = xls.parse(sheet_name)
        
        # Skip empty sheets
        if df.empty:
            print(f"⚠️  Sheet '{sheet_name}' is empty — skipping")
            continue

        # Define output directory
        output_dir = f"schemas/{sheet_name}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")

        # Process rows
        for idx, row in df.iterrows():
            # Skip empty rows
            if row.dropna().empty:
                continue

            # HELP ARTICLES — SPECIAL HANDLING FOR UNIQUE FILENAMES
            if sheet_name == "help-articles":
                title = str(row.get('title', '')).strip()
                slug = str(row.get('slug', '')).strip()
                content = str(row.get('content', '')).strip()

                # Generate unique filename
                if not slug:
                    slug = slugify(title) if title else f"article-{idx+1}"

                base_slug = slug
                counter = 1
                filename = f"{slug}.md"
                filepath = os.path.join(output_dir, filename)

                # Avoid filename collisions
                while os.path.exists(filepath):
                    filename = f"{base_slug}-{counter}.md"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                # Write Markdown file with frontmatter
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("---\n")
                        if title:
                            f.write(f"title: {title}\n")
                        f.write(f"slug: {slug}\n")
                        f.write("---\n\n")
                        f.write(content)
                    print(f"✅ Generated: {filepath}")
                except Exception as e:
                    print(f"❌ Failed to write {filepath}: {e}")

            # ALL OTHER SHEETS — USE SIMPLE INDEX-BASED NAMING (or ID if available)
            else:
                # Try to get a unique identifier
                id_field = None
                for key in ['id', 'service_id', 'faq_id', 'review_id', 'slug', 'name', 'title']:
                    if key in row and pd.notna(row[key]):
                        id_field = str(row[key]).strip()
                        break
                
                if not id_field:
                    id_field = f"item-{idx+1}"

                # Clean filename
                safe_id = slugify(id_field)
                base_id = safe_id
                counter = 1
                filename = f"{safe_id}.json"
                filepath = os.path.join(output_dir, filename)

                # Avoid filename collisions
                while os.path.exists(filepath):
                    filename = f"{base_id}-{counter}.json"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                # Convert row to dict and save as JSON
                item_data = {}
                for col in df.columns:
                    value = row[col]
                    # Handle NaN/NaT
                    if pd.isna(value):
                        continue
                    # Convert numpy types to native Python
                    if hasattr(value, 'item'):
                        value = value.item()
                    item_data[col] = value

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(item_data, f, indent=2, ensure_ascii=False, default=str)
                    print(f"✅ Generated: {filepath}")
                except Exception as e:
                    print(f"❌ Failed to write {filepath}: {e}")

    print("\n🎉 All files generated successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate schema files from Excel.')
    parser.add_argument('--input', type=str, default='templates/client-data.xlsx',
                        help='Path to input Excel file')
    args = parser.parse_args()
    main(args.input)
