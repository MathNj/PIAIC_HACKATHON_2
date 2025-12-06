# Console TODO List Manager

> **PIAIC Hackathon 2 Project** - A demonstration of Spec-Driven Development and clean Python architecture

A simple yet powerful console-based TODO list application built with Python 3.13+. This application demonstrates full CRUD (Create, Read, Update, Delete) operations with an intuitive menu-driven interface.

**🏆 Built for:** PIAIC (Presidential Initiative for Artificial Intelligence & Computing) Hackathon 2
**📅 Completed:** December 2025
**🔧 Methodology:** Specification-Driven Development (SDD)

## Features

✅ **Add Tasks** - Create new tasks with titles and optional descriptions
✅ **View Tasks** - Display all tasks with status indicators ([ ] incomplete, [x] complete)
✅ **Update Tasks** - Modify task titles and descriptions
✅ **Delete Tasks** - Remove tasks permanently
✅ **Mark Complete** - Track task completion status
✅ **User-Friendly** - Menu-driven interface with input validation

## Prerequisites

- Python 3.13 or later
- Terminal/Console access (Command Prompt, PowerShell, Terminal, etc.)

**No external dependencies required!** Uses Python standard library only.

## Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/MathNj/PIAIC_HACKATHON_2.git
cd PIAIC_HACKATHON_2
```

### Step 2: Verify Python Installation

Check if Python 3.13+ is installed:

```bash
python --version
```

**Expected output:** `Python 3.13.x` or later

**If Python is not installed or version is too old:**

- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** `brew install python@3.13` or download from [python.org](https://www.python.org/downloads/)
- **Linux:** `sudo apt install python3.13` or `sudo yum install python3.13`

### Step 3: Run the Application

No installation needed! Just run:

**Linux/Mac:**
```bash
python3 src/main.py
```

**Windows:**
```bash
python src\main.py
```

**Alternative (if `python` command doesn't work):**
```bash
python3 src/main.py  # Try python3
py src/main.py       # Or py on Windows
```

That's it! The application will start immediately with no setup or dependencies.

## Usage

### Running the Application

**Linux/Mac:**
```bash
python src/main.py
```

**Windows (Command Prompt):**
```cmd
python src\main.py
```

**Windows (PowerShell):**
```powershell
python src\main.py
```

### Example Session

```
=== TODO List Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Select option (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
Task added with ID 1

=== TODO List Manager ===
...
Select option (1-6): 2

=== Your Tasks ===
[1] [ ] Buy groceries

=== TODO List Manager ===
...
Select option (1-6): 5
Enter task ID: 1
Task 1 marked as complete.

=== TODO List Manager ===
...
Select option (1-6): 2

=== Your Tasks ===
[1] [x] Buy groceries

=== TODO List Manager ===
...
Select option (1-6): 6
Goodbye!
```

## Menu Options

| Option | Function | Description |
|--------|----------|-------------|
| 1 | Add Task | Create a new task with title and optional description |
| 2 | View Tasks | Display all tasks with IDs and completion status |
| 3 | Update Task | Modify task title and/or description |
| 4 | Delete Task | Permanently remove a task |
| 5 | Mark Complete | Mark a task as completed |
| 6 | Exit | Close the application |

## Features in Detail

### Adding Tasks
- Title is required (non-empty)
- Description is optional
- Tasks auto-assigned unique incrementing IDs (1, 2, 3...)

### Viewing Tasks
- Tasks displayed with format: `[ID] [Status] Title`
- Status indicators: `[ ]` = incomplete, `[x]` = complete
- Empty list shows: "No tasks available."

### Updating Tasks
- Update title, description, or both
- Press Enter to skip a field (keeps current value)
- Task ID and completion status preserved

### Deleting Tasks
- Permanently removes task from memory
- Deleted task IDs are not reused

### Marking Complete
- Changes status from `[ ]` to `[x]`
- Operation is idempotent (can mark already-complete tasks)

## Error Handling

The application handles all common errors gracefully:

- **Invalid menu choice** → "Invalid option. Please select 1-6."
- **Non-numeric input** → "Invalid input. Please enter a number."
- **Empty title** → "Title cannot be empty. Please try again."
- **Task not found** → "Task ID {id} not found."
- **Invalid task ID** → "Invalid ID format. Please enter a number."

## Project Structure

```
PIAIC_HACKATHON_2/
├── src/
│   └── main.py              # Single-file application
├── specs/
│   └── 001-todo-crud/       # Feature specifications
│       ├── spec.md          # Requirements and user stories
│       ├── plan.md          # Technical architecture
│       ├── tasks.md         # Task breakdown (35 tasks)
│       ├── data-model.md    # Entity definitions
│       ├── research.md      # Technical decisions
│       ├── quickstart.md    # Usage guide
│       └── contracts/
│           └── cli-interface.md  # I/O specifications
├── history/
│   └── prompts/
│       └── 001-todo-crud/   # Prompt history records
├── .specify/                # Development templates
├── README.md                # This file
└── .gitignore              # Git ignore patterns
```

## Technical Details

- **Language**: Python 3.13+
- **Dependencies**: None (standard library only)
- **Storage**: In-memory (data lost on exit - Phase I limitation)
- **Architecture**: Layered single-file design
  - Model Layer: Task dataclass
  - Logic Layer: TaskManager class
  - Presentation Layer: Menu and handler functions
- **Type Hints**: Full type annotations throughout
- **Docstrings**: Google style documentation

## Troubleshooting

### Common Issues and Solutions

#### Issue: "python: command not found"
**Solution:**
- Try `python3` instead of `python`
- On Windows, try `py` command
- Install Python 3.13+ from [python.org](https://www.python.org/downloads/)

#### Issue: "No module named 'typing'"
**Solution:** You're using Python version < 3.5. Upgrade to Python 3.13+

#### Issue: "SyntaxError" when running
**Solution:** Your Python version is too old. This app requires Python 3.13+ for modern type hints
```bash
python --version  # Check your version
```

#### Issue: Application freezes or doesn't respond
**Solution:**
- Make sure you're running in an interactive terminal
- Don't run with input redirection (`<` operator)
- Restart the application with `python src/main.py`

#### Issue: Special characters display incorrectly
**Solution:**
- **Windows:** Use Windows Terminal instead of Command Prompt
- Ensure your terminal supports UTF-8 encoding
- On Linux/Mac, this should work by default

#### Issue: Can't find src/main.py
**Solution:** Make sure you're in the correct directory
```bash
pwd           # Check current directory (Linux/Mac)
cd            # Check current directory (Windows)
ls src/       # Verify main.py exists
```

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Python version: `python --version`
3. Make sure you're in the project root directory
4. Check that `src/main.py` exists

## Limitations (Phase I)

⚠️ **Data is NOT persisted** - All tasks are lost when you exit the application. This is intentional for Phase I.

Future enhancements (Phase II+):
- Data persistence (file/database storage)
- Task priorities and categories
- Due dates and reminders
- Search and filtering
- Undo/redo operations
- Export functionality

## Development

### Specification-Driven Development

This project follows Spec-Driven Development (SDD) methodology:

1. **spec.md** - User stories with acceptance criteria (P1, P2, P3 priorities)
2. **plan.md** - Architecture decisions and technical design
3. **tasks.md** - 35 executable tasks organized by user story
4. **Implementation** - Code built to exact specifications
5. **Validation** - Manual testing against acceptance scenarios

### Task Breakdown

- **Phase 1**: Setup (4 tasks) - Project initialization
- **Phase 2**: Foundational (5 tasks) - Core infrastructure
- **Phase 3**: User Story 1 (7 tasks) - Add and View (MVP)
- **Phase 4**: User Story 2 (5 tasks) - Mark Complete
- **Phase 5**: User Story 3 (4 tasks) - Update
- **Phase 6**: User Story 4 (3 tasks) - Delete
- **Phase 7**: Polish (7 tasks) - Error handling and validation

**Total**: 35 tasks completed ✅

## Testing

Manual testing performed against all acceptance scenarios from spec.md:

✅ Adding tasks with various titles and descriptions
✅ Viewing empty and populated task lists
✅ Marking tasks complete
✅ Updating task details
✅ Deleting tasks
✅ Error handling for invalid inputs
✅ Edge cases (empty title, non-existent IDs, etc.)

## Contributing

This is a hackathon project demonstrating console CRUD operations. Contributions welcome for Phase II enhancements!

## License

Open source - feel free to use and modify.

## Author

Built for PIAIC Hackathon 2 using Spec-Driven Development methodology.

## Acknowledgments

- Python standard library for zero-dependency implementation
- Spec-Driven Development framework for structured approach
- PIAIC for the hackathon opportunity

---

**Ready to manage your tasks?** Run `python src/main.py` and start organizing! 🚀
