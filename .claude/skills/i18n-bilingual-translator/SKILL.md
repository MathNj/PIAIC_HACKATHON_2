---
name: i18n-bilingual-translator
description: Implement English/Urdu bilingual internationalization (i18n) in Next.js applications with RTL support. Use when implementing: (1) English/Urdu language switching, (2) RTL (right-to-left) layout for Urdu text, (3) Locale-based routing and middleware, (4) Translation management with next-intl, (5) Urdu typography with Noto Nastaliq font, (6) Bidirectional text handling, or (7) Language switcher UI components. This skill provides complete setup for App Router with server/client component translations, RTL styles, and production-ready bilingual support.
---

# i18n Bilingual Translator (English/Urdu)

This skill guides you through implementing comprehensive bilingual i18n support for English and Urdu in Next.js applications using next-intl.

## Architecture Overview

**next-intl approach** (recommended for Next.js App Router):
- **Server Components**: Use `getTranslations()` for server-side translation
- **Client Components**: Use `useTranslations()` hook for client-side translation
- **Locale Detection**: Middleware-based automatic locale detection
- **RTL Support**: Automatic direction switching (LTR for English, RTL for Urdu)

## Quick Start Workflow

### Step 1: Review Implementation Guide

Read the comprehensive implementation guide:
```bash
.claude/skills/i18n-bilingual-translator/references/i18n-integration-guide.md
```

This guide provides:
- Complete next-intl setup with App Router
- Translation file structure and organization
- RTL styling and typography
- Locale middleware configuration
- Testing procedures

### Step 2: Install Dependencies

```bash
cd frontend
npm install next-intl
npm install tailwindcss-rtl  # For RTL Tailwind utilities
```

### Step 3: Copy Configuration Files

**i18n config** - Copy `assets/i18n.ts` to `frontend/i18n.ts`:
```typescript
import {getRequestConfig} from 'next-intl/server';

export default getRequestConfig(async ({locale}) => ({
  messages: (await import(`./locales/${locale}.json`)).default
}));
```

**Middleware** - Copy `assets/middleware.ts` to `frontend/src/middleware.ts`:
- Configures locale detection and routing
- Supports 'en' (English) and 'ur' (Urdu)
- Uses 'as-needed' prefix strategy

**Update Next.js config** in `frontend/next.config.js`:
```javascript
const createNextIntlPlugin = require('next-intl/plugin');
const withNextIntl = createNextIntlPlugin('./i18n.ts');

module.exports = withNextIntl({
  // Your existing Next.js config
});
```

### Step 4: Copy Translation Files

1. **English translations** - Copy `assets/locales/en.json` to `frontend/locales/en.json`
   - Contains translations for: common, navigation, tasks, chat, auth, settings, errors
   - Organized by feature namespace

2. **Urdu translations** - Copy `assets/locales/ur.json` to `frontend/locales/ur.json`
   - Complete Urdu translations matching English structure
   - Professional Urdu terminology

### Step 5: Copy RTL Styles

**RTL stylesheet** - Copy `assets/styles/rtl.css` to `frontend/src/styles/rtl.css`:
- Urdu typography with Noto Nastaliq Urdu font
- RTL layout fixes for Tailwind utilities
- Direction-aware component styles
- Code block LTR preservation

**Import in layout**: `import '@/styles/rtl.css'`

### Step 6: Update App Router Structure

**Create locale-based layout** - Move `app/layout.tsx` to `app/[locale]/layout.tsx`:

```typescript
import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {Noto_Nastaliq_Urdu} from 'next/font/google';
import '@/styles/rtl.css';

const urduFont = Noto_Nastaliq_Urdu({
  weight: ['400', '700'],
  subsets: ['arabic'],
  variable: '--font-urdu',
});

export default async function LocaleLayout({
  children,
  params: {locale}
}: {
  children: React.ReactNode;
  params: {locale: string};
}) {
  const messages = await getMessages();
  const direction = locale === 'ur' ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={direction} className={locale === 'ur' ? urduFont.variable : ''}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

**Move all pages to locale directory**:
- `app/page.tsx` → `app/[locale]/page.tsx`
- `app/tasks/page.tsx` → `app/[locale]/tasks/page.tsx`
- `app/chat/page.tsx` → `app/[locale]/chat/page.tsx`

### Step 7: Add Language Switcher

**Copy component** - Copy `assets/components/LanguageSwitcher.tsx` to `frontend/src/components/LanguageSwitcher.tsx`

**Three variants provided**:
1. **Button variant**: Side-by-side buttons (default)
2. **Dropdown variant**: Compact select dropdown
3. **Flag variant**: Buttons with flag emojis (🇬🇧/🇵🇰)

**Use in navigation**:
```typescript
import LanguageSwitcher from '@/components/LanguageSwitcher';

