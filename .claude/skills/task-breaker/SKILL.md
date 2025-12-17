# Task Breaker Skill

## Metadata
```yaml
name: task-breaker
description: Breaks down large tasks into smaller, manageable subtasks with dependencies, estimates, and acceptance criteria. Enables effective sprint planning, work decomposition, and project management.
version: 1.0.0
category: planning
tags: [task-decomposition, project-management, sprint-planning, estimation, work-breakdown, agile]
dependencies: []
```

## When to Use This Skill

Use this skill when:
- User says "Break down this task" or "Split this feature into subtasks"
- Large feature needs to be decomposed for implementation
- Sprint planning requires task breakdown
- Need to estimate effort for complex work
- Creating implementation plan from requirements
- Building work breakdown structure (WBS)
- Need to identify dependencies between tasks
- Phase-based development requires task sequencing

## What This Skill Provides

### 1. Task Decomposition Strategies
- **Vertical slicing**: Full-stack features (frontend + backend + database)
- **Horizontal slicing**: Layer-by-layer (database → API → UI)
- **Dependency-first**: Start with foundational tasks
- **Risk-based**: High-risk items first
- **Value-based**: Highest business value first

### 2. Task Properties
- **Title**: Clear, actionable task name
- **Description**: Detailed what/why/how
- **Acceptance Criteria**: Definition of done
- **Estimate**: Story points or hours
- **Priority**: High/Normal/Low
- **Dependencies**: What must be done first
- **Category**: Type of work (feature/bug/refactor/docs)

### 3. Estimation Techniques
- **Story points**: Fibonacci sequence (1, 2, 3, 5, 8, 13)
- **T-shirt sizes**: XS, S, M, L, XL
- **Hours**: Time-based estimates
- **Complexity**: Simple, Medium, Complex
- **Relative sizing**: Compare to known tasks

### 4. Dependency Management
- **Sequential**: Task B requires Task A to complete
- **Parallel**: Tasks can be done simultaneously
- **Conditional**: Task depends on decision/outcome
- **Resource conflicts**: Same developer can't do both
- **Critical path**: Longest dependency chain

### 5. Quality Checks
- **SMART criteria**: Specific, Measurable, Achievable, Relevant, Time-bound
- **Size validation**: No task > 13 points or > 2 days
- **Coverage**: All requirements covered
- **Testability**: Each task has clear acceptance criteria
- **Independence**: Tasks don't overlap unnecessarily

---

## Implementation Examples

### Example 1: Basic Task Breakdown

