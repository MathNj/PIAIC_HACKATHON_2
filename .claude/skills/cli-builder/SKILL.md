---
name: "cli-builder"
description: "Builds command-line interface (CLI) applications using Click, Typer, or argparse. Creates commands, subcommands, options, arguments, and help documentation. Use when building CLI tools, scripts, or Phase I applications."
version: "1.0.0"
---

# CLI Builder Skill

## When to Use
- User says "Create CLI" or "Build command-line tool"
- Phase I development (monolithic CLI application)
- Need to scaffold CLI commands with arguments and options
- Building developer tools or automation scripts
- Want professional CLI with auto-generated help
- Need command groups and subcommands

## Context
This skill creates CLI applications using Python frameworks:
- **Typer**: Modern, type-hint based (recommended for new projects)
- **Click**: Mature, decorator-based
- **argparse**: Standard library (no dependencies)
- **Fire**: Automatic CLI from Python objects

## Workflow

### 1. Choose CLI Framework
- **Typer**: For modern Python with type hints
- **Click**: For maximum flexibility and ecosystem
- **argparse**: For no external dependencies
- **Fire**: For quick prototypes

### 2. Design Command Structure
- Single command or command groups
- Arguments (positional parameters)
- Options (flags and named parameters)
- Subcommands if needed

### 3. Implement Commands
- Add command logic
- Handle errors gracefully
- Provide helpful messages

### 4. Add Help Documentation
- Command descriptions
- Argument/option help text
- Examples

## Output Format

### Typer (Recommended)

**Installation**:
```bash
uv add typer[all]  # Includes rich for beautiful output
```

**Basic CLI**:
```python
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def hello(
    name: str = typer.Argument(..., help="Name to greet"),
    formal: bool = typer.Option(False, "--formal", "-f", help="Use formal greeting")
):
    """Greet someone."""
    if formal:
        typer.echo(f"Good day, {name}.")
    else:
        typer.echo(f"Hello, {name}!")

@app.command()
def goodbye(
    name: str,
    see_you: bool = typer.Option(False, help="Say 'see you' instead")
):
    """Say goodbye."""
    if see_you:
        typer.echo(f"See you later, {name}!")
    else:
        typer.echo(f"Goodbye, {name}!")

if __name__ == "__main__":
    app()
```

**Usage**:
```bash
python cli.py hello John
python cli.py hello --formal Alice
python cli.py goodbye Bob --see-you
python cli.py --help
```

---

### Example 1: Todo CLI (Typer)

**File**: `todo.py`
```python
import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
import json

app = typer.Typer(
    name="todo",
    help="A simple todo list manager",
    add_completion=False
)
console = Console()

# Data file path
TODO_FILE = Path.home() / ".todo" / "tasks.json"
TODO_FILE.parent.mkdir(exist_ok=True)

def load_tasks() -> List[dict]:
    """Load tasks from JSON file."""
    if TODO_FILE.exists():
        return json.loads(TODO_FILE.read_text())
    return []

def save_tasks(tasks: List[dict]):
    """Save tasks to JSON file."""
    TODO_FILE.write_text(json.dumps(tasks, indent=2))

@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority")
):
    """List all tasks."""
    tasks = load_tasks()

    # Apply filters
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if priority:
        tasks = [t for t in tasks if t.get("priority") == priority]

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    # Create table
    table = Table(title="📋 Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")

    for idx, task in enumerate(tasks, 1):
        priority_color = {"high": "red", "normal": "yellow", "low": "green"}.get(
            task.get("priority", "normal"), "white"
        )
        status_icon = {"pending": "⭕", "in_progress": "⏳", "completed": "✅"}.get(
            task.get("status", "pending"), "❓"
        )

        table.add_row(
            str(idx),
            task["title"],
            f"[{priority_color}]{task.get('priority', 'normal').upper()}[/{priority_color}]",
            f"{status_icon} {task.get('status', 'pending').title()}"
        )

    console.print(table)

@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Task description"),
    priority: str = typer.Option("normal", "--priority", "-p", help="Priority: low, normal, high"),
    due_date: Optional[str] = typer.Option(None, "--due", help="Due date (YYYY-MM-DD)")
):
    """Add a new task."""
    tasks = load_tasks()

    task = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "due_date": due_date
    }

    tasks.append(task)
    save_tasks(tasks)

    console.print(f"[green]✓ Task added: {title}[/green]")

@app.command("complete")
def complete_task(
    task_id: int = typer.Argument(..., help="Task ID to complete")
):
    """Mark a task as completed."""
    tasks = load_tasks()

    if task_id < 1 or task_id > len(tasks):
        console.print(f"[red]✗ Task ID {task_id} not found.[/red]")
        raise typer.Exit(code=1)

    tasks[task_id - 1]["status"] = "completed"
    save_tasks(tasks)

    console.print(f"[green]✓ Task {task_id} marked as completed.[/green]")

@app.command("delete")
def delete_task(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Delete a task."""
    tasks = load_tasks()

    if task_id < 1 or task_id > len(tasks):
        console.print(f"[red]✗ Task ID {task_id} not found.[/red]")
        raise typer.Exit(code=1)

    task_title = tasks[task_id - 1]["title"]

    if not force:
        confirm = typer.confirm(f"Delete task '{task_title}'?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    del tasks[task_id - 1]
    save_tasks(tasks)

    console.print(f"[green]✓ Task deleted: {task_title}[/green]")

@app.command("clear")
def clear_all(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Clear all tasks."""
    if not force:
        confirm = typer.confirm("Delete ALL tasks?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    save_tasks([])
    console.print("[green]✓ All tasks cleared.[/green]")

if __name__ == "__main__":
    app()
```

