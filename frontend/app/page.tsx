"use client";

/**
 * Modern Landing Page with Hero Section
 *
 * Features:
 * - Animated hero section with gradients
 * - Floating elements
 * - Professional design
 * - Interactive buttons
 * - Feature highlights
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import Link from "next/link";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-black text-gray-300">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20 lg:py-32">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-fade-in">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium text-gray-200">AI-Powered Task Management</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl lg:text-7xl font-extrabold mb-6 animate-slide-in-left">
            <span className="gradient-text">Manage Tasks</span>
            <br />
            <span className="text-white">Effortlessly</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl lg:text-2xl text-gray-400 mb-12 max-w-2xl mx-auto animate-slide-in-right">
            Your intelligent task companion with AI chat, priority management, and seamless collaboration.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 stagger-animation">
            <Link
              href="/signup"
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 via-indigo-700 to-purple-800 text-white rounded-xl font-semibold text-lg hover:shadow-2xl transition-all hover:-translate-y-1 hover-glow"
            >
              Start Free Trial →
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-4 bg-gray-700 text-white rounded-xl font-semibold text-lg border-2 border-gray-600 hover:border-blue-600 hover:shadow-lg transition-all hover:-translate-y-1"
            >
              Watch Demo
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto stagger-animation">
            <div className="text-center">
              <div className="text-3xl lg:text-4xl font-bold gradient-text mb-2">10K+</div>
              <div className="text-sm text-gray-400">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl lg:text-4xl font-bold gradient-text mb-2">99.9%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl lg:text-4xl font-bold gradient-text mb-2">4.9★</div>
              <div className="text-sm text-gray-400">User Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Everything you need to <span className="gradient-text">stay productive</span>
          </h2>
          <p className="text-xl text-gray-400">
            Powerful features designed for modern teams
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 stagger-animation">
          {/* Feature 1 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">AI Assistant</h3>
            <p className="text-gray-300">
              Chat with AI to create tasks, set priorities, and manage your workflow using natural language.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-pink-600 to-red-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Smart Priorities</h3>
            <p className="text-gray-300">
              Auto-detect urgency from keywords and get intelligent task prioritization suggestions.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-teal-600 to-cyan-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">📅</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Natural Dates</h3>
            <p className="text-gray-300">
              Type "tomorrow" or "next week" - our AI understands and converts temporal expressions.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">🔒</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Secure & Private</h3>
            <p className="text-gray-300">
              Bank-grade encryption with JWT authentication. Your data belongs to you.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-orange-600 to-yellow-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">💬</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Persistent Chat</h3>
            <p className="text-gray-300">
              All conversations are saved. Resume your chat context anytime, anywhere.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="card-glass hover-lift p-8 bg-gray-800/60 border border-gray-700 rounded-xl">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl flex items-center justify-center mb-4 hover-scale">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Analytics</h3>
            <p className="text-gray-300">
              Track completion rates, identify patterns, and optimize your productivity.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="relative overflow-hidden rounded-3xl">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-indigo-800 to-purple-900 opacity-90"></div>
          <div className="relative px-8 py-20 lg:px-16 text-center text-white">
            <h2 className="text-4xl lg:text-5xl font-bold mb-6 animate-fade-in">
              Ready to boost your productivity?
            </h2>
            <p className="text-xl mb-10 opacity-90 max-w-2xl mx-auto animate-fade-in">
              Join thousands of users who are already managing their tasks smarter, not harder.
            </p>
            <Link
              href="/signup"
              className="inline-block px-10 py-5 bg-gray-100 text-blue-800 rounded-xl font-bold text-lg hover:shadow-2xl transition-all hover:-translate-y-1 animate-scale-in"
            >
              Get Started - It's Free
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
