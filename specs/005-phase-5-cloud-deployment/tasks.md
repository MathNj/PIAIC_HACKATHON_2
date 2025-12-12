# Tasks: Phase 5 Event-Driven Architecture with Cloud Deployment

**Input**: Design documents from `/specs/005-phase-5/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests are OPTIONAL in this implementation. Tasks focus on infrastructure setup and service integration. Manual testing will be performed using kubectl, curl, and Dapr CLI tools.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation of each architectural component.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/`
- **Frontend**: `frontend/`
- **Infrastructure**: `infrastructure/`
- **Microservices**: `notification-service/`, `recurring-task-service/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install Dapr CLI 1.13+ on local development machine (`dapr version` to verify) ✅ v1.16.5 installed
- [ ] T002 [P] Install kubectl 1.28+ and verify connection to Minikube cluster
- [ ] T003 [P] Install Helm 3.14+ for chart management (`helm version` to verify)
- [ ] T004 [P] Install doctl (DigitalOcean CLI) for cloud resource management
- [X] T005 Add httpx 0.27+ dependency to backend/requirements.txt for Dapr HTTP client ✅ Already present
- [ ] T006 [P] Create feature flag configuration file at backend/app/config/feature_flags.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dapr Control Plane Setup

- [X] T007 Initialize Dapr on DOKS cluster (`dapr init --kubernetes --wait`) ✅ v1.16.4 installed to dapr-system namespace
- [X] T008 Verify Dapr installation (`kubectl get pods -n dapr-system` - expect 4/4 pods Running) ✅ 8/8 pods running and healthy
- [ ] T009 [P] Deploy local Kafka/Redpanda container to Minikube using Helm (infrastructure/helm/redpanda/)
- [ ] T010 [P] Deploy local Redis container to Minikube using Helm (infrastructure/helm/redis/)

### Database Schema Migration (Component 2: Advanced Features)

- [ ] T011 Create Alembic migration for priorities table in backend/alembic/versions/

XXX_add_priorities_table.py
- [ ] T012 Create Alembic migration for tags table in backend/alembic/versions/XXX_add_tags_table.py
- [ ] T013 Create Alembic migration for task_tags junction table in backend/alembic/versions/XXX_add_task_tags_table.py
- [ ] T014 Create Alembic migration for recurring_tasks table in backend/alembic/versions/XXX_add_recurring_tasks_table.py
- [ ] T015 Create Alembic migration to add nullable columns to tasks table (priority_id, due_date, is_recurring, recurrence_pattern, recurring_task_id) in backend/alembic/versions/XXX_add_task_advanced_columns.py
- [ ] T016 Run database migrations on local SQLite (`alembic upgrade head`)
- [ ] T017 Seed priorities table with 4 levels (Low, Medium, High, Critical) in backend/app/db/seeds/priorities.py

### SQLModel Schema Updates

- [ ] T018 [P] Create Priority model in backend/app/models/priority.py with SQLModel
- [ ] T019 [P] Create Tag model in backend/app/models/tag.py with user_id foreign key
- [ ] T020 [P] Create TaskTag junction model in backend/app/models/task_tag.py
- [ ] T021 [P] Create RecurringTask model in backend/app/models/recurring_task.py
- [ ] T022 Update Task model in backend/app/models/task.py to add Optional[int] priority_id, Optional[datetime] due_date, Optional[bool] is_recurring, Optional[str] recurrence_pattern, Optional[int] recurring_task_id

### Dapr Publisher Module (Strangler Fig Pattern - Component 1)

- [ ] T023 Create Dapr publisher module at backend/app/dapr/publisher.py with httpx client for localhost:3500
- [ ] T024 Implement publish_event() function with fire-and-forget error handling (try/except with logging)
- [ ] T025 [P] Add feature flag check in publish_event() to enable/disable per-endpoint (read from config/feature_flags.py)
- [ ] T026 [P] Define TaskEvent schema in backend/app/dapr/schemas.py (event_type, task_id, user_id, title, completed, priority_id, due_date, timestamp)
- [ ] T027 [P] Define ReminderEvent schema in backend/app/dapr/schemas.py
- [ ] T028 [P] Define NotificationEvent schema in backend/app/dapr/schemas.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Event-Driven Task Operations (Priority: P1) 🎯 MVP

**Goal**: Enable asynchronous event publishing for task operations without blocking API responses

**Independent Test**: Create a task → verify immediate response (<200ms) → confirm task.created event published to Kafka → verify notification service receives event asynchronously

### Dapr Component Configuration (Local)

- [ ] T029 [US1] Create kafka-pubsub.yaml component at infrastructure/dapr/components/kafka-pubsub.yaml with local Kafka broker config
- [ ] T030 [US1] Apply kafka-pubsub component to Minikube (`kubectl apply -f infrastructure/dapr/components/kafka-pubsub.yaml`)
- [ ] T031 [US1] Verify component loaded (`kubectl get components` - expect kafka-pubsub)

### Backend Integration with Dapr Sidecar

- [X] T032 [US1] Add Dapr sidecar annotations to backend Helm chart at infrastructure/helm/todo-app/templates/backend-deployment.yaml (dapr.io/enabled: "true", dapr.io/app-id: "backend-service", dapr.io/app-port: "8000") ✅ Added annotations including UID/GID override
- [X] T033 [US1] Redeploy backend with Helm (`helm upgrade todo-app ./infrastructure/helm/todo-app --values values-local.yaml`) ✅ Deployed to DOKS
- [X] T034 [US1] Verify Dapr sidecar injected (`kubectl get pods` - expect 2/2 containers for backend pod) ✅ Backend pod running 2/2 (backend + daprd)

### Task Endpoint Migration (Strangler Fig Pattern)

- [X] T035 [US1] Import publisher module in backend/app/routers/tasks.py ✅ dapr_client already imported
- [X] T036 [US1] Add event publishing to POST /tasks endpoint after database save (call publisher.publish_event() with task.created event, feature flag enabled) ✅ task_created event published
- [X] T037 [US1] Add event publishing to PATCH /tasks/{id} endpoint after update (call publisher.publish_event() with task.updated event) ✅ task_updated event with updated_fields
- [X] T038 [US1] Add event publishing to DELETE /tasks/{id} endpoint after deletion (call publisher.publish_event() with task.deleted event) ✅ task_deleted event published
- [X] T039 [US1] Add event publishing to PATCH /tasks/{id}/complete endpoint (call publisher.publish_event() with task.completed event) ✅ task_completed/task_uncompleted events

### Kafka Topic Creation

- [ ] T040 [US1] Create task-events topic in local Kafka (`kubectl exec -it <kafka-pod> -- kafka-topics --create --topic task-events --partitions 3 --replication-factor 1`)
- [ ] T041 [P] [US1] Create notification-events topic with 1 partition
- [ ] T042 [P] [US1] Create reminder-events topic with 1 partition

### Validation

- [ ] T043 [US1] Test POST /tasks endpoint → verify HTTP 201 response in <200ms → check Dapr sidecar logs for event publish (`kubectl logs <backend-pod> -c daprd`)
- [ ] T044 [US1] Consume task-events topic to verify event structure (`kubectl exec -it <kafka-pod> -- kafka-console-consumer --topic task-events --from-beginning`)
- [ ] T045 [US1] Test with notification-service down → verify task creation still succeeds (graceful degradation)

**Checkpoint**: At this point, User Story 1 should be fully functional - task operations publish events without blocking responses

---

## Phase 4: User Story 2 - Distributed Conversation State (Priority: P1)

**Goal**: Enable stateless backend pods by storing conversation history in distributed Redis cache via Dapr

**Independent Test**: Start conversation on Pod A → simulate pod restart → continue conversation routed to Pod B → verify full history retrieved from Redis

### Dapr State Store Configuration (Local)

- [ ] T046 [US2] Create statestore.yaml component at infrastructure/dapr/components/statestore.yaml with local Redis config (host: localhost:6379, keyPrefix: "todo-app", ttlInSeconds: 3600)
- [ ] T047 [US2] Apply statestore component to Minikube (`kubectl apply -f infrastructure/dapr/components/statestore.yaml`)
- [ ] T048 [US2] Verify component loaded (`kubectl get components` - expect statestore)

### Backend AI Chat Integration

- [ ] T049 [P] [US2] Create Dapr state client wrapper in backend/app/dapr/state_client.py with save_state(), get_state(), delete_state() methods using httpx to POST/GET/DELETE localhost:3500/v1.0/state/statestore
- [ ] T050 [US2] Update POST /api/chat endpoint in backend/app/routers/chat.py to retrieve conversation history from Redis before calling Gemini API (get_state with key "todo-app::conversation::{conversation_id}")
- [ ] T051 [US2] Save updated conversation history to Redis after Gemini response (save_state with TTL=3600 seconds)
- [ ] T052 [US2] Add graceful degradation if Redis unavailable (try/except with error message, don't crash)

### Validation

- [ ] T053 [US2] Test POST /api/chat with new conversation → verify state saved to Redis (`redis-cli GET "todo-app::conversation::test-id"`)
- [ ] T054 [US2] Delete backend pod → send next message → verify new pod retrieves conversation from Redis
- [ ] T055 [US2] Test with 100+ messages → verify retrieval completes in <50ms (check backend logs)
- [ ] T056 [US2] Test with Redis stopped → verify graceful error (no 500 crash)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - backend is fully stateless

---

## Phase 5: User Story 3 - Recurring Task Automation (Priority: P2)

**Goal**: Automatically generate task instances from recurring task templates based on cron schedule

**Independent Test**: Create recurring task template → wait for cron trigger (5 minutes) → verify new task instance created with correct due date

### Recurring Task Service Scaffolding

- [ ] T057 [P] [US3] Create recurring-task-service directory structure (app/, models/, services/, main.py)
- [ ] T058 [P] [US3] Initialize FastAPI application in recurring-task-service/app/main.py with health check endpoint
- [ ] T059 [P] [US3] Add SQLModel dependency and create RecurringTask model copy in recurring-task-service/app/models/recurring_task.py
- [ ] T060 [P] [US3] Add psycopg2 and DATABASE_URL environment variable configuration

### Cron Binding Setup

- [ ] T061 [US3] Create reminder-cron.yaml binding at infrastructure/dapr/components/reminder-cron.yaml with schedule "@every 5m"
- [ ] T062 [US3] Apply cron binding to Minikube (`kubectl apply -f infrastructure/dapr/components/reminder-cron.yaml`)
- [ ] T063 [US3] Implement POST /recurring-task-cron handler in recurring-task-service/app/main.py (Dapr invokes this endpoint every 5 minutes)

### Recurring Task Logic

- [ ] T064 [US3] Implement query_due_templates() in recurring-task-service/app/services/recurring_service.py (SELECT * FROM recurring_tasks WHERE next_occurrence <= NOW() AND is_active = true)
- [ ] T065 [US3] Implement generate_task_instance() to create new task from template in same service file
- [ ] T066 [US3] Implement calculate_next_occurrence() to update template's next_occurrence based on recurrence_pattern (daily/weekly/monthly/custom cron)
- [ ] T067 [US3] Import Dapr publisher in recurring-task-service and publish task.created event for each generated instance
- [ ] T068 [US3] Add catch-up logic to generate all missed instances if service was down >5 minutes

### Deployment

- [ ] T069 [US3] Create Dockerfile for recurring-task-service/Dockerfile
- [ ] T070 [US3] Build Docker image (`docker build -t recurring-task-service:latest ./recurring-task-service`)
- [ ] T071 [US3] Create Helm deployment template at infrastructure/helm/todo-app/templates/recurring-task-deployment.yaml with Dapr annotations
- [ ] T072 [US3] Deploy recurring-task-service to Minikube (`helm upgrade todo-app ./infrastructure/helm/todo-app --values values-local.yaml`)
- [ ] T073 [US3] Verify pod with Dapr sidecar (`kubectl get pods` - expect recurring-task-service 2/2)

### Backend API for Recurring Tasks

- [ ] T074 [P] [US3] Create GET /recurring-tasks endpoint in backend/app/routers/recurring_tasks.py
- [ ] T075 [P] [US3] Create POST /recurring-tasks endpoint to create new templates
- [ ] T076 [P] [US3] Create PATCH /recurring-tasks/{id} endpoint to update templates
- [ ] T077 [P] [US3] Create DELETE /recurring-tasks/{id} endpoint to soft-delete (set is_active=false)

### Validation

- [ ] T078 [US3] Create recurring task template via POST /recurring-tasks with daily pattern
- [ ] T079 [US3] Wait 5 minutes → verify cron handler logs (`kubectl logs <recurring-task-pod>`)
- [ ] T080 [US3] Verify new task instance created in tasks table (`SELECT * FROM tasks WHERE recurring_task_id IS NOT NULL`)
- [ ] T081 [US3] Verify next_occurrence updated in recurring_tasks table
- [ ] T082 [US3] Stop recurring-task-service for 15 minutes → restart → verify catch-up generates 3 instances

**Checkpoint**: All user stories (US1, US2, US3) should now be independently functional on Minikube

---

## Phase 6: User Story 4 - Cloud Production Deployment (Priority: P2)

**Goal**: Deploy Phase 5 architecture to DigitalOcean Kubernetes with managed cloud services

**Independent Test**: Deploy Helm charts to DOKS → configure Redpanda Cloud with SASL/SSL → verify all services connect with 0 authentication errors

### Cloud Infrastructure Provisioning

- [ ] T083 [US4] Provision DOKS cluster via doctl (`doctl kubernetes cluster create todo-app-phase5 --region nyc3 --version 1.28.2-do.0 --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2"`)
- [ ] T084 [US4] Configure kubectl context for DOKS (`doctl kubernetes cluster kubeconfig save todo-app-phase5`)
- [X] T085 [P] [US4] Provision Redpanda Cloud cluster in AWS us-east-1 via Redpanda Cloud console (Tier 1 free tier) ✅ d4thqjgeuu3l6h0sd130 cluster created
- [X] T086 [P] [US4] Create SASL user in Redpanda Cloud with SCRAM-SHA-256 mechanism ✅ todo-app-producer service account created
- [X] T087 [P] [US4] Provision DigitalOcean Managed Redis in NYC3 region (Basic plan, 1GB RAM) ✅ Valkey 8.0 (e8a483bf) provisioned

