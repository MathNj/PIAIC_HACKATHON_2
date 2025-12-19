# Feature Specification: Event-Driven Microservices

**Feature Branch**: `010-microservices`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Create @specs/features/microservices.md. Define two services: 1. **Recurring Task Service:** Listens to `task-events`. If a task is completed AND recurring, it calculates the next due date and calls the `add_task` tool/API. 2. **Notification Service:** Listens to the `reminder-cron` binding. Queries DB for tasks due in the next 15 mins. Publishes to `reminders` topic."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Recurring Task Creation (Priority: P1)

When a user completes a recurring task (e.g., "Daily standup meeting"), the system automatically creates a new instance of that task with the next due date calculated based on the recurrence pattern, so users don't have to manually recreate repetitive tasks.

**Why this priority**: This is the core value proposition for recurring tasks - automation of repetitive task management. Without this, users would need to manually recreate tasks, defeating the purpose of the recurring task feature.

**Independent Test**: Can be fully tested by marking a recurring task as complete and verifying a new task instance is created with the correct next due date. Delivers immediate value by eliminating manual task recreation.

**Acceptance Scenarios**:

1. **Given** a recurring task with pattern "daily" and due date "2025-12-11 09:00", **When** user marks the task as completed, **Then** a new task is created with due date "2025-12-12 09:00" and all other attributes copied
2. **Given** a recurring task with pattern "weekly" and due date "2025-12-11 14:00", **When** user marks the task as completed, **Then** a new task is created with due date "2025-12-18 14:00"
3. **Given** a recurring task with pattern "monthly" and due date "2025-12-11 10:00", **When** user marks the task as completed, **Then** a new task is created with due date "2026-01-11 10:00"
4. **Given** a recurring task with pattern "yearly" and due date "2025-12-11 08:00", **When** user marks the task as completed, **Then** a new task is created with due date "2026-12-11 08:00"

---

### User Story 2 - Proactive Task Reminders (Priority: P2)

Users receive notifications for tasks that are approaching their due date (within 15 minutes), so they can stay on top of time-sensitive work and never miss important deadlines.

**Why this priority**: This enhances task management by providing proactive notifications, but the system remains functional without it. Users can still see due dates manually in the UI.

**Independent Test**: Can be tested by creating tasks with due dates 15 minutes in the future and verifying reminder notifications are published. Delivers value by reducing missed deadlines.

**Acceptance Scenarios**:

1. **Given** a task with due date 12 minutes in the future, **When** the cron scheduler runs, **Then** a reminder notification is published to the `reminders` topic
2. **Given** a task with due date 5 minutes in the future, **When** the cron scheduler runs, **Then** a reminder notification is published to the `reminders` topic
3. **Given** a task with due date 20 minutes in the future, **When** the cron scheduler runs, **Then** no reminder is published (outside 15-minute window)
4. **Given** a task with due date in the past, **When** the cron scheduler runs, **Then** no reminder is published (already overdue)
5. **Given** a completed task with due date 10 minutes in the future, **When** the cron scheduler runs, **Then** no reminder is published (task already completed)

---

### Edge Cases

- What happens when a recurring task is completed multiple times in quick succession before the service processes the event?
- How does the Recurring Task Service handle tasks with invalid or missing recurrence patterns?
- What happens if the Notification Service cannot connect to the database?
- How does the system handle reminder notifications for tasks that are deleted between query and publish?
- What happens if the `add_task` API call fails when creating the next recurring task instance?
- How does the system prevent duplicate reminders if the cron job runs multiple times within the same 15-minute window?
- What happens when a recurring task's due date calculation results in an invalid date (e.g., February 30)?

## Requirements *(mandatory)*

### Functional Requirements

#### Recurring Task Service

- **FR-001**: Service MUST subscribe to the `task-events` Dapr pub/sub topic to receive task lifecycle events
- **FR-002**: Service MUST filter incoming events to only process task completion events (status changed to completed)
- **FR-003**: Service MUST verify that the completed task has `is_recurring` flag set to `true` before processing
- **FR-004**: Service MUST extract the `recurrence_pattern` field from the task (values: "daily", "weekly", "monthly", "yearly")
- **FR-005**: Service MUST calculate the next due date based on the recurrence pattern and current due date:
  - Daily: Add 1 day
  - Weekly: Add 7 days
  - Monthly: Add 1 month (same day of month)
  - Yearly: Add 1 year (same month and day)
