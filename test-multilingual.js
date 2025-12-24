/**
 * Quick Multilingual Test Script
 * Run with: node test-multilingual.js
 */

// Language detection function (copied from languageDetection.ts)
function detectLanguage(text) {
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      code: 'en',
      name: 'English',
      direction: 'ltr',
      fontFamily: 'var(--font-geist-sans)'
    };
  }

  let urduCount = 0;
  let arabicCount = 0;
  let frenchCount = 0;
  let latinCount = 0;

  for (const char of trimmed) {
    const code = char.charCodeAt(0);

    // Urdu/Arabic: U+0600 - U+06FF
    if ((code >= 0x0600 && code <= 0x06FF) || (code >= 0xFB50 && code <= 0xFDFF)) {
      // Urdu-specific: ٹ ڈ ڑ ں ھ ہ ے
      if ([0x0679, 0x0688, 0x0691, 0x06BA, 0x06BE, 0x06C1, 0x06C3].includes(code)) {
        urduCount += 2;
      } else {
        urduCount++;
        arabicCount++;
      }
    }
    // French accents
    else if ([
      0x00E0, 0x00E2, 0x00E4, 0x00E9, 0x00E8, 0x00EA, 0x00EB,
      0x00EF, 0x00EE, 0x00F4, 0x00F9, 0x00FB, 0x00FC, 0x00FF, 0x00E7
    ].includes(code)) {
      frenchCount++;
      latinCount++;
    }
    // Basic Latin
    else if ((code >= 0x0041 && code <= 0x005A) || (code >= 0x0061 && code <= 0x007A)) {
      latinCount++;
    }
  }

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

  return {
    code: 'en',
    name: 'English',
    direction: 'ltr',
    fontFamily: 'var(--font-geist-sans)'
  };
}

// Test cases
const tests = [
  {
    name: 'Urdu: Show my list',
    text: 'میری فہرست دکھائیں',
    expected: { code: 'ur', direction: 'rtl' }
  },
  {
    name: 'Urdu: Show shopping list',
    text: 'میری خریداری کی فہرست دکھائیں',
    expected: { code: 'ur', direction: 'rtl' }
  },
  {
    name: 'Urdu: Create task for tomorrow',
    text: 'کل کے لیے کام بنائیں',
    expected: { code: 'ur', direction: 'rtl' }
  },
  {
    name: 'French: Show my list',
    text: 'Montre-moi ma liste',
    expected: { code: 'fr', direction: 'ltr' }
  },
  {
    name: 'French: Show task list',
    text: "Montre-moi ma liste de tâches s'il te plaît",
    expected: { code: 'fr', direction: 'ltr' }
  },
  {
    name: 'French: Create task',
    text: 'Créer une tâche pour demain',
    expected: { code: 'fr', direction: 'ltr' }
  },
  {
    name: 'Arabic: Show my list',
    text: 'أرني قائمة المهام الخاصة بي',
    expected: { code: 'ar', direction: 'rtl' }
  },
  {
    name: 'English: Show my tasks',
    text: 'Show me my tasks',
    expected: { code: 'en', direction: 'ltr' }
  },
  {
    name: 'Mixed: English + Urdu',
    text: 'Add task tomorrow میں کل',
    expected: { code: 'ur', direction: 'rtl' } // Urdu detected due to Urdu-specific chars
  }
];

console.log('🧪 Multilingual Language Detection Tests\n');
console.log('=' .repeat(80));

let passed = 0;
let failed = 0;

tests.forEach((test, index) => {
  const result = detectLanguage(test.text);

  const codeMatch = !test.expected.code || result.code === test.expected.code;
  const directionMatch = result.direction === test.expected.direction;
  const success = codeMatch && directionMatch;

  if (success) {
    passed++;
    console.log(`\n✅ Test ${index + 1}: ${test.name}`);
  } else {
    failed++;
    console.log(`\n❌ Test ${index + 1}: ${test.name}`);
  }

  console.log(`   Input:    "${test.text}"`);
  console.log(`   Expected: ${test.expected.code || 'any'} (${test.expected.direction})`);
  console.log(`   Result:   ${result.code} (${result.direction})`);
  console.log(`   Font:     ${result.fontFamily}`);
});

console.log('\n' + '='.repeat(80));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed (${tests.length} total)`);

if (failed === 0) {
  console.log('\n🎉 All tests passed! Language detection is working correctly.\n');
} else {
  console.log('\n⚠️  Some tests failed. Please review the implementation.\n');
  process.exit(1);
}
