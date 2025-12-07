# Implementation Plan: Console CRUD Operations

**Branch**: `001-todo-crud` | **Date**: 2025-12-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-crud/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a console-based TODO list application with full CRUD operations (Create, Read, Update, Delete) plus task completion tracking. The application runs as a single-file Python script with in-memory storage, providing a menu-driven interface for managing tasks. No external dependencies or persistence - data is stored in Python data structures and lost on restart (Phase I constraint).

**Technical Approach**: Layered architecture within a single file:
- **Model Layer**: Task data class with type hints
- **Logic Layer**: TaskManager class handling all business operations
- **Presentation Layer**: Main loop with menu display and user input handling

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (Python standard library only - typing, sys modules)
**Storage**: In-memory (Python list or dictionary - NO file/database persistence)
**Testing**: Manual testing against acceptance criteria (no test framework for Phase I)
**Target Platform**: Console/Terminal (Windows, Linux, macOS)
**Project Type**: Single file console application
**Performance Goals**: Instant response (<100ms) for all operations with up to 100 tasks
**Constraints**:
- Single file implementation (src/main.py)
- No external pip packages
- No persistence (data lost on restart)
- Standard library only
**Scale/Scope**: Single-user, up to 100 tasks, 6 menu operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: spec.md created and validated before planning
- ✅ **PASS**: All requirements documented with testable acceptance criteria
- ✅ **PASS**: User stories prioritized (P1-P3)

### Principle II: In-Memory Storage Only (Phase I)
- ✅ **PASS**: FR-004 explicitly requires in-memory storage (list or dictionary)
- ✅ **PASS**: No database or file persistence specified
- ✅ **PASS**: Assumption #5 acknowledges data loss on restart is acceptable
- ✅ **PASS**: "Out of Scope" explicitly excludes data persistence

### Principle III: Standard Library Only
- ✅ **PASS**: No external dependencies specified in spec
- ✅ **PASS**: Technical Context confirms standard library only
- ✅ **PASS**: No framework, ORM, or third-party packages mentioned

### Principle IV: Continuous Loop Interface
- ✅ **PASS**: FR-001 requires main menu with 6 options
- ✅ **PASS**: FR-002 explicitly requires continuous loop returning to menu
- ✅ **PASS**: FR-016 requires Exit option to terminate
- ✅ **PASS**: User input validation with graceful error handling (FR-015)

### Technology Constraints Compliance
- ✅ **PASS**: Python 3.13+ specified
- ✅ **PASS**: Type hints will be used (constitution requirement)
- ✅ **PASS**: Docstrings will be added (Google style)
- ✅ **PASS**: Single file structure (src/main.py) confirmed
- ✅ **PASS**: Error handling with try-except blocks planned

**Constitution Check Result**: ✅ ALL GATES PASSED - No violations, ready to proceed

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-crud/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (minimal - no unknowns)
├── data-model.md        # Phase 1 output (Task entity definition)
├── quickstart.md        # Phase 1 output (how to run the app)
├── contracts/           # Phase 1 output (CLI interface contract)
│   └── cli-interface.md # Menu options and I/O format
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
└── main.py              # Single-file implementation
                         # Contains: Task class, TaskManager class, main() function

# NO tests/ directory for Phase I
# Manual testing against acceptance criteria in spec.md
```

**Structure Decision**: Single file architecture selected per constitution Principle II (Technology Constraints). The src/main.py file will contain three logical layers:

1. **Model Layer** (lines 1-50): Task class with id, title, description, completed attributes
2. **Logic Layer** (lines 51-300): TaskManager class with methods:
   - `add_task(title: str, description: str) -> int`
   - `view_tasks() -> list[Task]`
   - `update_task(task_id: int, title: str, description: str) -> bool`
   - `delete_task(task_id: int) -> bool`
   - `mark_complete(task_id: int) -> bool`
   - `get_task(task_id: int) -> Task | None`
3. **Presentation Layer** (lines 301-500): main() function with:
   - Menu display function
   - Input handling with validation
   - While loop for continuous operation
   - Error message formatting

No tests directory needed - Phase I uses manual validation against spec acceptance scenarios.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All principles and constraints satisfied.

## Phase 0: Research & Unknowns Resolution

**Status**: ✅ COMPLETE - No unknowns to resolve

All technical decisions are straightforward and dictated by constitution:
- Language: Python 3.13+ (constitution requirement)
- Storage: In-memory list or dict (constitution requirement)
- Structure: Single file (constitution requirement)
- Dependencies: Standard library only (constitution requirement)

**Research Summary**: No external research required. Standard Python patterns will be used:
- `typing` module for type hints (Task, Optional, List)
- `sys` module for exit() if needed
- Dictionary for O(1) task lookup by ID: `{id: Task}`
- Auto-incrementing ID using counter variable

## Phase 1: Design Artifacts

### Architecture Decision: Storage Structure

**Decision**: Use Python dictionary `{int: Task}` for task storage

**Rationale**:
- O(1) lookup by task ID for update/delete/mark_complete operations
- Maintains task ID as key for natural indexing
- Simple to implement: `self._tasks: dict[int, Task] = {}`
- Easy to iterate for view_tasks: `self._tasks.values()`

**Alternatives Considered**:
- List of Task objects: Requires O(n) search by ID, less efficient
- List with index=ID: Wastes memory if tasks deleted (gaps in list)

### Architecture Decision: ID Generation

**Decision**: Use simple counter variable incremented on each add

**Rationale**:
- Meets FR-003 requirement (auto-assign unique incrementing IDs)
- Simple to implement: `self._next_id = 1`, increment after each add
- No collision risk in single-user environment
- IDs persist within session (in-memory)

**Alternatives Considered**:
- UUID: Overkill for in-memory single-user app, not incrementing integers
- Max ID + 1: Requires scanning dictionary, unnecessary complexity

### Architecture Decision: User Input Validation

**Decision**: Validate and sanitize at presentation layer before calling TaskManager

**Rationale**:
- Separation of concerns: TaskManager handles business logic, main() handles I/O
- Allows TaskManager methods to assume valid input
- Centralized error messaging in presentation layer

**Validation Rules**:
- Menu choice: Must be 1-6, re-prompt on invalid
- Task ID: Must be numeric and positive, re-prompt on invalid
- Title: Must be non-empty string, re-prompt on empty
- Description: Optional, empty string allowed

## Phase 1 Artifacts

### 1. Data Model (data-model.md)

See [data-model.md](./data-model.md) for complete entity definitions.

**Summary**:
- **Task Entity**: 4 attributes (id, title, description, completed)
- **TaskManager**: Encapsulates task list and provides CRUD + complete operations
- **Validation Rules**: Documented for each field

### 2. CLI Interface Contract (contracts/cli-interface.md)

See [contracts/cli-interface.md](./contracts/cli-interface.md) for complete I/O specifications.

**Summary**:
- Main menu format (6 numbered options)
- Input prompts for each operation
- Output formats for success/error messages
- Status indicator format: [x] vs [ ]

### 3. Quickstart Guide (quickstart.md)

See [quickstart.md](./quickstart.md) for setup and usage instructions.

**Summary**:
- Prerequisites: Python 3.13+
- How to run: `python src/main.py`
- Basic usage examples
- Troubleshooting

## Implementation Strategy

### Layered Architecture (Single File)

```python
# src/main.py structure:

