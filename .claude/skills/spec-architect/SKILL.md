---
name: "spec-architect"
description: "Generates Spec-Kit Plus compliant feature specifications for the Todo App. Use when designing features or creating specs following the project's spec-driven development workflow."
version: "2.0.0"
---

# Spec Architecture Skill

## When to Use
- User asks to "design" or "spec out" a new feature (e.g., "Recurring Tasks", "Tags", "Collaboration")
- User says "Create a feature spec" or "Run spec architect"
- Starting Phase II or new feature work
- Before implementation to establish clear requirements

## Context
This skill follows the Spec-Kit Plus methodology from `CLAUDE.md`:
- Specs live in `/specs/features/[feature-name].md`
- Technology-agnostic (focus on "what", not "how")
- Referenced with `@specs/features/[feature].md`
- Always create PHR after completing spec

## Workflow
1. **Analyze Intent**: Identify the core problem and user goal
2. **Define User Stories**: Create 3-5 "As a user, I want..." statements with value propositions
3. **Define Acceptance Criteria**: Create testable, bulleted checklists for 'Done'
4. **Data Modeling**: Define required fields (align with SQLModel for backend)
5. **API Contract**: Define REST endpoints, request/response schemas, status codes
6. **UI Requirements**: Define key screens, interactions, and UX flows (technology-agnostic)
7. **Dependencies**: Identify integration points with existing features
8. **Non-Functional Requirements**: Consider performance, security, accessibility

## Output Template (Markdown)
Save to: `/specs/features/[feature-name].md`

```markdown
# Feature: [Feature Name]

## Overview
[2-3 sentence description of what this feature does and why it's valuable]

## User Stories
- **US-1**: As a [user type], I want [goal], so that [benefit]
- **US-2**: As a [user type], I want [goal], so that [benefit]
- **US-3**: As a [user type], I want [goal], so that [benefit]

## Acceptance Criteria
- [ ] **AC-1**: [Testable criterion]
- [ ] **AC-2**: [Testable criterion]
- [ ] **AC-3**: [Testable criterion]
- [ ] **AC-4**: [Testable criterion]

## Data Model (Backend)
### New Tables/Models Required
- **Model Name**: [e.g., Tag, Recurring Task, Comment]
  - `id`: Integer (Primary Key)
  - `user_id`: UUID (Foreign Key to User)
  - `[field]`: [Type] ([constraints])
  - `created_at`: DateTime (UTC)
  - `updated_at`: DateTime (UTC)

### Relationships
- [Describe relationships with existing models]

### Indexes
- Index on `user_id` for multi-user isolation
- [Additional indexes for performance]

## API Endpoints

### 1. [Endpoint Name]
- **Method**: GET/POST/PUT/DELETE
- **Path**: `/api/{user_id}/[resource]`
- **Auth**: Required (JWT Bearer token)
- **Request Body** (if applicable):
  ```json
  {
    "field": "value"
  }
  ```
- **Response (200/201)**:
  ```json
  {
    "id": 1,
    "field": "value"
  }
  ```
- **Errors**:
  - `400`: Validation error
  - `401`: Unauthorized
  - `403`: Forbidden (user_id mismatch)
  - `404`: Resource not found

### 2. [Additional endpoints...]

## UI Requirements (Technology-Agnostic)

### Key Screens
1. **[Screen Name]**:
   - Description: [What user sees]
   - Actions: [What user can do]
   - Navigation: [How to access]

### User Flows
1. **[Flow Name]**: [Step by step user interaction]

### Components Needed
- [Component 1]: [Purpose]
- [Component 2]: [Purpose]

## Dependencies & Integration
- **Existing Features**: [List features this depends on]
- **Database Schema**: [Changes or additions]
- **Authentication**: [How auth is integrated]

## Non-Functional Requirements
- **Performance**: [Response time, query optimization]
- **Security**: [Data validation, authorization]
- **Accessibility**: [WCAG compliance, keyboard navigation]
- **Testing**: [Unit tests, integration tests needed]

## Implementation Phases
1. **Phase 1**: [Backend models and API]
2. **Phase 2**: [Frontend UI components]
3. **Phase 3**: [Integration and testing]

## Out of Scope
- [Explicitly state what is NOT included in this feature]

## References
- Related Specs: `@specs/features/[related-feature].md`
- API Docs: `@specs/api/rest-endpoints.md`
- Database Schema: `@specs/database/schema.md`
```

## Post-Spec Actions
1. Save spec to `/specs/features/[feature-name].md`
2. Update `/specs/overview.md` if needed
3. Create PHR using `/sp.phr` or manual creation:
   - Title: "[Feature Name] Specification"
   - Stage: `spec`
   - Feature: `[feature-name]`
4. Suggest next step: "Run `/sp.plan` to create implementation plan"

## Example
**Input**: "Design a tagging system for tasks"

**Output**: Complete spec at `/specs/features/task-tags.md` with:
- User stories for creating, assigning, filtering by tags
- Tag model (id, user_id, name, color, created_at)
- API endpoints: POST/GET/DELETE `/api/{user_id}/tags`
- Tag assignment endpoint: POST `/api/{user_id}/tasks/{task_id}/tags/{tag_id}`
- UI requirements: Tag input component, tag filter chips, color picker
- Acceptance criteria: User can create tags, assign to tasks, filter task list by tag

## Quality Checklist
Before finalizing:
- [ ] All user stories have clear value propositions
- [ ] Acceptance criteria are testable and measurable
- [ ] Data model includes all necessary fields and relationships
- [ ] API endpoints follow RESTful conventions
- [ ] Security and authorization are addressed
- [ ] Dependencies on existing features are identified
- [ ] Non-functional requirements are specified
- [ ] Implementation is broken into logical phases