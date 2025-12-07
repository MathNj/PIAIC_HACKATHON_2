# Tasks: Console CRUD Operations

**Input**: Design documents from `/specs/001-todo-crud/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md, research.md, quickstart.md

**Tests**: Tests are NOT included in this task list per Phase I constitution (manual testing only)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single file project**: `src/main.py` (all code in one file per plan.md)
- No tests/ directory for Phase I (manual testing only)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create src/ directory in repository root
- [x] T002 Create src/main.py with Python 3.13+ shebang and imports (typing, dataclasses)
- [x] T003 [P] Define Task dataclass with id, title, description, completed attributes in src/main.py
- [x] T004 [P] Define TaskManager class skeleton with __init__ in src/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement TaskManager.__init__ with _tasks dict and _next_id counter in src/main.py
- [x] T006 Implement display_menu() function with main menu format from contracts in src/main.py
- [x] T007 Implement get_menu_choice() function with input validation (1-6) in src/main.py
- [x] T008 Implement main() function with while loop and menu dispatch structure in src/main.py
- [x] T009 Add if __name__ == "__main__" entry point calling main() in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks with title/description and view all tasks in a list

**Independent Test**: Add multiple tasks with different titles and descriptions, then view the task list to verify all tasks appear with correct IDs, statuses ([ ] for incomplete), and titles

### Implementation for User Story 1

- [x] T010 [P] [US1] Implement TaskManager.add_task(title, description) method returning task ID in src/main.py
- [x] T011 [P] [US1] Implement TaskManager.view_tasks() method returning sorted list of tasks in src/main.py
- [x] T012 [US1] Implement handle_add_task(manager) function with title validation and description input in src/main.py
- [x] T013 [US1] Implement handle_view_tasks(manager) function with task list formatting per contract in src/main.py
- [x] T014 [US1] Wire up menu option 1 to handle_add_task in main() function in src/main.py
- [x] T015 [US1] Wire up menu option 2 to handle_view_tasks in main() function in src/main.py
- [x] T016 [US1] Wire up menu option 6 (Exit) with "Goodbye!" message and break in main() function in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks, view tasks, and exit

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to mark tasks as complete by ID, changing status from [ ] to [x]

**Independent Test**: Add tasks using P1 functionality, mark specific tasks complete by ID, then view tasks to verify completed tasks show [x] status while incomplete show [ ] status

### Implementation for User Story 2

- [x] T017 [P] [US2] Implement TaskManager.mark_complete(task_id) method returning success boolean in src/main.py
- [x] T018 [P] [US2] Implement TaskManager.get_task(task_id) helper method returning Task or None in src/main.py
- [x] T019 [US2] Implement handle_mark_complete(manager) function with ID validation and error handling in src/main.py
- [x] T020 [US2] Wire up menu option 5 to handle_mark_complete in main() function in src/main.py
- [x] T021 [US2] Update handle_view_tasks to format status indicator correctly ([x] vs [ ]) in src/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add, view, mark complete, and exit

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to update task title and/or description by ID while preserving ID and completion status

**Independent Test**: Create a task using P1 functionality, update its title and/or description by ID, then view tasks to verify the task retains its ID and completion status while displaying updated content

### Implementation for User Story 3

- [x] T022 [US3] Implement TaskManager.update_task(task_id, title, description) method with None-skipping in src/main.py
- [x] T023 [US3] Implement handle_update_task(manager) function with ID validation and optional field inputs in src/main.py
- [x] T024 [US3] Add "No changes made." logic when both title and description are None in handle_update_task in src/main.py
- [x] T025 [US3] Wire up menu option 3 to handle_update_task in main() function in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can add, view, update, mark complete, and exit

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: Enable users to delete tasks by ID, removing them from the task list permanently

**Independent Test**: Create multiple tasks using P1 functionality, delete specific tasks by ID, then view tasks to verify only the specified tasks are removed while others remain

### Implementation for User Story 4

- [x] T026 [US4] Implement TaskManager.delete_task(task_id) method returning success boolean in src/main.py
- [x] T027 [US4] Implement handle_delete_task(manager) function with ID validation and error handling in src/main.py
- [x] T028 [US4] Wire up menu option 4 to handle_delete_task in main() function in src/main.py

**Checkpoint**: All user stories should now be independently functional - full CRUD + complete operations available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling refinements, edge cases, and final validation

- [x] T029 [P] Add error handling for non-numeric task IDs across all ID input functions in src/main.py
- [x] T030 [P] Add error handling for empty title validation in handle_add_task with retry loop in src/main.py
- [x] T031 [P] Add "Task ID {id} not found" error messages for update/delete/mark_complete operations in src/main.py
- [x] T032 Add final integration test using quickstart.md example scenarios
- [x] T033 Verify all CLI contract messages match contracts/cli-interface.md exactly
- [x] T034 [P] Add type hints to all function signatures per constitution requirement in src/main.py
- [x] T035 [P] Add docstrings (Google style) to Task, TaskManager, and all functions in src/main.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories should proceed sequentially in priority order: US1 → US2 → US3 → US4
  - US1 must complete first (adds MVP: Add + View)
  - US2 adds Mark Complete (depends on US1's view functionality)
  - US3 adds Update (independent of US2)
  - US4 adds Delete (independent of US2, US3)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 (extends view_tasks formatting for status display)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US2
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent of US2, US3

### Within Each User Story

- Models before services (Task dataclass before TaskManager)
- Services before presentation (TaskManager methods before handler functions)
- Core implementation before wiring (handlers before menu dispatch)
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003 (Task dataclass) and T004 (TaskManager skeleton) can run in parallel
- **Phase 3 (US1)**: T010 (add_task method) and T011 (view_tasks method) can run in parallel
- **Phase 4 (US2)**: T017 (mark_complete method) and T018 (get_task helper) can run in parallel
- **Phase 7 (Polish)**: T029 (ID validation), T030 (title validation), T031 (error messages), T034 (type hints), T035 (docstrings) can all run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Launch core business logic methods together:
Task T010: "Implement TaskManager.add_task(title, description) method"
Task T011: "Implement TaskManager.view_tasks() method"

# Then implement presentation layer handlers sequentially:
Task T012: "Implement handle_add_task(manager) function"
Task T013: "Implement handle_view_tasks(manager) function"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → File structure and data models ready
2. Complete Phase 2: Foundational → Menu system and main loop ready
3. Complete Phase 3: User Story 1 → Add and View tasks working
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md scenarios
5. Demonstrate or deploy if ready (minimal viable TODO list)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Ready** (add + view + exit)
3. Add User Story 2 → Test independently → **Version 1.1** (+ mark complete)
4. Add User Story 3 → Test independently → **Version 1.2** (+ update)
5. Add User Story 4 → Test independently → **Version 1.3** (+ delete - full CRUD)
6. Complete Polish → **Version 1.0 Release** (production-ready)

### Sequential Strategy (Single Developer)

1. Complete phases 1-2 (Setup + Foundational)
2. Implement US1 → validate → commit
3. Implement US2 → validate → commit
4. Implement US3 → validate → commit
5. Implement US4 → validate → commit
6. Polish → final validation → release

---

## Notes

- All code in single file: src/main.py (per plan.md architecture decision)
- [P] tasks = different logical sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests (Phase I uses manual testing per constitution)
- Commit after each phase completion
- Stop at any checkpoint to validate story independently against spec.md acceptance scenarios
- Error messages must match contracts/cli-interface.md exactly

---

## Validation Checklist (Use during Phase 7)

Per contracts/cli-interface.md Implementation Checklist:

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

---

## Total Task Count

- **Setup**: 4 tasks
- **Foundational**: 5 tasks (blocking)
- **User Story 1**: 7 tasks (MVP)
- **User Story 2**: 5 tasks
- **User Story 3**: 4 tasks
- **User Story 4**: 3 tasks
- **Polish**: 7 tasks

**TOTAL**: 35 tasks

**Parallel Opportunities**: 11 tasks marked [P] can run concurrently with other tasks

**MVP Scope**: Phases 1-3 only (16 tasks) delivers add + view + exit functionality
