# build_public_pages.py
import os
import yaml
import json

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_index_page():
    """Generate simple directory listing"""
    links = []
    base_url = "https://raw.githubusercontent.com/DFYRANKINGS/diditan-group-ai-data/main"

    for root, dirs, files in os.walk("schema-files"):
        for file in files:
            if file.endswith((".json", ".yaml", ".md", ".llm")):
                filepath = os.path.join(root, file).replace("\\", "/")
                urlpath = filepath
                full_url = f"{base_url}/{urlpath}"
                display_path = filepath.replace("schema-files/", "")
                links.append(f'<li><a href="{full_url}" target="_blank">{escape_html(display_path)}</a></li>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Data Directory</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 10px 0; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Data Directory</h1>
        <p>Browse machine-readable structured data for search engines and AI assistants.</p>
    </div>
    <h2>📁 All Schema Files</h2>
    <ul>
{''.join(sorted(links))}
    </ul>
    <p><em>Last updated: {os.popen('date -u "+%Y-%m-%d %H:%M UTC"').read().strip()}</em></p>
</body>
</html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html generated")

def generate_faq_page():
    """Generate a human-friendly FAQ page from faq schemas"""
    faqs = []
    faq_dir = "schema-files/faqs"
    
    if not os.path.exists(faq_dir):
        print("⚠️ No FAQs found — skipping faq.html")
        return

    for file in os.listdir(faq_dir):
        if file.endswith(".yaml") or file.endswith(".json"):
            filepath = os.path.join(faq_dir, file)
            try:
                data = load_yaml(filepath) if file.endswith(".yaml") else load_json(filepath)
                if isinstance(data, list):
                    faqs.extend(data)
                elif isinstance(data, dict):
                    faqs.append(data)
            except Exception as e:
                print(f"❌ Error loading {filepath}: {e}")

    if not faqs:
        print("⚠️ No FAQ content loaded — skipping faq.html")
        return

    # Build HTML Q&A
    qa_blocks = []
    for item in faqs:
        question = escape_html(str(item.get("question", item.get("name", "Untitled"))))
        answer = escape_html(str(item.get("answer", item.get("description", "No answer provided."))))
        qa_blocks.append(f"""
        <div style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50;">{question}</h3>
            <p>{answer}</p>
        </div>
        """)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FAQs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <h1>❓ Frequently Asked Questions</h1>
    {''.join(qa_blocks)}
    <p><em>Last updated: {os.popen('date -u "+%Y-%m-%d %H:%M UTC"').read().strip()}</em></p>
</body>
</html>"""

    with open("faqs.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ faqs.html generated")

def generate_help_articles_page():
    """Generate help articles page from markdown or schema files"""
    articles = []
    help_dir = "schema-files/help-articles"
    
    if not os.path.exists(help_dir):
        print("⚠️ No help articles found — skipping help.html")
        return

    for file in os.listdir(help_dir):
        if file.endswith(".md"):
            filepath = os.path.join(help_dir, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                title = file.replace(".md", "").replace("-", " ").title()
                # Simple MD to HTML (just paragraphs for now)
                paragraphs = "\n".join(f"<p>{escape_html(p)}</p>" for p in content.split("\n\n") if p.strip())
                articles.append(f"""
                <article style="margin: 40px 0; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                    <h2>{escape_html(title)}</h2>
                    {paragraphs}
                </article>
                """)

    if not articles:
        print("⚠️ No help articles loaded — skipping help.html")
        return

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Help Articles</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.7; }}
        h1 {{ color: #2c3e50; }}
        article {{ background: #fff; }}
    </style>
</head>
<body>
    <h1>📘 Help Articles</h1>
    {''.join(articles)}
    <p><em>Last updated: {os.popen('date -u "+%Y-%m-%d %H:%M UTC"').read().strip()}</em></p>
</body>
</html>"""

    with open("help.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ help.html generated")

if __name__ == "__main__":
    generate_index_page()
    generate_faq_page()
    generate_help_articles_page()
