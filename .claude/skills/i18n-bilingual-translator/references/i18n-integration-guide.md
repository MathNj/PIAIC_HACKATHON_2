# Next.js Bilingual i18n Integration Guide (English/Urdu)

## Overview

This guide provides step-by-step instructions for implementing bilingual i18n support in Next.js applications with English (LTR) and Urdu (RTL) locales.

## Architecture Pattern

**next-intl** approach (recommended for App Router):
1. **Server Components**: Use `getTranslations()` for server-side translation
2. **Client Components**: Use `useTranslations()` hook for client-side translation
3. **Locale Detection**: Middleware-based locale detection and routing
4. **RTL Support**: Automatic direction switching based on locale

## Implementation Steps

### Phase 1: Install Dependencies

```bash
cd frontend
npm install next-intl
```

### Phase 2: Configure i18n

#### 2.1 Create i18n Configuration

Create `frontend/i18n.ts`:

```typescript
import {getRequestConfig} from 'next-intl/server';

export default getRequestConfig(async ({locale}) => ({
  messages: (await import(`./locales/${locale}.json`)).default
}));
```

#### 2.2 Configure Next.js

Update `frontend/next.config.js`:

```javascript
const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Your existing config
};

module.exports = withNextIntl(nextConfig);
```

#### 2.3 Create Middleware for Locale Detection

Create `frontend/src/middleware.ts`:

```typescript
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // Supported locales
  locales: ['en', 'ur'],

  // Default locale
  defaultLocale: 'en',

  // Locale detection
  localeDetection: true,

  // Locale prefix strategy
  localePrefix: 'as-needed'
});

export const config = {
  // Match all pathnames except API routes and static files
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
```

### Phase 3: Create Translation Files

#### 3.1 English Translations

Create `frontend/locales/en.json`:

```json
{
  "common": {
    "appName": "Todo App",
    "welcome": "Welcome",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  },
  "navigation": {
    "home": "Home",
    "tasks": "Tasks",
    "chat": "AI Chat",
    "settings": "Settings",
    "logout": "Logout"
  },
  "tasks": {
    "title": "Tasks",
    "createTask": "Create Task",
    "editTask": "Edit Task",
    "deleteTask": "Delete Task",
    "taskTitle": "Task Title",
    "taskDescription": "Task Description",
    "status": "Status",
    "pending": "Pending",
    "completed": "Completed"
  },
  "chat": {
    "title": "AI Assistant",
    "newConversation": "New Chat",
    "conversations": "Conversations",
    "sendMessage": "Send Message",
    "typeMessage": "Type your message...",
    "noConversations": "No conversations yet"
  },
  "auth": {
    "login": "Login",
    "register": "Register",
    "email": "Email",
    "password": "Password",
    "forgotPassword": "Forgot Password?",
    "loginSuccess": "Login successful",
    "loginError": "Login failed"
  }
}
```

#### 3.2 Urdu Translations

Create `frontend/locales/ur.json`:

```json
{
  "common": {
    "appName": "ٹوڈو ایپ",
    "welcome": "خوش آمدید",
    "loading": "لوڈ ہو رہا ہے...",
    "error": "خرابی",
    "success": "کامیابی"
  },
  "navigation": {
    "home": "ہوم",
    "tasks": "کام",
    "chat": "اے آئی چیٹ",
    "settings": "ترتیبات",
    "logout": "لاگ آؤٹ"
  },
  "tasks": {
    "title": "کام",
    "createTask": "کام بنائیں",
    "editTask": "کام میں ترمیم کریں",
    "deleteTask": "کام حذف کریں",
    "taskTitle": "کام کا عنوان",
    "taskDescription": "کام کی تفصیل",
    "status": "حالت",
    "pending": "زیر التواء",
    "completed": "مکمل"
  },
  "chat": {
    "title": "اے آئی اسسٹنٹ",
    "newConversation": "نئی چیٹ",
    "conversations": "گفتگو",
    "sendMessage": "پیغام بھیجیں",
    "typeMessage": "اپنا پیغام ٹائپ کریں...",
    "noConversations": "ابھی تک کوئی گفتگو نہیں"
  },
  "auth": {
    "login": "لاگ ان",
    "register": "رجسٹر کریں",
    "email": "ای میل",
    "password": "پاس ورڈ",
    "forgotPassword": "پاس ورڈ بھول گئے؟",
    "loginSuccess": "لاگ ان کامیاب",
    "loginError": "لاگ ان ناکام"
  }
}
```

### Phase 4: Update App Router Structure

#### 4.1 Create Locale Layout

Update `frontend/src/app/layout.tsx` to `frontend/src/app/[locale]/layout.tsx`:

```typescript
import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {notFound} from 'next/navigation';

type Props = {
  children: React.ReactNode;
  params: {locale: string};
};

export default async function LocaleLayout({
  children,
  params: {locale}
}: Props) {
  // Validate locale
  const locales = ['en', 'ur'];
  if (!locales.includes(locale)) {
    notFound();
  }

  // Get messages for current locale
  const messages = await getMessages();

  // Get direction for locale (LTR for English, RTL for Urdu)
  const direction = locale === 'ur' ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={direction}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

export function generateStaticParams() {
  return [{locale: 'en'}, {locale: 'ur'}];
}
```

#### 4.2 Update Pages

Move pages to locale-specific directories:
- `app/page.tsx` → `app/[locale]/page.tsx`
- `app/tasks/page.tsx` → `app/[locale]/tasks/page.tsx`
- `app/chat/page.tsx` → `app/[locale]/chat/page.tsx`

### Phase 5: Using Translations

#### 5.1 Server Components

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

#### 5.2 Client Components