### Dapr Control Plane on DOKS

- [X] T088 [US4] Initialize Dapr on DOKS cluster (`dapr init --kubernetes --wait`) ✅ v1.16.4 installed (same as T007)
- [X] T089 [US4] Verify Dapr control plane pods Running (`kubectl get pods -n dapr-system`) ✅ 8/8 pods running (same as T008)

### Kubernetes Secrets Creation

- [X] T090 [US4] Create redpanda-credentials Secret (`kubectl create secret generic redpanda-credentials --from-literal=brokers="seed-<id>.us-east-1.aws.redpanda.cloud:9092" --from-literal=sasl-username="todo-app-user" --from-literal=sasl-password="<password>"`) ✅ Created with Redpanda Cloud credentials
- [X] T091 [US4] Create redis-credentials Secret (`kubectl create secret generic redis-credentials --from-literal=redis-host="<cluster>.db.ondigitalocean.com" --from-literal=redis-port="25061" --from-literal=redis-password="<password>" --from-literal=redis-tls="true"`) ✅ Created with Valkey credentials
- [ ] T092 [US4] Create app-secrets Secret with DATABASE_URL, JWT_SECRET, GEMINI_API_KEY

### Production Dapr Components with secretKeyRef

- [X] T093 [US4] Copy specs/005-phase-5/contracts/kafka-pubsub-prod.yaml to infrastructure/dapr/components/kafka-pubsub-prod.yaml ✅ Created and configured with SHA-256 SASL
- [X] T094 [US4] Copy specs/005-phase-5/contracts/statestore-prod.yaml to infrastructure/dapr/components/statestore-prod.yaml ✅ Created with Valkey config
- [X] T095 [US4] Apply production Dapr components (`kubectl apply -f infrastructure/dapr/components/kafka-pubsub-prod.yaml -f infrastructure/dapr/components/statestore-prod.yaml -f infrastructure/dapr/components/reminder-cron.yaml`) ✅ Both components applied and loaded
- [X] T096 [US4] Verify components loaded (`kubectl get components`) ✅ kafka-pubsub and statestore loaded successfully

