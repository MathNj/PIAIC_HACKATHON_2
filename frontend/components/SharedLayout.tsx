"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import FloatingChatbot from "@/components/FloatingChatbot";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function SharedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { user, loading, signOut } = useAuth();
  const pathname = usePathname();
  const { t } = useLanguage();

  // FIX: Detect if we are on the dashboard
  const isDashboardOrChat = pathname?.startsWith("/dashboard") || pathname?.startsWith("/chat");

  // If on dashboard or chat page, render ONLY the children (these pages have their own layout/header)
  // This removes the duplicate navbar and footer from these views
  if (isDashboardOrChat) {
    return (
      <>
        {children}
        <FloatingChatbot />
      </>
    );
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
            <span className="text-2xl font-bold gradient-text hidden sm:block">{t('common.appName')}</span> {/* text-gray-900 removed, gradient-text handles color */}
          </Link>

          {/* Navigation Links / Auth Actions */}
          <div className="flex items-center gap-4">
            {!loading && !user && (
              <>
                <Link
                  href="/login"
                  className="px-5 py-2.5 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors rounded-lg hover:bg-white/50"
                >
                  {t('common.signIn')}
                </Link>
                <Link
                  href="/signup"
                  className="btn-primary hover-scale text-sm"
                >
                  {t('common.signUp')}
                </Link>
              </>
            )}
            {!loading && user && (
              <>
               <Link href="/dashboard" className="btn-secondary text-sm"> {/* Changed btn-primary to btn-secondary for dashboard link */}
                 {t('dashboard.title')}
               </Link>
               <Link href="/chat" className="btn-secondary text-sm">
                 {t('dashboard.newChat')}
               </Link>
               <button onClick={signOut} className="btn-secondary text-sm !text-red-600 hover:!text-red-800"> {/* Added logout button */}
                 {t('common.logout')}
               </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {children}

      {/* Floating Chatbot - Shows on all pages when logged in */}
      <FloatingChatbot />

      {/* Footer - Only shows on public pages now */}
      <footer className="relative z-10 bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg animate-glow"></div>
                <span className="text-xl font-bold gradient-text">{t('common.appName')}</span>
              </div>
              <p className="text-sm text-gray-400">
                {t('landing.footerTagline')}
              </p>
            </div>
            {/* ... rest of footer links ... */}
            <div>
              <h4 className="font-semibold text-white mb-4">{t('landing.footerProduct')}</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-indigo-400 transition-colors">{t('landing.footerFeatures')}</a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors">{t('landing.footerPricing')}</a></li>
              </ul>
            </div>
            {/* ... shortened for brevity, keep your original footer columns here ... */}
          </div>
          <div className="pt-8 border-t border-white/10 text-center">
            <p className="text-sm bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-semibold">
              {t('landing.footerCopyright')}
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}