```typescript
'use client';

import {useTranslations} from 'next-intl';

export default function TaskForm() {
  const t = useTranslations('tasks');

  return (
    <form>
      <label>{t('taskTitle')}</label>
      <input placeholder={t('taskTitle')} />

      <label>{t('taskDescription')}</label>
      <textarea placeholder={t('taskDescription')} />

      <button type="submit">{t('createTask')}</button>
    </form>
  );
}
```

### Phase 6: Language Switcher Component

Create `frontend/src/components/LanguageSwitcher.tsx`:

```typescript
'use client';

import {useLocale} from 'next-intl';
import {useRouter, usePathname} from 'next/navigation';
import {useTransition} from 'react';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (newLocale: string) => {
    startTransition(() => {
      // Replace current locale in pathname with new locale
      const newPathname = pathname.replace(`/${locale}`, `/${newLocale}`);
      router.replace(newPathname);
    });
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => switchLocale('en')}
        disabled={locale === 'en' || isPending}
        className={`px-3 py-1 rounded ${
          locale === 'en'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300'
        }`}
      >
        English
      </button>
      <button
        onClick={() => switchLocale('ur')}
        disabled={locale === 'ur' || isPending}
        className={`px-3 py-1 rounded ${
          locale === 'ur'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300'
        }`}
      >
        اردو
      </button>
    </div>
  );
}
```

### Phase 7: RTL Styles

#### 7.1 Tailwind CSS RTL Support

Install RTL plugin:

```bash
npm install tailwindcss-rtl
```

Update `tailwind.config.js`:

```javascript
module.exports = {
  plugins: [
    require('tailwindcss-rtl'),
  ],
  // ... rest of config
};
```

#### 7.2 RTL-Aware Styles

Use directional utilities:

```tsx
<div className="ms-4">  {/* margin-start (left in LTR, right in RTL) */}
<div className="me-4">  {/* margin-end (right in LTR, left in RTL) */}
<div className="ps-4">  {/* padding-start */}
<div className="pe-4">  {/* padding-end */}
<div className="text-start">  {/* text-align start */}
```

#### 7.3 Custom RTL Styles

Create `frontend/src/styles/rtl.css`:

```css
/* RTL-specific overrides */
[dir="rtl"] {
  /* Font family for Urdu */
  font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif;
}

/* Fix Tailwind utilities that don't have RTL equivalents */
[dir="rtl"] .float-left {
  float: right;
}

[dir="rtl"] .float-right {
  float: left;
}

/* Urdu typography improvements */
[dir="rtl"] {
  line-height: 1.8; /* Increase line height for better Urdu readability */
  font-size: 1.05em; /* Slightly larger for Urdu characters */
}
```

Import in layout:

```typescript
import '@/styles/rtl.css';
```

### Phase 8: Urdu Font Setup

#### 8.1 Google Fonts Integration

Update `frontend/src/app/[locale]/layout.tsx`:

```typescript
import {Noto_Nastaliq_Urdu} from 'next/font/google';

const urduFont = Noto_Nastaliq_Urdu({
  weight: ['400', '700'],
  subsets: ['arabic'],
  variable: '--font-urdu',
  display: 'swap',
});

export default async function LocaleLayout({children, params: {locale}}: Props) {
  const direction = locale === 'ur' ? 'rtl' : 'ltr';
  const fontClass = locale === 'ur' ? urduFont.variable : '';

  return (
    <html lang={locale} dir={direction} className={fontClass}>
      <body>{children}</body>
    </html>
  );
}
```

## Testing

### Manual Testing Checklist

1. **Locale switching**:
   - Click language switcher, URL should update with locale prefix
   - All text should translate
   - Direction should change (LTR ↔ RTL)

2. **RTL Layout**:
   - Navigation should flip (menu on right in Urdu)
   - Text alignment should be right-aligned
   - Margins/paddings should mirror

3. **Urdu Typography**:
   - Font should render properly (Noto Nastaliq Urdu)
   - Line height should be comfortable
   - No character breaking issues

4. **URL Structure**:
   - `/en/tasks` for English
   - `/ur/tasks` for Urdu
   - Default locale (en) can omit prefix: `/tasks` → `/en/tasks`

## Common Issues

**Issue**: Urdu text not displaying properly
**Solution**: Ensure Noto Nastaliq Urdu font is loaded, check browser font rendering

**Issue**: Layout breaks in RTL mode
**Solution**: Use Tailwind directional utilities (ms-, me-, ps-, pe-, text-start) instead of left/right

**Issue**: Translations not loading
**Solution**: Verify locale JSON files exist in `locales/` directory, check import path in i18n.ts

**Issue**: Middleware not detecting locale
**Solution**: Check middleware matcher pattern, ensure it excludes API routes

## Performance Optimization

- **Static Generation**: Use `generateStaticParams()` for pre-rendering both locales
- **Font Loading**: Use `font-display: swap` to prevent FOIT (Flash of Invisible Text)
- **Translation Splitting**: Split large translation files by page/component for lazy loading

## Best Practices

1. **Namespace organization**: Group translations by feature (`common`, `tasks`, `chat`, `auth`)
2. **Placeholders**: Use `{variable}` syntax for dynamic values
3. **Plural forms**: Use next-intl's `t.rich()` for plural handling
4. **Date/Time formatting**: Use next-intl's `format` utilities for locale-aware formatting
5. **RTL-first design**: Design with RTL in mind from the start, not as an afterthought
6. **Translation keys**: Use descriptive keys (`tasks.createTask` not `t1`)
7. **Missing translations**: next-intl will fallback to default locale if translation is missing

## Security Considerations

- ✓ Validate locale parameter to prevent injection attacks
- ✓ Use `notFound()` for invalid locales
- ✓ Sanitize user-generated content before translation interpolation
- ✓ Don't expose sensitive data in translation keys
