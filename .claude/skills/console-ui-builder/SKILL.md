---
name: "console-ui-builder"
description: "Builds rich, interactive console UIs using Rich, Textual, and other terminal UI libraries. Creates progress bars, tables, panels, syntax highlighting, interactive menus, and TUI applications. Use when building CLI tools that need visual polish or full terminal UIs."
version: "1.0.0"
---

# Console UI Builder Skill

## When to Use
- User says "Create console UI" or "Build terminal interface"
- Need rich formatting in CLI output (colors, tables, progress bars)
- Building interactive terminal applications (TUI)
- Want syntax highlighting in terminal
- Need dashboard or monitoring display in terminal
- Creating wizard-style CLI flows

## Context
This skill creates console UIs using modern Python libraries:
- **Rich**: Beautiful terminal formatting (tables, progress, panels, syntax)
- **Textual**: Full TUI framework (like curses but better)
- **Click**: CLI framework with color support
- **Prompt Toolkit**: Interactive prompts and autocomplete
- **Questionary**: Beautiful questionnaires

## Workflow

### 1. Choose UI Type
- **Simple Formatting**: Rich for colors, tables, progress
- **Interactive Prompts**: Questionary or Prompt Toolkit
- **Full TUI**: Textual for dashboard-style apps
- **CLI Framework**: Click with Rich integration

### 2. Design Components
- Layout (panels, columns, tables)
- Interactive elements (prompts, menus)
- Progress indicators
- Syntax highlighting

### 3. Implement UI
- Create widgets/components
- Add event handlers (for TUI)
- Style with themes

### 4. Test in Terminal
- Verify on different terminal emulators
- Check colors and Unicode support

## Output Format

### Rich - Terminal Formatting

**Installation**:
```bash
uv add rich
```

**Basic Usage**:
```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()

# Print with color
console.print("Hello [bold magenta]World[/bold magenta]!")
console.print("[red]Error:[/red] Something went wrong")
console.print("[green]✓[/green] Success!")

# Panel
console.print(Panel("Important message", title="Alert", border_style="red"))

# Table
table = Table(title="Tasks")
table.add_column("ID", style="cyan")
table.add_column("Title", style="magenta")
table.add_column("Status", style="green")

table.add_row("1", "Buy groceries", "✓ Done")
table.add_row("2", "Write code", "⏳ In Progress")
table.add_row("3", "Deploy app", "⭕ Pending")

console.print(table)

# Progress Bar
for i in track(range(100), description="Processing..."):
    # Do work
    pass

# Syntax Highlighting
code = '''
def hello():
    print("Hello, World!")
'''
syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)

# Markdown
md = Markdown("# Title\n\nThis is **bold** and *italic*")
console.print(md)
```

---

### Example 1: Task List Display

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

