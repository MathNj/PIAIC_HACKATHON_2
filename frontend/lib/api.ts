/**
 * API client with automatic JWT token injection.
 *
 * Provides helper methods (get, post, put, patch, delete) that automatically:
 * - Attach Authorization Bearer header
 * - Handle 401 errors by redirecting to login
 * - Handle 422 validation errors from FastAPI
 * - Parse JSON responses
 */

import { getJWT, signOut } from "./auth";
import type { ApiError, ValidationError } from "./types";

// Production backend URL - stable domain that won't change with deployments
const API_BASE_URL = process.env.NODE_ENV === "production"
  ? "https://backend-mathnjs-projects.vercel.app"
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Make an authenticated API request.
 *
 * @param path - API endpoint path (e.g., "/api/user-id/tasks")
 * @param options - Fetch options
 * @returns Parsed JSON response
 */
async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = getJWT();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Attach JWT token if available
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
    credentials: "include",
  };

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, config);

    // Handle 401 Unauthorized (expired/invalid token)
    if (response.status === 401) {
      console.warn("Unauthorized request, session expired");

      // Clear session and redirect to login
      signOut();

      // Redirect to login page
      if (typeof window !== "undefined") {
        window.location.href = "/login?session_expired=true";
      }

      return Promise.reject(new Error("Unauthorized - session expired"));
    }

    // Handle 403 Forbidden (user_id mismatch)
    if (response.status === 403) {
      const error = await response.json().catch(() => ({ detail: "Forbidden" }));
      throw new Error(error.detail || "Access forbidden");
    }

    // Handle 404 Not Found
    if (response.status === 404) {
      const error = await response.json().catch(() => ({ detail: "Not found" }));
      throw new Error(error.detail || "Resource not found");
    }

    // Handle 422 Unprocessable Entity (validation errors from FastAPI)
    if (response.status === 422) {
      const errorData = await response.json().catch(() => ({ detail: "Validation failed" }));

      // FastAPI returns validation errors in detail array
      if (Array.isArray(errorData.detail)) {
        const validationErrors = errorData.detail as ValidationError[];

        // Format validation errors into readable message
        const errorMessages = validationErrors.map((err) => {
          const field = err.loc.slice(1).join(".");  // Remove "body" prefix
          return `${field}: ${err.msg}`;
        }).join(", ");

        const apiError: ApiError = {
          status: 422,
          message: errorMessages || "Validation failed",
          detail: validationErrors,
        };

        throw apiError;
      }

      throw new Error(errorData.detail || "Validation failed");
    }

    // Handle 500+ Server Errors
    if (response.status >= 500) {
      const error = await response.json().catch(() => ({ detail: "Server error" }));
      const apiError: ApiError = {
        status: response.status,
        message: error.detail || "Internal server error",
      };
      throw apiError;
    }

    // Handle other HTTP errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle 204 No Content (e.g., DELETE responses)
    if (response.status === 204) {
      return {} as T;
    }

    // Parse JSON response
    return response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

/**
 * API helper methods
 */
export const api = {
  /**
   * GET request
   *
   * @param path - API endpoint path
   * @returns Promise with parsed response
   */
  get: <T = any>(path: string): Promise<T> => {
    return request<T>(path, { method: "GET" });
  },

  /**
   * POST request
   *
   * @param path - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @returns Promise with parsed response
   */
  post: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PUT request
   *
   * @param path - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @returns Promise with parsed response
   */
  put: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PATCH request
   *
   * @param path - API endpoint path
   * @param body - Request body (will be JSON stringified)
   * @returns Promise with parsed response
   */
  patch: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * DELETE request
   *
   * @param path - API endpoint path
   * @returns Promise with parsed response (usually empty for 204)
   */
  delete: <T = any>(path: string): Promise<T> => {
    return request<T>(path, { method: "DELETE" });
  },
};
