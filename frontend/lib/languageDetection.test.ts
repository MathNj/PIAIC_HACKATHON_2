/**
 * Language Detection Tests
 * Tests for Urdu, French, Arabic, and English language detection
 */

import { detectLanguage } from './languageDetection';

describe('Language Detection', () => {
  describe('Urdu Detection', () => {
    test('detects Urdu from Urdu-specific characters', () => {
      const text = 'میری فہرست دکھائیں';
      const result = detectLanguage(text);

      expect(result.code).toBe('ur');
      expect(result.name).toBe('Urdu');
      expect(result.direction).toBe('rtl');
      expect(result.fontFamily).toContain('Noto Nastaliq Urdu');
    });

    test('detects Urdu from longer text', () => {
      const text = 'میری خریداری کی فہرست دکھائیں کل کا کام';
      const result = detectLanguage(text);

      expect(result.code).toBe('ur');
      expect(result.direction).toBe('rtl');
    });

    test('detects Urdu with Urdu-specific characters ٹ ڈ ڑ', () => {
      const text = 'ٹیسٹ ڈیٹا ڑکھنا';
      const result = detectLanguage(text);

      expect(result.code).toBe('ur');
      expect(result.direction).toBe('rtl');
    });
  });

  describe('French Detection', () => {
    test('detects French from accents', () => {
      const text = 'Montréal est une belle ville française';
      const result = detectLanguage(text);

      expect(result.code).toBe('fr');
      expect(result.name).toBe('French');
      expect(result.direction).toBe('ltr');
      expect(result.fontFamily).toContain('geist-sans');
    });

    test('detects French from common phrases', () => {
      const text = "Montre-moi ma liste de tâches s'il te plaît";
      const result = detectLanguage(text);

      expect(result.code).toBe('fr');
      expect(result.direction).toBe('ltr');
    });

    test('detects French with various accents', () => {
      const text = 'àâäéèêëïîôùûüÿç';
      const result = detectLanguage(text);

      expect(result.code).toBe('fr');
    });
  });

  describe('Arabic Detection', () => {
    test('detects Arabic from Arabic script without Urdu chars', () => {
      const text = 'أرني قائمة المهام الخاصة بي';
      const result = detectLanguage(text);

      expect(result.code).toBe('ar');
      expect(result.name).toBe('Arabic');
      expect(result.direction).toBe('rtl');
      expect(result.fontFamily).toContain('Noto Sans Arabic');
    });
  });

  describe('English Detection', () => {
    test('detects English from basic Latin', () => {
      const text = 'Show me my task list';
      const result = detectLanguage(text);

      expect(result.code).toBe('en');
      expect(result.name).toBe('English');
      expect(result.direction).toBe('ltr');
      expect(result.fontFamily).toContain('geist-sans');
    });
  });

  describe('Edge Cases', () => {
    test('handles empty string', () => {
      const result = detectLanguage('');

      expect(result.code).toBe('en');
      expect(result.direction).toBe('ltr');
    });

    test('handles whitespace only', () => {
      const result = detectLanguage('   \n\t  ');

      expect(result.code).toBe('en');
    });

    test('handles mixed language (English majority)', () => {
      const text = 'Add task tomorrow میں کل';
      const result = detectLanguage(text);

      // English is majority, should detect as English
      expect(result.direction).toBe('ltr');
    });
  });

  describe('Performance', () => {
    test('completes detection in under 10ms', () => {
      const text = 'میری فہرست دکھائیں کل کا کام '.repeat(10);

      const start = performance.now();
      detectLanguage(text);
      const end = performance.now();

      expect(end - start).toBeLessThan(10);
    });
  });
});