```python
"""
Break down a large feature into manageable subtasks.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class TaskCategory(str, Enum):
    """Task categories."""
    FEATURE = "feature"
    BUG = "bug"
    REFACTOR = "refactor"
    DOCS = "docs"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"

@dataclass
class Subtask:
    """Subtask with all necessary properties."""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    estimate_points: int  # Fibonacci: 1, 2, 3, 5, 8, 13
    priority: TaskPriority = TaskPriority.NORMAL
    category: TaskCategory = TaskCategory.FEATURE
    dependencies: List[str] = field(default_factory=list)  # IDs of prerequisite tasks
    tags: List[str] = field(default_factory=list)
    assignee: Optional[str] = None

    def __post_init__(self):
        """Validate task after creation."""
        # Validate estimate
        valid_points = [1, 2, 3, 5, 8, 13]
        if self.estimate_points not in valid_points:
            raise ValueError(f"Estimate must be one of {valid_points}")

        # Validate acceptance criteria
        if not self.acceptance_criteria:
            raise ValueError("At least one acceptance criterion required")

    def is_ready_to_start(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_tasks for dep in self.dependencies)


class TaskBreaker:
    """Break down large tasks into manageable subtasks."""

    @staticmethod
    def break_down_feature(
        feature_name: str,
        description: str,
        requirements: List[str]
    ) -> List[Subtask]:
        """
        Break down a feature into implementation tasks.

        Args:
            feature_name: Name of the feature
            description: Detailed description
            requirements: List of requirements

        Returns:
            List of subtasks ordered by dependencies
        """
        subtasks = []

        # Example: User Authentication Feature
        # This would be customized based on actual requirements

        # Task 1: Database Schema
        subtasks.append(Subtask(
            id="AUTH-1",
            title="Create User database schema",
            description="Design and implement SQLModel schema for User table with authentication fields",
            acceptance_criteria=[
                "User model created with email, username, hashed_password fields",
                "Alembic migration generated and tested",
                "Indexes created for email and username",
                "Unique constraints enforced"
            ],
            estimate_points=3,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            tags=["database", "sqlmodel"]
        ))

        # Task 2: Password Hashing (depends on AUTH-1)
        subtasks.append(Subtask(
            id="AUTH-2",
            title="Implement password hashing utility",
            description="Create functions for hashing and verifying passwords using bcrypt",
            acceptance_criteria=[
                "hash_password() function implemented",
                "verify_password() function implemented",
                "Unit tests cover edge cases",
                "Salt rounds configurable via environment variable"
            ],
            estimate_points=2,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-1"],
            tags=["security", "backend"]
        ))

        # Task 3: Registration Endpoint (depends on AUTH-1, AUTH-2)
        subtasks.append(Subtask(
            id="AUTH-3",
            title="Create user registration API endpoint",
            description="Implement POST /api/v1/auth/register endpoint with validation",
            acceptance_criteria=[
                "POST /api/v1/auth/register endpoint created",
                "Email and password validation implemented",
                "Duplicate email/username handling",
                "Returns 201 with user data on success",
                "Integration tests pass"
            ],
            estimate_points=5,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-1", "AUTH-2"],
            tags=["api", "backend", "fastapi"]
        ))

        # Task 4: JWT Token Generation (depends on AUTH-1)
        subtasks.append(Subtask(
            id="AUTH-4",
            title="Implement JWT token generation",
            description="Create utility functions for generating and validating JWT tokens",
            acceptance_criteria=[
                "create_access_token() function implemented",
                "verify_token() function implemented",
                "Token expiration configurable",
                "Refresh token support",
                "Unit tests for token lifecycle"
            ],
            estimate_points=3,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-1"],
            tags=["security", "jwt", "backend"]
        ))

        # Task 5: Login Endpoint (depends on AUTH-2, AUTH-4)
        subtasks.append(Subtask(
            id="AUTH-5",
            title="Create login API endpoint",
            description="Implement POST /api/v1/auth/login with JWT token response",
            acceptance_criteria=[
                "POST /api/v1/auth/login endpoint created",
                "Email/password authentication working",
                "Returns JWT token on success",
                "Returns 401 for invalid credentials",
                "Updates last_login_at timestamp",
                "Integration tests pass"
            ],
            estimate_points=3,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-2", "AUTH-4"],
            tags=["api", "backend", "authentication"]
        ))

        # Task 6: Auth Middleware (depends on AUTH-4)
        subtasks.append(Subtask(
            id="AUTH-6",
            title="Create authentication middleware",
            description="Implement FastAPI dependency for protecting routes with JWT",
            acceptance_criteria=[
                "get_current_user() dependency created",
                "Validates JWT from Authorization header",
                "Returns 401 for missing/invalid token",
                "Injects current user into route",
                "Unit tests for all error cases"
            ],
            estimate_points=2,
            priority=TaskPriority.HIGH,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-4"],
            tags=["middleware", "backend"]
        ))

        # Task 7: Frontend Login Form (depends on AUTH-5)
        subtasks.append(Subtask(
            id="AUTH-7",
            title="Create login page UI",
            description="Build login form with Next.js App Router and Tailwind CSS",
            acceptance_criteria=[
                "Login form with email and password fields",
                "Form validation (client-side)",
                "Calls /api/v1/auth/login endpoint",
                "Stores JWT token in cookie/localStorage",
                "Redirects to dashboard on success",
                "Shows error messages for failed login"
            ],
            estimate_points=5,
            priority=TaskPriority.NORMAL,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-5"],
            tags=["frontend", "nextjs", "ui"]
        ))

        # Task 8: Frontend Registration Form (depends on AUTH-3)
        subtasks.append(Subtask(
            id="AUTH-8",
            title="Create registration page UI",
            description="Build registration form with validation",
            acceptance_criteria=[
                "Registration form with email, username, password fields",
                "Password strength indicator",
                "Form validation matching backend rules",
                "Calls /api/v1/auth/register endpoint",
                "Redirects to login on success",
                "Shows error messages (duplicate email, etc.)"
            ],
            estimate_points=5,
            priority=TaskPriority.NORMAL,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-3"],
            tags=["frontend", "nextjs", "ui"]
        ))

        # Task 9: Protected Route HOC (depends on AUTH-6, AUTH-7)
        subtasks.append(Subtask(
            id="AUTH-9",
            title="Create protected route wrapper",
            description="Build HOC/middleware for protecting Next.js pages",
            acceptance_criteria=[
                "withAuth HOC created",
                "Checks for valid JWT token",
                "Redirects to login if not authenticated",
                "Fetches current user data",
                "Provides user context to components"
            ],
            estimate_points=3,
            priority=TaskPriority.NORMAL,
            category=TaskCategory.FEATURE,
            dependencies=["AUTH-6", "AUTH-7"],
            tags=["frontend", "nextjs", "authentication"]
        ))

        # Task 10: E2E Tests (depends on all)
        subtasks.append(Subtask(
            id="AUTH-10",
            title="Write end-to-end authentication tests",
            description="Create E2E tests for complete authentication flow",
            acceptance_criteria=[
                "Test: User registration flow",
                "Test: Login with valid credentials",
                "Test: Login with invalid credentials",
                "Test: Access protected route without auth",
                "Test: Access protected route with valid token",
                "Test: Token expiration handling",
                "All tests pass in CI/CD"
            ],
            estimate_points=5,
            priority=TaskPriority.NORMAL,
            category=TaskCategory.TESTING,
            dependencies=["AUTH-7", "AUTH-8", "AUTH-9"],
            tags=["testing", "e2e", "playwright"]
        ))

        return subtasks


# Usage Example
if __name__ == "__main__":
    breaker = TaskBreaker()

    feature_subtasks = breaker.break_down_feature(
        feature_name="User Authentication",
        description="Implement complete user authentication system with JWT",
        requirements=[
            "User registration with email/password",
            "User login with JWT token",
            "Protected API routes",
            "Frontend login/registration pages"
        ]
    )

    print(f"Feature broken down into {len(feature_subtasks)} subtasks:\n")

    for task in feature_subtasks:
        print(f"[{task.id}] {task.title} ({task.estimate_points}pts)")
        if task.dependencies:
            print(f"  Depends on: {', '.join(task.dependencies)}")
        print(f"  Acceptance Criteria:")
        for criterion in task.acceptance_criteria:
            print(f"    - {criterion}")
        print()

    # Calculate total estimate
    total_points = sum(task.estimate_points for task in feature_subtasks)
    print(f"Total Estimate: {total_points} story points")
```

