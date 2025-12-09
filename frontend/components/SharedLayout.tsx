"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function SharedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { user, loading, signOut } = useAuth();
  const pathname = usePathname();

  // FIX: Detect if we are on the dashboard
  const isDashboardOrChat = pathname?.startsWith("/dashboard") || pathname?.startsWith("/chat");

  // If on dashboard or chat page, render ONLY the children (these pages have their own layout/header)
  // This removes the duplicate navbar and footer from these views
  if (isDashboardOrChat) {
    return <>{children}</>;
  }

  return (
    <>
      <nav className="sticky top-0 z-40 w-full glass border-b border-gray-200 shadow-lg py-3"> {/* Changed glass-dark to glass, border-white/10 to border-gray-200 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          {/* Branding */}
          <Link href="/" className="flex items-center gap-2 transition-all hover:opacity-80">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center animate-glow">
              <span className="text-white font-bold text-xl">✓</span>
            </div>
            <span className="text-2xl font-bold gradient-text hidden sm:block">TaskFlow</span> {/* text-gray-900 removed, gradient-text handles color */}
          </Link>

          {/* Navigation Links / Auth Actions */}
          <div className="flex items-center gap-4">
            {!loading && !user && (
              <>
                <Link
                  href="/login"
                  className="px-5 py-2.5 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors rounded-lg hover:bg-white/50"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="btn-primary hover-scale text-sm"
                >
                  Get Started
                </Link>
              </>
            )}
            {!loading && user && (
              <>
               <Link href="/dashboard" className="btn-secondary text-sm"> {/* Changed btn-primary to btn-secondary for dashboard link */}
                 Dashboard
               </Link>
               <Link href="/chat" className="btn-secondary text-sm">
                 Chat
               </Link>
               <button onClick={signOut} className="btn-secondary text-sm !text-red-600 hover:!text-red-800"> {/* Added logout button */}
                 Logout
               </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {children}

      {/* Footer - Only shows on public pages now */}
      <footer className="relative z-10 border-t border-gray-200 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg"></div>
                <span className="text-xl font-bold gradient-text">TaskFlow</span>
              </div>
              <p className="text-sm text-gray-600">
                AI-powered task management for modern teams.
              </p>
            </div>
            {/* ... rest of footer links ... */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-indigo-600 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-indigo-600 transition-colors">Pricing</a></li>
              </ul>
            </div>
            {/* ... shortened for brevity, keep your original footer columns here ... */}
          </div>
          <div className="pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            <p>&copy; 2025 TaskFlow. Built with ❤️ for Hackathon II.</p>
          </div>
        </div>
      </footer>
    </>
  );
}