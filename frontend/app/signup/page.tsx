"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signUp, signIn } from "@/lib/auth";

export default function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
      setError("Password must include uppercase, lowercase, and a number");
      return;
    }

    setLoading(true);
    try {
      await signUp(email, name, password);
      await signIn(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred during signup");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900 relative overflow-hidden flex items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-5xl lg:flex rounded-3xl overflow-hidden glass shadow-2xl"> {/* Wider container, flex for columns */}
        {/* Left Section: Branding & Welcome Message */}
        <div className="lg:w-1/2 p-8 lg:p-12 flex flex-col justify-center items-center text-center bg-gradient-to-br from-indigo-700 to-purple-700 text-white">
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-6 shadow-lg">
            <span className="text-indigo-600 font-bold text-3xl">✓</span>
          </div>
          <h1 className="text-4xl font-extrabold mb-4 animate-fade-in">TaskFlow</h1>
          <p className="text-indigo-100 text-lg mb-6 max-w-sm animate-slide-in-right">
            Your intelligent task companion with AI chat, priority management, and seamless collaboration.
          </p>
          <div className="flex gap-3 animate-slide-in-left">
            <Link href="/login" className="btn-secondary bg-white text-indigo-700 px-6 py-3 hover:bg-gray-100">
              Sign In
            </Link>
          </div>
        </div>

        {/* Right Section: Signup Form */}
        <div className="lg:w-1/2 p-8 lg:p-12 bg-gray-800/50 backdrop-blur-md flex flex-col justify-center">
          <h2 className="text-3xl font-bold text-white mb-6 text-center lg:text-left">Create Your Account</h2>
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="••••••••"
              />
              <p className="mt-2 text-xs text-gray-400">
                Minimum 8 characters, with uppercase, lowercase, and a number.
              </p>
            </div>
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="Re-enter your password"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-900/50 p-3 border border-red-700 text-center">
                <p className="text-sm text-red-300">{error}</p>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary hover-scale flex justify-center items-center py-3 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
              >
                {loading ? (
                  <>
                    <div className="spinner-sm mr-2"></div>
                    <span>Creating Account...</span>
                  </>
                ) : (
                  "Create Account"
                )}
              </button>
            </div>
          </form>

          <div className="text-center mt-6">
            <p className="text-sm text-gray-400">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-medium text-indigo-400 hover:text-indigo-300"
              >
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Spinner for loading state, adapted for dark mode */}
      <style jsx>{`
        .spinner-sm {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.2);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </main>
  );
}
