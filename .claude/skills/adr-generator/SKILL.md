---
name: "adr-generator"
description: "Creates Architecture Decision Records (ADRs) documenting significant architectural decisions with context, options considered, rationale, and consequences. Use when architectural decisions need formal documentation, tradeoff analysis is required, or team alignment on technical choices is needed."
version: "1.0.0"
---

# ADR Generator Skill

## When to Use
- User says "Create an ADR for..." or "Document this architectural decision"
- Significant architectural decision made (passes 3-part test: Impact + Alternatives + Scope)
- Need to document technology choices, patterns, or design decisions
- Team needs alignment on technical direction
- Future developers need to understand "why" decisions were made
- Planning Phase transitions (I→II, II→III, etc.)

## Context
This skill implements the ADR (Architecture Decision Record) pattern from the constitution:
- **Purpose**: Document architecturally significant decisions with full context and rationale
- **Format**: Markdown files in `history/adr/` directory
- **Numbering**: Sequential (001, 002, 003, ...)
- **Status**: Proposed → Accepted/Rejected/Superseded
- **Lifecycle**: ADRs are immutable once accepted (new ADRs supersede old ones)

## Workflow

### 1. Validate Significance (3-Part Test)
Before creating an ADR, verify the decision is architecturally significant:

**Test Questions**:
1. **Impact**: Does this have long-term architectural consequences? (frameworks, data models, APIs, security, platform)
2. **Alternatives**: Were multiple viable options considered?
3. **Scope**: Is this cross-cutting or system-defining?

**Result**: If all three are YES, create an ADR. Otherwise, document in code comments or commit messages.

### 2. Gather Information
- **Decision Title**: Concise description (5-8 words)
- **Context**: What problem are we solving? What constraints exist?
- **Options Considered**: At least 2-3 alternatives with pros/cons
- **Chosen Option**: Which was selected and why?
- **Consequences**: Positive, negative, and neutral impacts

### 3. Determine ADR Number
- Check `history/adr/` for existing ADRs
- Increment highest number by 1
- Format as 3-digit zero-padded (001, 002, etc.)

### 4. Create ADR File
- **Filename**: `history/adr/NNN-decision-title-slug.md`
- **Status**: Start with "Proposed" (becomes "Accepted" after approval)
- **Date**: YYYY-MM-DD format

### 5. Write ADR Content
Use the template below, filling all sections completely.

### 6. Review with User
- Present ADR draft for review
- Incorporate feedback
- Update status to "Accepted" upon approval

## Output Format

### ADR Template

```markdown
# ADR-NNN: [Decision Title]

**Status**: Proposed | Accepted | Rejected | Superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Decision Makers**: [User/Team/Role]
**Tags**: #[tag1] #[tag2] #[tag3]

---

## Context

[What is the issue we're addressing? What factors led to this decision?]

**Problem Statement**:
[Clear description of the problem or need]

**Constraints**:
- [Constraint 1: e.g., budget, timeline, team expertise]
- [Constraint 2: e.g., existing technology stack]
- [Constraint 3: e.g., regulatory requirements]

**Assumptions**:
- [Assumption 1: what we're taking for granted]
- [Assumption 2: expected future conditions]

---

## Decision

[What decision was made? State clearly and concisely.]

**Chosen Option**: [Option name/description]

**Rationale**:
[Why was this option chosen over alternatives? What makes it the best fit?]

---

## Options Considered

### Option 1: [Name]

**Description**:
[Detailed description of this approach]

**Pros**:
- ✅ [Advantage 1]
- ✅ [Advantage 2]
- ✅ [Advantage 3]

**Cons**:
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]
- ❌ [Disadvantage 3]

**Cost/Complexity**: [Low/Medium/High]

---

### Option 2: [Name]

**Description**:
[Detailed description of this approach]

**Pros**:
- ✅ [Advantage 1]
- ✅ [Advantage 2]

**Cons**:
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]

**Cost/Complexity**: [Low/Medium/High]

---

### Option 3: [Name]

**Description**:
[Detailed description of this approach]

**Pros**:
- ✅ [Advantage 1]
- ✅ [Advantage 2]

**Cons**:
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]

**Cost/Complexity**: [Low/Medium/High]

---

## Consequences

### Positive
- [Benefit 1: how this improves the system]
- [Benefit 2: opportunities this creates]
- [Benefit 3: problems this solves]

### Negative
- [Tradeoff 1: what we're giving up]
- [Tradeoff 2: new constraints introduced]
- [Tradeoff 3: increased complexity or cost]

### Neutral
- [Impact 1: neither good nor bad, just different]
- [Impact 2: changes that don't affect quality]

---

## Implementation Notes

**Immediate Actions**:
1. [Action 1: what needs to happen first]
2. [Action 2: next steps]
3. [Action 3: follow-up tasks]

**Migration Path** (if applicable):
[How to transition from current state to new architecture]

**Testing Strategy**:
[How to validate this decision works as expected]

**Rollback Plan**:
[How to reverse this decision if needed]

**Timeline**:
- [Milestone 1]: [Date]
- [Milestone 2]: [Date]
- [Complete by]: [Date]

---

## References

- [Related ADR-XXX]: [Title and link]
- [Spec]: [Path to relevant specification]
- [External Doc]: [URL to vendor documentation, RFC, etc.]
- [Discussion]: [Link to issue, PR, or meeting notes]

---

## Review History

| Date | Reviewer | Action | Notes |
|------|----------|--------|-------|
| YYYY-MM-DD | [Name] | Proposed | Initial draft |
| YYYY-MM-DD | [Name] | Accepted | Approved by team |

---

**Supersedes**: ADR-XXX (if applicable)
**Superseded by**: ADR-YYY (if applicable)
```

