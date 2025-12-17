---
name: "python-uv-setup"
description: "Sets up Python projects using uv (ultra-fast Python package manager). Configures pyproject.toml, manages virtual environments, handles dependencies, and integrates with modern Python tooling. Use when initializing Python projects or migrating from pip/poetry to uv."
version: "1.0.0"
---

# Python UV Setup Skill

## When to Use
- User says "Set up Python with uv" or "Initialize uv project"
- Starting a new Python project
- Migrating from pip/poetry/pipenv to uv
- Need fast dependency resolution and installation
- Want modern Python project structure with pyproject.toml
- Setting up Python monorepo packages

## Context
This skill configures Python projects using **uv**, an extremely fast Python package manager written in Rust:
- **Speed**: 10-100x faster than pip
- **Modern**: Uses pyproject.toml (PEP 517/518)
- **Compatible**: Drop-in replacement for pip, pip-tools, virtualenv
- **Lock Files**: Deterministic builds with uv.lock
- **Tool Management**: Built-in tool execution (like pipx)

## Workflow

### 1. Install uv
Check if uv is installed, install if needed

### 2. Initialize Project
Create pyproject.toml with metadata and dependencies

### 3. Configure Virtual Environment
Set up isolated Python environment

### 4. Add Dependencies
Install and lock dependencies

### 5. Configure Tools
Set up ruff, mypy, pytest, black

## Output Format

### Installation

**Windows (PowerShell)**:
```powershell
# Install uv
irm https://astral.sh/uv/install.ps1 | iex

# Verify installation
uv --version
```

**Unix/macOS**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

**Alternative (pip)**:
```bash
pip install uv
```

---

### Project Initialization

**New Project**:
```bash
# Create new project with uv
uv init my-project
cd my-project

# This creates:
# ├── pyproject.toml
# ├── .python-version
# └── src/
#     └── my_project/
#         └── __init__.py
```

**Existing Project**:
```bash
# Initialize in existing directory
cd existing-project
uv init

# Or just create pyproject.toml manually
```

---

### pyproject.toml Template

