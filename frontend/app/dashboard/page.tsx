"use client";

import { useState, useEffect, Fragment, useMemo } from "react";
import { useAuth } from "@/components/AuthProvider";
import { tasksApi } from "@/lib/tasks-api";
import type { Task, TaskCreateInput, TaskPriority } from "@/lib/types";
import { Dialog, Transition } from "@headlessui/react";
import Link from "next/link";
import VoiceButton from "@/components/VoiceButton";
import { LanguageSwitcher, useLanguage } from "@/lib/i18n/LanguageContext";

// Priority ID to string mapping (backend uses 1=High, 2=Medium, 3=Low)
const PRIORITY_ID_MAP: { [key: number]: TaskPriority } = {
  1: "high",
  2: "normal",
  3: "low",
};

// Reverse mapping: string to ID
const PRIORITY_STRING_TO_ID: { [key in TaskPriority]: number } = {
  high: 1,
  normal: 2,
  low: 3,
};

// Helper function to get priority string from priority_id
function getPriorityString(priority_id?: number | null): TaskPriority {
  if (!priority_id || !PRIORITY_ID_MAP[priority_id]) return "normal";
  return PRIORITY_ID_MAP[priority_id];
}

// Priority styling constants
const PRIORITY_STYLES: { [key in TaskPriority]: { badge: string; border: string; text: string } } = {
  low: {
    badge: "bg-cyan-900/50 border border-cyan-700 text-cyan-300",
    border: "border-cyan-500",
    text: "text-cyan-300",
  },
  normal: {
    badge: "bg-gray-700/50 border border-gray-600 text-gray-300",
    border: "border-gray-500",
    text: "text-gray-300",
  },
  high: {
    badge: "bg-red-900/50 border border-red-700 text-red-300",
    border: "border-red-500",
    text: "text-red-300",
  },
};

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const { language, t } = useLanguage();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [priorityFilter, setPriorityFilter] = useState<"all" | TaskPriority>("all");

  // Dialog states
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  useEffect(() => {
    if (!user) return;
    fetchTasks();
  }, [user, filter]);

  const fetchTasks = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setError(null);
      // Fetch all tasks for count calculations, then filter for display
      const allTasks = await tasksApi.list(user.id, { status: "all", sort: "created" });
      setTasks(allTasks);
    } catch (err) {
      handleApiError(err, "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  const handleApiError = (err: any, defaultMessage: string) => {
    console.error(defaultMessage, err);
    setError(err instanceof Error ? err.message : defaultMessage);
  };

  const handleCreateTask = async (taskData: TaskCreateInput) => {
    if (!user) return;
    try {
      const newTask = await tasksApi.create(user.id, taskData);
      // Update local state with the new task, then re-fetch all tasks to ensure counts are accurate
      setTasks(prev => [newTask, ...prev]);
      setShowCreateDialog(false);
      fetchTasks(); // Re-fetch to update all counts and filtered view
    } catch (err) {
      handleApiError(err, "Failed to create task");
    }
  };

  const handleUpdateTask = async (taskData: Partial<TaskCreateInput>) => {
    if (!user || !editingTask) return;
    try {
      const updatedTask = await tasksApi.update(user.id, editingTask.id, taskData);
      setTasks(tasks.map(t => (t.id === editingTask.id ? updatedTask : t)));
      setEditingTask(null);
      fetchTasks(); // Re-fetch to update all counts and filtered view
    } catch (err) {
      handleApiError(err, "Failed to update task");
    }
  };

  const handleToggleComplete = async (task: Task) => {
    if (!user) return;
    try {
      const updatedTask = await tasksApi.toggleComplete(user.id, task.id);
      setTasks(tasks.map(t => (t.id === task.id ? updatedTask : t)));
      fetchTasks(); // Re-fetch to update all counts and filtered view
    } catch (err) {
      handleApiError(err, "Failed to update task status");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user) return;
    try {
      await tasksApi.delete(user.id, taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
      fetchTasks(); // Re-fetch to update all counts and filtered view
    } catch (err) {
      handleApiError(err, "Failed to delete task");
    }
  };

  // Task count calculations
  const overdueTaskCount = useMemo(() => {
    const now = new Date();
    return tasks.filter(task => !task.completed && task.due_date && new Date(task.due_date) < now).length;
  }, [tasks]);

  const highPriorityTaskCount = useMemo(() => {
    return tasks.filter(task => !task.completed && task.priority_id === 1).length; // 1 = High
  }, [tasks]);

  const otherTaskCount = useMemo(() => {
    const now = new Date();
    return tasks.filter(task => !task.completed && task.priority_id !== 1 && (!task.due_date || new Date(task.due_date) >= now)).length;
  }, [tasks]);

  const filteredTasks = tasks.filter(task => {
    // Filter by completion status
    if (filter === "pending" && task.completed) return false;
    if (filter === "completed" && !task.completed) return false;

    // Filter by priority
    if (priorityFilter !== "all") {
      const priorityId = PRIORITY_STRING_TO_ID[priorityFilter];
      if (task.priority_id !== priorityId) return false;
    }

    return true;
  });

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="spinner-lg"></div>
      </div>
    );
  }

  return (
    // UPDATED: Removed min-h-screen to let Layout handle height if needed, keeping gradient for style
    <main className="w-full min-h-[calc(100vh-4rem)] text-white relative bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#0c4a6e]">
      <nav className="glass py-3 px-4 sm:px-6 lg:px-8 flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <span className="text-xl font-bold text-white">Welcome, {user?.name || user?.email || "Test User"}!</span>
        </div>
        <div className="flex items-center gap-4">
          <LanguageSwitcher className="btn-secondary text-sm hover:bg-white/10" />
          <Link href="/chat" className="btn-secondary text-sm">
            {t('dashboard.newChat')}
          </Link>
          <Link href="/dashboard" className="btn-secondary text-sm">
            {t('dashboard.title')}
          </Link>
          <button onClick={signOut} className="btn-secondary text-sm !text-red-600 hover:!text-red-800">
            {t('common.signOut')}
          </button>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        
        {/* Dashboard Header with Task Counts */}
        <DashboardHeader
          userName={user?.name || "User"}
          overdueCount={overdueTaskCount}
          highPriorityCount={highPriorityTaskCount}
          otherCount={otherTaskCount}
          t={t}
        />

        {/* Error Message Display */}
        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
        
        {/* UPDATED: Cleaned up Toolbar */}
        <Toolbar
          filter={filter}
          setFilter={setFilter}
          priorityFilter={priorityFilter}
          setPriorityFilter={setPriorityFilter}
          onNewTask={() => setShowCreateDialog(true)}
          t={t}
        />

        {loading ? <LoadingSpinner t={t} /> : (
          filteredTasks.length === 0 ? (
            <EmptyState onNewTask={() => setShowCreateDialog(true)} t={t} />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-in">
              {filteredTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onEdit={() => setEditingTask(task)}
                  onDelete={handleDeleteTask}
                  t={t}
                />
              ))}
            </div>
          )
        )}
      </div>

      <TaskDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSave={handleCreateTask}
        title="Create New Task"
        t={t}
      />

      <TaskDialog
        isOpen={!!editingTask}
        onClose={() => setEditingTask(null)}
        onSave={handleUpdateTask}
        task={editingTask}
        title="Edit Task"
        t={t}
      />

      {/* Voice Commands Button */}
      <VoiceButton
        language={language === 'ur' ? 'ur-PK' : 'en-US'}
        onCreateTask={(title) => handleCreateTask({ title, description: "", priority_id: 2 })}
        onCompleteTask={(taskId) => {
          const task = tasks.find(t => t.id === taskId);
          if (task) handleToggleComplete(task);
        }}
        onDeleteTask={(taskId) => handleDeleteTask(taskId)}
        onListTasks={() => setFilter('all')}
      />

      <style jsx global>{`
        .btn-secondary {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          font-weight: 500;
          transition: all 0.2s;
        }
        .btn-secondary:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.3);
        }
        .spinner-lg {
          width: 50px; height: 50px; border: 4px solid rgba(255, 255, 255, 0.2);
          border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </main>
  );
}

// ============================================
// SUB-COMPONENTS
// ============================================

const DashboardHeader = ({ userName, overdueCount, highPriorityCount, otherCount, t }: { userName: string; overdueCount: number; highPriorityCount: number; otherCount: number; t: (key: string) => string }) => {
  return (
    <header className="mb-8 p-6 glass rounded-2xl shadow-lg flex flex-col md:flex-row justify-between items-center animate-fade-in">
      <div className="text-center md:text-left mb-4 md:mb-0">
        <h1 className="text-3xl font-bold gradient-text">{t('common.welcome')}, {userName}!</h1>
        <p className="text-gray-400 mt-1">{t('dashboard.overviewMessage')}</p>
      </div>
      <div className="flex flex-wrap justify-center md:justify-end gap-4 w-full md:w-auto">
        <div className="card px-5 py-3 text-center">
          <p className="text-xl font-bold text-red-400">{overdueCount}</p>
          <p className="text-sm text-gray-400">{t('dashboard.overdue')}</p>
        </div>
        <div className="card px-5 py-3 text-center">
          <p className="text-xl font-bold text-orange-400">{highPriorityCount}</p>
          <p className="text-sm text-gray-400">{t('dashboard.highPriority')}</p>
        </div>
        <div className="card px-5 py-3 text-center">
          <p className="text-xl font-bold text-cyan-400">{otherCount}</p>
          <p className="text-sm text-gray-400">{t('dashboard.otherTasks')}</p>
        </div>
      </div>
    </header>
  );
};

const ErrorMessage = ({ message, onDismiss }: { message: string, onDismiss: () => void }) => (
  <div className="mb-6 rounded-lg bg-red-900/50 p-4 border border-red-700 flex justify-between items-center animate-fade-in">
    <p className="text-sm text-red-300">{message}</p>
    <button onClick={onDismiss} className="text-red-300 hover:text-red-100">&times;</button>
  </div>
);

// UPDATED: Completely refactored Toolbar for better alignment
const Toolbar = ({ filter, setFilter, priorityFilter, setPriorityFilter, onNewTask, t }: any) => {
  const statusFilters = ["all", "pending", "completed"] as const;
  const priorityFilters = ["all", "low", "normal", "high"] as const;

  return (
    <div className="mb-8 flex flex-col md:flex-row gap-4 justify-between items-center w-full">
      {/* Left Side: Filter Groups */}
      <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">

        {/* Status Filter Group */}
        <div className="glass p-1 rounded-lg flex gap-1">
          {statusFilters.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${filter === f ? "bg-indigo-600 text-white shadow-md" : "text-gray-300 hover:bg-white/10"}`}
            >
              {t(`tasks.${f}`)}
            </button>
          ))}
        </div>

        {/* Priority Filter Group */}
        <div className="glass p-1 rounded-lg flex gap-1">
          {priorityFilters.map(p => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-all ${priorityFilter === p ? (p === "all" ? "bg-gray-500" : `${PRIORITY_STYLES[p].badge} bg-opacity-100`) : "text-gray-300 hover:bg-white/10"}`}
            >
              {p === "all" ? t('tasks.all') : t(`priorities.${p}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Right Side: Action Button */}
      <button
        onClick={onNewTask}
        className="w-full md:w-auto btn-primary hover-scale flex justify-center items-center py-2.5 px-6"
      >
        {t('tasks.newTask')}
      </button>
    </div>
  );
};

