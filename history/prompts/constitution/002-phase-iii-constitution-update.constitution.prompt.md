---
id: 002
title: Phase III Constitution Update - AI Agent & MCP
stage: constitution
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 002-fullstack-web-app
user: agent
command: /sp.constitution
labels: ["phase-iii", "ai-agent", "mcp", "governance", "constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution version incremented to 3.0.0
  - All placeholders resolved
  - Phase III principles added
  - Sync Impact Report generated
---

## Prompt

```
# PHASE III CONSTITUTION: AI AGENT & MCP

## 1. ARCHITECTURE
- **Core Pattern:** Stateless AI Agent using Model Context Protocol (MCP).
- **Frameworks:** OpenAI Agents SDK, Official MCP Python SDK, OpenAI ChatKit (Frontend).
- **State Management:** NO in-memory state. All conversation history must be fetched from and saved to the `conversations` and `messages` tables on every request.

## 2. STRICT CONSTRAINTS
- **MCP Compliance:** All Task operations (Add, List, Delete) must be implemented as strict MCP Tools.
- **Agent Identity:** The Agent is a helpful assistant that manages the user's specific Todo list.
- **Security:** The Agent must strictly respect `user_id`. It cannot access data belonging to other users.
- **Tool Outputs:** Tools must return structured strings/JSON that the LLM can interpret easily.

## 3. FILE STRUCTURE
- `backend/mcp/`: Contains tool definitions.
- `backend/agents/`: Contains the Agent runner logic.
- `backend/models.py`: Updated with Conversation/Message schemas.
```

## Response snapshot

Successfully updated project constitution from version 2.0.0 to 3.0.0 (MAJOR version bump) to reflect Phase III AI Agent & MCP principles.

**Key Changes:**

1. **Phase Status Updates:**
   - Phase I: Monolithic Script → ✅ COMPLETED
   - Phase II: Modular Monolith → ✅ COMPLETED
   - Phase III: Agent-Augmented System → 🚧 CURRENT PHASE

2. **New Phase III Sections Added:**
   - Architecture Pattern: Stateless AI Agent with MCP
   - State Management (CRITICAL CONSTRAINT): Database-backed conversation history
   - MCP Compliance (NON-NEGOTIABLE): All task operations as MCP tools
   - Security Constraints (CRITICAL): User_id validation and multi-tenancy
   - Natural Language Processing: Task extraction from natural language
   - Frontend Integration: OpenAI ChatKit requirements
   - Code Quality Standards (Phase III specific)

3. **Technology Stack Updated:**
   - Phase III: Phase II stack + OpenAI Agents SDK + MCP Python SDK + OpenAI ChatKit

4. **MCP Tool Requirements Defined:**
   - list_tasks, create_task, update_task, delete_task
   - toggle_task_completion, get_task_summary, suggest_task_prioritization
   - All tools require JWT authentication and user_id validation

5. **Database Schema Requirements:**
   - conversations table: id, user_id, title, created_at, updated_at
   - messages table: id, conversation_id, role, content, created_at

6. **File Structure Defined:**
   - backend/mcp/: MCP tool definitions
   - backend/mcp/server.py: MCP server initialization
   - backend/agents/: Agent orchestration logic
   - frontend/lib/chatkit-config.ts: ChatKit configuration
   - frontend/app/agent/page.tsx: Agent chat interface

**Sync Impact Report:**
- Version: 2.0.0 → 3.0.0 (MAJOR)
- Change Type: Phase transition with new architectural constraints
- Templates Status: All aligned (plan-template, spec-template, tasks-template, mcp-tool-maker skill)
- Follow-up TODOs: Create Phase III spec, document MCP patterns in ADR, update deployment docs

**Version Bump Rationale:**
MAJOR version bump required because:
- Phase transition (Phase II → Phase III)
- New architectural pattern (stateless AI agent)
- New technology stack components (OpenAI Agents SDK, MCP SDK, ChatKit)
- New governance constraints (MCP compliance, state management rules)
- Backward compatible at user-facing level but requires new infrastructure

## Outcome

- ✅ Impact: Constitution successfully updated for Phase III with comprehensive AI Agent & MCP governance
- 🧪 Tests: Version validation passed, no unresolved placeholders, dates in ISO format
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Create Phase III spec for conversation/message models, implement MCP tools, integrate ChatKit
- 🧠 Reflection: Clear governance enables disciplined Phase III development with stateless agent architecture

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update completed successfully
- Graders run and results (PASS/FAIL): PASS - All validation checks passed
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Begin Phase III spec creation for conversation persistence