export default function Navigation() {
  return (
    <nav>
      {/* Your navigation items */}
      <LanguageSwitcher />
    </nav>
  );
}
```

### Step 8: Use Translations in Components

**Server components**:
```typescript
import {useTranslations} from 'next-intl';

export default function TasksPage() {
  const t = useTranslations('tasks');

  return (
    <div>
      <h1>{t('title')}</h1>
      <button>{t('createTask')}</button>
    </div>
  );
}
```

**Client components**:
```typescript
'use client';

import {useTranslations} from 'next-intl';

export default function TaskForm() {
  const t = useTranslations('tasks');

  return (
    <form>
      <input placeholder={t('taskTitle')} />
      <button>{t('createTask')}</button>
    </form>
  );
}
```

## Key Implementation Details

### Translation Namespace Organization

Organize translations by feature:
- `common`: Shared terms (app name, loading, error, success)
- `navigation`: Menu items and navigation
- `tasks`: Task management UI
- `chat`: AI chat interface
- `auth`: Authentication flows
- `settings`: Settings page
- `errors`: Error messages

**Access with**: `const t = useTranslations('namespace')`

### RTL Layout Guidelines

**Use Tailwind directional utilities**:
- `ms-4` (margin-start) instead of `ml-4` (margin-left)
- `me-4` (margin-end) instead of `mr-4` (margin-right)
- `ps-4` (padding-start) instead of `pl-4`
- `pe-4` (padding-end) instead of `pr-4`
- `text-start` instead of `text-left`

**Benefits**: Automatically adapts to LTR/RTL based on `dir` attribute.

### Urdu Typography Best Practices

1. **Font**: Use Noto Nastaliq Urdu (Google Fonts)
2. **Line height**: 1.8 (increased for Nastaliq script)
3. **Font size**: 1.05em (slightly larger for readability)
4. **Letter spacing**: 0.01em (better character flow)

**Configured in**: `assets/styles/rtl.css`

### URL Structure

With `localePrefix: 'as-needed'`:
- English (default): `/tasks`, `/chat`, `/settings`
- Urdu: `/ur/tasks`, `/ur/chat`, `/ur/settings`

Middleware automatically redirects based on browser language.

## Testing Checklist

1. **Language switching**:
   - Click language switcher
   - URL updates with locale prefix (for Urdu)
   - All text translates
   - Direction changes (LTR ↔ RTL)

2. **RTL layout verification**:
   - Navigation menu flips to right side
   - Text aligns right
   - Margins/paddings mirror
   - Icons flip correctly

3. **Typography**:
   - Urdu font renders (Noto Nastaliq Urdu)
   - Line height comfortable
   - No character breaking

4. **Browser compatibility**:
   - Test Chrome, Firefox, Safari, Edge
   - Verify font rendering on all browsers

## Common Issues

**Urdu text not displaying**: Ensure Noto Nastaliq Urdu font is loaded via Google Fonts

**Layout breaks in RTL**: Use Tailwind directional utilities (ms-, me-, ps-, pe-) not left/right

**Translations not loading**: Verify JSON files in `locales/` directory, check i18n.ts import path

**Middleware not working**: Check matcher pattern excludes API routes and static files

## Asset Templates

All asset templates are production-ready and can be copied directly:

- **Translations**: `assets/locales/en.json`, `assets/locales/ur.json`
- **i18n Config**: `assets/i18n.ts`
- **Middleware**: `assets/middleware.ts`
- **Language Switcher**: `assets/components/LanguageSwitcher.tsx` (3 variants)
- **RTL Styles**: `assets/styles/rtl.css`

## Performance Optimization

- **Static generation**: Use `generateStaticParams()` for both locales
- **Font loading**: Use `font-display: swap` to prevent FOIT
- **Translation splitting**: Split large files by page for lazy loading

## Best Practices

1. **Namespace organization**: Group by feature, not by page
2. **Descriptive keys**: Use `tasks.createTask` not `t1`
3. **Placeholders**: Use `{variable}` syntax for dynamic values
4. **RTL-first**: Design with RTL in mind from start
5. **Fallbacks**: next-intl falls back to default locale if translation missing
6. **Code blocks**: Keep code in LTR (handled by rtl.css)
7. **Validation**: Validate locale parameter to prevent injection attacks

## Reference Files

- **Integration Guide**: `references/i18n-integration-guide.md` - Complete step-by-step setup with detailed examples
