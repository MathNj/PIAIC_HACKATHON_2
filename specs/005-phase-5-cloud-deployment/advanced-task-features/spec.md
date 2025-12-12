# Feature Specification: Advanced Task Management Features

**Feature Branch**: `009-advanced-task-features`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Update @specs/features/task-crud.md and create @specs/database/schema-v2.md to include Advanced Level functionality: 1. Schema Updates: Add priority (High, Medium, Low), tags (List of strings), due_date (DateTime), is_recurring (Boolean) and recurrence_pattern (string, e.g., 'daily', 'weekly'). 2. Logic Updates: Search & Filter - API must support filtering by priority, tags, and date range. Sorting: Support sorting by due_date and priority. Ensure these changes are compatible with SQLModel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prioritize Tasks by Urgency (Priority: P1)

As an authenticated user, I want to assign priority levels (High, Medium, Low) to my tasks so that I can focus on the most urgent work first and organize my task list by importance.

**Why this priority**: Priority levels are the foundational organizational feature that provides immediate value. Users can instantly categorize tasks by urgency without needing complex filtering or sorting first. This is the minimum viable enhancement that transforms a flat task list into a prioritized action plan.

**Independent Test**: Can be fully tested by creating tasks with different priority levels (High, Medium, Low), verifying priority display in the UI, and confirming tasks can be sorted by priority. Delivers immediate organizational value without requiring tags or due dates.

**Acceptance Scenarios**:

1. **Given** user is creating a new task, **When** user selects "High" priority from dropdown, **Then** task is saved with priority_id=1 and displays red "High" badge
2. **Given** user has existing tasks, **When** user edits task and changes priority from "Low" to "Medium", **Then** priority updates and task displays yellow "Medium" badge
3. **Given** user has 5 High, 3 Medium, and 2 Low priority tasks, **When** user sorts by "Priority: High to Low", **Then** all High priority tasks appear first, followed by Medium, then Low
4. **Given** task without assigned priority (null), **When** viewing task, **Then** task displays gray "No Priority" badge and sorts to bottom of priority list
5. **Given** user creates task without selecting priority, **When** task is saved, **Then** priority defaults to null and user can assign priority later

---

### User Story 2 - Organize Tasks with Tags (Priority: P1)

As an authenticated user, I want to add multiple tags to tasks (e.g., "work", "personal", "urgent", "research") so that I can categorize tasks across multiple dimensions and quickly filter related tasks.

**Why this priority**: Tags provide flexible categorization that complements priority levels. Users immediately benefit from organizing tasks by context (work/personal), project, or category. This is essential for users managing tasks across different areas of life.

**Independent Test**: Can be fully tested by creating tasks with various tags, filtering by single or multiple tags, and verifying tag-based search works correctly. Delivers independent organizational value alongside priority levels.

**Acceptance Scenarios**:

1. **Given** user is creating a task "Prepare presentation", **When** user types tags "work, urgent, Q4" separated by commas, **Then** task is saved with 3 tags and displays all three as badges
2. **Given** user has tasks tagged with "work", "personal", "urgent", **When** user filters by tag "work", **Then** only tasks containing "work" tag appear in list
3. **Given** user filters by tags "work" AND "urgent", **When** viewing results, **Then** only tasks with both tags appear (intersection filtering)
4. **Given** user is editing task with tags "research, draft", **When** user adds "final" and removes "draft", **Then** task displays tags "research, final"
5. **Given** user types tag "Work" (capitalized), **When** task is saved, **Then** tag is normalized to lowercase "work" to prevent duplicate tags with different casing

---

### User Story 3 - Set Due Dates and Track Deadlines (Priority: P2)

As an authenticated user, I want to assign due dates to tasks so that I can track deadlines, see what's coming due soon, and sort tasks by urgency based on time sensitivity.

**Why this priority**: Due dates add time-based urgency on top of user-defined priority. Combined with P1 features (priority + tags), users can now manage tasks holistically (importance + category + deadline). Less critical than basic organization because users can work effectively without explicit deadlines.