def display_task_dashboard(tasks):
    """Display task dashboard with Rich."""
    console = Console()

    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )

    # Header
    header = Panel(
        Text("📋 Todo App Dashboard", justify="center", style="bold blue"),
        border_style="blue"
    )
    layout["header"].update(header)

    # Task table
    table = Table(title="Tasks", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Due Date", style="yellow")

    for task in tasks:
        # Color-code priority
        priority_color = {
            "high": "red",
            "normal": "yellow",
            "low": "green"
        }.get(task["priority"], "white")

        # Status icons
        status_icon = {
            "pending": "⭕",
            "in_progress": "⏳",
            "completed": "✅"
        }.get(task["status"], "❓")

        table.add_row(
            str(task["id"]),
            task["title"],
            f"[{priority_color}]{task['priority'].upper()}[/{priority_color}]",
            f"{status_icon} {task['status'].replace('_', ' ').title()}",
            task.get("due_date", "N/A")
        )

    layout["body"].update(table)

    # Footer stats
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    pending = total - completed

    footer = Panel(
        f"[green]✓ {completed} Completed[/green] | "
        f"[yellow]⏳ {pending} Pending[/yellow] | "
        f"[blue]Total: {total}[/blue]",
        border_style="dim"
    )
    layout["footer"].update(footer)

    console.print(layout)

# Usage
tasks = [
    {"id": 1, "title": "Buy groceries", "priority": "high", "status": "pending", "due_date": "2025-12-20"},
    {"id": 2, "title": "Write documentation", "priority": "normal", "status": "in_progress", "due_date": "2025-12-22"},
    {"id": 3, "title": "Deploy to production", "priority": "high", "status": "pending", "due_date": "2025-12-25"},
]
display_task_dashboard(tasks)
```

---

### Example 2: Progress Tracking

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
import time

def deploy_with_progress():
    """Show deployment progress with multiple steps."""
    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        # Step 1: Building
        build_task = progress.add_task("[cyan]Building application...", total=100)
        for i in range(100):
            time.sleep(0.02)
            progress.update(build_task, advance=1)

        # Step 2: Running tests
        test_task = progress.add_task("[yellow]Running tests...", total=50)
        for i in range(50):
            time.sleep(0.03)
            progress.update(test_task, advance=1)

        # Step 3: Deploying
        deploy_task = progress.add_task("[green]Deploying...", total=100)
        for i in range(100):
            time.sleep(0.01)
            progress.update(deploy_task, advance=1)

    console.print("\n[bold green]✓ Deployment successful![/bold green]")
```

---

### Example 3: Live Dashboard

```python
from rich.console import Console
from rich.live import Live
from rich.table import Table
import time
import random

def generate_metrics():
    """Generate fake metrics."""
    return {
        "cpu": random.randint(10, 90),
        "memory": random.randint(40, 80),
        "requests": random.randint(100, 500),
        "errors": random.randint(0, 10)
    }

def create_metrics_table(metrics):
    """Create metrics table."""
    table = Table(title="System Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status", justify="center")

    # CPU
    cpu_status = "🔴" if metrics["cpu"] > 80 else "🟡" if metrics["cpu"] > 60 else "🟢"
    table.add_row("CPU Usage", f"{metrics['cpu']}%", cpu_status)

    # Memory
    mem_status = "🔴" if metrics["memory"] > 80 else "🟡" if metrics["memory"] > 60 else "🟢"
    table.add_row("Memory Usage", f"{metrics['memory']}%", mem_status)

    # Requests
    table.add_row("Requests/min", str(metrics["requests"]), "📊")

    # Errors
    err_status = "🔴" if metrics["errors"] > 5 else "🟢"
    table.add_row("Errors", str(metrics["errors"]), err_status)

    return table

def live_dashboard(duration=10):
    """Display live updating dashboard."""
    console = Console()

    with Live(create_metrics_table(generate_metrics()), console=console, refresh_per_second=2) as live:
        for _ in range(duration * 2):  # Update every 0.5 seconds
            time.sleep(0.5)
            metrics = generate_metrics()
            live.update(create_metrics_table(metrics))

# Usage
live_dashboard(duration=10)
```

---

### Questionary - Interactive Prompts

**Installation**:
```bash
uv add questionary
```

**Basic Usage**:
```python
import questionary

# Text input
name = questionary.text("What is your name?").ask()

# Confirm (yes/no)
confirmed = questionary.confirm("Do you want to continue?").ask()

# Select (single choice)
priority = questionary.select(
    "Select priority:",
    choices=["High", "Normal", "Low"]
).ask()

# Checkbox (multiple choice)
features = questionary.checkbox(
    "Select features:",
    choices=["Authentication", "Database", "API", "Frontend"]
).ask()

# Password
password = questionary.password("Enter password:").ask()

# Path
file_path = questionary.path("Select file:").ask()
```

---

### Example 4: Interactive Task Creator

```python
import questionary
from rich.console import Console
from rich.panel import Panel

def create_task_interactive():
    """Create task with interactive prompts."""
    console = Console()

    console.print(Panel("[bold blue]Create New Task[/bold blue]", border_style="blue"))

    # Collect task details
    task = {}

    task["title"] = questionary.text(
        "Task title:",
        validate=lambda text: len(text) > 0 or "Title cannot be empty"
    ).ask()

    task["description"] = questionary.text(
        "Description (optional):",
        multiline=True
    ).ask()

    task["priority"] = questionary.select(
        "Priority:",
        choices=[
            questionary.Choice("🔴 High", value="high"),
            questionary.Choice("🟡 Normal", value="normal"),
            questionary.Choice("🟢 Low", value="low")
        ]
    ).ask()

    task["category"] = questionary.select(
        "Category:",
        choices=["Work", "Personal", "Shopping", "Health", "Other"]
    ).ask()

    has_due_date = questionary.confirm("Set due date?").ask()
    if has_due_date:
        task["due_date"] = questionary.text("Due date (YYYY-MM-DD):").ask()

    # Confirmation
    console.print("\n[bold]Task Summary:[/bold]")
    console.print(f"Title: {task['title']}")
    console.print(f"Description: {task.get('description', 'N/A')}")
    console.print(f"Priority: {task['priority']}")
    console.print(f"Category: {task['category']}")
    console.print(f"Due Date: {task.get('due_date', 'None')}")

    confirmed = questionary.confirm("\nCreate this task?").ask()

    if confirmed:
        console.print("\n[green]✓ Task created successfully![/green]")
        return task
    else:
        console.print("\n[yellow]Task creation cancelled.[/yellow]")
        return None

# Usage
task = create_task_interactive()
```

---

### Textual - Full TUI Framework

**Installation**:
```bash
uv add textual
```

**Basic TUI App**:
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Input, DataTable
from textual.containers import Container, Horizontal

class TodoApp(App):
    """A simple todo app."""

    CSS = """
    Screen {
        background: $surface;
    }

    #task-input {
        dock: top;
        height: 3;
        margin: 1;
    }

    #tasks-table {
        height: 1fr;
        margin: 1;
    }

    .button-row {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Input(placeholder="Enter new task...", id="task-input")
        yield DataTable(id="tasks-table")
        yield Horizontal(
            Button("Add Task", variant="success", id="add-button"),
            Button("Delete Selected", variant="error", id="delete-button"),
            Button("Quit", variant="primary", id="quit-button"),
            classes="button-row"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the table."""
        table = self.query_one("#tasks-table", DataTable)
        table.add_columns("ID", "Task", "Status")
        table.add_row("1", "Sample task", "Pending")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "add-button":
            self.add_task()
        elif event.button.id == "delete-button":
            self.delete_selected()
        elif event.button.id == "quit-button":
            self.exit()

    def add_task(self) -> None:
        """Add a new task."""
        task_input = self.query_one("#task-input", Input)
        table = self.query_one("#tasks-table", DataTable)

        if task_input.value:
            task_id = len(table.rows) + 1
            table.add_row(str(task_id), task_input.value, "Pending")
            task_input.value = ""

    def delete_selected(self) -> None:
        """Delete selected task."""
        table = self.query_one("#tasks-table", DataTable)
        if table.cursor_row is not None:
            table.remove_row(table.cursor_row)

if __name__ == "__main__":
    app = TodoApp()
    app.run()
```

---

### Example 5: CLI Wizard

```python
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import questionary
import time

def setup_wizard():
    """Interactive setup wizard."""
    console = Console()

    # Welcome screen
    console.print(Panel(
        "[bold blue]Welcome to Todo App Setup Wizard[/bold blue]\n\n"
        "This wizard will guide you through the setup process.",
        title="🚀 Setup",
        border_style="blue"
    ))

    # Step 1: Database
    console.print("\n[bold cyan]Step 1:[/bold cyan] Database Configuration")
    db_type = questionary.select(
        "Select database:",
        choices=["SQLite (Local)", "PostgreSQL (Production)", "MySQL"]
    ).ask()

    if "PostgreSQL" in db_type:
        db_host = questionary.text("Database host:", default="localhost").ask()
        db_port = questionary.text("Database port:", default="5432").ask()
        db_name = questionary.text("Database name:").ask()
        db_user = questionary.text("Database user:").ask()
        db_password = questionary.password("Database password:").ask()
    else:
        db_path = questionary.text("Database path:", default="./data/todo.db").ask()

    # Step 2: Authentication
    console.print("\n[bold cyan]Step 2:[/bold cyan] Authentication")
    auth_method = questionary.select(
        "Select authentication method:",
        choices=["JWT (Recommended)", "Session-based", "OAuth2"]
    ).ask()

    jwt_secret = questionary.password("JWT secret key (leave empty to generate):").ask()
    if not jwt_secret:
        import secrets
        jwt_secret = secrets.token_urlsafe(32)
        console.print(f"[green]✓ Generated secret: {jwt_secret[:20]}...[/green]")

    # Step 3: Features
    console.print("\n[bold cyan]Step 3:[/bold cyan] Features")
    features = questionary.checkbox(
        "Select features to enable:",
        choices=[
            "Email notifications",
            "Task reminders",
            "File attachments",
            "Collaboration",
            "API access"
        ]
    ).ask()

    # Summary
    console.print("\n" + "="*50)
    console.print("[bold]Configuration Summary:[/bold]")
    console.print(f"Database: {db_type}")
    console.print(f"Authentication: {auth_method}")
    console.print(f"Features: {', '.join(features)}")
    console.print("="*50)

    confirmed = questionary.confirm("\nProceed with this configuration?").ask()

    if confirmed:
        # Simulate setup with progress
        console.print("\n[bold]Installing...[/bold]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Setting up...", total=100)
            for i in range(100):
                time.sleep(0.03)
                progress.update(task, advance=1)

        console.print("\n[bold green]✓ Setup complete![/bold green]")
    else:
        console.print("\n[yellow]Setup cancelled.[/yellow]")

# Usage
setup_wizard()
```

---

### Styling and Themes

**Rich Themes**:
```python
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold cyan",
    "highlight": "bold magenta"
})

