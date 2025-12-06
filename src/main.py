#!/usr/bin/env python3
"""Console TODO List Manager - Phase I Implementation

A simple console-based TODO list application with full CRUD operations.
Supports adding, viewing, updating, deleting, and marking tasks complete.
"""

from typing import Optional
from dataclasses import dataclass


# ============================================================================
# MODEL LAYER
# ============================================================================

@dataclass
class Task:
    """Represents a TODO task.

    Attributes:
        id: Unique auto-incrementing identifier
        title: Task name (required, non-empty)
        description: Optional detailed description
        completed: Completion status (default False)
    """
    id: int
    title: str
    description: str
    completed: bool = False


# ============================================================================
# LOGIC LAYER
# ============================================================================

class TaskManager:
    """Manages in-memory task collection with CRUD operations.

    Attributes:
        _tasks: Dictionary mapping task ID to Task object
        _next_id: Counter for auto-incrementing task IDs
    """

    def __init__(self) -> None:
        """Initialize TaskManager with empty task collection."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str) -> int:
        """Add a new task with auto-assigned ID.

        Args:
            title: Task name (non-empty)
            description: Optional task details

        Returns:
            Assigned task ID
        """
        task_id = self._next_id
        task = Task(id=task_id, title=title, description=description, completed=False)
        self._tasks[task_id] = task
        self._next_id += 1
        return task_id

    def view_tasks(self) -> list[Task]:
        """Retrieve all tasks sorted by ID.

        Returns:
            List of Task objects sorted by ID (empty if no tasks)
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve single task by ID.

        Args:
            task_id: ID of task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def mark_complete(self, task_id: int) -> bool:
        """Set task's completed status to True.

        Args:
            task_id: ID of task to mark complete

        Returns:
            True if task found and marked, False if not found
        """
        task = self.get_task(task_id)
        if task:
            task.completed = True
            return True
        return False

    def update_task(self, task_id: int, title: Optional[str], description: Optional[str]) -> bool:
        """Update task title and/or description.

        Args:
            task_id: ID of task to update
            title: New title, or None to keep current
            description: New description, or None to keep current

        Returns:
            True if task found and updated, False if not found
        """
        task = self.get_task(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Remove task from collection.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task found and deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


# ============================================================================
# PRESENTATION LAYER
# ============================================================================

def display_menu() -> None:
    """Display the main menu with all available options."""
    print("\n=== TODO List Manager ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete")
    print("6. Exit")


def get_menu_choice() -> int:
    """Get and validate menu selection from user.

    Returns:
        Valid menu choice (1-6)
    """
    while True:
        try:
            choice = int(input("Select option (1-6): "))
            if 1 <= choice <= 6:
                return choice
            print("Invalid option. Please select 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def handle_add_task(manager: TaskManager) -> None:
    """Handle adding a new task with title and description.

    Args:
        manager: TaskManager instance
    """
    # Validate title (non-empty required)
    while True:
        title = input("Enter task title: ").strip()
        if title:
            break
        print("Title cannot be empty. Please try again.")

    # Get optional description
    description = input("Enter task description (optional): ")

    task_id = manager.add_task(title, description)
    print(f"Task added with ID {task_id}")


def handle_view_tasks(manager: TaskManager) -> None:
    """Display all tasks with status indicators.

    Args:
        manager: TaskManager instance
    """
    print("\n=== Your Tasks ===")
    tasks = manager.view_tasks()

    if not tasks:
        print("No tasks available.")
    else:
        for task in tasks:
            status = "[x]" if task.completed else "[ ]"
            print(f"[{task.id}] {status} {task.title}")


def get_task_id() -> int:
    """Get and validate task ID from user.

    Returns:
        Valid task ID (positive integer)
    """
    while True:
        try:
            task_id = int(input("Enter task ID: ").strip())
            if task_id > 0:
                return task_id
            print("Invalid ID format. Please enter a number.")
        except ValueError:
            print("Invalid ID format. Please enter a number.")


def handle_mark_complete(manager: TaskManager) -> None:
    """Handle marking a task as complete.

    Args:
        manager: TaskManager instance
    """
    task_id = get_task_id()

    if manager.mark_complete(task_id):
        print(f"Task {task_id} marked as complete.")
    else:
        print(f"Task ID {task_id} not found.")


def handle_update_task(manager: TaskManager) -> None:
    """Handle updating task title and/or description.

    Args:
        manager: TaskManager instance
    """
    task_id = get_task_id()

    # Check if task exists
    if not manager.get_task(task_id):
        print(f"Task ID {task_id} not found.")
        return

    # Get new title (optional - empty means skip)
    new_title_input = input("Enter new title (press Enter to skip): ").strip()
    new_title = new_title_input if new_title_input else None

    # Get new description (optional - empty means skip)
    new_description_input = input("Enter new description (press Enter to skip): ")
    new_description = new_description_input if new_description_input else None

    # Check if any changes were made
    if new_title is None and new_description is None:
        print("No changes made.")
    else:
        manager.update_task(task_id, new_title, new_description)
        print(f"Task {task_id} updated successfully.")


def handle_delete_task(manager: TaskManager) -> None:
    """Handle deleting a task.

    Args:
        manager: TaskManager instance
    """
    task_id = get_task_id()

    if manager.delete_task(task_id):
        print(f"Task {task_id} deleted successfully.")
    else:
        print(f"Task ID {task_id} not found.")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """Main application loop."""
    manager = TaskManager()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(manager)
        elif choice == 2:
            handle_view_tasks(manager)
        elif choice == 3:
            handle_update_task(manager)
        elif choice == 4:
            handle_delete_task(manager)
        elif choice == 5:
            handle_mark_complete(manager)
        elif choice == 6:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