**Independent Test**: Can be tested by creating tasks with various due dates (today, tomorrow, next week), filtering by date ranges (overdue, due today, due this week), and sorting by due date. Delivers deadline tracking independently.

**Acceptance Scenarios**:

1. **Given** user is creating task "Submit report", **When** user selects due date "2025-12-15" from date picker, **Then** task is saved with due_date and displays "Due Dec 15" next to task
2. **Given** task has due_date "2025-12-10" and today is "2025-12-12", **When** viewing task, **Then** task displays "Overdue by 2 days" in red text
3. **Given** user filters by "Due This Week", **When** today is "2025-12-11", **Then** only tasks with due_date between 2025-12-11 and 2025-12-17 appear
4. **Given** user has tasks with various due dates, **When** user sorts by "Due Date: Soonest First", **Then** tasks with nearest due dates appear first, followed by far-future dates, followed by no due date
5. **Given** task is marked complete with due_date "2025-12-20", **When** viewing completed tasks, **Then** task shows original due date and "Completed on Dec 18" (if completed early)

---

### User Story 4 - Create Recurring Tasks (Priority: P3)

As an authenticated user, I want to mark tasks as recurring with patterns (daily, weekly, monthly) so that repetitive tasks automatically regenerate without manual re-creation.

**Why this priority**: Recurring tasks are a quality-of-life feature that automates repetitive task creation. Users can work effectively by manually creating repeat tasks, making this enhancement helpful but not essential for core productivity. Depends on due dates (P2) to determine recurrence timing.

**Independent Test**: Can be tested by creating a recurring task with pattern "daily", verifying task regenerates automatically at specified intervals, and confirming recurrence pattern can be edited or disabled. Delivers automation value independently.

**Acceptance Scenarios**:

1. **Given** user creates task "Daily standup" with is_recurring=true and recurrence_pattern="daily", **When** task is completed today, **Then** new instance of task is created with due_date=tomorrow
2. **Given** recurring task "Weekly team meeting" with pattern "weekly", **When** today is Monday and task is completed, **Then** new instance is created with due_date=next Monday
3. **Given** recurring task with pattern "monthly", **When** task is completed on "2025-12-15", **Then** new instance is created with due_date="2026-01-15"
4. **Given** user views recurring task, **When** hovering over task, **Then** tooltip displays "Recurring: Daily" or "Recurring: Weekly"
5. **Given** user edits recurring task, **When** user changes recurrence_pattern from "weekly" to "monthly" or sets is_recurring=false, **Then** future instances follow new pattern or stop generating

---

### User Story 5 - Advanced Search and Filtering (Priority: P2)

As an authenticated user, I want to filter tasks by multiple criteria simultaneously (priority + tags + date range) and search by text so that I can quickly find specific tasks or focus on relevant subsets.

**Why this priority**: Advanced filtering makes the enhanced features (priority, tags, due dates) actionable. Without filtering, users must manually scan through tagged/prioritized tasks. This synthesizes P1/P2 features into a powerful query interface.

**Independent Test**: Can be tested by creating tasks with various combinations of priority, tags, and due dates, then applying complex filters (e.g., "High priority + 'work' tag + due this week") and verifying correct results. Delivers powerful search independently.

**Acceptance Scenarios**:

1. **Given** user has 20 tasks with mixed priorities, tags, and due dates, **When** user filters by "High priority + tag:'work' + due this week", **Then** only tasks matching all three criteria appear
2. **Given** user types search query "presentation" in search box, **When** searching, **Then** tasks with "presentation" in title or description appear (case-insensitive)
3. **Given** user filters by date range "2025-12-10 to 2025-12-15", **When** viewing results, **Then** only tasks with due_date in that range appear (inclusive)
4. **Given** user applies filter "tags:'work' OR tags:'urgent'", **When** viewing results, **Then** tasks with either tag appear (union filtering)
5. **Given** user has active filters applied, **When** user clicks "Clear all filters", **Then** all tasks display and filter controls reset to defaults