- **FR-006**: Service MUST create a new task by calling the `add_task` API endpoint with:
  - Same title, description, priority_id, tag_ids, is_recurring, and recurrence_pattern
  - Calculated next due date
  - Completed status reset to `false`
  - New created_at and updated_at timestamps
- **FR-007**: Service MUST handle API call failures gracefully with retry logic (exponential backoff, max 3 retries)
- **FR-008**: Service MUST log all recurring task creation events including task ID, old due date, new due date, and recurrence pattern
- **FR-009**: Service MUST ignore non-recurring tasks (is_recurring = false) in task-events
- **FR-010**: Service MUST validate that recurrence_pattern is one of the allowed values before processing

#### Notification Service

- **FR-011**: Service MUST use Dapr cron binding named `reminder-cron` to trigger reminder checks on a schedule
- **FR-012**: Service MUST query the database for tasks matching these criteria:
  - due_date is between NOW and NOW + 15 minutes
  - completed = false (task not yet completed)
  - user_id is not null (task belongs to a user)
- **FR-013**: Service MUST publish a reminder event to the `reminders` Dapr pub/sub topic for each matching task
- **FR-014**: Reminder event payload MUST include: task_id, user_id, title, due_date, priority_id, and time_until_due
- **FR-015**: Service MUST track which tasks have already received reminders to prevent duplicate notifications
- **FR-016**: Service MUST clear the reminder tracking cache after the task's due date has passed
- **FR-017**: Service MUST handle database connection failures with appropriate error logging and retry logic
- **FR-018**: Service MUST limit the number of reminders processed in a single cron execution to prevent overwhelming the pub/sub system
- **FR-019**: Service MUST log all reminder publications including task ID, user ID, and due date
- **FR-020**: Service MUST handle timezone conversions appropriately (all due dates stored in UTC)

### Key Entities *(include if feature involves data)*

- **Task Event**: Represents a task lifecycle event published to `task-events` topic
  - Attributes: event_type (created, updated, deleted, completed), task_id, user_id, task data (title, description, priority_id, due_date, is_recurring, recurrence_pattern, completed), timestamp
  - Relationships: Associated with a specific task and user

- **Reminder Event**: Represents a notification for an upcoming task published to `reminders` topic
  - Attributes: task_id, user_id, title, due_date, priority_id, time_until_due (minutes), timestamp
  - Relationships: Associated with a specific task and user

- **Recurring Task**: Task with is_recurring flag enabled
  - Attributes: All standard task attributes plus is_recurring (boolean), recurrence_pattern (enum: daily/weekly/monthly/yearly)
  - Relationships: Creates new task instances when completed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a recurring task is marked complete, a new task instance is created within 5 seconds
- **SC-002**: The next recurring task instance has the correct due date calculated based on the recurrence pattern (100% accuracy)
- **SC-003**: Users receive reminder notifications for tasks due within 15 minutes with 95% delivery success rate
- **SC-004**: The Notification Service checks for upcoming tasks at least every 5 minutes to ensure timely reminders
- **SC-005**: No duplicate recurring task instances are created for the same completion event (100% deduplication)
- **SC-006**: No duplicate reminder notifications are sent for the same task (100% deduplication)
- **SC-007**: Both services handle event processing with latency under 2 seconds (95th percentile)
- **SC-008**: Services recover automatically from transient failures (database unavailable, API timeout) within 30 seconds

## Assumptions

- Both services will use Dapr for pub/sub and bindings integration
- Task API endpoints already exist and support task creation
- Database connection credentials are available via environment variables or configuration
- Cron schedule for reminder-cron binding is configurable (default: every 5 minutes)
- All due dates are stored in UTC timezone in the database
- The system uses Dapr's guaranteed delivery semantics for pub/sub messages
- Services will be deployed as independent containers/processes in the Kubernetes cluster
- Reminder notifications will be consumed by a separate frontend/notification delivery service (out of scope for this spec)
- Task completion events are published to `task-events` topic by the existing Task API

## Out of Scope

- Frontend UI changes to display recurring task indicators
- User preferences for reminder timing (fixed at 15 minutes)
- Email or push notification delivery (reminders topic consumption)
- Manual triggering of recurring task creation by users
- Pausing or skipping recurring task instances
- Modification of recurrence patterns on existing tasks (handled by Task API)
- Historical tracking of recurring task chains
- Custom recurrence patterns (e.g., "every 2 weeks", "first Monday of month")
