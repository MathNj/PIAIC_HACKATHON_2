"use client";

/**
 * AuthProvider - Global authentication context provider
 *
 * Responsibilities:
 * - Wrap entire app in authentication context
 * - Expose session/user through context
 * - Redirect user to /login if session missing on protected routes
 * - Provide logout functionality
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getSession, signOut as authSignOut } from "@/lib/auth";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signOut: () => {},
});

/**
 * Hook to access auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component
 *
 * Wraps the application and provides authentication state.
 * Automatically redirects to /login for protected routes if user is not authenticated.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication on mount and route changes
    const checkAuth = () => {
      const session = getSession();

      if (session) {
        setUser(session);
        setLoading(false);
      } else {
        setUser(null);
        setLoading(false);

        // Public routes that don't require authentication
        const publicRoutes = ["/", "/login", "/signup"];
        const isPublicRoute = publicRoutes.some(route => pathname === route);

        // Redirect to login if on protected route
        if (!isPublicRoute && typeof window !== "undefined") {
          router.push("/login");
        }
      }
    };

    checkAuth();

    // Listen for storage events (logout in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "jwt_token" || e.key === "user") {
        checkAuth();
      }
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [pathname, router]);

  const signOut = () => {
    authSignOut();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