---

### User Story 6 - Sort Tasks by Multiple Dimensions (Priority: P3)

As an authenticated user, I want to sort tasks by due date, priority, or creation date so that I can view my task list organized in the way that best fits my current workflow.

**Why this priority**: Sorting provides flexible task list organization but is less critical than filtering. Users can manually scan through filtered results. Nice-to-have feature that enhances usability after core filtering is in place.

**Independent Test**: Can be tested by creating tasks with various due dates and priorities, applying different sort options, and verifying correct sort order for each dimension. Delivers flexible organization independently.

**Acceptance Scenarios**:

1. **Given** user has tasks with due dates spanning 2 weeks, **When** user selects "Sort by: Due Date (Soonest First)", **Then** tasks display in ascending due date order (overdue tasks first)
2. **Given** user has High, Medium, Low priority tasks, **When** user selects "Sort by: Priority (High to Low)", **Then** all High priority tasks appear first, then Medium, then Low, then null priority
3. **Given** user sorts by priority, **When** multiple tasks have same priority, **Then** secondary sort applies by creation date (newest first)
4. **Given** user applies sort "Due Date: Latest First", **When** viewing results, **Then** tasks without due dates appear first, followed by far-future dates, ending with soonest dates
5. **Given** user has both filters and sorting applied, **When** changing sort option, **Then** filters remain active and only sort order changes

---

### Edge Cases

- **What happens when user assigns invalid recurrence pattern?** System should validate recurrence_pattern field accepts only predefined values ("daily", "weekly", "monthly", "yearly") and return validation error "Invalid recurrence pattern. Use: daily, weekly, monthly, or yearly" for other values.

- **What happens when user creates recurring task without due date?** System should either: (1) require due_date when is_recurring=true, or (2) default to creating first instance with due_date=tomorrow for "daily" pattern, next Monday for "weekly", etc.

- **What happens when user filters by non-existent tag?** System should return empty result set with message "No tasks found with tag 'nonexistent'" rather than showing all tasks or error.

- **What happens when user sets priority to null after it was assigned?** System should allow null priority (representing "no priority set") and display as "No Priority" badge, sorting to bottom of priority list.

- **What happens when task is overdue by several months?** System should calculate days overdue up to reasonable limit (e.g., 365 days) and display "Overdue by 365+ days" for very old tasks to avoid large numbers.

- **What happens when user enters 50+ tags on a single task?** System should enforce reasonable limit (e.g., max 10 tags per task) and display validation error "Maximum 10 tags per task" to prevent abuse.

- **What happens when completing recurring task creates conflict with manually created similar task?** System should create new recurring instance regardless of existing tasks, allowing duplicates. User can manually delete unwanted duplicates.

- **What happens when user searches with special characters or SQL operators in search query?** System should sanitize search input, treat special characters as literals (not regex or SQL), and use parameterized queries to prevent SQL injection.

## Requirements *(mandatory)*

### Functional Requirements

**Priority Management**

- **FR-001**: System MUST support three predefined priority levels: High (id=1), Medium (id=2), Low (id=3)
- **FR-002**: System MUST store priorities in separate `priorities` table with columns: id (int), name (varchar), level (int), color (varchar)
- **FR-003**: System MUST pre-populate priorities table with: (1, 'High', 1, '#EF4444'), (2, 'Medium', 2, '#F59E0B'), (3, 'Low', 3, '#10B981')
- **FR-004**: System MUST add `priority_id` column to tasks table as nullable foreign key referencing priorities.id
- **FR-005**: System MUST allow users to assign priority to task during creation or edit (optional field)
- **FR-006**: System MUST allow users to update or remove task priority at any time
- **FR-007**: System MUST display priority as colored badge in UI (High=red, Medium=yellow, Low=green, None=gray)
- **FR-008**: System MUST support filtering tasks by one or more priority levels (e.g., "show High and Medium only")
- **FR-009**: System MUST support sorting tasks by priority level (High first, then Medium, then Low, then null)