---

### Example 2: Dependency Graph

```python
"""
Visualize task dependencies and find critical path.
"""

from typing import List, Set, Dict
import networkx as nx
import matplotlib.pyplot as plt

class DependencyAnalyzer:
    """Analyze task dependencies and ordering."""

    def __init__(self, tasks: List[Subtask]):
        """Initialize with list of tasks."""
        self.tasks = {task.id: task for task in tasks}
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """Build directed graph of dependencies."""
        G = nx.DiGraph()

        # Add all tasks as nodes
        for task_id, task in self.tasks.items():
            G.add_node(task_id, **{
                "title": task.title,
                "estimate": task.estimate_points,
                "priority": task.priority.value
            })

        # Add dependencies as edges
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                G.add_edge(dep_id, task_id)  # dep -> task

        return G

    def get_execution_order(self) -> List[List[str]]:
        """
        Get tasks in execution order (topological sort).

        Returns:
            List of task levels (tasks in same level can run in parallel)
        """
        levels = []

        # Get topological generations
        for generation in nx.topological_generations(self.graph):
            levels.append(list(generation))

        return levels

    def get_critical_path(self) -> List[str]:
        """
        Find critical path (longest dependency chain).

        Returns:
            List of task IDs in critical path
        """
        # Find longest path
        longest_path = nx.dag_longest_path(self.graph, weight='estimate')
        return longest_path

    def get_ready_tasks(self, completed: Set[str]) -> List[str]:
        """
        Get tasks that are ready to start.

        Args:
            completed: Set of completed task IDs

        Returns:
            List of task IDs that can be started
        """
        ready = []

        for task_id, task in self.tasks.items():
            if task_id not in completed:
                if task.is_ready_to_start(list(completed)):
                    ready.append(task_id)

        return ready

    def visualize_dependencies(self, output_file: str = "task_graph.png"):
        """
        Create visual dependency graph.

        Args:
            output_file: Path to save graph image
        """
        pos = nx.spring_layout(self.graph)

        # Color nodes by priority
        colors = []
        for node in self.graph.nodes():
            priority = self.graph.nodes[node]['priority']
            if priority == 'high':
                colors.append('red')
            elif priority == 'normal':
                colors.append('yellow')
            else:
                colors.append('green')

        # Draw graph
        plt.figure(figsize=(12, 8))
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color=colors,
            node_size=2000,
            font_size=8,
            arrows=True
        )

        plt.title("Task Dependency Graph")
        plt.savefig(output_file)
        print(f"✓ Dependency graph saved to {output_file}")


# Usage
analyzer = DependencyAnalyzer(feature_subtasks)

# Get execution order
print("Execution Order (by level):")
levels = analyzer.get_execution_order()
for i, level in enumerate(levels, 1):
    print(f"\nLevel {i} (can run in parallel):")
    for task_id in level:
        task = analyzer.tasks[task_id]
        print(f"  - [{task_id}] {task.title} ({task.estimate_points}pts)")

# Find critical path
print("\nCritical Path:")
critical = analyzer.get_critical_path()
total_critical_points = sum(analyzer.tasks[tid].estimate_points for tid in critical)
print(f"  {' → '.join(critical)}")
print(f"  Total: {total_critical_points} points")

# Simulate progress
completed = set()
print("\nReady to Start:")
ready = analyzer.get_ready_tasks(completed)
for task_id in ready:
    print(f"  - [{task_id}] {analyzer.tasks[task_id].title}")

# Visualize
analyzer.visualize_dependencies()
```

