---
name: "phr-documenter"
description: "Automates Prompt History Record (PHR) creation with proper frontmatter, routing (constitution/feature/general), metadata extraction, and validation. Use after completing user requests to document implementation work, planning sessions, debugging, or spec creation."
version: "1.0.0"
---

# PHR Documenter Skill

## When to Use
- After completing any implementation work (code changes, features)
- After planning/architecture discussions
- After debugging sessions
- After spec/task/plan creation
- After multi-step workflows
- Constitutional requirement: Create PHR for every user input

## Context
This skill implements the PHR (Prompt History Record) pattern from the constitution:
- **Purpose**: Document every user interaction with full context
- **Location**: `history/prompts/` (constitution, feature-name, or general subdirectories)
- **Format**: Markdown with YAML frontmatter
- **Template**: `.specify/templates/phr-template.prompt.md`
- **Numbering**: Sequential ID (001, 002, 003...)
- **Routing**: Automatic based on stage and feature context

## Workflow

### 1. Detect Stage
Determine the stage from user interaction:
- `constitution` - Constitution updates or reviews
- `spec` - Feature specification creation
- `plan` - Implementation planning
- `tasks` - Task generation or execution
- `red` - Test writing (TDD red phase)
- `green` - Implementation (TDD green phase)
- `refactor` - Code refactoring
- `explainer` - Code explanation or documentation
- `misc` - Other feature-related work
- `general` - General work not tied to specific feature

### 2. Resolve Route
Determine destination directory:
- **Constitution**: `history/prompts/constitution/`
- **Feature stages**: `history/prompts/<feature-name>/` (requires feature context)
- **General**: `history/prompts/general/`

### 3. Allocate ID
- Read existing PHRs in target directory
- Increment highest ID by 1
- On collision, increment again
- Format as 3-digit zero-padded (001, 002, 003...)

### 4. Extract Metadata
From conversation context:
- **ID**: Sequential number
- **Title**: 3-7 words describing the work
- **Stage**: Detected stage
- **Date**: YYYY-MM-DD format
- **Surface**: "agent"
- **Model**: claude-sonnet-4-5-20250929
- **Feature**: Feature name or "none"
- **Branch**: Current git branch
- **User**: System username
- **Command**: Current command or "direct"
- **Labels**: Array of relevant topics
- **Links**: SPEC, TICKET, ADR, PR (URLs or "null")
- **Files**: List of created/modified files
- **Tests**: List of tests run/added
- **Prompt**: Full user input (verbatim)
- **Response**: Key assistant output (concise but representative)

### 5. Fill Template
Read PHR template and replace all placeholders:
```yaml
---
id: {{ID}}
title: {{TITLE}}
stage: {{STAGE}}
date: {{DATE_ISO}}
surface: {{SURFACE}}
model: {{MODEL}}
feature: {{FEATURE}}
branch: {{BRANCH}}
user: {{USER}}
command: {{COMMAND}}
labels: {{LABELS_YAML}}
links:
  spec: {{SPEC_URL}}
  ticket: {{TICKET_URL}}
  adr: {{ADR_URL}}
  pr: {{PR_URL}}
files:
{{FILES_YAML}}
tests:
{{TESTS_YAML}}
---

## Prompt

{{PROMPT_TEXT}}

## Response snapshot

{{RESPONSE_TEXT}}

## Outcome

- ✅ Impact: {{IMPACT}}
- 🧪 Tests: {{TESTS_SUMMARY}}
- 📁 Files: {{FILES_SUMMARY}}
- 🔁 Next prompts: {{NEXT_PROMPTS}}
- 🧠 Reflection: {{REFLECTION}}

## Evaluation notes (flywheel)

- Failure modes observed: {{FAILURE_MODES}}
- Graders run and results (PASS/FAIL): {{GRADER_RESULTS}}
- Prompt variant (if applicable): {{PROMPT_VARIANT}}
- Next experiment (smallest change to try): {{NEXT_EXPERIMENT}}
```

