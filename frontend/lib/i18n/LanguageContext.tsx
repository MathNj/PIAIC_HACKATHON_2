/**
 * Language Context for Multi-language Support
 *
 * Provides i18n functionality for English and Urdu languages.
 * Uses React Context to make translations available throughout the app.
 */

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import enTranslations from './translations/en.json';
import urTranslations from './translations/ur.json';

export type Language = 'en' | 'ur';

export type Translations = typeof enTranslations;

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  isRTL: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<Language, Translations> = {
  en: enTranslations,
  ur: urTranslations,
};

interface LanguageProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

export function LanguageProvider({ children, defaultLanguage = 'en' }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);
  const [mounted, setMounted] = useState(false);

  // Load language from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const savedLanguage = localStorage.getItem('language') as Language | null;
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'ur')) {
      setLanguageState(savedLanguage);
    }
  }, []);

  // Save language to localStorage and update document direction
  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);

    // Update document direction for RTL languages
    if (typeof document !== 'undefined') {
      document.documentElement.dir = lang === 'ur' ? 'rtl' : 'ltr';
      document.documentElement.lang = lang === 'ur' ? 'ur' : 'en';
    }
  };

  // Translation function with nested key support
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[language];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to English if key not found
        value = translations.en;
        for (const fallbackKey of keys) {
          if (value && typeof value === 'object' && fallbackKey in value) {
            value = value[fallbackKey];
          } else {
            return key; // Return key if translation not found
          }
        }
        break;
      }
    }

    return typeof value === 'string' ? value : key;
  };

  const isRTL = language === 'ur';

  // Set initial direction on mount
  useEffect(() => {
    if (mounted && typeof document !== 'undefined') {
      document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
      document.documentElement.lang = language === 'ur' ? 'ur' : 'en';
    }
  }, [language, isRTL, mounted]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, isRTL }}>
      {children}
    </LanguageContext.Provider>
  );
}

/**
 * Hook to access language context
 */
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

/**
 * Language Switcher Component
 */
export function LanguageSwitcher({ className = '' }: { className?: string }) {
  const { language, setLanguage } = useLanguage();

  return (
    <button
      onClick={() => setLanguage(language === 'en' ? 'ur' : 'en')}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${className}`}
      title={language === 'en' ? 'Switch to Urdu' : 'Switch to English'}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
        />
      </svg>
      <span className="text-sm font-medium">
        {language === 'en' ? 'اردو' : 'English'}
      </span>
    </button>
  );
}