**Tag Management**

- **FR-010**: System MUST support multiple tags per task stored as many-to-many relationship
- **FR-011**: System MUST create `tags` table with columns: id (int), name (varchar unique), created_at (timestamp)
- **FR-012**: System MUST create `task_tags` junction table with columns: task_id (int FK), tag_id (int FK), primary key (task_id, tag_id)
- **FR-013**: System MUST normalize tag names to lowercase before storing to prevent case-sensitive duplicates
- **FR-014**: System MUST trim whitespace from tag names and reject empty tags
- **FR-015**: System MUST enforce maximum tag name length of 30 characters
- **FR-016**: System MUST enforce maximum 10 tags per task
- **FR-017**: System MUST allow users to add, remove, or update tags on existing tasks
- **FR-018**: System MUST support filtering tasks by one or more tags with AND/OR logic
- **FR-019**: System MUST display tags as pill-shaped badges in UI with distinct colors per tag
- **FR-020**: System MUST auto-suggest existing tags while user types to encourage tag reuse

**Due Date Management**

- **FR-021**: System MUST add `due_date` column to tasks table as nullable DateTime field
- **FR-022**: System MUST allow users to set, update, or remove due date on any task
- **FR-023**: System MUST validate due_date is valid DateTime format (ISO 8601)
- **FR-024**: System MUST allow due dates in the past (for tracking overdue tasks)
- **FR-025**: System MUST calculate days until due or days overdue from current date
- **FR-026**: System MUST display due date in human-readable format (e.g., "Due Dec 15", "Due Tomorrow", "Due in 3 days")
- **FR-027**: System MUST highlight overdue tasks with red text or warning indicator
- **FR-028**: System MUST support filtering by date ranges: overdue, due today, due this week, due this month, custom range
- **FR-029**: System MUST support sorting tasks by due date (ascending: soonest first, descending: latest first)
- **FR-030**: System MUST treat tasks without due_date as lowest priority when sorting by due date

**Recurring Task Management**

- **FR-031**: System MUST add `is_recurring` boolean column to tasks table (default: false)
- **FR-032**: System MUST add `recurrence_pattern` varchar column to tasks table (nullable, values: 'daily', 'weekly', 'monthly', 'yearly')
- **FR-033**: System MUST validate recurrence_pattern is one of allowed values when is_recurring=true
- **FR-034**: System MUST require due_date when is_recurring=true (cannot have recurring task without due date)
- **FR-035**: System MUST create new task instance when recurring task is marked complete, with:
  - New due_date calculated from recurrence_pattern (daily: +1 day, weekly: +7 days, monthly: +1 month, yearly: +1 year)
  - Same title, description, priority, tags as original
  - completed=false, created_at=now(), is_recurring=true, recurrence_pattern preserved
- **FR-036**: System MUST display recurring indicator (e.g., "🔁 Daily") in task UI
- **FR-037**: System MUST allow users to disable recurrence by setting is_recurring=false
- **FR-038**: System MUST allow users to change recurrence_pattern on existing recurring task

**Advanced Filtering**

- **FR-039**: System MUST support filtering by priority: single or multiple priority levels
- **FR-040**: System MUST support filtering by tags: single tag, multiple tags with AND logic, multiple tags with OR logic
- **FR-041**: System MUST support filtering by due date ranges: overdue (< today), today (= today), this week (next 7 days), this month (current calendar month), custom range (start_date to end_date)
- **FR-042**: System MUST support combining multiple filters simultaneously (e.g., High priority + 'work' tag + due this week)
- **FR-043**: System MUST support text search across task title and description (case-insensitive substring match)
- **FR-044**: System MUST return empty result set with informative message when no tasks match filters
- **FR-045**: System MUST preserve filter state in URL query parameters for bookmarking and sharing
- **FR-046**: System MUST provide "Clear all filters" button to reset to unfiltered view

