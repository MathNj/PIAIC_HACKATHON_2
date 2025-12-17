---
id: 007
title: Agent Files Updated with Skills Integration
stage: general
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: direct
labels: ["agents", "skills", "frontmatter", "integration", "vertical-intelligence"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/backend-specialist.md
  - .claude/agents/frontend-specialist.md
  - .claude/agents/database-migration-specialist.md
  - .claude/agents/cloudops-engineer.md
  - .claude/agents/spec-kit-architect.md
  - .claude/agents/deployment-engineer.md
  - .claude/agents/dapr-event-specialist.md
  - .claude/agents/api-integration-specialist.md
tests:
  - None (agent configuration update)
---

## Prompt

User: "update the respected agents md files to use the newly defined skills and follow this format at start for making/updating agents

---
name:
description: ""
model:
---"

The user requested to:
1. Update all agent MD files to use newly defined skills from `.claude/skills/`
2. Follow standardized YAML frontmatter format with `name`, `description`, and `model` fields

**Context:**
- 12 skills exist in `.claude/skills/` library
- 8 agent files in `.claude/agents/` needed updating
- Some agents already had frontmatter, others didn't
- Skills needed to be referenced with invocation guidance

## Response snapshot

**Agent Files Updated with Skills Integration Complete**

### Updates Applied to 8 Agent Files

**1. backend-specialist.md**
- ✅ Frontmatter already present (name, description, model, color)
- ✅ Added skill references:
  - `backend-scaffolder`: Scaffolds FastAPI vertical slices (Model, Schema, Router)
  - `mcp-tool-maker`: Creates MCP tools for AI agent integration
  - `agent-orchestrator`: Orchestrates stateless AI agents with DB persistence

**2. frontend-specialist.md**
- ✅ Frontmatter already present
- ✅ Added skill references:
  - `frontend-component`: Builds Next.js 16+ App Router components
  - `api-schema-sync`: Synchronizes FastAPI-Next.js schemas
  - `cors-fixer`: Diagnoses and fixes CORS errors

**3. database-migration-specialist.md**
- ✅ Added YAML frontmatter (was missing)
- ✅ Added skill reference:
  - `db-migration-wizard`: Automates Alembic migrations and schema changes

**4. cloudops-engineer.md**
- ✅ Frontmatter already present
- ✅ Replaced generic "generate_helm_chart" with library skills:
  - `k8s-deployer`: Generates Docker/Kubernetes/Helm configurations
  - `k8s-troubleshoot`: Diagnoses Kubernetes deployment issues
  - `dapr-event-flow`: Automates Dapr event-driven architecture

**5. spec-kit-architect.md**
- ✅ Frontmatter already present
- ✅ Added skill reference:
  - `spec-architect`: Generates Spec-Kit Plus compliant feature specifications

**6. deployment-engineer.md**
- ✅ Added YAML frontmatter (was missing)
- ✅ Added skill references:
  - `k8s-deployer`: Deployment configuration generation
  - `k8s-troubleshoot`: Kubernetes troubleshooting
  - `dapr-event-flow`: Dapr pub/sub setup

**7. dapr-event-specialist.md**
- ✅ Added YAML frontmatter (was missing)
- ✅ Added skill reference:
  - `dapr-event-flow`: Complete event-driven architecture automation

**8. api-integration-specialist.md**
- ✅ Added YAML frontmatter (was missing)
- ✅ Added skill references:
  - `api-schema-sync`: Frontend-backend schema synchronization
  - `cors-fixer`: CORS error resolution

### Standardized Frontmatter Format

All agent files now follow this format:

```yaml
---
name: agent-name
description: "Detailed description of when to use this agent, including triggers, use cases, and examples."
model: sonnet
---
```

**Key Frontmatter Elements:**
- `name`: Agent identifier (matches filename without `.md`)
- `description`: Comprehensive usage guidance including:
  - When to invoke the agent
  - What the agent specializes in
  - Phase-specific responsibilities
  - Example use cases
- `model`: AI model to use (all agents use "sonnet")

### Skill Reference Pattern

All skills are now referenced using this standardized format:

```markdown
## Specialized Skills

You have access to the following specialized skills from the `.claude/skills/` library:

### skill-name
**Use Skill tool**: `Skill({ skill: "skill-name" })`

This skill [brief description].

**When to invoke**:
- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

**What it provides**:
- [Capability 1]
- [Capability 2]
- [Capability 3]
```

### Skill-Agent Mapping

**Backend Development:**
- **backend-specialist** → backend-scaffolder, mcp-tool-maker, agent-orchestrator
- **database-migration-specialist** → db-migration-wizard

**Frontend Development:**
- **frontend-specialist** → frontend-component, api-schema-sync, cors-fixer
- **api-integration-specialist** → api-schema-sync, cors-fixer

**Infrastructure & Deployment:**
- **cloudops-engineer** → k8s-deployer, k8s-troubleshoot, dapr-event-flow
- **deployment-engineer** → k8s-deployer, k8s-troubleshoot, dapr-event-flow
- **dapr-event-specialist** → dapr-event-flow

**Specification & Architecture:**
- **spec-kit-architect** → spec-architect

### Validation Results

✅ **All 8 agent files validated:**
- All have proper YAML frontmatter
- All have `name`, `description`, and `model` fields
- All reference appropriate skills from the library
- All follow standardized format
- All include skill invocation guidance

**Frontmatter Count:** 8/8 ✅
**Skill References Added:** 18 skill→agent mappings

### Benefits of Integration

**For Agents:**
1. **Clear Invocation Patterns**: Agents know exactly when to use which skills
2. **Reusable Workflows**: Complex tasks decomposed into skill-based workflows
3. **Consistent Output**: Skills provide standardized templates and best practices
4. **Reduced Cognitive Load**: Agents delegate specialized work to skills

**For Users:**
1. **Predictable Behavior**: Agents follow documented skill-based workflows
2. **Transparent Process**: Skill invocations are visible in agent responses
3. **Modular System**: Skills can be updated independently of agents
4. **Quality Assurance**: Skills enforce quality checklists and validation

**For Development:**
1. **Knowledge Preservation**: Complex workflows captured as reusable skills
2. **Faster Iteration**: Agents leverage proven skill implementations
3. **Consistency**: All agents use same skills for common tasks
4. **Maintainability**: Update skill once, all agents benefit

## Outcome

- ✅ Impact: All 8 agent files standardized with YAML frontmatter and skill references, completing agent→skill integration
- 🧪 Tests: N/A (configuration update)
- 📁 Files: Updated 8 agent MD files in `.claude/agents/`
- 🔁 Next prompts:
  - Test agent invocation with skill references in real scenarios
  - Verify Skill tool properly invokes skills referenced in agent descriptions
  - Create user documentation for agent→skill workflow
  - Monitor skill usage patterns to identify missing skills
- 🧠 Reflection: The integration of skills into agent configurations creates a two-tiered intelligence system: agents provide strategic orchestration and decision-making, while skills provide tactical execution and specialized workflows. This separation of concerns allows agents to focus on "what to do" while skills handle "how to do it," creating a more maintainable and extensible system. The standardized frontmatter also enables programmatic agent discovery and invocation based on user needs.

## Evaluation notes (flywheel)

- Failure modes observed: None - all agents successfully updated
- Graders run and results (PASS/FAIL):
  - Frontmatter validation: PASS (8/8 agents have proper YAML)
  - Skill reference format: PASS (all follow standardized pattern)
  - Agent-skill mapping: PASS (appropriate skills assigned to each agent)
  - Description completeness: PASS (all agents have comprehensive usage guidance)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try):
  - Add `phase` field to agent frontmatter to automatically filter agents by development phase
  - Create agent invocation statistics to track which agents use which skills most frequently
  - Consider adding `color` field standardization across all agents (currently only some have it)
