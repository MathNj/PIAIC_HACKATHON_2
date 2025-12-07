# Quickstart Guide: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-05
**Version**: 1.0

## Overview

This guide explains how to set up, run, and use the Console TODO List Manager application.

## Prerequisites

**Required**:
- Python 3.13 or later
- Terminal/Console access (Command Prompt, PowerShell, Terminal, etc.)

**Not Required**:
- No external packages (uses Python standard library only)
- No database installation
- No pip install commands
- No virtual environment (though recommended for good practice)

## Installation

### Step 1: Verify Python Version

```bash
python --version
```

Expected output: `Python 3.13.x` or later

**Troubleshooting**:
- If command not found: Install Python 3.13+ from python.org
- If version < 3.13: Upgrade Python or use `python3` command
- Windows: Try `py --version` if `python` doesn't work

### Step 2: Navigate to Project Directory

```bash
cd /path/to/HACKATHON_2
```

### Step 3: Verify File Structure

```bash
ls src/main.py
```

Expected: File exists at `src/main.py`

## Running the Application

### Start the Application

**Linux/Mac**:
```bash
python src/main.py
```

**Windows (Command Prompt)**:
```cmd
python src\main.py
```

**Windows (PowerShell)**:
```powershell
python src\main.py
```

**Alternative** (if `python` doesn't work):
```bash
python3 src/main.py
# or
py src/main.py
```

### Expected Output

```
=== TODO List Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Select option (1-6): _
```

## Usage Guide

### Adding Your First Task

1. Select option `1` (Add Task)
2. Enter a task title when prompted
3. Enter description or press Enter to skip
4. See confirmation: "Task added with ID 1"

**Example**:
```
Select option (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
Task added with ID 1
```

### Viewing Tasks

1. Select option `2` (View Tasks)
2. See list of all tasks with IDs and status

**Example**:
```
Select option (1-6): 2
=== Your Tasks ===
[1] [ ] Buy groceries
[2] [ ] Call dentist
[3] [x] Submit timesheet
```

**Status Indicators**:
- `[ ]` - Task is incomplete
- `[x]` - Task is complete

### Marking a Task Complete

1. Select option `5` (Mark Complete)
2. Enter the task ID from the task list
3. See confirmation message

**Example**:
```
Select option (1-6): 5
Enter task ID to mark complete: 1
Task 1 marked as complete.
```

### Updating a Task

1. Select option `3` (Update Task)
2. Enter the task ID
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)
5. See confirmation message

**Example** (update title only):
```
Select option (1-6): 3
Enter task ID to update: 1
Enter new title (press Enter to skip): Buy groceries and supplies
Enter new description (press Enter to skip):
Task 1 updated successfully.
```

### Deleting a Task

1. Select option `4` (Delete Task)
2. Enter the task ID
3. See confirmation message

**Example**:
```
Select option (1-6): 4
Enter task ID to delete: 2
Task 2 deleted successfully.
```

### Exiting the Application

1. Select option `6` (Exit)
2. See "Goodbye!" message
3. Application terminates

**Important**: All data is lost when you exit (Phase I uses in-memory storage only)

## Common Workflows

### Daily Task Management

```
1. Start application
2. Add tasks for the day (option 1)
3. View task list (option 2)
4. Mark tasks complete as you finish them (option 5)
5. Review completed tasks (option 2)
6. Exit when done (option 6)
```

### Correcting a Mistake

**Wrong Title**:
```
1. View tasks to find the ID (option 2)
2. Update task with correct title (option 3)
```

**Wrong Task Added**:
```
1. View tasks to find the ID (option 2)
2. Delete the task (option 4)
```

### Batch Adding Tasks

```
1. Select Add Task (option 1)
2. Add first task
3. (Menu redisplays automatically)
4. Select Add Task again (option 1)
5. Add second task
6. Repeat until all tasks added
```

## Error Messages & Solutions

### "Invalid input. Please enter a number."

**Cause**: You entered non-numeric input (letters, symbols)
**Solution**: Enter only digits (1-6 for menu, valid IDs for operations)

### "Invalid option. Please select 1-6."

**Cause**: You entered a number outside the range 1-6
**Solution**: Enter a number from 1 to 6

### "Invalid ID format. Please enter a number."