const LoadingSpinner = ({ t }: { t: (key: string) => string }) => (
  <div className="text-center py-12">
    <div className="inline-block spinner-lg"></div>
    <p className="text-gray-400 mt-4">{t('tasks.loadingTasks')}</p>
  </div>
);

const EmptyState = ({ onNewTask, t }: { onNewTask: () => void; t: (key: string) => string }) => (
  <div className="text-center py-16 glass-dark rounded-2xl shadow-lg border border-white/10 animate-scale-in">
    <div className="text-6xl mb-4 animate-bounce">📝</div>
    <h3 className="text-2xl font-semibold text-white mb-2">{t('tasks.noTasks')}</h3>
    <p className="text-gray-400 mb-6">{t('tasks.noTasksMessage')}</p>
    <button onClick={onNewTask} className="btn-primary hover-scale py-2.5 px-6">{t('tasks.createTask')}</button>
  </div>
);

const TaskCard = ({ task, onToggleComplete, onEdit, onDelete, t }: { task: Task, onToggleComplete: (task: Task) => void, onEdit: (task: Task) => void, onDelete: (id: number) => void, t: (key: string) => string }) => {
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return <span className="font-medium text-red-400">{t('tasks.overdue')}</span>;
    if (diffDays === 0) return <span className="font-medium text-orange-400">{t('tasks.today')}</span>;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const priority = getPriorityString(task.priority_id);

  return (
    <div className={`glass-dark rounded-xl p-5 border-l-4 hover:shadow-2xl transition-all duration-300 flex flex-col ${task.completed ? "border-green-500 bg-white/5 opacity-75" : PRIORITY_STYLES[priority].border}`}>
      <div className="flex items-start gap-4 flex-1">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggleComplete(task)}
          className="mt-1 h-5 w-5 text-indigo-500 bg-transparent border-gray-600 rounded focus:ring-indigo-500 cursor-pointer"
        />
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-lg ${task.completed ? "line-through text-gray-500" : "text-white"}`}>{task.title}</h3>
          {task.description && <p className="text-sm text-gray-400 mt-1">{task.description}</p>}
          <div className="flex flex-wrap items-center gap-3 mt-3 text-xs">
            <span className={`inline-flex items-center px-3 py-1 rounded-full font-medium ${PRIORITY_STYLES[priority].badge}`}>
              {t(`priorities.${priority}`)}
            </span>
            {task.due_date && <span className="text-gray-400">📅 {t('tasks.due')}: {formatDate(task.due_date)}</span>}
            <span className="text-gray-500">{t('tasks.created')}: {new Date(task.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      {/* Action buttons at the bottom */}
      <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-700/50">
        <button
          onClick={() => onToggleComplete(task)}
          className={`btn-secondary text-xs px-3 py-1.5 flex-1 ${task.completed ? "!border-yellow-600/50 hover:!bg-yellow-600/30 text-yellow-300" : "!border-green-600/50 hover:!bg-green-600/30 text-green-300"}`}
        >
          {task.completed ? t('tasks.markIncomplete') : t('tasks.markComplete')}
        </button>
        <button onClick={() => onEdit(task)} className="btn-secondary text-xs px-3 py-1.5 flex-1">{t('common.edit')}</button>
        <button onClick={() => { if (confirm(t('tasks.areYouSure'))) onDelete(task.id); }} className="btn-secondary text-xs px-3 py-1.5 flex-1 !border-red-800/50 hover:!bg-red-800/50 text-red-300">{t('common.delete')}</button>
      </div>
    </div>
  );
};

const TaskDialog = ({ isOpen, onClose, onSave, task, title, t }: { isOpen: boolean, onClose: () => void, onSave: (data: any) => Promise<void>, task?: Task | null, title: string, t: (key: string) => string }) => {
  const [formData, setFormData] = useState({ title: "", description: "", priority_id: 2, due_date: "" }); // 2 = Normal
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        priority_id: task.priority_id || 2, // Default to Normal if null
        due_date: task.due_date ? task.due_date.split('T')[0] : ""
      });
    } else {
      setFormData({ title: "", description: "", priority_id: 2, due_date: "" }); // 2 = Normal
    }
  }, [task, isOpen]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    // Convert priority_id from string to number
    const processedValue = name === "priority_id" ? parseInt(value, 10) : value;
    setFormData({ ...formData, [name]: processedValue });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    // Clean formData: convert to proper backend format
    const cleanedData: any = {};

    // Always include title (required)
    cleanedData.title = formData.title;

    // For description, allow empty string (to clear description)
    if (formData.description !== undefined) {
      cleanedData.description = formData.description || null;
    }

    // Include priority_id
    if (formData.priority_id) {
      cleanedData.priority_id = formData.priority_id;
    }

    // Convert due_date to ISO 8601 datetime format or null
    if (formData.due_date) {
      cleanedData.due_date = `${formData.due_date}T00:00:00Z`;
    } else if (task) {
      // If editing and due_date is empty, explicitly set to null to clear it
      cleanedData.due_date = null;
    }

    await onSave(cleanedData);
    setIsSaving(false);
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0">
          <div className="fixed inset-0 bg-blue-900 bg-opacity-30 backdrop-blur-sm" />
        </Transition.Child>
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-200" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl glass-dark border border-white/10 p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title as="h3" className="text-2xl font-bold text-white mb-6">{task ? t('tasks.editTask') : t('tasks.createNewTask')}</Dialog.Title>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <FormInput name="title" label={`${t('tasks.taskTitle')} ${t('tasks.required')}`} value={formData.title} onChange={handleChange} required />
                  <FormTextArea name="description" label={t('tasks.taskDescription')} value={formData.description} onChange={handleChange} />
                  <FormSelect name="priority_id" label={t('tasks.priority')} value={formData.priority_id} onChange={handleChange}>
                    <option value="3">🔵 {t('priorities.low')}</option>
                    <option value="2">🟡 {t('priorities.normal')}</option>
                    <option value="1">🔴 {t('priorities.high')}</option>
                  </FormSelect>
                  <FormInput name="due_date" label={t('tasks.dueDate')} type="date" value={formData.due_date} onChange={handleChange} min={new Date().toISOString().split('T')[0]} />
                  <div className="flex gap-3 pt-4">
                    <button type="button" onClick={onClose} className="flex-1 btn-secondary" disabled={isSaving}>{t('common.cancel')}</button>
                    <button type="submit" className="flex-1 btn-primary" disabled={isSaving}>{isSaving ? t('tasks.saving') : t('common.save')}</button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

// Form components
const FormInput = (props: any) => (
  <div>
    <label htmlFor={props.name} className="block text-sm font-medium text-gray-300 mb-2">{props.label}</label>
    <input {...props} id={props.name} className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
  </div>
);
const FormTextArea = (props: any) => (
  <div>
    <label htmlFor={props.name} className="block text-sm font-medium text-gray-300 mb-2">{props.label}</label>
    <textarea {...props} id={props.name} rows={3} className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
  </div>
);
const FormSelect = (props: any) => (
  <div>
    <label htmlFor={props.name} className="block text-sm font-medium text-gray-300 mb-2">{props.label}</label>
    <select {...props} id={props.name} className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
  </div>
);