## Common Decision Categories

### 1. Technology Stack Decisions
**Example**: Choosing FastAPI vs Flask for backend

**Key Considerations**:
- Performance requirements
- Team expertise
- Ecosystem maturity
- Long-term support

### 2. Architecture Pattern Decisions
**Example**: Monolith vs Microservices vs Event-Driven

**Key Considerations**:
- System complexity
- Team size and structure
- Scalability needs
- Operational overhead

### 3. Data Storage Decisions
**Example**: PostgreSQL vs MongoDB vs Redis

**Key Considerations**:
- Data structure (relational vs document)
- Query patterns
- Consistency requirements
- Scalability needs

### 4. Integration Pattern Decisions
**Example**: REST vs GraphQL vs gRPC

**Key Considerations**:
- Client diversity
- Data fetching complexity
- Performance requirements
- Tooling and ecosystem

### 5. Deployment Strategy Decisions
**Example**: Docker Compose vs Kubernetes vs Serverless

**Key Considerations**:
- Infrastructure complexity
- Scaling requirements
- Cost constraints
- Team DevOps expertise

## Examples

### Example 1: Technology Choice ADR

**Trigger**: "We need to choose between FastAPI and Flask for our backend"

**Output**:
```markdown
# ADR-003: Use FastAPI for Backend API Framework

**Status**: Accepted
**Date**: 2025-12-15
**Decision Makers**: Development Team
**Tags**: #backend #framework #python #api

## Context

The Todo App requires a Python-based REST API framework for Phase II implementation. The backend must support:
- RESTful API endpoints
- JWT authentication
- SQLModel ORM integration
- OpenAPI documentation
- High performance (100+ req/sec)

**Constraints**:
- Python 3.13+ required
- Team has experience with Flask but not FastAPI
- Must integrate with existing authentication system
- Development timeline: 4 weeks

## Decision

**Chosen Option**: FastAPI

**Rationale**: FastAPI provides built-in async support, automatic OpenAPI docs, and native Pydantic validation, which align perfectly with our SQLModel usage and performance requirements. The learning curve is acceptable given the superior DX and built-in features.

## Options Considered

### Option 1: FastAPI

**Pros**:
- ✅ Built-in async/await support (2-3x faster than Flask)
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Native Pydantic integration (matches SQLModel)
- ✅ Dependency injection system
- ✅ Modern Python type hints

**Cons**:
- ❌ Team needs to learn FastAPI
- ❌ Smaller ecosystem than Flask
- ❌ Fewer third-party extensions

**Cost/Complexity**: Medium (learning curve offset by productivity gains)

### Option 2: Flask

**Pros**:
- ✅ Team already knows Flask
- ✅ Large ecosystem of extensions
- ✅ Mature and stable

**Cons**:
- ❌ No async support without extensions
- ❌ Manual OpenAPI documentation
- ❌ Less type-safe
- ❌ More boilerplate code

**Cost/Complexity**: Low (familiar)

### Option 3: Django REST Framework

**Pros**:
- ✅ Batteries-included framework
- ✅ Admin panel out of the box

**Cons**:
- ❌ Too heavy for our needs
- ❌ Opinionated ORM (can't use SQLModel easily)
- ❌ Slower than FastAPI

**Cost/Complexity**: High (overkill)

## Consequences

### Positive
- Automatic API documentation reduces documentation burden
- Type safety catches errors at development time
- Async support enables higher throughput
- Pydantic validation integrates seamlessly with SQLModel

### Negative
- 1-2 week learning curve for team
- Smaller community means fewer Stack Overflow answers
- Some Flask extensions don't have FastAPI equivalents

### Neutral
- Different project structure than Flask
- Testing patterns are similar but slightly different

## Implementation Notes

**Immediate Actions**:
1. Install FastAPI and Uvicorn: `pip install fastapi uvicorn sqlmodel`
2. Team completes FastAPI tutorial (2 hours)
3. Set up project structure: `backend/app/main.py`

**Migration Path**: N/A (greenfield project)

**Testing Strategy**:
- Use pytest with TestClient for endpoint testing
- Achieve 80% code coverage

**Timeline**:
- Week 1: Team training
- Week 2-3: Core API development
- Week 4: Testing and refinement

## References

- [FastAPI Docs]: https://fastapi.tiangolo.com
- [Spec]: @specs/api/rest-endpoints.md
- [SQLModel Integration]: https://sqlmodel.tiangolo.com
```