**Cause**: You entered non-numeric task ID
**Solution**: Enter the numeric ID shown in task list

### "Title cannot be empty. Please try again."

**Cause**: You pressed Enter without typing a title
**Solution**: Type at least one character for the title

### "Task ID {id} not found."

**Cause**: Task with that ID doesn't exist (deleted or never created)
**Solution**: View task list (option 2) to see valid IDs

### "No tasks available."

**Cause**: Task list is empty (no tasks added yet, or all deleted)
**Solution**: Add a task using option 1

## Tips & Best Practices

### Tip 1: View Tasks Often
Use option 2 frequently to see current task IDs and statuses

### Tip 2: Descriptive Titles
Use clear, action-oriented titles: "Buy groceries" not "Groceries"

### Tip 3: Use Descriptions
Add context in descriptions to remember details later

### Tip 4: Data is Temporary
Remember: Data is lost when you exit. Don't use for long-term storage in Phase I.

### Tip 5: Task IDs Increment
Deleted task IDs are not reused. If you delete task 2, the next task will be 3, not 2.

## Troubleshooting

### Application Won't Start

**Problem**: `python: command not found`
**Solution**: Install Python 3.13+ or use `python3` or `py` command

**Problem**: `No such file or directory: src/main.py`
**Solution**: Ensure you're in the correct directory (HACKATHON_2 root)

**Problem**: `SyntaxError` when starting
**Solution**: Ensure you're using Python 3.13+ (check version with `python --version`)

### Application Crashes

**Problem**: Unexpected crash during operation
**Solution**: Report as a bug - application should handle all errors gracefully

### Strange Characters Display

**Problem**: Special characters show as � or squares
**Solution**: Ensure terminal supports UTF-8 encoding

**Windows Users**: Use Windows Terminal instead of Command Prompt for better UTF-8 support

### Can't Enter Input

**Problem**: Application doesn't wait for input
**Solution**: Ensure running in interactive terminal (not redirected I/O)

## Limitations (Phase I)

1. **No Data Persistence**: All data lost when you exit
2. **No Undo**: Deleted tasks cannot be recovered
3. **No Search**: Must view full list to find tasks
4. **No Filtering**: Cannot filter by status or other criteria
5. **No Sorting Options**: Tasks always sorted by ID
6. **No Due Dates**: Only title, description, and completion status
7. **No Priority Levels**: All tasks equal priority
8. **Single User**: No multi-user support or collaboration
9. **No Export**: Cannot save task list to file

These limitations will be addressed in future phases.

## Next Steps

After you're comfortable with basic usage:

1. Try all 6 menu options to understand full functionality
2. Test edge cases (invalid IDs, empty list, etc.)
3. Experiment with longer titles and descriptions
4. Practice the common workflows listed above

## Getting Help

**Questions or Issues?**
- Check the error messages section above
- Review the usage guide for specific operations
- Verify you're using Python 3.13+
- Ensure you're in the correct directory

**Found a Bug?**
- Note the exact error message
- Note the steps to reproduce
- Report to development team

## Examples

### Example Session: Grocery Shopping List

```
=== TODO List Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Select option (1-6): 1
Enter task title: Buy milk
Enter task description (optional): 2% milk, 1 gallon
Task added with ID 1

=== TODO List Manager ===
...
Select option (1-6): 1
Enter task title: Buy eggs
Enter task description (optional): Dozen large eggs
Task added with ID 2

=== TODO List Manager ===
...
Select option (1-6): 2
=== Your Tasks ===
[1] [ ] Buy milk
[2] [ ] Buy eggs

=== TODO List Manager ===
...
Select option (1-6): 5
Enter task ID to mark complete: 1
Task 1 marked as complete.

=== TODO List Manager ===
...
Select option (1-6): 2
=== Your Tasks ===
[1] [x] Buy milk
[2] [ ] Buy eggs

=== TODO List Manager ===
...
Select option (1-6): 6
Goodbye!
```

## Summary

1. **Start**: `python src/main.py`
2. **Add tasks**: Option 1
3. **View list**: Option 2
4. **Update/Delete/Complete**: Options 3/4/5
5. **Exit**: Option 6
6. **Remember**: Data is lost on exit (Phase I limitation)

Enjoy using the Console TODO List Manager!
