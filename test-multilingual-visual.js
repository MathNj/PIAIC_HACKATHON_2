/**
 * Visual Multilingual Rendering Demonstration
 * Shows how messages will appear in the chat interface
 */

// Import the detection function (copy-paste from test file)
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

    if ((code >= 0x0600 && code <= 0x06FF) || (code >= 0xFB50 && code <= 0xFDFF)) {
      if ([0x0679, 0x0688, 0x0691, 0x06BA, 0x06BE, 0x06C1, 0x06C3].includes(code)) {
        urduCount += 2;
      } else {
        urduCount++;
        arabicCount++;
      }
    }
    else if ([
      0x00E0, 0x00E2, 0x00E4, 0x00E9, 0x00E8, 0x00EA, 0x00EB,
      0x00EF, 0x00EE, 0x00F4, 0x00F9, 0x00FB, 0x00FC, 0x00FF, 0x00E7
    ].includes(code)) {
      frenchCount++;
      latinCount++;
    }
    else if ((code >= 0x0041 && code <= 0x005A) || (code >= 0x0061 && code <= 0x007A)) {
      latinCount++;
    }
  }

  const totalChars = trimmed.length;
  const arabicScriptPercent = (urduCount + arabicCount) / totalChars;

  if (arabicScriptPercent > 0.3) {
    const urduSpecificCount = Array.from(trimmed).filter(char => {
      const code = char.charCodeAt(0);
      return [0x0679, 0x0688, 0x0691, 0x06BA, 0x06BE, 0x06C1, 0x06C3].includes(code);
    }).length;

    if (urduSpecificCount > 0) {
      return {
        code: 'ur',
        name: 'Urdu',
        direction: 'rtl',
        fontFamily: "'Noto Nastaliq Urdu', 'Noto Sans Arabic', serif"
      };
    }

    return {
      code: 'ar',
      name: 'Arabic',
      direction: 'rtl',
      fontFamily: "'Noto Sans Arabic', 'Noto Nastaliq Urdu', serif"
    };
  }

  const latinPercent = latinCount / totalChars;

  if (frenchCount / totalChars > 0.05) {
    return {
      code: 'fr',
      name: 'French',
      direction: 'ltr',
      fontFamily: 'var(--font-geist-sans)'
    };
  }

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

// Simulated conversation with multilingual messages
const conversation = [
  { role: 'user', content: 'Hello! I need help with my tasks' },
  { role: 'assistant', content: 'Hello! I\'d be happy to help you manage your tasks. What would you like to do?' },
  { role: 'user', content: 'میری فہرست دکھائیں' },
  { role: 'assistant', content: 'یہاں آپ کے کام ہیں. آپ کی فہرست میں ابھی کوئی کام نہیں ہے۔' },
  { role: 'user', content: 'کل کے لیے ایک کام بنائیں' },
  { role: 'assistant', content: 'ٹھیک ہے، میں کل کے لیے ایک کام بنا رہا ہوں۔ کام کا عنوان کیا ہونا چاہیے؟' },
  { role: 'user', content: 'Montre-moi ma liste de tâches' },
  { role: 'assistant', content: 'Voici votre liste de tâches. Vous avez actuellement aucune tâche.' },
  { role: 'user', content: 'Créer une tâche pour demain' },
  { role: 'assistant', content: 'D\'accord, je vais créer une tâche pour demain. Quel est le titre de la tâche?' },
  { role: 'user', content: 'Switch back to English please' },
  { role: 'assistant', content: 'Of course! I\'m now responding in English. How can I help you?' },
];

console.log('\n🎨 Multilingual Chat Rendering Demonstration\n');
console.log('=' .repeat(100));

conversation.forEach((msg, index) => {
  const langInfo = detectLanguage(msg.content);
  const isRTL = langInfo.direction === 'rtl';
  const isUser = msg.role === 'user';

  console.log(`\n[Message ${index + 1}] ${msg.role.toUpperCase()}`);
  console.log('─'.repeat(100));

  // Show detected language info
  console.log(`  Language:  ${langInfo.name} (${langInfo.code})`);
  console.log(`  Direction: ${langInfo.direction.toUpperCase()} ${isRTL ? '→←' : '←→'}`);
  console.log(`  Font:      ${langInfo.fontFamily}`);
  console.log(`  Alignment: ${isRTL ? 'RIGHT' : 'LEFT'}`);

  // Visual representation
  console.log('\n  Visual Preview:');
  if (isUser) {
    console.log('  ┌────────────────────────────────────────────────────────────────┐');
    if (isRTL) {
      console.log(`  │                                                    ${msg.content} 👤│`);
    } else {
      console.log(`  │                                     ${msg.content} 👤│`);
    }
    console.log('  └────────────────────────────────────────────────────────────────┘');
  } else {
    console.log('  ┌────────────────────────────────────────────────────────────────┐');
    if (isRTL) {
      console.log(`  │${msg.content.padStart(msg.content.length + 58)} 🤖│`);
    } else {
      console.log(`  │🤖 ${msg.content}${' '.repeat(Math.max(0, 60 - msg.content.length))}│`);
    }
    console.log('  └────────────────────────────────────────────────────────────────┘');
  }

  // Show HTML attributes that would be applied
  console.log('\n  HTML Attributes:');
  console.log(`  <div dir="${langInfo.direction}" style="font-family: ${langInfo.fontFamily}; text-align: ${isRTL ? 'right' : 'left'};">`);
  console.log(`    ${msg.content}`);
  console.log(`  </div>`);
});

console.log('\n' + '='.repeat(100));
console.log('\n✨ Multilingual rendering is fully functional!');
console.log('   • Urdu: RTL with Noto Nastaliq Urdu font');
console.log('   • French: LTR with Geist Sans font');
console.log('   • Arabic: RTL with Noto Sans Arabic font');
console.log('   • English: LTR with Geist Sans font');
console.log('\n📝 To test in the browser:');
console.log('   1. Open http://localhost:3000/chat');
console.log('   2. Send: "میری فہرست دکھائیں" (Urdu)');
console.log('   3. Send: "Montre-moi ma liste" (French)');
console.log('   4. Observe RTL/LTR rendering and font changes\n');