# IMPORTS (Lines 1-10)
from typing import Optional
from dataclasses import dataclass

# MODEL LAYER (Lines 11-30)
@dataclass
class Task:
    """Represents a TODO task."""
    id: int
    title: str
    description: str
    completed: bool = False

# LOGIC LAYER (Lines 31-250)
class TaskManager:
    """Manages in-memory task collection."""
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str) -> int:
        """Add new task, return assigned ID."""
        ...

    def view_tasks(self) -> list[Task]:
        """Return all tasks sorted by ID."""
        ...

    def update_task(self, task_id: int, title: Optional[str],
                    description: Optional[str]) -> bool:
        """Update task fields. None = skip field. Return success."""
        ...

    def delete_task(self, task_id: int) -> bool:
        """Remove task. Return success."""
        ...

    def mark_complete(self, task_id: int) -> bool:
        """Set completed=True. Return success."""
        ...

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID. Return None if not found."""
        ...

# PRESENTATION LAYER (Lines 251-450)
def display_menu() -> None:
    """Print main menu options."""
    ...

def get_menu_choice() -> int:
    """Get and validate menu selection (1-6)."""
    ...

def handle_add_task(manager: TaskManager) -> None:
    """Prompt for title/desc, call manager.add_task()."""
    ...

def handle_view_tasks(manager: TaskManager) -> None:
    """Call manager.view_tasks(), format output."""
    ...

def handle_update_task(manager: TaskManager) -> None:
    """Prompt for ID + fields, call manager.update_task()."""
    ...

def handle_delete_task(manager: TaskManager) -> None:
    """Prompt for ID, call manager.delete_task()."""
    ...

def handle_mark_complete(manager: TaskManager) -> None:
    """Prompt for ID, call manager.mark_complete()."""
    ...

def main() -> None:
    """Main application loop."""
    manager = TaskManager()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(manager)
        elif choice == 2:
            handle_view_tasks(manager)
        elif choice == 3:
            handle_update_task(manager)
        elif choice == 4:
            handle_delete_task(manager)
        elif choice == 5:
            handle_mark_complete(manager)
        elif choice == 6:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
```

### Key Design Patterns

1. **Data Class for Task**: Uses `@dataclass` decorator for automatic __init__, __repr__
2. **Manager Pattern**: TaskManager encapsulates collection and operations
3. **Command Pattern**: Each menu option maps to handler function
4. **Separation of Concerns**: Model/Logic/Presentation layers clearly separated
5. **Fail-Fast Validation**: Validate input at presentation layer, assume valid in logic layer

### Error Handling Strategy

**Presentation Layer**:
- Try-except blocks around user input (ValueError for int conversion)
- Loop until valid input received
- Display user-friendly error messages

**Logic Layer**:
- Return bool for success/failure (update, delete, mark_complete)
- Return None for not found (get_task)
- No exceptions thrown (invalid inputs prevented by presentation layer)

### Testing Strategy (Phase I)

**Manual Testing Against Acceptance Criteria**:
1. Test each user story's acceptance scenarios from spec.md
2. Test all edge cases listed in spec.md
3. Verify all functional requirements (FR-001 to FR-016)
4. Validate success criteria (SC-001 to SC-007)

**No Automated Tests**: Per constitution, Phase I focuses on core functionality without test framework overhead.

## Next Steps

1. ✅ Planning complete (this file)
2. ➡️ Run `/sp.tasks` to generate actionable task list
3. ⏭️ Run `/sp.implement` to execute tasks
4. ⏭️ Manual validation against spec acceptance criteria
5. ⏭️ Commit completed feature

## Dependencies & Blockers

**Dependencies**: None - all requirements satisfied by Python 3.13+ standard library

**Blockers**: None identified

**Risks**: None - straightforward implementation with well-defined scope