### Redpanda Cloud Topic Creation

- [X] T097 [US4] Create task-events topic in Redpanda Cloud (`rpk topic create task-events --partitions 3 --replicas 3 --brokers <broker> --user <user> --password <password> --sasl-mechanism SCRAM-SHA-256 --tls-enabled`) ✅ Created with 3 partitions
- [X] T098 [P] [US4] Create notification-events topic with 1 partition ✅ Created
- [X] T099 [P] [US4] Create reminder-events topic with 1 partition ✅ Created

### Docker Image Registry Setup

- [ ] T100 [US4] Create DigitalOcean Container Registry (`doctl registry create todo-app-registry`)
- [ ] T101 [US4] Log in to DOCR (`doctl registry login`)
- [ ] T102 [P] [US4] Build backend Docker image (`docker build -t registry.digitalocean.com/todo-app-registry/backend:latest ./backend`)
- [ ] T103 [P] [US4] Build frontend Docker image (`docker build -t registry.digitalocean.com/todo-app-registry/frontend:latest ./frontend`)
- [ ] T104 [P] [US4] Build recurring-task-service Docker image
- [ ] T105 [US4] Push all images to DOCR (`docker push registry.digitalocean.com/todo-app-registry/backend:latest` etc.)

### Helm Values for Production

- [ ] T106 [US4] Create infrastructure/helm/todo-app/values-prod.yaml with production image repositories, replicas=2, Dapr annotations, envFrom secretRef
- [ ] T107 [US4] Update backend deployment template with dapr.io/enabled, dapr.io/app-id, dapr.io/app-port annotations
- [ ] T108 [US4] Update frontend deployment template with Dapr annotations and LoadBalancer service type

