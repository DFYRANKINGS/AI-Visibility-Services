import os
import pandas as pd
import json
import re
import sys

def slugify(text):
    """Generate clean, URL-friendly slug from text"""
    if not text:
        return "untitled"
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', str(text))
    text = re.sub(r'[\s]+', '-', text.strip().lower())
    return text or "untitled"

def main(input_file="templates/client-data.xlsx"):
    print(f"📂 Opening Excel file: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ FATAL: Excel file not found at {input_file}")
        sys.exit(1)
    else:
        print(f"✅ Excel file confirmed at: {input_file}")

    try:
        xlsx = pd.ExcelFile(input_file)
        print(f"📄 Available sheets in workbook: {xlsx.sheet_names}")
    except Exception as e:
        print(f"❌ Failed to load Excel file: {e}")
        sys.exit(1)

    # Map your actual sheet names to output dirs
    sheet_config = {
        "organization": "schemas/organization",
        "Services": "schemas/Services",           # ← Match folder case
        "Products": "schemas/products",
        "FAQs": "schemas/FAQs",                   # ← Match folder case
        "Help Articles": "schemas/Help Articles", # ← Match folder case
        "Reviews": "schemas/Reviews",
        "Locations": "schemas/Locations",
        "Team": "schemas/team",
        "Awards & Certifications": "schemas/awards",
        "Press/News Mentions": "schemas/press",
        "Case Studies": "schemas/case-studies",
        "core_info": "schemas/core-info"
    }

    for sheet_name in xlsx.sheet_names:
        if sheet_name not in sheet_config:
            print(f"⚠️ Skipping unsupported sheet: {sheet_name}")
            continue

        print(f"\n📄 Processing sheet: {sheet_name}")
        df = xlsx.parse(sheet_name)
        
        # CLEAN COLUMN NAMES — strip whitespace
        df.columns = df.columns.str.strip()
        print(f"🧹 Cleaned column names: {list(df.columns)}")

        if df.empty:
            print(f"⚠️ Sheet '{sheet_name}' is empty — skipping")
            continue

        # Ensure output_dir is relative to repo root, not ai-generators/
        output_dir = os.path.join("..", sheet_config[sheet_name])
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory (ABSOLUTE): {os.path.abspath(output_dir)}")
        print(f"📁 Output directory (RELATIVE): {output_dir}")

        processed_count = 0

        for idx, row in df.iterrows():
            # Skip completely empty rows
            if row.dropna().empty:
                continue

            # HELP ARTICLES — SPECIAL HANDLING
            if sheet_name == "Help Articles":
                title = str(row.get('title', '')).strip()
                slug = str(row.get('slug', '')).strip()
                content = str(row.get('article', '')).strip()  # ← Uses 'article' column

                # DEBUG PRINT
                print(f"📄 ROW {idx+1} → title='{title}' | slug='{slug}' | content_length={len(content)}")

                # Skip if both title and content are empty
                if not title and not content:
                    print(f"⚠️ Skipping row {idx+1}: no title or content")
                    continue

                if not slug:
                    slug = slugify(title) if title else f"article-{idx+1}"

                base_slug = slug
                counter = 1
                filename = f"{slug}.md"
                filepath = os.path.join(output_dir, filename)

                while os.path.exists(filepath):
                    filename = f"{base_slug}-{counter}.md"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("---\n")
                        if title:
                            f.write(f"title: {title}\n")
                        f.write(f"slug: {slug}\n")
                        f.write("---\n\n")
                        f.write(content)
                    print(f"✅ Generated: {filepath}")
                    processed_count += 1
                except Exception as e:
                    print(f"❌ Failed to write {filepath}: {e}")

            # FAQs
            elif sheet_name == "FAQs":
                question = str(row.get('question', '')).strip()
                answer = str(row.get('answer', '')).strip()

                if not question:
                    question = f"Untitled FAQ {idx+1}"

                safe_id = slugify(question)
                base_id = safe_id
                counter = 1
                filename = f"{safe_id}.json"
                filepath = os.path.join(output_dir, filename)

                while os.path.exists(filepath):
                    filename = f"{base_id}-{counter}.json"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                item_data = {
                    "question": question,
                    "answer": answer
                }

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(item_data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Generated: {filepath}")
                    processed_count += 1
                except Exception as e:
                    print(f"❌ Failed to write {filepath}: {e}")

            # ALL OTHER SHEETS
            else:
                id_field = None
                for key in ['service_id', 'product_id', 'faq_id', 'review_id', 'location_id', 'case_id', 'slug', 'name', 'title']:
                    if key in row and pd.notna(row[key]):
                        id_field = str(row[key]).strip()
                        break
                
                if not id_field:
                    id_field = f"item-{idx+1}"

                safe_id = slugify(id_field)
                base_id = safe_id
                counter = 1
                filename = f"{safe_id}.json"
                filepath = os.path.join(output_dir, filename)

                while os.path.exists(filepath):
                    filename = f"{base_id}-{counter}.json"
                    filepath = os.path.join(output_dir, filename)
                    counter += 1

                item_data = {}
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        continue
                    if hasattr(value, 'item'):
                        value = value.item()
                    item_data[col] = value

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(item_data, f, indent=2, ensure_ascii=False, default=str)
                    print(f"✅ Generated: {filepath}")
                    processed_count += 1
                except Exception as e:
                    print(f"❌ Failed to write {filepath}: {e}")

        print(f"📊 Total processed in '{sheet_name}': {processed_count} items")

    print("\n🎉 All files generated successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate schema files from Excel.')
    parser.add_argument('--input', type=str, default='templates/client-data.xlsx',
                        help='Path to input Excel file')
    args = parser.parse_args()
    main(args.input)