---

### Example 3: Sprint Planning

```python
"""
Plan sprints based on task breakdown and team capacity.
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta

@dataclass
class SprintPlan:
    """Sprint planning information."""
    sprint_number: int
    start_date: datetime
    end_date: datetime
    capacity_points: int
    tasks: List[Subtask]

    @property
    def total_points(self) -> int:
        """Calculate total story points in sprint."""
        return sum(task.estimate_points for task in self.tasks)

    @property
    def utilization(self) -> float:
        """Calculate sprint capacity utilization."""
        return (self.total_points / self.capacity_points) * 100

    def can_add_task(self, task: Subtask) -> bool:
        """Check if task can be added without exceeding capacity."""
        return (self.total_points + task.estimate_points) <= self.capacity_points


class SprintPlanner:
    """Plan sprints from task list."""

    def __init__(
        self,
        tasks: List[Subtask],
        team_velocity: int = 20,  # Story points per sprint
        sprint_duration_days: int = 14
    ):
        """
        Initialize sprint planner.

        Args:
            tasks: List of all tasks
            team_velocity: Story points the team can complete per sprint
            sprint_duration_days: Sprint length in days
        """
        self.tasks = tasks
        self.team_velocity = team_velocity
        self.sprint_duration_days = sprint_duration_days
        self.analyzer = DependencyAnalyzer(tasks)

    def plan_sprints(self, start_date: datetime) -> List[SprintPlan]:
        """
        Automatically plan sprints based on dependencies and capacity.

        Args:
            start_date: When to start Sprint 1

        Returns:
            List of sprint plans
        """
        sprints = []
        completed = set()
        sprint_num = 1
        current_date = start_date

        while len(completed) < len(self.tasks):
            # Create new sprint
            sprint_end = current_date + timedelta(days=self.sprint_duration_days)
            sprint = SprintPlan(
                sprint_number=sprint_num,
                start_date=current_date,
                end_date=sprint_end,
                capacity_points=self.team_velocity,
                tasks=[]
            )

            # Get ready tasks
            ready_tasks = self.analyzer.get_ready_tasks(completed)

            # Sort by priority (high first)
            ready_tasks.sort(
                key=lambda tid: (
                    self.analyzer.tasks[tid].priority.value != 'high',
                    self.analyzer.tasks[tid].estimate_points
                )
            )

            # Fill sprint capacity
            for task_id in ready_tasks:
                task = self.analyzer.tasks[task_id]

                if sprint.can_add_task(task):
                    sprint.tasks.append(task)
                    completed.add(task_id)

            # Add sprint to list
            if sprint.tasks:
                sprints.append(sprint)
                sprint_num += 1
                current_date = sprint_end
            else:
                # No more tasks can be added (blocked by dependencies)
                break

        return sprints


# Usage
planner = SprintPlanner(
    tasks=feature_subtasks,
    team_velocity=20,  # 20 points per 2-week sprint
    sprint_duration_days=14
)

sprints = planner.plan_sprints(start_date=datetime.now())

print(f"Feature requires {len(sprints)} sprints:\n")

for sprint in sprints:
    print(f"Sprint {sprint.sprint_number}")
    print(f"  Dates: {sprint.start_date.date()} to {sprint.end_date.date()}")
    print(f"  Capacity: {sprint.total_points}/{sprint.capacity_points} points ({sprint.utilization:.1f}%)")
    print(f"  Tasks:")
    for task in sprint.tasks:
        print(f"    - [{task.id}] {task.title} ({task.estimate_points}pts)")
    print()

# Calculate timeline
total_days = (sprints[-1].end_date - sprints[0].start_date).days
print(f"Total Timeline: {total_days} days ({len(sprints)} sprints)")
print(f"Total Effort: {sum(sprint.total_points for sprint in sprints)} story points")
```

