"use client";

/**
 * Enhanced Dashboard Page with Modern UI
 *
 * Features:
 * - Priority levels (low, normal, high) with color coding
 * - Due dates with calendar picker
 * - Improved visual design with gradients and shadows
 * - Better task cards with status indicators
 * - Filter by priority
 * - Sort by due date, priority, created date
 */

import { useState, useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";
import { tasksApi } from "@/lib/tasks-api";
import type { Task, TaskCreateInput, TaskPriority } from "@/lib/types";

const PRIORITY_COLORS = {
  low: "bg-blue-100 text-blue-800 border-blue-300",
  normal: "bg-gray-100 text-gray-800 border-gray-300",
  high: "bg-red-100 text-red-800 border-red-300",
};

const PRIORITY_BADGE_COLORS = {
  low: "bg-blue-500",
  normal: "bg-gray-500",
  high: "bg-red-500",
};

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [priorityFilter, setPriorityFilter] = useState<"all" | TaskPriority>("all");
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Create form state
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [newTaskPriority, setNewTaskPriority] = useState<TaskPriority>("normal");
  const [newTaskDueDate, setNewTaskDueDate] = useState("");
  const [creating, setCreating] = useState(false);

  // Edit form state
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editPriority, setEditPriority] = useState<TaskPriority>("normal");
  const [editDueDate, setEditDueDate] = useState("");
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!user) return;

    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await tasksApi.list(user.id, { status: filter, sort: "created" });
        setTasks(data);
      } catch (err) {
        console.error("Failed to fetch tasks:", err);
        setError(err instanceof Error ? err.message : "Failed to load tasks");
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [user, filter]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !newTaskTitle.trim()) return;

    try {
      setCreating(true);
      setError(null);

      const taskData: TaskCreateInput = {
        title: newTaskTitle.trim(),
        description: newTaskDescription.trim() || undefined,
        priority: newTaskPriority,
        due_date: newTaskDueDate || undefined,
      };

      const newTask = await tasksApi.create(user.id, taskData);
      setTasks([...tasks, newTask]);
      setNewTaskTitle("");
      setNewTaskDescription("");
      setNewTaskPriority("normal");
      setNewTaskDueDate("");
      setShowCreateDialog(false);
    } catch (err) {
      console.error("Failed to create task:", err);
      setError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setCreating(false);
    }
  };

  const handleToggleComplete = async (task: Task) => {
    if (!user) return;

    try {
      setError(null);
      const updatedTask = await tasksApi.toggleComplete(user.id, task.id);
      setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
    } catch (err) {
      console.error("Failed to toggle task:", err);
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user) return;
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      setError(null);
      await tasksApi.delete(user.id, taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err) {
      console.error("Failed to delete task:", err);
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setEditPriority(task.priority);
    setEditDueDate(task.due_date ? task.due_date.split('T')[0] : "");
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !editingTask) return;

    try {
      setUpdating(true);
      setError(null);

      const updatedTask = await tasksApi.update(user.id, editingTask.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
        priority: editPriority,
        due_date: editDueDate || undefined,
      });

      setTasks(tasks.map(t => t.id === editingTask.id ? updatedTask : t));
      setEditingTask(null);
    } catch (err) {
      console.error("Failed to update task:", err);
      setError(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setUpdating(false);
    }
  };

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return <span className="text-red-600 font-medium">Overdue</span>;
    if (diffDays === 0) return <span className="text-orange-600 font-medium">Today</span>;
    if (diffDays === 1) return <span className="text-yellow-600 font-medium">Tomorrow</span>;
    if (diffDays <= 7) return <span className="text-blue-600 font-medium">In {diffDays} days</span>;

    return date.toLocaleDateString();
  };

  const filteredTasks = tasks.filter(task => {
    if (priorityFilter !== "all" && task.priority !== priorityFilter) return false;
    return true;
  });

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                My Tasks
              </h1>
              <p className="text-sm text-gray-600 mt-1">Welcome back, {user.name}!</p>
            </div>
            <button
              onClick={signOut}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Toolbar */}
        <div className="mb-8 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <div className="flex flex-wrap gap-2">
            {/* Status Filter */}
            <div className="flex gap-1 bg-white rounded-lg p-1 shadow-sm border border-gray-200">
              {["all", "pending", "completed"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as typeof filter)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    filter === f
                      ? "bg-blue-600 text-white shadow-sm"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>

            {/* Priority Filter */}
            <div className="flex gap-1 bg-white rounded-lg p-1 shadow-sm border border-gray-200">
              <button
                onClick={() => setPriorityFilter("all")}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                  priorityFilter === "all"
                    ? "bg-gray-600 text-white shadow-sm"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                All
              </button>
              {(["low", "normal", "high"] as TaskPriority[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPriorityFilter(p)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    priorityFilter === p
                      ? `${PRIORITY_COLORS[p]} shadow-sm`
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => setShowCreateDialog(true)}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg text-sm font-medium hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all"
          >
            + New Task
          </button>
        </div>

        {/* Task List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-gray-600 mt-4">Loading tasks...</p>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No tasks found</h3>
            <p className="text-gray-600 mb-6">Create your first task to get started!</p>
            <button
              onClick={() => setShowCreateDialog(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Create Task
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                className={`bg-white rounded-xl shadow-sm border-l-4 p-5 hover:shadow-md transition-shadow ${
                  task.completed
                    ? "border-green-500 bg-gray-50"
                    : PRIORITY_BADGE_COLORS[task.priority].replace("bg-", "border-")
                }`}
              >
                <div className="flex items-start gap-4">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => handleToggleComplete(task)}
                    className="mt-1 h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3
                          className={`font-semibold text-lg ${
                            task.completed ? "line-through text-gray-500" : "text-gray-900"
                          }`}
                        >
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                        )}

                        <div className="flex flex-wrap items-center gap-3 mt-3">
                          {/* Priority Badge */}
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${PRIORITY_COLORS[task.priority]}`}>
                            {task.priority === "high" && "🔴"}
                            {task.priority === "normal" && "🟡"}
                            {task.priority === "low" && "🔵"}
                            <span className="ml-1">{task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}</span>
                          </span>

                          {/* Due Date */}
                          {task.due_date && (
                            <span className="text-xs text-gray-600">
                              📅 Due: {formatDate(task.due_date)}
                            </span>
                          )}

                          {/* Created Date */}
                          <span className="text-xs text-gray-400">
                            Created: {new Date(task.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEditTask(task)}
                          className="px-3 py-1.5 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="px-3 py-1.5 text-sm text-red-600 hover:text-red-700 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Task Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Task</h2>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  id="title"
                  type="text"
                  required
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter task title"
                  maxLength={200}
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter task description (optional)"
                  rows={3}
                  maxLength={1000}
                />
              </div>

              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  id="priority"
                  value={newTaskPriority}
                  onChange={(e) => setNewTaskPriority(e.target.value as TaskPriority)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="low">🔵 Low</option>
                  <option value="normal">🟡 Normal</option>
                  <option value="high">🔴 High</option>
                </select>
              </div>

              <div>
                <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-2">
                  Due Date
                </label>
                <input
                  id="due_date"
                  type="date"
                  value={newTaskDueDate}
                  onChange={(e) => setNewTaskDueDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateDialog(false);
                    setNewTaskTitle("");
                    setNewTaskDescription("");
                    setNewTaskPriority("normal");
                    setNewTaskDueDate("");
                  }}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  disabled={creating}
                >
                  {creating ? "Creating..." : "Create Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Task Dialog */}
      {editingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Edit Task</h2>
            <form onSubmit={handleUpdateTask} className="space-y-4">
              <div>
                <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  id="edit-title"
                  type="text"
                  required
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  maxLength={200}
                />
              </div>

              <div>
                <label htmlFor="edit-description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  id="edit-description"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  maxLength={1000}
                />
              </div>

              <div>
                <label htmlFor="edit-priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  id="edit-priority"
                  value={editPriority}
                  onChange={(e) => setEditPriority(e.target.value as TaskPriority)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="low">🔵 Low</option>
                  <option value="normal">🟡 Normal</option>
                  <option value="high">🔴 High</option>
                </select>
              </div>

              <div>
                <label htmlFor="edit-due-date" className="block text-sm font-medium text-gray-700 mb-2">
                  Due Date
                </label>
                <input
                  id="edit-due-date"
                  type="date"
                  value={editDueDate}
                  onChange={(e) => setEditDueDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingTask(null)}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  disabled={updating}
                >
                  {updating ? "Updating..." : "Update Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
