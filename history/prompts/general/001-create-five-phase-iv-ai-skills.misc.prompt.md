---
id: 001
title: Create five Phase IV AI skills
stage: misc
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 006-phase-3-skills-fix
user: Najma-LP
command: skill-creator
labels: ["skills", "phase-iv", "ai-tools", "docker", "kubernetes", "sre", "voice", "testing"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/voice-integrator/SKILL.md
  - .claude/skills/voice-integrator/assets/useVoiceInput.tsx
  - .claude/skills/voice-integrator/assets/VoiceInputButton.tsx
  - .claude/skills/voice-integrator/assets/chatkit-integration-example.tsx
  - .claude/skills/voice-integrator.skill
  - .claude/skills/unit-test-writer/SKILL.md
  - .claude/skills/unit-test-writer/assets/conftest.template.py
  - .claude/skills/unit-test-writer/assets/test_fastapi_endpoint.template.py
  - .claude/skills/unit-test-writer/assets/test_mcp_tool.template.py
  - .claude/skills/unit-test-writer/references/pytest-patterns.md
  - .claude/skills/unit-test-writer/references/mocking-guide.md
  - .claude/skills/unit-test-writer.skill
  - .claude/skills/docker-ai-pilot/SKILL.md
  - .claude/skills/docker-ai-pilot/scripts/gordon_wrapper.py
  - .claude/skills/docker-ai-pilot/scripts/apply_dockerfile_improvements.py
  - .claude/skills/docker-ai-pilot/assets/dockerfile-templates/fastapi.Dockerfile
  - .claude/skills/docker-ai-pilot/assets/dockerfile-templates/nextjs.Dockerfile
  - .claude/skills/docker-ai-pilot/assets/dockerfile-templates/python-cli.Dockerfile
  - .claude/skills/docker-ai-pilot/references/gordon-commands.md
  - .claude/skills/docker-ai-pilot/references/dockerfile-best-practices.md
  - .claude/skills/docker-ai-pilot.skill
  - .claude/skills/kubectl-ai-pilot/SKILL.md
  - .claude/skills/kubectl-ai-pilot/scripts/kubectl_ai_wrapper.py
  - .claude/skills/kubectl-ai-pilot/scripts/apply_k8s_manifest.py
  - .claude/skills/kubectl-ai-pilot/assets/k8s-templates/deployment.yaml
  - .claude/skills/kubectl-ai-pilot/assets/k8s-templates/service.yaml
  - .claude/skills/kubectl-ai-pilot/references/kubectl-ai-commands.md
  - .claude/skills/kubectl-ai-pilot.skill
  - .claude/skills/kagent-debugger/SKILL.md
  - .claude/skills/kagent-debugger/scripts/kagent_wrapper.py
  - .claude/skills/kagent-debugger/scripts/generate_sre_report.py
  - .claude/skills/kagent-debugger/assets/report-templates/health-report-template.md
  - .claude/skills/kagent-debugger/references/kagent-commands.md
  - .claude/skills/kagent-debugger.skill
tests:
  - gordon_wrapper.py tested with docker ai --version fallback
  - kubectl_ai_wrapper.py tested with kubectl ai fallback
  - kagent_wrapper.py tested with fallback strategy
---

## Prompt

I need to create 5 skills using the skill-creator:
1. voice-integrator - Speech-to-Text integration for Next.js ChatKit using browser's native SpeechRecognition API
2. unit-test-writer - Generate pytest unit tests for FastAPI endpoints and MCP tools with strict database mocking
3. docker-ai-pilot - Interface with Docker AI (Gordon) for intelligent containerization with automatic fallback
4. kubectl-ai-pilot - Interface with kubectl-ai for AI-assisted Kubernetes operations and manifest generation
5. kagent-debugger - AI-powered SRE operations for cluster health analysis, resource optimization, and crash loop diagnosis

After creation, commit all skills to the repository.

## Response snapshot

Successfully created all 5 skills following the Skill Creation Process:

**1. voice-integrator (8KB)**
- Custom React hook `useVoiceInput` wrapping browser SpeechRecognition API
- `VoiceInputButton` component with visual feedback (pulsing animation)
- ChatKit integration example demonstrating transcript injection
- Browser compatibility checks with graceful degradation
- Quality criteria: browser compatibility, visual feedback, ChatKit integration, error handling

**2. unit-test-writer (16KB)**
- conftest.template.py with shared pytest fixtures (mock_db_session, mock_current_user)
- test_fastapi_endpoint.template.py with 3 required test cases (Happy Path 201, Validation Error 422, Logic Error 404)
- test_mcp_tool.template.py for MCP schema validation
- pytest-patterns.md reference with AAA pattern, parametrization, fixtures
- mocking-guide.md with database query chain mocking patterns
- Quality criteria: strict isolation, 3 test cases minimum, MCP schema validation, pytest fixtures

**3. docker-ai-pilot (20KB)**
- gordon_wrapper.py wrapping `docker ai` CLI commands with fallback
- apply_dockerfile_improvements.py for automatic application with backup and rollback
- Dockerfile templates: FastAPI (multi-stage, ~150MB), Next.js (optimized), Python CLI
- gordon-commands.md reference with natural language patterns
- dockerfile-best-practices.md with multi-stage builds, security hardening
- Gordon-first strategy with automatic fallback when unavailable

**4. kubectl-ai-pilot (16KB)**
- kubectl_ai_wrapper.py wrapping `kubectl ai` commands with --auto-confirm handling
- apply_k8s_manifest.py with YAML validation, kubectl dry-run, apply history
- K8s templates: Deployment (with probes, security context), Service
- kubectl-ai-commands.md reference with manifest generation patterns
- kubectl-ai first strategy for Phase IV compliance

**5. kagent-debugger (18KB)**
- kagent_wrapper.py with three core commands: analyze (health), optimize (resources), diagnose (crashes)
- generate_sre_report.py combining all analyses with P0/P1/P2 prioritization
- health-report-template.md showing complete SRE report structure
- kagent-commands.md reference with cluster health, optimization, crash diagnosis
- AI-powered SRE with structured reports and automatic fallback

All skills packaged as .skill files and committed with hash `ffcc291`:
```
feat(skills): add Phase IV skills for AI-assisted deployment and SRE operations

Add 5 comprehensive skills for Phase IV deployment automation and SRE operations:

1. voice-integrator (8KB)
   - Speech-to-Text integration for Next.js ChatKit
   - Browser SpeechRecognition API with React hooks
   - Visual feedback and error handling

2. unit-test-writer (16KB)
   - pytest test generation for FastAPI endpoints and MCP tools
   - Strict database mocking patterns
   - 3 test cases minimum: Happy Path, Validation Error, Logic Error

3. docker-ai-pilot (20KB)
   - Docker AI (Gordon) integration for intelligent containerization
   - Dockerfile optimization with automatic fallback
   - Multi-stage build templates for FastAPI, Next.js, Python CLI

4. kubectl-ai-pilot (16KB)
   - kubectl-ai integration for AI-assisted K8s operations
   - Natural language manifest generation with verification
   - Deployment and Service templates with best practices

5. kagent-debugger (18KB)
   - AI-powered SRE operations for cluster health and optimization
   - Cluster health analysis, resource optimization, crash loop diagnosis
   - Structured SRE reports with P0/P1/P2 prioritization

All skills follow progressive disclosure pattern (metadata → SKILL.md → references)
and implement automatic fallback when AI tools unavailable.
```

## Outcome

- ✅ Impact: Created 5 production-ready skills for Phase IV deployment automation (78KB total, 34 files, 9,473 insertions)
- 🧪 Tests: Validated wrapper scripts with fallback strategies (gordon, kubectl-ai, kagent)
- 📁 Files: 34 files created across 5 skill packages
- 🔁 Next prompts: Skills ready for use by cloudops-engineer, deployment-engineer, and backend-specialist agents
- 🧠 Reflection: Progressive disclosure pattern kept SKILL.md files concise (<500 lines) while bundling comprehensive resources. All skills implement intelligent fallback for AI tool unavailability.

## Evaluation notes (flywheel)

- Failure modes observed: None - all skills successfully created and packaged
- Graders run and results (PASS/FAIL): Manual validation - PASS (all .skill files under 20KB, proper directory structure, complete SKILL.md)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skills in actual deployment scenarios to validate fallback strategies and gather usage patterns