---

### Example 4: Template-Based Breakdown

```python
"""
Use templates for common task patterns.
"""

class TaskTemplate:
    """Template for common task types."""

    @staticmethod
    def crud_api_endpoint(resource_name: str, base_id: str) -> List[Subtask]:
        """
        Template for CRUD API endpoint implementation.

        Args:
            resource_name: Name of resource (e.g., "Task", "User")
            base_id: Base ID prefix (e.g., "TASK", "USER")

        Returns:
            List of subtasks for complete CRUD implementation
        """
        resource_lower = resource_name.lower()
        tasks = []

        # 1. Database Model
        tasks.append(Subtask(
            id=f"{base_id}-1",
            title=f"Create {resource_name} database model",
            description=f"Implement SQLModel schema for {resource_name} with all required fields",
            acceptance_criteria=[
                f"{resource_name} model created with all fields",
                "Alembic migration generated",
                "Indexes created for foreign keys",
                "Constraints properly defined"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            tags=["database", "sqlmodel"]
        ))

        # 2. Pydantic Schemas
        tasks.append(Subtask(
            id=f"{base_id}-2",
            title=f"Create {resource_name} Pydantic schemas",
            description=f"Define Create, Update, Read schemas for {resource_name}",
            acceptance_criteria=[
                f"{resource_name}Create schema defined",
                f"{resource_name}Update schema defined",
                f"{resource_name}Read schema defined",
                "Field validators implemented"
            ],
            estimate_points=2,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-1"],
            tags=["backend", "pydantic"]
        ))

        # 3. CREATE endpoint
        tasks.append(Subtask(
            id=f"{base_id}-3",
            title=f"Implement POST /{resource_lower}s endpoint",
            description=f"Create new {resource_name} with validation",
            acceptance_criteria=[
                f"POST /api/v1/{resource_lower}s endpoint created",
                "Request validation working",
                "Returns 201 with created resource",
                "JWT authentication required",
                "Integration tests pass"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2"],
            tags=["api", "backend", "fastapi"]
        ))

        # 4. READ (list) endpoint
        tasks.append(Subtask(
            id=f"{base_id}-4",
            title=f"Implement GET /{resource_lower}s endpoint",
            description=f"List all {resource_name}s with pagination",
            acceptance_criteria=[
                f"GET /api/v1/{resource_lower}s endpoint created",
                "Pagination implemented (limit/offset)",
                "Filtering by user_id working",
                "Returns 200 with list of resources",
                "Integration tests pass"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2"],
            tags=["api", "backend", "fastapi"]
        ))

        # 5. READ (single) endpoint
        tasks.append(Subtask(
            id=f"{base_id}-5",
            title=f"Implement GET /{resource_lower}s/{{id}} endpoint",
            description=f"Get single {resource_name} by ID",
            acceptance_criteria=[
                f"GET /api/v1/{resource_lower}s/{{id}} endpoint created",
                "Returns 200 with resource",
                "Returns 404 if not found",
                "User ownership validated",
                "Integration tests pass"
            ],
            estimate_points=2,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2"],
            tags=["api", "backend", "fastapi"]
        ))

        # 6. UPDATE endpoint
        tasks.append(Subtask(
            id=f"{base_id}-6",
            title=f"Implement PATCH /{resource_lower}s/{{id}} endpoint",
            description=f"Update existing {resource_name}",
            acceptance_criteria=[
                f"PATCH /api/v1/{resource_lower}s/{{id}} endpoint created",
                "Partial updates supported",
                "Returns 200 with updated resource",
                "Returns 404 if not found",
                "User ownership validated",
                "Integration tests pass"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2"],
            tags=["api", "backend", "fastapi"]
        ))

        # 7. DELETE endpoint
        tasks.append(Subtask(
            id=f"{base_id}-7",
            title=f"Implement DELETE /{resource_lower}s/{{id}} endpoint",
            description=f"Delete {resource_name}",
            acceptance_criteria=[
                f"DELETE /api/v1/{resource_lower}s/{{id}} endpoint created",
                "Returns 204 on success",
                "Returns 404 if not found",
                "User ownership validated",
                "Soft delete if applicable",
                "Integration tests pass"
            ],
            estimate_points=2,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2"],
            tags=["api", "backend", "fastapi"]
        ))

        return tasks

    @staticmethod
    def frontend_page(page_name: str, base_id: str, backend_dep: str) -> List[Subtask]:
        """
        Template for frontend page implementation.

        Args:
            page_name: Name of page (e.g., "Task List", "User Profile")
            base_id: Base ID prefix
            backend_dep: ID of backend task this depends on

        Returns:
            List of subtasks for page implementation
        """
        page_lower = page_name.lower().replace(" ", "-")
        tasks = []

        # 1. Page layout
        tasks.append(Subtask(
            id=f"{base_id}-1",
            title=f"Create {page_name} page layout",
            description=f"Build Next.js App Router page for {page_name}",
            acceptance_criteria=[
                f"Page created at /app/{page_lower}/page.tsx",
                "Layout and header implemented",
                "Responsive design with Tailwind CSS",
                "Loading state handled"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            dependencies=[backend_dep],
            tags=["frontend", "nextjs", "ui"]
        ))

        # 2. Data fetching
        tasks.append(Subtask(
            id=f"{base_id}-2",
            title=f"Implement data fetching for {page_name}",
            description="Fetch data from backend API",
            acceptance_criteria=[
                "API client function created",
                "SWR/React Query for caching",
                "Error handling implemented",
                "Loading and error states shown"
            ],
            estimate_points=2,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-1"],
            tags=["frontend", "api-integration"]
        ))

        # 3. Components
        tasks.append(Subtask(
            id=f"{base_id}-3",
            title=f"Build components for {page_name}",
            description="Create reusable components for page",
            acceptance_criteria=[
                "All components created and styled",
                "Props properly typed (TypeScript)",
                "Accessibility (ARIA) labels added",
                "Components documented"
            ],
            estimate_points=5,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-1"],
            tags=["frontend", "components", "react"]
        ))

        # 4. Interactions
        tasks.append(Subtask(
            id=f"{base_id}-4",
            title=f"Implement user interactions for {page_name}",
            description="Add event handlers and state management",
            acceptance_criteria=[
                "All button clicks handled",
                "Form submissions working",
                "Optimistic updates implemented",
                "Success/error messages shown"
            ],
            estimate_points=3,
            category=TaskCategory.FEATURE,
            dependencies=[f"{base_id}-2", f"{base_id}-3"],
            tags=["frontend", "interactions"]
        ))

        return tasks


# Usage - Generate tasks from templates
print("CRUD API Template:")
task_crud = TaskTemplate.crud_api_endpoint("Task", "TASK-API")
for task in task_crud:
    print(f"  [{task.id}] {task.title} ({task.estimate_points}pts)")

print("\nFrontend Page Template:")
task_page = TaskTemplate.frontend_page("Task List", "TASK-UI", "TASK-API-4")
for task in task_page:
    print(f"  [{task.id}] {task.title} ({task.estimate_points}pts)")
```