### 6. Validate PHR
Ensure completeness:
- [ ] No unresolved placeholders ({{THIS}}, [THAT])
- [ ] Title, stage, and dates match frontmatter
- [ ] PROMPT_TEXT is complete (not truncated)
- [ ] File exists at expected path
- [ ] Path matches routing rules

### 7. Write PHR
- Compute output path:
  - Constitution: `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
  - Feature: `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
  - General: `history/prompts/general/<ID>-<slug>.general.prompt.md`
- Write completed PHR with agent file tools
- Confirm absolute path in output

## Output Format

### PHR File Structure

**Filename**: `<ID>-<title-slug>.<stage>.prompt.md`

**Example**: `010-utility-skills-expansion.general.prompt.md`

**Content**:
```markdown
---
id: 010
title: Utility Skills Expansion - CRUD Builder, Doc Generator, and More
stage: general
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: direct
labels: ["skills", "crud", "documentation", "testing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/crud-builder/SKILL.md
  - .claude/skills/doc-generator/SKILL.md
tests:
  - None (skill documentation)
---

## Prompt

User: "crud builder
doc generator
fastapi endpoint generator
integration tester
monorepo setup
deployment validator add these aswell"

## Response snapshot

**Six New Utility Skills Created**

[Full response details...]

## Outcome

- ✅ Impact: Six new utility skills created
- 🧪 Tests: N/A (skill documentation)
- 📁 Files: Created 6 new skills
- 🔁 Next prompts: Use skills for development
- 🧠 Reflection: Skills library expanded

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skills
```

## Examples

### Example 1: Constitution PHR

**Trigger**: User executes `/sp.constitution`

**Output**: `history/prompts/constitution/005-constitution-acknowledgment-phase-iii.constitution.prompt.md`

```yaml
---
id: 005
title: Constitution Acknowledgment - Phase III
stage: constitution
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: /sp.constitution
labels: ["constitution", "governance", "phase-iii"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - None
---

## Prompt

/sp.constitution

## Response snapshot

**Project Constitution Acknowledged**

Current Phase: Phase III (Agent-Augmented System)
New Principle: Reusable Intelligence (Vertical Intelligence)
Required Skills: MCP Tool Maker, Agent Orchestrator, Spec-Writer

[Full constitution display...]

## Outcome

- ✅ Impact: Constitution reviewed and acknowledged
- 🧪 Tests: N/A
- 📁 Files: CLAUDE.md reviewed
- 🔁 Next prompts: Create required skills
- 🧠 Reflection: Constitutional governance in place

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
```

---

### Example 2: Feature Implementation PHR

**Trigger**: User implements task CRUD endpoints

**Output**: `history/prompts/task-management/008-backend-crud-implementation.green.prompt.md`

```yaml
---
id: 008
title: Backend CRUD Implementation - Task Model
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: task-management
branch: feature/task-crud
user: Najma-LP
command: direct
labels: ["backend", "crud", "fastapi", "sqlmodel", "pytest"]
links:
  spec: @specs/features/task-crud.md
  ticket: https://github.com/user/repo/issues/42
  adr: null
  pr: null
files:
  - backend/app/models/task.py
  - backend/app/schemas/task.py
  - backend/app/routers/task.py
  - backend/tests/test_task.py
tests:
  - pytest backend/tests/test_task.py -v (10/10 passed)
---

## Prompt

User: "Create CRUD for Task model with title, description, status, priority, due_date"

## Response snapshot

**Complete CRUD Operations Created for Task Model**

### Files Created:
1. ✅ Model: backend/app/models/task.py
2. ✅ Schemas: backend/app/schemas/task.py
3. ✅ Router: backend/app/routers/task.py
4. ✅ Tests: backend/tests/test_task.py

[Full implementation details...]

## Outcome

- ✅ Impact: Complete Task CRUD implemented with JWT auth
- 🧪 Tests: 10/10 pytest tests passing
- 📁 Files: 4 new files created
- 🔁 Next prompts:
  - Run database migration
  - Create frontend TaskList component
  - Add task filtering endpoints
- 🧠 Reflection: CRUD pattern consistently applied

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL):
  - CRUD endpoints: PASS
  - JWT authentication: PASS
  - User isolation: PASS
  - Pagination: PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try):
  - Add task filtering by status and priority
```