---

### Example 2: Architecture Pattern ADR

**Trigger**: "Should we use event-driven architecture for notifications?"

**Output**:
```markdown
# ADR-007: Event-Driven Architecture for Notifications (Phase V)

**Status**: Accepted
**Date**: 2025-12-15
**Decision Makers**: Architecture Team
**Tags**: #architecture #events #notifications #phase-v #dapr #kafka

## Context

The Todo App needs a notification system to alert users when:
- Tasks are created
- Tasks are updated
- Tasks approach due dates
- Tasks are completed

**Problem Statement**: Direct API calls from backend to notification service create tight coupling and reduce system resilience.

**Constraints**:
- Must support multiple notification channels (email, push, SMS)
- Must handle temporary notification service outages
- Must support future expansion (webhooks, Slack, etc.)

## Decision

**Chosen Option**: Event-Driven Architecture with Dapr + Kafka/Redpanda

**Rationale**: Event-driven architecture decouples services, enables async processing, and supports multiple subscribers without code changes. Dapr abstracts the messaging layer, making it easier to swap Kafka for other brokers if needed.

## Options Considered

### Option 1: Event-Driven (Dapr + Kafka)

**Pros**:
- ✅ Loose coupling between services
- ✅ Notification service can be offline temporarily
- ✅ Easy to add new subscribers (webhooks, analytics)
- ✅ Built-in retry and dead-letter queues

**Cons**:
- ❌ Increased operational complexity (Kafka cluster)
- ❌ Eventual consistency (notifications not immediate)
- ❌ Debugging is harder (async flows)

**Cost/Complexity**: High (but necessary for Phase V)

### Option 2: Direct HTTP Calls

**Pros**:
- ✅ Simple to implement
- ✅ Immediate feedback (sync)
- ✅ Easy to debug

**Cons**:
- ❌ Tight coupling
- ❌ Backend blocks if notification service is down
- ❌ Hard to add new notification channels

**Cost/Complexity**: Low (but doesn't scale)

### Option 3: Message Queue (RabbitMQ)

**Pros**:
- ✅ Decouples services
- ✅ Simpler than Kafka

**Cons**:
- ❌ Not part of Phase V tech stack
- ❌ Less scalable than Kafka
- ❌ Dapr support is secondary

**Cost/Complexity**: Medium

## Consequences

### Positive
- Notification service failures don't impact task operations
- Can add analytics service to consume same events
- Supports future webhooks without backend changes
- Follows Phase V constitutional requirements

### Negative
- Notifications are eventual (1-2 second delay)
- Need to run Kafka/Redpanda cluster
- More moving parts to monitor and debug

### Neutral
- Event schemas become API contracts
- Need to version events for backward compatibility

## Implementation Notes

**Immediate Actions**:
1. Define event schemas in `backend/app/schemas/events.py`
2. Configure Dapr pub/sub component: `infrastructure/dapr/components/kafka-pubsub.yaml`
3. Implement event publisher in `backend/app/utils/dapr_client.py`
4. Create notification-service with event subscribers

**Migration Path**:
1. Phase IV: Add event publishing alongside existing logic
2. Phase V: Remove direct calls, rely solely on events
3. Test both paths in parallel before switching

**Testing Strategy**:
- Integration tests publish events and verify subscriber receives them
- Use local Redpanda for testing
- Implement health checks for Kafka connectivity

**Rollback Plan**:
If events prove too complex, revert to direct HTTP calls with retry logic and circuit breaker.

**Timeline**:
- Week 1: Event schemas and Dapr config
- Week 2: Publisher implementation
- Week 3: Notification service subscriber
- Week 4: Testing and deployment

## References

- [ADR-002]: Dapr as Service Mesh
- [Spec]: @specs/005-phase-5-cloud-deployment/event-streaming.md
- [Dapr Pub/Sub]: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- [CloudEvents Spec]: https://cloudevents.io/
```

## Quality Checklist

Before finalizing ADR:
- [ ] Decision passes 3-part significance test (Impact + Alternatives + Scope)
- [ ] At least 2-3 options considered with honest pros/cons
- [ ] Context explains the problem clearly
- [ ] Rationale justifies the chosen option
- [ ] Consequences include positive, negative, and neutral impacts
- [ ] Implementation notes provide actionable next steps
- [ ] ADR number is unique and sequential
- [ ] File saved to `history/adr/NNN-title-slug.md`
- [ ] Status reflects current state (Proposed/Accepted)
- [ ] User has reviewed and approved the ADR

## Post-Creation

After creating ADR:
1. **Link from Related Docs**: Reference ADR in specs, code comments, README
2. **Communicate to Team**: Share ADR in team channels or meetings
3. **Create PHR**: Document ADR creation process
4. **Update Status**: Change from "Proposed" to "Accepted" after approval
5. **Track Implementation**: Ensure implementation notes are followed

**ADR is Immutable**: Once accepted, never modify. If decision changes, create new ADR that supersedes this one.
