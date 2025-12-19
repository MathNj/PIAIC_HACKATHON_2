/**
 * TypeScript type definitions for Task API.
 *
 * These types match the backend Pydantic schemas:
 * - TaskRead (response model)
 * - TaskCreate (request body for POST)
 * - TaskUpdate (request body for PUT)
 */

/**
 * Task priority levels.
 */
export type TaskPriority = "low" | "normal" | "high";

/**
 * Task model (matches backend TaskRead schema).
 *
 * Represents a complete task with all database fields.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string | null;
  completed: boolean;
  priority_id?: number | null;  // 1=High, 2=Medium, 3=Low, null=No priority
  due_date?: string | null;  // ISO 8601 datetime string
  is_recurring: boolean;
  recurrence_pattern?: string | null;
  tag_ids: number[];
  created_at: string;  // ISO 8601 datetime string
  updated_at: string;  // ISO 8601 datetime string
}

/**
 * Input for creating a new task (matches backend TaskCreate schema).
 *
 * user_id is extracted from JWT, not provided in request body.
 */
export interface TaskCreateInput {
  title: string;
  description?: string;
  priority_id?: number | null;  // 1=High, 2=Medium, 3=Low
  due_date?: string;  // ISO 8601 datetime string
  is_recurring?: boolean;
  recurrence_pattern?: string;
  tag_ids?: number[];
}

/**
 * Input for updating an existing task (matches backend TaskUpdate schema).
 *
 * All fields are optional for partial updates.
 */
export interface TaskUpdateInput {
  title?: string;
  description?: string;
  completed?: boolean;
  priority_id?: number | null;
  due_date?: string;  // ISO 8601 datetime string
  is_recurring?: boolean;
  recurrence_pattern?: string;
  tag_ids?: number[];
}

/**
 * Query parameters for listing tasks.
 */
export interface TaskListParams {
  status?: "all" | "pending" | "completed";
  sort?: "created" | "updated" | "title";
}

/**
 * API error structure.
 */
export interface ApiError {
  status: number;
  message: string;
  detail?: any;  // FastAPI validation errors or custom error details
}

/**
 * FastAPI validation error detail (422 responses).
 */
export interface ValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: any;
}

/**
 * User model (for authentication context).
 */
export interface User {
  id: string;
  email: string;
  name: string;
}

/**
 * Authentication response (login/signup).
 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
