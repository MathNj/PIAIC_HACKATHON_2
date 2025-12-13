/**
 * Authentication utilities for JWT-based authentication.
 *
 * This module provides authentication functions that integrate with the backend's
 * JWT validation. Tokens are stored in localStorage for persistence.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://backend.testservers.online";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Sign in with email and password.
 *
 * @param email - User's email address
 * @param password - User's password
 * @returns Promise with authentication result
 */
export async function signIn(email: string, password: string): Promise<AuthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
      // credentials: "include", // Removed - not needed with JWT in Authorization header
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Invalid credentials" }));
      throw new Error(error.detail || "Invalid credentials");
    }

    const data: AuthResponse = await response.json();

    // Store token and user in localStorage
    if (data.access_token) {
      localStorage.setItem("jwt_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    console.error("Sign in error:", error);
    throw error;
  }
}

/**
 * Sign up a new user.
 *
 * @param email - User's email address
 * @param name - User's display name
 * @param password - User's password
 * @returns Promise with signup result
 */
export async function signUp(email: string, name: string, password: string): Promise<User> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, name, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Signup failed" }));
      throw new Error(error.detail || "Signup failed");
    }

    const user: User = await response.json();
    return user;
  } catch (error) {
    console.error("Sign up error:", error);
    throw error;
  }
}

/**
 * Sign out the current user.
 * Clears session and JWT token from localStorage.
 */
export function signOut(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("user");
  }
}

/**
 * Get the current session/user.
 *
 * @returns User object if authenticated, null otherwise
 */
export function getSession(): User | null {
  if (typeof window === "undefined") return null;

  const userStr = localStorage.getItem("user");
  if (!userStr) return null;

  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * Get the current JWT token.
 *
 * @returns JWT token string or null
 */
export function getJWT(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jwt_token");
}

/**
 * Check if user is authenticated.
 *
 * @returns true if user has a valid JWT token
 */
export function isAuthenticated(): boolean {
  return getJWT() !== null;
}

/**
 * Get the current user.
 *
 * @returns User object or null
 */
export function getCurrentUser(): User | null {
  return getSession();
}