---

## CLI Tool

```python
"""
CLI for task breakdown operations.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

app = typer.Typer(name="task-breaker", help="Task Breakdown Tool")
console = Console()

@app.command("break")
def break_down_feature(
    feature: str = typer.Argument(..., help="Feature name"),
    template: str = typer.Option(None, help="Template to use (crud-api, frontend-page)")
):
    """Break down a feature into subtasks."""
    if template == "crud-api":
        tasks = TaskTemplate.crud_api_endpoint(feature, feature.upper())
    elif template == "frontend-page":
        tasks = TaskTemplate.frontend_page(feature, f"{feature.upper()}-UI", "API-1")
    else:
        console.print("[yellow]No template specified. Using custom breakdown...[/yellow]")
        return

    # Display as table
    table = Table(title=f"{feature} - Task Breakdown")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Points", justify="right", style="green")
    table.add_column("Dependencies", style="yellow")

    for task in tasks:
        table.add_row(
            task.id,
            task.title,
            str(task.estimate_points),
            ", ".join(task.dependencies) if task.dependencies else "-"
        )

    console.print(table)
    console.print(f"\nTotal: {sum(t.estimate_points for t in tasks)} story points")

@app.command("deps")
def show_dependencies(tasks_json: str = typer.Argument(..., help="Tasks JSON file")):
    """Show dependency tree."""
    # Load tasks from JSON
    # ...

    tree = Tree("📋 Task Dependencies")

    # Build tree structure
    # ...

    console.print(tree)

@app.command("plan")
def plan_sprint(
    tasks_json: str = typer.Argument(..., help="Tasks JSON file"),
    velocity: int = typer.Option(20, help="Team velocity (points per sprint)")
):
    """Plan sprints from tasks."""
    # Load tasks, create planner, generate sprints
    # ...

    console.print(f"[cyan]Sprint Plan (Velocity: {velocity} points/sprint)[/cyan]\n")

    # Display sprints
    # ...

if __name__ == "__main__":
    app()
```