**Advanced Sorting**

- **FR-047**: System MUST support sorting by due_date (ascending/descending)
- **FR-048**: System MUST support sorting by priority (High to Low / Low to High)
- **FR-049**: System MUST support sorting by created_at (newest/oldest first)
- **FR-050**: System MUST apply secondary sort by created_at when primary sort has ties (e.g., multiple tasks with same priority)
- **FR-051**: System MUST treat null values consistently in sorting: null priority sorts to end, null due_date sorts to end
- **FR-052**: System MUST preserve sort selection across page refreshes

**API Enhancements**

- **FR-053**: System MUST extend GET /api/{user_id}/tasks endpoint to accept query parameters: priority[], tags[], due_date_from, due_date_to, search, sort_by, sort_order
- **FR-054**: System MUST extend POST /api/{user_id}/tasks endpoint to accept: priority_id, tags[], due_date, is_recurring, recurrence_pattern
- **FR-055**: System MUST extend PUT /api/{user_id}/tasks/{id} endpoint to allow updating priority_id, tags[], due_date, is_recurring, recurrence_pattern
- **FR-056**: System MUST implement GET /api/priorities endpoint to return list of available priorities
- **FR-057**: System MUST implement GET /api/{user_id}/tags endpoint to return user's existing tags for autocomplete
- **FR-058**: System MUST validate all new fields (priority_id exists, tags are valid, due_date is valid DateTime, recurrence_pattern is allowed value)
- **FR-059**: System MUST return HTTP 400 Bad Request with specific validation errors for invalid inputs

**Database Schema Compatibility**

- **FR-060**: All schema changes MUST be compatible with SQLModel and support both SQLite (local) and PostgreSQL (production)
- **FR-061**: System MUST create Alembic migration scripts for schema updates (priorities table, tags table, task_tags table, new columns on tasks table)
- **FR-062**: System MUST maintain backward compatibility: existing tasks without new fields should continue working
- **FR-063**: System MUST create appropriate indexes: tasks.priority_id, tasks.due_date, tasks.is_recurring, tags.name, task_tags.task_id, task_tags.tag_id
- **FR-064**: System MUST enforce foreign key constraints: tasks.priority_id → priorities.id, task_tags.task_id → tasks.id, task_tags.tag_id → tags.id

### Key Entities

- **Priority**: Represents task urgency level with attributes:
  - `id` (integer): Unique identifier (1=High, 2=Medium, 3=Low)
  - `name` (string): Display name ("High", "Medium", "Low")
  - `level` (integer): Numeric level for sorting (1=highest urgency)
  - `color` (string): Hex color code for UI badges

- **Tag**: Represents task category label with attributes:
  - `id` (integer): Unique auto-incrementing identifier
  - `name` (string): Tag name (unique, lowercase, max 30 chars)
  - `created_at` (timestamp): Tag creation date

- **TaskTag**: Junction table for many-to-many relationship between tasks and tags
  - `task_id` (integer): Foreign key to tasks.id
  - `tag_id` (integer): Foreign key to tags.id
  - Composite primary key: (task_id, tag_id)

- **Task (Enhanced)**: Extends existing Task entity with new attributes:
  - `priority_id` (integer, nullable): Foreign key to priorities.id
  - `due_date` (DateTime, nullable): Task deadline
  - `is_recurring` (boolean): Whether task regenerates on completion
  - `recurrence_pattern` (string, nullable): Recurrence frequency ('daily', 'weekly', 'monthly', 'yearly')
  - *All existing Task attributes remain unchanged*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priority to task and see colored badge displayed within 2 seconds of saving