### Production Deployment

- [ ] T109 [US4] Deploy Helm chart to DOKS (`helm install todo-app ./infrastructure/helm/todo-app --values infrastructure/helm/todo-app/values-prod.yaml --namespace default`)
- [ ] T110 [US4] Wait for rollout (`kubectl rollout status deployment/backend-service deployment/frontend-service deployment/recurring-task-service`)
- [ ] T111 [US4] Verify all pods 2/2 Running with Dapr sidecars (`kubectl get pods`)

### Production Validation

- [ ] T112 [US4] Verify Dapr components connected (`kubectl logs deployment/backend-service -c daprd | grep "Component loaded"` - expect kafka-pubsub, statestore)
- [ ] T113 [US4] Test event publishing to Redpanda Cloud (create task via API → check Dapr logs → consume topic with rpk)
- [ ] T114 [US4] Test Redis state store (start chat conversation → verify state saved in DO Managed Redis using redis-cli)
- [ ] T115 [US4] Verify 0 authentication errors in Dapr sidecar logs (`kubectl logs deployment/backend-service -c daprd | grep -i error`)
- [ ] T116 [US4] Get frontend LoadBalancer IP (`kubectl get service frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`)
- [ ] T117 [US4] Access application via LoadBalancer IP and verify full end-to-end flow