**Usage**:
```bash
# Add tasks
python todo.py add "Buy groceries" --priority high --due 2025-12-20
python todo.py add "Write code" -d "Implement new feature" -p normal

# List tasks
python todo.py list
python todo.py list --status pending
python todo.py list --priority high

# Complete task
python todo.py complete 1

# Delete task
python todo.py delete 2
python todo.py delete 2 --force

# Clear all
python todo.py clear --force
```

---

### Click Framework

**Installation**:
```bash
uv add click
```

**Basic CLI**:
```python
import click

@click.group()
def cli():
    """Todo CLI application."""
    pass

@cli.command()
@click.argument('title')
@click.option('--priority', '-p', default='normal', help='Task priority')
def add(title, priority):
    """Add a new task."""
    click.echo(f"Adding task: {title} (priority: {priority})")

@cli.command()
@click.option('--status', '-s', help='Filter by status')
def list(status):
    """List all tasks."""
    click.echo("Listing tasks...")

if __name__ == '__main__':
    cli()
```

---

### Example 2: Database CLI Tool

```python
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Database management CLI")
console = Console()

@app.command()
def migrate(
    direction: str = typer.Argument("up", help="Migration direction: up or down"),
    steps: int = typer.Option(1, "--steps", "-n", help="Number of migrations to run"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show migrations without running")
):
    """Run database migrations."""
    if direction not in ["up", "down"]:
        console.print("[red]Error: direction must be 'up' or 'down'[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[yellow]DRY RUN: Would run {steps} migrations {direction}[/yellow]")
    else:
        console.print(f"[green]Running {steps} migrations {direction}...[/green]")
        # Migration logic here

@app.command()
def seed(
    table: Optional[str] = typer.Option(None, "--table", "-t", help="Specific table to seed"),
    clear: bool = typer.Option(False, "--clear", help="Clear table before seeding")
):
    """Seed database with sample data."""
    if clear:
        console.print("[yellow]Clearing existing data...[/yellow]")

    if table:
        console.print(f"[green]Seeding table: {table}[/green]")
    else:
        console.print("[green]Seeding all tables...[/green]")

@app.command()
def backup(
    output: str = typer.Option("backup.sql", "--output", "-o", help="Backup file path"),
    compress: bool = typer.Option(False, "--compress", "-c", help="Compress backup")
):
    """Create database backup."""
    console.print(f"[green]Creating backup: {output}[/green]")
    if compress:
        console.print("[cyan]Compressing...[/cyan]")

@app.command()
def status():
    """Show database status."""
    table = Table(title="Database Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Status", "✅ Connected")
    table.add_row("Migrations", "5/5 applied")
    table.add_row("Tables", "12")
    table.add_row("Size", "245 MB")

    console.print(table)

if __name__ == "__main__":
    app()
```

**Usage**:
```bash
python db.py migrate up --steps 3
python db.py migrate down --dry-run
python db.py seed --table users --clear
python db.py backup --output backup.sql --compress
python db.py status
```

---

### Example 3: Git-Style Subcommands

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

# User management commands
user_app = typer.Typer(help="User management commands")
app.add_typer(user_app, name="user")

@user_app.command("create")
def user_create(
    username: str,
    email: str,
    admin: bool = typer.Option(False, "--admin", help="Create as admin")
):
    """Create a new user."""
    role = "admin" if admin else "user"
    console.print(f"[green]Creating {role}: {username} ({email})[/green]")

@user_app.command("delete")
def user_delete(
    username: str,
    force: bool = typer.Option(False, "--force", "-f")
):
    """Delete a user."""
    if not force:
        confirm = typer.confirm(f"Delete user '{username}'?")
        if not confirm:
            return

    console.print(f"[red]Deleting user: {username}[/red]")

@user_app.command("list")
def user_list(
    active_only: bool = typer.Option(False, "--active-only", help="Show only active users")
):
    """List all users."""
    filter_text = " (active only)" if active_only else ""
    console.print(f"[cyan]Listing users{filter_text}[/cyan]")

# Task commands
task_app = typer.Typer(help="Task management commands")
app.add_typer(task_app, name="task")

@task_app.command("create")
def task_create(title: str, assignee: Optional[str] = None):
    """Create a new task."""
    console.print(f"[green]Creating task: {title}[/green]")
    if assignee:
        console.print(f"[cyan]Assigned to: {assignee}[/cyan]")