- **SC-002**: Users can add multiple tags to task (up to 10) and see tag suggestions appear within 300ms of typing
- **SC-003**: Users can filter task list by priority + tags + date range and see filtered results within 1 second
- **SC-004**: System supports sorting by due date or priority with 100+ tasks without performance degradation (< 1 second)
- **SC-005**: Recurring task automatically creates new instance within 1 second of marking original complete
- **SC-006**: Advanced filtering API endpoint responds within 500ms for queries across 500 tasks with multiple filters
- **SC-007**: Tag autocomplete suggests relevant tags from user's existing tags within 300ms
- **SC-008**: Users can search task text and see matching results highlighted within 1 second for 100+ tasks
- **SC-009**: Database queries with multiple joins (tasks + priorities + tags) complete within 200ms with appropriate indexes
- **SC-010**: Schema migration scripts execute without data loss on existing production database
- **SC-011**: All new features work correctly in both SQLite (local development) and PostgreSQL (production)
- **SC-012**: Filter and sort selections persist across page refreshes via URL query parameters

### Implementation Validation

- **SC-013**: Alembic migration scripts successfully add priorities, tags, task_tags tables and new columns to tasks table
- **SC-014**: SQLModel models correctly define relationships: Task.priority (many-to-one), Task.tags (many-to-many)
- **SC-015**: Foreign key constraints enforced at database level prevent orphaned records
- **SC-016**: Tag name uniqueness enforced at database level (case-insensitive) prevents duplicate tags
- **SC-017**: API validation rejects invalid recurrence_pattern, tags exceeding limit, or invalid date formats with clear error messages
- **SC-018**: UI displays all new features (priority badges, tag pills, due date indicators, recurring icons) with correct styling

## Assumptions

1. **Recurrence Logic**: Recurring tasks create new instance on completion, not on due date passing. More complex scheduling (e.g., "every Monday and Friday") is out of scope.
2. **Tag Ownership**: Tags are user-scoped (each user has their own tag namespace). Global tags across all users are not supported.
3. **Priority Customization**: Priority levels are fixed (High/Medium/Low). Users cannot create custom priority levels.
4. **Time Zone Handling**: All due dates stored in UTC. Client-side conversion to user's local time zone handled by frontend.
5. **Recurring Task Instances**: Each recurring task instance is independent - editing one instance does not affect others.
6. **Bulk Operations**: Bulk update of priority/tags across multiple tasks is out of scope for this phase.
7. **Tag Colors**: Tag colors are auto-generated from tag name (hash-based color selection) rather than user-defined.
8. **Search Performance**: Text search uses simple substring matching. Full-text search with ranking is deferred to future enhancement.
9. **Overdue Notifications**: System displays overdue status in UI but does not send notifications (email/push). Notifications deferred to Phase V.
10. **Complex Recurrence**: Advanced patterns like "every 2nd Tuesday" or "monthly on 15th" are not supported. Only simple daily/weekly/monthly/yearly.

## Dependencies

- **Database Migration Tool**: Alembic for PostgreSQL schema migrations
- **SQLModel**: Version 0.0.14+ for new relationships (many-to-many, foreign keys)
- **Backend Changes**: FastAPI route updates for new query parameters and request body fields
- **Frontend Changes**: UI components for priority dropdown, tag input with autocomplete, date picker, filter controls, sort controls
- **Date Handling**: Python datetime library (backend), JavaScript Date API or date-fns library (frontend)

## Out of Scope

- Custom priority levels (user-defined priorities beyond High/Medium/Low)
- Global tags shared across all users
- Tag hierarchies or tag categories
- Subtasks or task dependencies
- Recurring patterns more complex than daily/weekly/monthly/yearly (e.g., "every 2nd Monday", "quarterly")
- Calendar view of tasks by due date
- Due date time component (only date, no specific time like "3:00 PM")
- Notifications or reminders for upcoming/overdue tasks (deferred to Phase V)
- Task templates (pre-configured tasks with priority/tags/recurrence)
- Bulk operations (apply tags or priority to multiple tasks at once)
- Tag renaming or merging (deleting tag affects all tasks)
- Analytics (most used tags, completion rate by priority)
- Export/import with new fields (CSV/JSON)
- Full-text search with ranking or fuzzy matching
- Undo/redo for tag or priority changes