---

### Example 3: General Work PHR

**Trigger**: User creates new skills

**Output**: `history/prompts/general/010-utility-skills-expansion.general.prompt.md`

```yaml
---
id: 010
title: Utility Skills Expansion
stage: general
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-phase-5
user: Najma-LP
command: direct
labels: ["skills", "crud", "documentation", "testing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/crud-builder/SKILL.md
  - .claude/skills/doc-generator/SKILL.md
tests:
  - None (skill documentation)
---

## Prompt

User: "crud builder
doc generator
fastapi endpoint generator
integration tester
monorepo setup
deployment validator add these aswell"

## Response snapshot

**Six New Utility Skills Created**

[Full details...]

## Outcome

- ✅ Impact: Six new utility skills created
- 🧪 Tests: N/A
- 📁 Files: 6 new skills, 3 agents updated
- 🔁 Next prompts: Use skills for development
- 🧠 Reflection: Skills library expanded

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skills
```

## Automated PHR Creation

### Python Script

**File**: `scripts/create-phr.py`
```python
#!/usr/bin/env python3
"""Automate PHR creation."""

import os
import sys
from datetime import datetime
from pathlib import Path
import re

class PHRDocumenter:
    def __init__(self, stage: str, title: str, feature: str = None):
        self.stage = stage
        self.title = title
        self.feature = feature
        self.base_dir = Path("history/prompts")

    def slugify(self, text: str) -> str:
        """Convert text to URL slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def get_next_id(self, directory: Path) -> str:
        """Get next available ID."""
        if not directory.exists():
            return "001"

        existing_ids = []
        for file in directory.glob("*.prompt.md"):
            match = re.match(r'^(\d+)-', file.name)
            if match:
                existing_ids.append(int(match.group(1)))

        next_id = max(existing_ids, default=0) + 1
        return f"{next_id:03d}"

    def determine_route(self) -> Path:
        """Determine PHR destination directory."""
        if self.stage == "constitution":
            return self.base_dir / "constitution"
        elif self.feature:
            return self.base_dir / self.feature
        else:
            return self.base_dir / "general"

    def create_phr(self, prompt: str, response: str, files: list, tests: list):
        """Create PHR file."""
        route = self.determine_route()
        route.mkdir(parents=True, exist_ok=True)

        phr_id = self.get_next_id(route)
        slug = self.slugify(self.title)

        # Determine filename
        if self.stage == "constitution":
            filename = f"{phr_id}-{slug}.constitution.prompt.md"
        elif self.feature:
            filename = f"{phr_id}-{slug}.{self.stage}.prompt.md"
        else:
            filename = f"{phr_id}-{slug}.general.prompt.md"

        filepath = route / filename

        # Get current branch
        try:
            import subprocess
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            branch = "main"

        # Generate content
        content = f"""---
id: {phr_id}
title: {self.title}
stage: {self.stage}
date: {datetime.now().strftime('%Y-%m-%d')}
surface: agent
model: claude-sonnet-4-5-20250929
feature: {self.feature or 'none'}
branch: {branch}
user: {os.getenv('USER', 'unknown')}
command: direct
labels: []
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
{chr(10).join([f'  - {f}' for f in files]) if files else '  - None'}
tests:
{chr(10).join([f'  - {t}' for t in tests]) if tests else '  - None'}
---

## Prompt

{prompt}

## Response snapshot

{response}

## Outcome

- ✅ Impact: [Brief impact statement]
- 🧪 Tests: [Test summary]
- 📁 Files: [Files summary]
- 🔁 Next prompts:
  - [Next step 1]
  - [Next step 2]
- 🧠 Reflection: [Key insights]

## Evaluation notes (flywheel)

- Failure modes observed: [Any issues encountered]
- Graders run and results (PASS/FAIL):
  - [Grader 1]: [PASS/FAIL]
  - [Grader 2]: [PASS/FAIL]
- Prompt variant (if applicable): [Variant if tested]
- Next experiment (smallest change to try): [Next experiment]
"""

        # Write PHR
        filepath.write_text(content)

        print(f"\n✅ PHR created: {filepath}")
        print(f"   ID: {phr_id}")
        print(f"   Stage: {self.stage}")
        print(f"   Route: {route}")

        return filepath

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create Prompt History Record")
    parser.add_argument("--title", required=True, help="PHR title")
    parser.add_argument("--stage", required=True, help="Stage (constitution, spec, plan, etc.)")
    parser.add_argument("--feature", help="Feature name (optional)")
    parser.add_argument("--prompt", required=True, help="User prompt")
    parser.add_argument("--response", required=True, help="Assistant response")
    parser.add_argument("--files", nargs="*", default=[], help="Modified files")
    parser.add_argument("--tests", nargs="*", default=[], help="Tests run")

    args = parser.parse_args()

    documenter = PHRDocumenter(args.stage, args.title, args.feature)
    documenter.create_phr(args.prompt, args.response, args.files, args.tests)
```

