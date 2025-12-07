# CLI Interface Contract: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-05
**Version**: 1.0
**Status**: Complete

## Overview

This document specifies the exact console input/output contract for the TODO list application. All prompts, menu formats, success messages, and error messages are defined here.

## General Format

**Character Encoding**: UTF-8
**Line Endings**: Platform-specific (\n on Unix, \r\n on Windows - handled by Python print())
**Input Method**: stdin (keyboard input via `input()`)
**Output Method**: stdout (console output via `print()`)

## Main Menu

**Display Format**:
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

**Requirements**:
- Header with "=== TODO List Manager ===" on first line
- Six numbered options (1-6) on separate lines
- Prompt "Select option (1-6): " on last line
- Cursor waits at end of prompt for user input
- Menu displayed after application starts and after each operation completes

**Valid Inputs**: 1, 2, 3, 4, 5, 6 (single digit)

**Invalid Input Handling**:
- Non-numeric input (e.g., "abc"): Display "Invalid input. Please enter a number." and re-prompt
- Out of range numeric input (e.g., "7", "0"): Display "Invalid option. Please select 1-6." and re-prompt
- Empty input (just Enter): Display "Invalid input. Please enter a number." and re-prompt

## Operation 1: Add Task

**Prompt Sequence**:
```
Enter task title: _
Enter task description (optional): _
```

**Success Output**:
```
Task added with ID {task_id}
```

**Example**:
```
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
Task added with ID 1
```

**Validation & Error Messages**:

| Condition | Error Message | Behavior |
|-----------|---------------|----------|
| Empty title | "Title cannot be empty. Please try again." | Re-prompt for title (loop until non-empty) |
| Empty description | N/A (allowed) | Accept empty string, continue |

**Implementation Notes**:
- Title validation occurs before calling TaskManager.add_task()
- Description can be empty string (no validation needed)
- Task ID auto-assigned by TaskManager, displayed in success message

## Operation 2: View Tasks

**Output Format (Non-Empty List)**:
```
=== Your Tasks ===
[1] [ ] Buy groceries
[2] [x] Call dentist
[3] [ ] Finish report
```

**Output Format (Empty List)**:
```
=== Your Tasks ===
No tasks available.
```

**Format Specifications**:
- Header: "=== Your Tasks ===" on first line
- Each task: `[{id}] [{status}] {title}` on separate line
- Status indicator: `[ ]` for incomplete (completed=False), `[x]` for complete (completed=True)
- Tasks sorted by ID ascending
- Title only (description NOT shown in list view)

**Example with Multiple Tasks**:
```
=== Your Tasks ===
[1] [x] Buy groceries
[5] [ ] Pay bills
[7] [x] Submit timesheet
[9] [ ] Review PR #123
```

**Notes**:
- Gap in IDs (1, 5, 7, 9) is normal after deletions
- Status indicator has exactly one space between brackets: `[ ]` or `[x]`
- One space after status before title

## Operation 3: Update Task

**Prompt Sequence**:
```
Enter task ID to update: _
Enter new title (press Enter to skip): _
Enter new description (press Enter to skip): _
```

**Success Output**:
```
Task {task_id} updated successfully.
```

**Example (Update Both)**:
```
Enter task ID to update: 1
Enter new title (press Enter to skip): Buy groceries and supplies
Enter new description (press Enter to skip): Milk, eggs, bread, cleaning supplies
Task 1 updated successfully.
```

**Example (Update Title Only)**:
```
Enter task ID to update: 2
Enter new title (press Enter to skip): Call dentist for cleaning
Enter new description (press Enter to skip):
Task 2 updated successfully.
```

**Example (Skip Both)**:
```
Enter task ID to update: 3
Enter new title (press Enter to skip):
Enter new description (press Enter to skip):
No changes made.
```

**Validation & Error Messages**:

| Condition | Error Message | Behavior |
|-----------|---------------|----------|
| Non-numeric ID | "Invalid ID format. Please enter a number." | Re-prompt for ID |
| Task ID not found | "Task ID {task_id} not found." | Return to main menu |
| Both fields skipped | "No changes made." | Return to main menu |
| Empty title after prompt | N/A (treated as skip) | Keep current title |
| Empty description after prompt | N/A (treated as skip) | Keep current description |

**Implementation Notes**:
- Empty input (just Enter) treated as None (skip field)
- At least one field must be changed, or display "No changes made."
- Task ID and completed status never change during update

## Operation 4: Delete Task

**Prompt**:
```
Enter task ID to delete: _
```

**Success Output**:
```
Task {task_id} deleted successfully.
```

**Example**:
```
Enter task ID to delete: 2
Task 2 deleted successfully.
```

**Validation & Error Messages**:

| Condition | Error Message | Behavior |
|-----------|---------------|----------|
| Non-numeric ID | "Invalid ID format. Please enter a number." | Re-prompt for ID |
| Task ID not found | "Task ID {task_id} not found." | Return to main menu |

**Implementation Notes**:
- No confirmation prompt (delete is immediate)
- Deleted task ID not reused for future tasks

## Operation 5: Mark Complete

**Prompt**:
```
Enter task ID to mark complete: _
```

**Success Output**:
```
Task {task_id} marked as complete.
```

**Example**:
```
Enter task ID to mark complete: 1
Task 1 marked as complete.
```

**Validation & Error Messages**:

| Condition | Error Message | Behavior |
|-----------|---------------|----------|
| Non-numeric ID | "Invalid ID format. Please enter a number." | Re-prompt for ID |
| Task ID not found | "Task ID {task_id} not found." | Return to main menu |
| Task already complete | N/A (no error) | Still display success message (idempotent) |

**Implementation Notes**:
- Operation is idempotent (can mark already-complete task with no error)
- No "unmark" operation (tasks cannot become incomplete once complete)

## Operation 6: Exit

**Output**:
```
Goodbye!
```

**Behavior**:
- Display "Goodbye!" message
- Terminate application (exit while loop, program ends)
- No data saved (in-memory only, data lost on exit)

## Error Handling Patterns

### Input Validation Loop Pattern

For numeric inputs (menu choice, task ID):
```
while True:
    try:
        value = int(input(prompt))
        # Additional range/existence validation
        return value
    except ValueError:
        print("Invalid input. Please enter a number.")
```

### Non-Empty String Validation Pattern

For required fields (task title):
```
while True:
    value = input(prompt)
    if value.strip():  # Non-empty after removing whitespace
        return value.strip()
    print("Title cannot be empty. Please try again.")
```

### Optional String Input Pattern

For optional fields (description, update fields):
```
value = input(prompt)
return value if value else None  # Empty string -> None for "skip"
```

## Status Indicators

**Format**: `[{char}]` where char is one of:
- ` ` (space) - Incomplete task (completed=False)
- `x` (lowercase x) - Complete task (completed=True)

**Examples**:
- Incomplete: `[ ]` - three characters total
- Complete: `[x]` - three characters total

**Color**: Not used (plain text only for Phase I)

## Message Templates

### Success Messages
```
Task added with ID {task_id}
Task {task_id} updated successfully.
Task {task_id} deleted successfully.
Task {task_id} marked as complete.
No changes made.
Goodbye!
```

### Error Messages
```
Invalid input. Please enter a number.
Invalid option. Please select 1-6.
Invalid ID format. Please enter a number.
Title cannot be empty. Please try again.
Task ID {task_id} not found.
No tasks available.
```

## Edge Cases & Special Scenarios

### Empty Task List
```
=== Your Tasks ===
No tasks available.
```

### Large Task List (100 tasks)
- Display all tasks without pagination
- No scrolling or paging controls
- User's terminal handles scrollback

### Task with Long Title
- Display full title (no truncation)
- Title wraps naturally based on terminal width
- No artificial length limit

### Task with Special Characters
- Support UTF-8 characters in title and description
- Examples: "Café meeting", "Review PR #123", "Fix bug → release"

### Deleted Task Gaps
```
=== Your Tasks ===
[1] [x] First task
[5] [ ] Fifth task (IDs 2-4 were deleted)
[6] [ ] Sixth task
```

## Acceptance Criteria Mapping

This contract satisfies the following functional requirements from spec.md:

- **FR-001**: Main menu with 6 options ✅
- **FR-002**: Continuous loop (returns to menu after each operation) ✅
- **FR-003**: Auto-assign IDs (shown in success message) ✅
- **FR-005**: Require non-empty title (validation with error message) ✅
- **FR-006**: Accept optional description (allows empty) ✅
- **FR-008**: Display format `[ID] [Status] Title` ✅
- **FR-009**: "No tasks available." for empty list ✅
- **FR-012**: Allow skipping update fields (press Enter) ✅
- **FR-014**: Error message for non-existent task ID ✅
- **FR-015**: Validate input with error messages ✅
- **FR-016**: Exit option terminates application ✅

## Implementation Checklist

- [ ] Main menu displays with correct format
- [ ] All 6 operations have correct prompts
- [ ] Success messages match templates exactly
- [ ] Error messages match templates exactly
- [ ] Status indicators format correctly ([ ] vs [x])
- [ ] Input validation loops until valid
- [ ] Empty list displays "No tasks available."
- [ ] Update operation allows skipping fields
- [ ] Exit displays "Goodbye!" and terminates
- [ ] All messages end with appropriate newline
