// Language switcher component for English/Urdu bilingual support
// Copy this file to: frontend/src/components/LanguageSwitcher.tsx

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
        className={`px-3 py-1 rounded transition-colors ${
          locale === 'en'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
        } ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
        aria-label="Switch to English"
      >
        English
      </button>
      <button
        onClick={() => switchLocale('ur')}
        disabled={locale === 'ur' || isPending}
        className={`px-3 py-1 rounded transition-colors ${
          locale === 'ur'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
        } ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
        aria-label="Switch to Urdu"
      >
        اردو
      </button>
    </div>
  );
}

// Alternative: Dropdown variant for more compact UI
export function LanguageSwitcherDropdown() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = event.target.value;
    startTransition(() => {
      const newPathname = pathname.replace(`/${locale}`, `/${newLocale}`);
      router.replace(newPathname);
    });
  };

  return (
    <select
      value={locale}
      onChange={switchLocale}
      disabled={isPending}
      className="px-3 py-1 rounded border border-gray-300 bg-white text-gray-800 hover:border-gray-400 focus:border-blue-500 focus:outline-none"
      aria-label="Select language"
    >
      <option value="en">English</option>
      <option value="ur">اردو</option>
    </select>
  );
}

// Alternative: Icon-based variant with flag emojis
export function LanguageSwitcherWithFlags() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (newLocale: string) => {
    startTransition(() => {
      const newPathname = pathname.replace(`/${locale}`, `/${newLocale}`);
      router.replace(newPathname);
    });
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => switchLocale('en')}
        disabled={locale === 'en' || isPending}
        className={`flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
          locale === 'en'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
        }`}
        aria-label="Switch to English"
      >
        <span className="text-lg">🇬🇧</span>
        <span className="text-sm font-medium">EN</span>
      </button>
      <button
        onClick={() => switchLocale('ur')}
        disabled={locale === 'ur' || isPending}
        className={`flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
          locale === 'ur'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
        }`}
        aria-label="Switch to Urdu"
      >
        <span className="text-lg">🇵🇰</span>
        <span className="text-sm font-medium">UR</span>
      </button>
    </div>
  );
}
