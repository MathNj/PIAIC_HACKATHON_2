import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Allow ACME challenge requests to pass through (for Let's Encrypt SSL)
  if (request.nextUrl.pathname.startsWith('/.well-known/acme-challenge/')) {
    // This path should be handled by nginx-ingress/cert-manager
    // Don't process it with Next.js
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
