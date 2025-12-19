// Middleware for locale detection and routing
// Copy this file to: frontend/src/middleware.ts

import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // Supported locales
  locales: ['en', 'ur'],

  // Default locale (used when no locale is specified in URL)
  defaultLocale: 'en',

  // Enable automatic locale detection based on Accept-Language header
  localeDetection: true,

  // Locale prefix strategy:
  // - 'always': Always show locale prefix (/en/tasks, /ur/tasks)
  // - 'as-needed': Show prefix only for non-default locale (/tasks for en, /ur/tasks for ur)
  // - 'never': Never show prefix (not recommended for bilingual apps)
  localePrefix: 'as-needed'
});

export const config = {
  // Match all pathnames except:
  // - API routes (/api/*)
  // - Next.js internals (/_next/*)
  // - Vercel internals (/_vercel/*)
  // - Static files (files with extensions like .png, .jpg, .css, etc.)
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
