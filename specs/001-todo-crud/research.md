# Research: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-05
**Status**: Complete

## Overview

This document captures research findings and technical decisions for implementing the console-based TODO list application. All technical constraints are pre-defined by the project constitution, resulting in minimal research requirements.

## Technical Decisions

### Decision 1: Storage Data Structure

**Question**: Which Python data structure should store tasks?

**Options Considered**:
1. **List of Task objects** - Sequential storage with index-based access
2. **Dictionary {id: Task}** - Hash-based storage with key-based access
3. **List with index=ID** - Direct index access using task ID

**Decision**: Dictionary `{int: Task}`

**Rationale**:
- O(1) lookup complexity for get/update/delete/mark_complete operations
- Natural mapping of task ID to task object
- Efficient iteration over values for view_tasks
- No wasted memory from deleted task gaps (unlike list with index=ID)
- Simple implementation with clear semantics

**Trade-offs**:
- Slightly more memory overhead than list (hash table overhead)
- Not ordered by default (but can sort values by ID when viewing)
- Benefit: O(1) operations vastly outweigh minor memory cost for expected scale (up to 100 tasks)

### Decision 2: ID Generation Strategy

**Question**: How to generate unique auto-incrementing task IDs?

**Options Considered**:
1. **Counter variable** - Simple integer incremented on each add
2. **UUID** - Universally unique identifier
3. **Max ID + 1** - Scan existing IDs and add 1 to maximum

**Decision**: Counter variable starting at 1

**Rationale**:
- Meets FR-003 requirement for "unique incrementing integer IDs"
- Simple to implement: `self._next_id = 1`, increment after add
- No collision risk in single-user in-memory environment
- Predictable IDs for testing and debugging (1, 2, 3, ...)
- O(1) ID generation (no scanning required)

**Trade-offs**:
- IDs not reused after deletion (counter only increments)
- Benefit: Simplicity and performance far outweigh any "gap" concerns

### Decision 3: Input Validation Layer

**Question**: Where should input validation occur?

**Options Considered**:
1. **Presentation layer only** - Validate before calling TaskManager
2. **Logic layer only** - TaskManager validates and returns errors
3. **Both layers** - Redundant validation at presentation and logic

**Decision**: Presentation layer only

**Rationale**:
- Separation of concerns: Presentation handles I/O, Logic handles business rules
- TaskManager methods can assume valid input (cleaner code, no defensive checks)
- Centralized error messaging in presentation layer (consistent user experience)
- Easier to test logic layer with known-valid inputs
- Follows "fail-fast" principle at system boundary

**Trade-offs**:
- TaskManager not usable as library without validation wrapper
- Benefit: For single-file console app, cleaner architecture and code outweighs library reusability concerns

### Decision 4: Task Data Representation

**Question**: How to represent the Task entity in Python?

**Options Considered**:
1. **Dictionary** - `{"id": 1, "title": "...", ...}`
2. **Named Tuple** - `Task = namedtuple("Task", ["id", "title", ...])`
3. **Data Class** - `@dataclass class Task:`
4. **Regular Class** - Manual __init__ and __repr__ methods

**Decision**: Data Class with `@dataclass` decorator

**Rationale**:
- Type hints for all attributes (constitution requirement)
- Automatic __init__, __repr__, __eq__ generation (less boilerplate)
- Mutable by default (needed for update operations)
- Cleaner syntax than namedtuple or dict
- Better IDE support and type checking than dictionary

**Trade-offs**:
- Requires Python 3.7+ (satisfied by Python 3.13+ requirement)
- Slightly more overhead than dict (negligible for 100 tasks)

## Best Practices Applied

### Python Standard Library Usage

**Modules Used**:
- `typing`: For type hints (Optional, List, Dict)
- `dataclasses`: For @dataclass decorator

**Modules NOT Used**:
- No `sys` module needed (print/input sufficient for I/O)
- No `json`, `pickle`, `sqlite3` (violates in-memory constraint)
- No `argparse`, `click` (violates standard library constraint - these are external for argparse or click)

**Note**: Actually, `argparse` IS in standard library, but not needed since we use menu-driven interface, not command-line arguments.

### Error Handling Patterns

**Pattern**: Try-except with user-friendly messages and retry loop

```python
while True:
    try:
        choice = int(input("Select option (1-6): "))
        if 1 <= choice <= 6:
            return choice
        print("Invalid option. Please select 1-6.")
    except ValueError:
        print("Invalid input. Please enter a number.")
```

**Benefits**:
- Graceful handling of non-numeric input
- Clear error messages matching spec edge cases
- Continues looping until valid input (no crash)

### Code Organization Patterns

**Pattern**: Layered architecture in single file with clear sections

1. **Imports** (top of file)
2. **Model Layer** (data classes)
3. **Logic Layer** (business logic classes)
4. **Presentation Layer** (I/O functions)
5. **Entry Point** (if __name__ == "__main__")

**Benefits**:
- Clear separation of concerns
- Easy to locate code by responsibility
- Facilitates future refactoring (if needed in Phase II)

## Research Summary

**Unknowns Resolved**: All (4 decisions documented above)

**External Resources**: None required - all decisions based on Python standard patterns and constitution constraints

**Open Questions**: None

**Ready for Implementation**: ✅ Yes - proceed to task generation