---

## Best Practices

1. **Task Size**:
   - Keep tasks small (< 13 story points, < 2 days)
   - If > 13 points, break down further
   - Aim for 3-5 points for most tasks

2. **Dependencies**:
   - Minimize dependencies for parallelization
   - Identify critical path early
   - Plan for blockers

3. **Acceptance Criteria**:
   - Make criteria testable
   - Include happy path and edge cases
   - Define "done" clearly

4. **Estimation**:
   - Use relative sizing (compare to known tasks)
   - Include time for testing and documentation
   - Account for unknown unknowns (add buffer)

5. **Prioritization**:
   - High-risk items first
   - High-value features prioritized
   - Consider dependencies

---

## Quality Checklist

Before finalizing task breakdown:
- [ ] All tasks have clear titles and descriptions
- [ ] Acceptance criteria defined for each task
- [ ] Estimates in Fibonacci sequence (1, 2, 3, 5, 8, 13)
- [ ] No task > 13 points or > 2 days
- [ ] Dependencies identified and documented
- [ ] Tasks ordered by dependencies
- [ ] Critical path identified
- [ ] Sprint capacity considered
- [ ] All requirements covered
- [ ] Tasks are testable and independent

This skill enables effective decomposition of large features into manageable, estimable, and trackable subtasks for agile development.