**Basic Template**:
```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.8",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**FastAPI Backend Template**:
```toml
[project]
name = "todo-backend"
version = "0.1.0"
description = "Todo App FastAPI Backend"
authors = [{name = "Developer", email = "dev@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.8",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

---

### Virtual Environment Management

**Create Virtual Environment**:
```bash
# uv creates .venv automatically on first install
uv venv

# Or specify Python version
uv venv --python 3.11

# Or specify custom path
uv venv .venv-custom
```

**Activate Virtual Environment**:
```bash
# Windows
.venv\Scripts\activate

# Unix/macOS
source .venv/bin/activate
```

**Using uv run (No Activation Needed)**:
```bash
# Run commands in venv without activation
uv run python script.py
uv run pytest
uv run uvicorn app.main:app --reload
```

---

### Dependency Management

**Add Dependencies**:
```bash
# Add production dependency
uv add fastapi

# Add with version constraint
uv add "fastapi>=0.100.0"

# Add multiple packages
uv add fastapi uvicorn sqlmodel

# Add dev dependency
uv add --dev pytest ruff mypy

# Add optional dependency group
uv add --optional test pytest pytest-cov
```

**Install Dependencies**:
```bash
# Install all dependencies from pyproject.toml
uv sync

# Install including dev dependencies
uv sync --dev

# Install from requirements.txt
uv pip install -r requirements.txt
```

**Update Dependencies**:
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add --upgrade fastapi
```

**Remove Dependencies**:
```bash
uv remove fastapi
```

**Lock Dependencies**:
```bash
# Generate uv.lock file
uv lock

# Install from lock file
uv sync --frozen
```

---

### Tool Execution

**Run Tools Without Installing Globally**:
```bash
# Run black
uv run black .

# Run pytest
uv run pytest tests/

# Run mypy
uv run mypy app/

# Run ruff
uv run ruff check .

# Run custom script
uv run python scripts/migrate.py
```

**Run Specific Tool Version**:
```bash
# Run specific version without installing
uv tool run ruff@0.1.0 check .

# Run tool from git
uv tool run --from git+https://github.com/user/repo.git tool-name
```

---

### Migration from Other Tools

**From pip + requirements.txt**:
```bash
# Install uv
pip install uv

# Create pyproject.toml
uv init

# Convert requirements.txt
uv add $(cat requirements.txt)

# Or import directly
uv pip install -r requirements.txt
```

**From Poetry**:
```bash
# Poetry uses pyproject.toml, so it's mostly compatible
# Just install dependencies with uv
uv sync

# If using poetry.lock, regenerate with uv
uv lock
```

**From Pipenv**:
```bash
# Export Pipfile to requirements.txt
pipenv requirements > requirements.txt

# Install with uv
uv pip install -r requirements.txt

# Create pyproject.toml
uv init
uv add $(cat requirements.txt)
```

---

### Project Structure

**Recommended Structure**:
```
my-project/
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Lock file (generated)
├── .python-version         # Python version specification
├── README.md
├── .gitignore
├── .venv/                  # Virtual environment (in .gitignore)
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── scripts/
    └── migrate.py
```

**.gitignore**:
```
# Virtual environments
.venv/
venv/
env/

# uv
uv.lock

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

### Common Commands Cheat Sheet

```bash
# Project Setup
uv init                    # Initialize new project
uv venv                    # Create virtual environment
uv sync                    # Install dependencies

# Dependency Management
uv add <package>           # Add dependency
uv add --dev <package>     # Add dev dependency
uv remove <package>        # Remove dependency
uv lock                    # Generate lock file
uv sync --frozen           # Install from lock file

# Running Commands
uv run <command>           # Run command in venv
uv run python script.py    # Run Python script
uv run pytest              # Run tests
uv run uvicorn app:app     # Run server

# Tool Execution
uv tool run ruff check .   # Run tool without installing

# Updates
uv sync --upgrade          # Update all dependencies
uv add --upgrade <pkg>     # Update specific package

# Information
uv pip list                # List installed packages
uv pip show <package>      # Show package info
uv --version               # Check uv version
```

---

### Example: FastAPI Project Setup

**Step 1: Create Project**
```bash
mkdir todo-backend
cd todo-backend
uv init
```

**Step 2: Add Dependencies**
```bash
uv add fastapi uvicorn[standard] sqlmodel pydantic-settings alembic
uv add --dev pytest pytest-asyncio httpx ruff mypy black
```

**Step 3: Create Project Structure**
```bash
mkdir -p app/{models,schemas,routers}
mkdir tests

# Create files
touch app/__init__.py
touch app/main.py
touch app/database.py
```

**Step 4: Install Dependencies**
```bash
uv sync
```

**Step 5: Run Development Server**
```bash
uv run uvicorn app.main:app --reload
```

---

### Example: Python Library Setup

**pyproject.toml for Library**:
```toml
[project]
name = "my-library"
version = "0.1.0"
description = "A useful library"
authors = [{name = "Author", email = "author@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]

[project.urls]
Homepage = "https://github.com/user/my-library"
Documentation = "https://my-library.readthedocs.io"
Repository = "https://github.com/user/my-library.git"
Issues = "https://github.com/user/my-library/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_library"]
```

**Build and Publish**:
```bash
# Build package
uv run python -m build

# Check distribution
uv run twine check dist/*

# Upload to PyPI
uv run twine upload dist/*
```

---

### Integration with CI/CD

**GitHub Actions**:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Set up Python
        run: uv venv --python 3.11

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run pytest

      - name: Run linting
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy app/
```

---

### Performance Comparison

**Installation Speed**:
```
Installing 100 packages:
- pip: 45 seconds
- poetry: 60 seconds
- uv: 2 seconds (20-30x faster)
```

**Dependency Resolution**:
```
Resolving complex dependency graph:
- pip: 120 seconds
- poetry: 90 seconds
- uv: 3 seconds (30-40x faster)
```

---

### Troubleshooting

**Issue: uv not found**
```bash
# Add uv to PATH
# Windows: Add %USERPROFILE%\.cargo\bin to PATH
# Unix: Add ~/.cargo/bin to PATH

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Issue: Python version not found**
```bash
# Specify Python path
uv venv --python /path/to/python3.11

# Or install Python with uv
uv python install 3.11
```

**Issue: Lock file conflicts**
```bash
# Regenerate lock file
rm uv.lock
uv lock
```

**Issue: Package not found**
```bash
# Update package index
uv sync --upgrade

# Or specify index URL
uv add --index-url https://pypi.org/simple package-name
```

---

### Best Practices

1. **Always Use Lock Files**
   - Commit `uv.lock` to version control
   - Use `uv sync --frozen` in CI/CD

2. **Separate Dev Dependencies**
   - Use `[project.optional-dependencies]` for dev tools
   - Keep production dependencies minimal

3. **Use uv run Instead of Activation**
   - Simpler workflow
   - Works in CI/CD without activation

4. **Pin Python Version**
   - Create `.python-version` file
   - Ensures consistency across environments

5. **Regular Updates**
   - Run `uv sync --upgrade` periodically
   - Test after updates

## Quality Checklist

Before finalizing uv setup:
- [ ] uv installed and in PATH
- [ ] pyproject.toml created with correct metadata
- [ ] Dependencies added (production and dev)
- [ ] Virtual environment created (.venv)
- [ ] Lock file generated (uv.lock)
- [ ] .gitignore includes .venv and __pycache__
- [ ] README.md includes setup instructions
- [ ] CI/CD configured to use uv
- [ ] Python version pinned (.python-version)
- [ ] All commands tested (uv sync, uv run)

## Post-Setup

After setting up uv:
1. **Test Installation**: Run `uv run python --version`
2. **Run Tests**: Execute `uv run pytest`
3. **Verify Linting**: Run `uv run ruff check .`
4. **Update README**: Document uv setup for team
5. **Configure IDE**: Set Python interpreter to `.venv/bin/python`
6. **Train Team**: Share uv commands cheat sheet