console = Console(theme=custom_theme)

console.print("This is a success message", style="success")
console.print("This is an error message", style="error")
console.print("This is a warning", style="warning")
```

**Textual CSS**:
```python
CSS = """
/* Global styles */
Screen {
    background: #1e1e2e;
    color: #cdd6f4;
}

/* Widget styles */
Button {
    background: #89b4fa;
    color: #1e1e2e;
    border: tall #74c7ec;
}

Button:hover {
    background: #74c7ec;
}

Button.success {
    background: #a6e3a1;
}

Button.error {
    background: #f38ba8;
}

Input {
    border: tall #89b4fa;
}

Input:focus {
    border: tall #f9e2af;
}
"""
```

---

### Best Practices

1. **Use Rich for Simple Formatting**
   - Quick colored output
   - Tables and progress bars
   - No event handling needed

2. **Use Questionary for Interactive Prompts**
   - Linear wizard flows
   - Form-like inputs
   - Simple user interactions

3. **Use Textual for Full TUIs**
   - Dashboard applications
   - Complex layouts
   - Event-driven interactions

4. **Test Terminal Compatibility**
   - Check on different terminals (Windows Terminal, iTerm2, etc.)
   - Fallback for terminals without color support

5. **Keep It Responsive**
   - Show progress for long operations
   - Provide cancel options
   - Give feedback for user actions

## Quality Checklist

Before finalizing console UI:
- [ ] Colors display correctly in terminal
- [ ] Unicode characters render properly
- [ ] Layout adapts to terminal size
- [ ] Progress indicators work
- [ ] Interactive elements respond to input
- [ ] Error messages are clear
- [ ] Keyboard shortcuts documented
- [ ] Tested on multiple terminals
- [ ] Graceful degradation for limited terminals

## Post-Creation

After building console UI:
1. **Test in Multiple Terminals**: Windows Terminal, iTerm2, Terminal.app
2. **Document Keyboard Shortcuts**: List all hotkeys
3. **Add Help Command**: Implement `--help` or `?` key
4. **Create Demo GIF**: Show UI in action
5. **Optimize Performance**: Reduce redraws, cache when possible
