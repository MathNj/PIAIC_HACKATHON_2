---
id: 001
title: Create Microservices Spec
stage: spec
date: 2025-12-11
surface: agent
model: claude-sonnet-4.5
feature: microservices
branch: 010-microservices
user: Najma-LP
command: /sp.specify
labels: ["microservices", "event-driven", "dapr", "recurring-tasks", "notifications", "spec"]
links:
  spec: specs/010-microservices/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/010-microservices/spec.md
  - specs/010-microservices/checklists/requirements.md
tests:
  - All checklist items validated and passed
---

## Prompt

/sp.specify "Create @specs/features/microservices.md.
Define two services:
1. **Recurring Task Service:** Listens to `task-events`. If a task is completed AND recurring, it calculates the next due date and calls the `add_task` tool/API.
2. **Notification Service:** Listens to the `reminder-cron` binding. Queries DB for tasks due in the next 15 mins. Publishes to `reminders` topic."

## Response snapshot

Created comprehensive specification for event-driven microservices on branch `010-microservices`:

**Services Defined:**
1. **Recurring Task Service**
   - Subscribes to `task-events` Dapr pub/sub topic
   - Filters for task completion events where `is_recurring = true`
   - Calculates next due date based on recurrence pattern (daily/weekly/monthly/yearly)
   - Creates new task instance via API with reset completion status
   - Includes retry logic and comprehensive error handling

2. **Notification Service**
   - Uses Dapr cron binding (`reminder-cron`) for scheduled execution
   - Queries database for tasks due within 15 minutes
   - Publishes reminder events to `reminders` topic
   - Implements deduplication to prevent duplicate notifications
   - Handles timezone conversions (UTC storage)

**Specification Structure:**
- 2 prioritized user stories (P1: Recurring tasks, P2: Reminders)
- 20 functional requirements (FR-001 to FR-020)
- 8 measurable success criteria (latency, accuracy, deduplication metrics)
- 7 edge cases identified
- Comprehensive assumptions and out-of-scope sections

**Quality Validation:**
- All checklist items passed
- No clarifications needed - all requirements clear and testable
- Success criteria are measurable and technology-agnostic
- Ready for `/sp.plan` or `/sp.clarify`

## Outcome

- ✅ Impact: Created complete specification for two event-driven microservices enabling recurring task automation and proactive reminders
- 🧪 Tests: All quality checklist items validated (Content Quality, Requirement Completeness, Feature Readiness)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: `/sp.plan` to create architectural plan, or `/sp.tasks` to generate implementation tasks
- 🧠 Reflection: Specification successfully defines clear service boundaries, event flows, and measurable outcomes without implementation details

## Evaluation notes (flywheel)

- Failure modes observed: None - specification creation completed without issues
- Graders run and results (PASS/FAIL): All quality checklist items PASS
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed with `/sp.plan` to design Dapr component configurations and service architecture