**Usage**:
```bash
python scripts/create-phr.py \
  --title "Backend CRUD Implementation" \
  --stage "green" \
  --feature "task-management" \
  --prompt "Create CRUD for Task model" \
  --response "Complete CRUD operations created" \
  --files "backend/app/models/task.py" "backend/app/routers/task.py" \
  --tests "pytest backend/tests/test_task.py -v (10/10 passed)"
```

## Quality Checklist

Before finalizing PHR:
- [ ] ID is unique and sequential
- [ ] Title is descriptive (3-7 words)
- [ ] Stage is correct
- [ ] Feature context identified (if applicable)
- [ ] Prompt is verbatim (not truncated)
- [ ] Response is representative
- [ ] All files listed
- [ ] All tests documented
- [ ] Outcome section complete
- [ ] Evaluation notes filled
- [ ] No unresolved placeholders
- [ ] File path matches routing rules

## Routing Rules

### Constitution PHR
- **Stage**: `constitution`
- **Path**: `history/prompts/constitution/`
- **Filename**: `<ID>-<slug>.constitution.prompt.md`
- **Example**: `005-constitution-acknowledgment-phase-iii.constitution.prompt.md`

### Feature PHR
- **Stages**: `spec`, `plan`, `tasks`, `red`, `green`, `refactor`, `explainer`, `misc`
- **Path**: `history/prompts/<feature-name>/`
- **Filename**: `<ID>-<slug>.<stage>.prompt.md`
- **Example**: `008-backend-crud-implementation.green.prompt.md`

### General PHR
- **Stage**: `general`
- **Path**: `history/prompts/general/`
- **Filename**: `<ID>-<slug>.general.prompt.md`
- **Example**: `010-utility-skills-expansion.general.prompt.md`

## Common PHR Types

### 1. Implementation PHR (green stage)
- Code changes and feature implementation
- Files created/modified
- Tests added and passing
- Outcome: feature working

### 2. Planning PHR (plan stage)
- Architecture decisions
- Implementation strategy
- Task breakdown
- Outcome: clear roadmap

### 3. Spec PHR (spec stage)
- Feature requirements
- Acceptance criteria
- User stories
- Outcome: spec created

### 4. Debugging PHR (misc stage)
- Bug investigation
- Root cause analysis
- Fix applied
- Outcome: bug resolved

### 5. Documentation PHR (explainer stage)
- Code explanation
- Documentation creation
- Architecture diagrams
- Outcome: knowledge captured

## Post-Creation

After creating PHR:
1. **Verify Path**: Check file exists at expected location
2. **Validate Content**: Ensure no placeholders remain
3. **Link References**: Update related specs/ADRs with PHR link
4. **Commit**: Add PHR to git
5. **Continue Work**: PHR doesn't block next task
