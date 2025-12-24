/**
 * Language Detection Utility for Multilingual Chat
 * Supports: English, Urdu (اردو), French (Français), Arabic (العربية)
 */

export type LanguageCode = 'en' | 'ur' | 'fr' | 'ar';

interface LanguageInfo {
  code: LanguageCode;
  name: string;
  direction: 'ltr' | 'rtl';
  fontFamily: string;
}

/**
 * Detect language from text content
 * Returns language code, direction, and appropriate font
 */
export function detectLanguage(text: string): LanguageInfo {
  // Remove whitespace and check if empty
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      code: 'en',
      name: 'English',
      direction: 'ltr',
      fontFamily: 'var(--font-geist-sans)'
    };
  }

  // Count character ranges
  let urduCount = 0;
  let arabicCount = 0;
  let frenchCount = 0;
  let latinCount = 0;

  for (const char of trimmed) {
    const code = char.charCodeAt(0);

    // Urdu (uses Arabic script but includes specific Urdu characters)
    // Arabic script range: 0x0600 - 0x06FF
    // Urdu-specific characters: ٹ (U+0679), ڈ (U+0688), ڑ (U+0691), etc.
    if ((code >= 0x0600 && code <= 0x06FF) || (code >= 0xFB50 && code <= 0xFDFF)) {
      // Check for Urdu-specific characters
      if ([0x0679, 0x0688, 0x0691, 0x06BA, 0x06BE, 0x06C1, 0x06C3].includes(code)) {
        urduCount += 2; // Weight Urdu-specific chars higher
      } else {
        urduCount++;
        arabicCount++; // Also count as Arabic (shared script)
      }
    }
    // French accents: àâäéèêëïîôùûüÿç
    else if ([
      0x00E0, 0x00E2, 0x00E4, 0x00E9, 0x00E8, 0x00EA, 0x00EB,
      0x00EF, 0x00EE, 0x00F4, 0x00F9, 0x00FB, 0x00FC, 0x00FF, 0x00E7
    ].includes(code)) {
      frenchCount++;
      latinCount++;
    }
    // Basic Latin (English/French shared)
    else if ((code >= 0x0041 && code <= 0x005A) || (code >= 0x0061 && code <= 0x007A)) {
      latinCount++;
    }
  }

  // Decision logic
  const totalChars = trimmed.length;

  // Check for Arabic script (Urdu or Arabic)
  const arabicScriptPercent = (urduCount + arabicCount) / totalChars;

  if (arabicScriptPercent > 0.3) {
    // Count actual Urdu-specific characters (not weighted)
    const urduSpecificCount = Array.from(trimmed).filter(char => {
      const code = char.charCodeAt(0);
      return [0x0679, 0x0688, 0x0691, 0x06BA, 0x06BE, 0x06C1, 0x06C3].includes(code);
    }).length;

    // If we have ANY Urdu-specific characters, it's Urdu
    if (urduSpecificCount > 0) {
      return {
        code: 'ur',
        name: 'Urdu',
        direction: 'rtl',
        fontFamily: "'Noto Nastaliq Urdu', 'Noto Sans Arabic', serif"
      };
    }

    // Otherwise Arabic
    return {
      code: 'ar',
      name: 'Arabic',
      direction: 'rtl',
      fontFamily: "'Noto Sans Arabic', 'Noto Nastaliq Urdu', serif"
    };
  }

  // For mixed language, prefer majority
  const latinPercent = latinCount / totalChars;

  // If >5% French-specific characters, likely French
  if (frenchCount / totalChars > 0.05) {
    return {
      code: 'fr',
      name: 'French',
      direction: 'ltr',
      fontFamily: 'var(--font-geist-sans)'
    };
  }

  // Check for common French words as fallback
  const lowerText = trimmed.toLowerCase();
  const frenchWords = ['montre', 'liste', 'tâche', 'taches', 'créer', 'creer', 'pour', 'demain', 'sil', "s'il"];
  const hasFrenchWords = frenchWords.some(word => lowerText.includes(word));

  if (hasFrenchWords && latinPercent > 0.7) {
    return {
      code: 'fr',
      name: 'French',
      direction: 'ltr',
      fontFamily: 'var(--font-geist-sans)'
    };
  }

  // Default to English
  return {
    code: 'en',
    name: 'English',
    direction: 'ltr',
    fontFamily: 'var(--font-geist-sans)'
  };
}

/**
 * Get text alignment based on language direction
 */
export function getTextAlign(direction: 'ltr' | 'rtl'): 'left' | 'right' {
  return direction === 'rtl' ? 'right' : 'left';
}

/**
 * Get flex direction for chat bubbles
 */
export function getChatBubbleAlignment(direction: 'ltr' | 'rtl', role: 'user' | 'assistant') {
  if (role === 'user') {
    return 'justify-end'; // User messages always on right
  }
  return direction === 'rtl' ? 'justify-end' : 'justify-start';
}
