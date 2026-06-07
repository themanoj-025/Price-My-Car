"""Render README.md to HTML and open in browser for visual preview."""
import markdown
import os

md_path = os.path.join(os.path.dirname(__file__), 'README.md')
html_path = os.path.join(os.path.dirname(__file__), '_readme_preview.html')

with open(md_path, 'r', encoding='utf-8') as f:
    md = f.read()

body = markdown.markdown(md, extensions=['fenced_code', 'tables', 'codehilite'])

html = f'''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>README Preview</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css">
<style>
.markdown-body {{ max-width: 960px; margin: 40px auto; padding: 20px; }}
body {{ background: #0d1117; }}
</style>
</head><body>
<article class="markdown-body">
{body}
</article>
</body></html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Preview written to: {html_path}")