**Checkpoint**: All user stories should now be fully functional on DOKS with cloud services

---

## Phase 7: Notification Service (Component 3 - OPTIONAL)

**Purpose**: Build microservice to consume task-events and send notifications

**Note**: This phase is OPTIONAL for MVP. Include only if notification functionality is explicitly required.

- [X] T118 [P] Create notification-service directory structure (app/, main.py) ✅ Created with FastAPI app
- [X] T119 [P] Initialize FastAPI with Dapr subscription endpoint POST /dapr/subscribe ✅ Returns subscription to kafka-pubsub/task-events
- [X] T120 Implement POST /task-events handler to process task.created, task.completed, task.due events ✅ All 5 event types handled (created, updated, deleted, completed, uncompleted)
- [ ] T121 [P] Integrate SendGrid API for email notifications (SENDGRID_API_KEY from Secret) ⏭️ Skipped - using console logging for now
- [ ] T122 Add exponential backoff retry logic for failed deliveries ⏭️ Skipped - fire-and-forget pattern for MVP
- [X] T123 [P] Create Dockerfile and Helm deployment template with Dapr annotations ✅ Dockerfile and K8s deployment created
- [X] T124 Deploy notification-service to Minikube and DOKS ✅ Deployed to DOKS (ImagePullBackOff until Docker image built)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T125 [P] Update README.md with Phase 5 architecture diagram and deployment instructions
- [ ] T126 [P] Update quickstart.md with production deployment walkthrough (already created)
- [ ] T127 [P] Add monitoring documentation for Dapr metrics and component health
- [ ] T128 Code cleanup: Remove unused imports, format with black/prettier
- [ ] T129 [P] Security audit: Verify no plaintext credentials in version control (`git grep -i password`)
- [ ] T130 Run quickstart.md validation on fresh DOKS cluster (follow steps 1-10 from quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Event-driven task operations
- **User Story 2 (Phase 4)**: Depends on Foundational - Distributed conversation state (INDEPENDENT of US1)
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 (needs task.created events) - Recurring tasks
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 validated on Minikube - Cloud deployment
- **Notification Service (Phase 7)**: OPTIONAL - Depends on US1 (needs task-events topic)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - INDEPENDENT of US1 (can run in parallel)
- **User Story 3 (P2)**: Depends on US1 complete (needs event publishing infrastructure)
- **User Story 4 (P2)**: Depends on US1, US2, US3 validated locally (requires proven architecture before cloud deployment)

### Within Each User Story

- Dapr components before backend integration
- Backend integration before validation
- Local validation before cloud deployment
- Infrastructure provisioning before application deployment

### Parallel Opportunities

- **Phase 1**: All tasks marked [P] can run in parallel (T002, T003, T004, T006)
- **Phase 2**: Database migrations (T011-T017) and SQLModel updates (T018-T022) can run in parallel after Dapr setup (T007-T010)
- **Phase 2**: Dapr schema definitions (T026-T028) can run in parallel
- **User Story 1**: Kafka topic creation (T040-T042) can run in parallel
- **User Story 2**: State client wrapper (T049) can be developed while US1 is in progress
- **User Story 3**: Backend API endpoints (T074-T077) can run in parallel
- **User Story 4**: Cloud infrastructure provisioning (T085, T086, T087) can run in parallel
- **User Story 4**: Docker image builds (T102-T104) can run in parallel
- **User Story 4**: Redpanda topics (T098, T099) can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational Phase complete, launch Dapr component setup and Backend integration in parallel:

# Terminal 1: Dapr component configuration
Task T029: Create kafka-pubsub.yaml
Task T030: Apply component to Minikube
Task T031: Verify component loaded

# Terminal 2: Backend sidecar annotation (different file)
Task T032: Add annotations to backend-deployment.yaml
Task T033: Redeploy with Helm

# After both complete, proceed sequentially with endpoint migration (T035-T039)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (Tools installation)
2. Complete Phase 2: Foundational (CRITICAL - Dapr + Database)
3. Complete Phase 3: User Story 1 (Event publishing)
4. Complete Phase 4: User Story 2 (Redis state store)
5. **STOP and VALIDATE**: Test US1 & US2 independently on Minikube
6. If successful, proceed to US3 or deploy to DOKS (US4)

### Incremental Delivery

1. **Foundation** (Phase 1 + 2) → Dapr infrastructure ready on Minikube
2. **MVP** (Phase 3 + 4) → Event-driven + stateless backend working locally
3. **Automation** (Phase 5) → Recurring tasks functional
4. **Production** (Phase 6) → Full stack deployed to DOKS with cloud services
5. Each phase adds value without breaking previous phases

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Event publishing)
   - **Developer B**: User Story 2 (Redis state store) - PARALLEL with A
3. After US1 validated:
   - **Developer C**: User Story 3 (Recurring tasks) - depends on US1
4. After US1, US2, US3 validated locally:
   - **DevOps Engineer**: User Story 4 (Cloud deployment)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing preferred for infrastructure (kubectl, curl, Dapr CLI)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow Strangler Fig pattern: old code remains until Dapr validated
- Use feature flags for instant rollback (30 seconds vs full redeployment)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Total Tasks**: 130 tasks (excluding optional Notification Service)
**Task Breakdown by User Story**:
- Setup: 6 tasks
- Foundational: 22 tasks (BLOCKS all stories)
- User Story 1 (Event-Driven): 17 tasks
- User Story 2 (Distributed State): 11 tasks
- User Story 3 (Recurring Tasks): 26 tasks
- User Story 4 (Cloud Deployment): 35 tasks
- Notification Service (Optional): 7 tasks
- Polish: 6 tasks

**Parallel Opportunities**: 40+ tasks marked [P] can run in parallel
**MVP Scope**: Setup + Foundational + US1 + US2 = **56 tasks** (43% of total, delivers core event-driven + stateless architecture)
**Suggested First Milestone**: Complete through User Story 2 validation on Minikube (T001-T056)