@task_app.command("list")
def task_list(user: Optional[str] = None):
    """List tasks."""
    if user:
        console.print(f"[cyan]Listing tasks for: {user}[/cyan]")
    else:
        console.print("[cyan]Listing all tasks[/cyan]")

if __name__ == "__main__":
    app()
```

**Usage**:
```bash
python cli.py user create john john@example.com --admin
python cli.py user delete john --force
python cli.py user list --active-only

python cli.py task create "Implement feature" --assignee john
python cli.py task list --user john
```

---

### argparse (Standard Library)

**No Installation Required**:
```python
import argparse
from typing import List

def main():
    parser = argparse.ArgumentParser(
        description="Todo CLI application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Buy groceries" --priority high
  %(prog)s list --status pending
  %(prog)s complete 1
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--priority", "-p", choices=["low", "normal", "high"],
                           default="normal", help="Task priority")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", "-s", help="Filter by status")
    list_parser.add_argument("--priority", "-p", help="Filter by priority")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("id", type=int, help="Task ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")
    delete_parser.add_argument("--force", "-f", action="store_true",
                              help="Skip confirmation")

    args = parser.parse_args()

    if args.command == "add":
        print(f"Adding task: {args.title} (priority: {args.priority})")
    elif args.command == "list":
        print("Listing tasks...")
    elif args.command == "complete":
        print(f"Marking task {args.id} as complete")
    elif args.command == "delete":
        print(f"Deleting task {args.id}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

### Advanced Features

**Progress Callback**:
```python
import typer
from rich.progress import Progress

def process_files(files: List[str]):
    """Process files with progress bar."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing...", total=len(files))

        for file in files:
            # Process file
            progress.update(task, advance=1)

@app.command()
def process(
    files: List[str] = typer.Argument(..., help="Files to process")
):
    """Process multiple files."""
    process_files(files)
```

**Config File Support**:
```python
import typer
from pathlib import Path
import json

CONFIG_FILE = Path.home() / ".config" / "myapp" / "config.json"

def load_config():
    """Load configuration."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(config):
    """Save configuration."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

@app.command()
def config(
    key: str = typer.Argument(..., help="Config key"),
    value: Optional[str] = typer.Argument(None, help="Config value (omit to get)"),
):
    """Get or set configuration."""
    cfg = load_config()

    if value is None:
        # Get config
        print(cfg.get(key, "Not set"))
    else:
        # Set config
        cfg[key] = value
        save_config(cfg)
        print(f"Set {key} = {value}")
```

**Environment Variables**:
```python
import typer
import os

@app.command()
def deploy(
    env: str = typer.Option(
        os.getenv("DEPLOY_ENV", "development"),
        "--env",
        "-e",
        help="Deployment environment"
    ),
    api_key: str = typer.Option(
        os.getenv("API_KEY"),
        "--api-key",
        envvar="API_KEY",
        help="API key for deployment"
    )
):
    """Deploy application."""
    print(f"Deploying to {env} with API key: {api_key[:10]}...")
```

---

### Testing CLIs

**Typer Testing**:
```python
from typer.testing import CliRunner
from my_cli import app

runner = CliRunner()

def test_add_command():
    result = runner.invoke(app, ["add", "Test task", "--priority", "high"])
    assert result.exit_code == 0
    assert "Task added" in result.output

def test_list_command():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0

def test_invalid_priority():
    result = runner.invoke(app, ["add", "Test", "--priority", "invalid"])
    assert result.exit_code != 0
```

---

### Best Practices

1. **Use Type Hints (Typer)**
   - Automatic validation
   - Better IDE support
   - Clear documentation

2. **Provide Good Help Text**
   - Command descriptions
   - Argument/option help
   - Usage examples

3. **Handle Errors Gracefully**
   - Clear error messages
   - Proper exit codes
   - Suggest fixes

4. **Add Confirmation for Destructive Actions**
   - Delete, clear, reset
   - Provide --force flag to skip

5. **Use Rich for Better Output**
   - Colors and formatting
   - Tables and progress bars
   - Icons for status

6. **Support Config Files**
   - Store user preferences
   - Environment-specific settings
   - JSON or TOML format

## Quality Checklist

Before finalizing CLI:
- [ ] Help text is clear and complete
- [ ] All commands have descriptions
- [ ] Arguments and options documented
- [ ] Error messages are helpful
- [ ] Destructive actions require confirmation
- [ ] Exit codes are appropriate (0=success, 1=error)
- [ ] Examples provided in help
- [ ] Config file support (if needed)
- [ ] Tests written for commands
- [ ] Works on Windows and Unix

## Post-Creation

After building CLI:
1. **Generate Shell Completion**: For bash, zsh, fish
2. **Create Man Page**: For Unix systems
3. **Package as Executable**: Use PyInstaller or similar
4. **Document in README**: Installation and usage
5. **Publish to PyPI**: If sharing publicly
6. **Add to PATH**: For easy access
