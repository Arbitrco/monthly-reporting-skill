# --- Python ---
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.Python
.venv/
venv/
env/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/

# --- Editor / OS ---
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo
*~

# --- Skill runtime artifacts ---
# Created at the working directory of whoever runs the skill — never committed
# upstream. If you fork and want to commit your sections, remove sections/ below.
reports/
fragments/
preview/

# Local brand override — usually user-specific. If you want to commit your
# brand config to your fork, remove this line.
brand.json

# Sections you author live in sections/. Comment out the line below if you
# want to commit your custom sections to your fork (recommended).
#sections/

# --- WeasyPrint debug output ---
*.weasyprint
