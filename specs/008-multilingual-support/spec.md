# Feature Specification: Multilingual Support (En, Ur, Fr, Ar)

**Spec ID**: 008
**Status**: Implemented
**Created**: 2025-12-25
**Last Updated**: 2025-12-25
**Phase**: Enhancement (Post Phase III)

---

## 1. Overview

The AI Chatbot must support multilingual conversations in four languages: English, Urdu (اردو), French (Français), and Arabic (العربية). The system must automatically detect the user's language and respond in the same language, with proper RTL (Right-to-Left) support for Urdu and Arabic.

**Value Proposition**: Users can interact with the AI assistant in their preferred language, making the application accessible to a global audience and improving user experience for non-English speakers.

---

## 2. User Stories

- **US-001**: As a user, I want to send messages in Urdu, and have the AI respond in Urdu
- **US-002**: As a user, I want to send messages in French, and have the AI respond in French
- **US-003**: As a user, I want to send messages in Arabic, and have the AI respond in Arabic
- **US-004**: As a user, I want Urdu and Arabic text to display right-to-left with proper font rendering
- **US-005**: As a user, I want English and French text to display left-to-right with standard fonts
- **US-006**: As a user, I want to switch between languages mid-conversation without losing context

---

## 3. Acceptance Criteria

### AC-1: Language Detection (Backend)
- [x] AI agent system prompt includes polyglot instructions for all 4 languages
- [x] Agent automatically detects language of user's message
- [x] Agent responds in the same language as user's message
- [x] Agent maintains language consistency throughout conversation
- [x] Agent handles language switching when user changes language

### AC-2: RTL Support (Frontend)
- [x] Urdu messages display with `dir="rtl"` and right-aligned text
- [x] Arabic messages display with `dir="rtl"` and right-aligned text
- [x] English messages display with `dir="ltr"` and left-aligned text
- [x] French messages display with `dir="ltr"` and left-aligned text
- [x] Chat bubbles maintain proper alignment regardless of language

### AC-3: Font Support (Frontend)
- [x] Noto Nastaliq Urdu font loaded from Google Fonts
- [x] Urdu text renders with Noto Nastaliq Urdu font
- [x] Arabic text renders with Noto Sans Arabic font
- [x] English/French text renders with Geist Sans font
- [x] Font switching happens automatically based on detected language

### AC-4: Language Auto-Detection (Frontend)
- [x] Client-side utility detects language from text content
- [x] Detection analyzes Unicode character ranges
- [x] Urdu-specific characters (ٹ ڈ ڑ) differentiate Urdu from Arabic
- [x] French accents (àâäéèêëïîôùûüÿç) identify French
- [x] Default fallback to English for Latin characters

### AC-5: User Experience
- [x] No manual language selection required
- [x] Seamless language switching without page reload
- [x] Proper text rendering for all languages
- [x] Consistent styling across languages
- [x] Messages in mixed conversations properly aligned

---

## 4. Technical Requirements

### 4.1 Backend (FastAPI)

#### System Prompt Update

The AI agent's system prompt must include multilingual instructions:

```python
default_system_prompt = (
    "You are a helpful AI assistant for a task management application. "
    "You have access to tools that let you create, update, list, delete, and manage tasks. "
    "\n\n🌍 MULTILINGUAL REQUIREMENT:\n"
    "You are a POLYGLOT assistant supporting English, Urdu (اردو), French (Français), and Arabic (العربية).\n"
    "- ALWAYS detect the language of the user's message\n"
    "- ALWAYS respond in the SAME language the user used\n"
    "- If user writes in Urdu, respond in Urdu. If French, respond in French. If Arabic, respond in Arabic.\n"
    "- NEVER reply in English if the user asks in another language (unless they explicitly request English)\n"
    "- Maintain the same language throughout the conversation unless the user switches\n"
    # ... rest of system prompt
)
```

**Key Requirements**:
- Language detection happens at LLM level (no separate detection API)
- Agent responds in same language as user's input
- Language persistence across conversation turns
- Support for language switching mid-conversation

### 4.2 Frontend (Next.js + TypeScript)

#### Font Integration

**Google Fonts Import** in `app/layout.tsx`:
```typescript
import { Noto_Nastaliq_Urdu } from "next/font/google";

const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  variable: "--font-noto-urdu",
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
});
```

**Font Variables**:
- `--font-geist-sans`: English, French (LTR)
- `--font-noto-urdu`: Urdu (RTL)
- Noto Sans Arabic: Arabic (RTL)

#### Language Detection Utility

**File**: `lib/languageDetection.ts`

```typescript
export type LanguageCode = 'en' | 'ur' | 'fr' | 'ar';

interface LanguageInfo {
  code: LanguageCode;
  name: string;
  direction: 'ltr' | 'rtl';
  fontFamily: string;
}

export function detectLanguage(text: string): LanguageInfo {
  // Character range analysis
  // Urdu: 0x0600-0x06FF with Urdu-specific chars (ٹ=0x0679, ڈ=0x0688, ڑ=0x0691)
  // Arabic: 0x0600-0x06FF without Urdu-specific chars
  // French: Latin + accents (àâäéèêëïîôùûüÿç)
  // English: Basic Latin (default)

  // Returns: { code, name, direction, fontFamily }
}
```

**Detection Logic**:
1. Count characters in each Unicode range
2. Calculate percentage thresholds:
   - >30% Urdu/Arabic script → RTL language
   - Urdu-specific chars present → Urdu
   - No Urdu-specific chars → Arabic
   - >10% French accents → French
   - Default → English

#### RTL Layout Application

**Component**: `components/FloatingChatbot.tsx`

```typescript
{messages.map(msg => {
  const langInfo = detectLanguage(msg.content);
  const isRTL = langInfo.direction === 'rtl';

  return (
    <div
      key={msg.id}
      dir={langInfo.direction}
      style={{
        fontFamily: langInfo.fontFamily,
        textAlign: isRTL ? 'right' : 'left'
      }}
    >
      {msg.content}
    </div>
  );
})}
```

**Styling Rules**:
- `dir="rtl"` for Urdu/Arabic
- `dir="ltr"` for English/French
- `text-align: right` for RTL
- `text-align: left` for LTR
- Dynamic `fontFamily` based on language

---

## 5. Implementation Details

### 5.1 Unicode Character Ranges

| Language | Unicode Range | Specific Characters | Example |
|----------|---------------|---------------------|---------|
| Urdu | U+0600 - U+06FF | ٹ (U+0679), ڈ (U+0688), ڑ (U+0691) | میری فہرست دکھائیں |
| Arabic | U+0600 - U+06FF | (no Urdu-specific) | أرني قائمتي |
| French | U+0041 - U+007A | àâäéèêëïîôùûüÿç | Montre-moi ma liste |
| English | U+0041 - U+007A | (basic Latin) | Show me my tasks |

### 5.2 Font Loading Strategy

**Optimization**:
- Fonts loaded via Next.js font optimization
- Variable fonts with multiple weights (400, 500, 600, 700)
- Subset loading: `["arabic"]` for Urdu/Arabic
- CSS variable injection for runtime switching

**Font Fallback Chain**:
- Urdu: `'Noto Nastaliq Urdu', 'Noto Sans Arabic', serif`
- Arabic: `'Noto Sans Arabic', 'Noto Nastaliq Urdu', serif`
- English/French: `var(--font-geist-sans), system-ui`

### 5.3 RTL Logic Flow

```
User sends message → detectLanguage(text) → LanguageInfo
                                               ↓
                        { code, direction, fontFamily }
                                               ↓
                        Apply to chat bubble DOM:
                        - dir={direction}
                        - style.fontFamily={fontFamily}
                        - style.textAlign={rtl ? 'right' : 'left'}
```

**Dynamic Styling**:
- No CSS classes for specific languages
- Runtime style injection based on detection
- Supports mixed-language conversations
- Each message independently styled

---

## 6. Testing Requirements

### 6.1 Unit Tests

**Language Detection**:
- [ ] Detect Urdu from Urdu-specific characters
- [ ] Detect Arabic from generic Arabic script
- [ ] Detect French from accents
- [ ] Detect English from basic Latin
- [ ] Handle empty strings
- [ ] Handle mixed-language text (prefer majority)

**Font Selection**:
- [ ] Return correct font for each language
- [ ] Fallback chain includes all fonts
- [ ] Variable fonts loaded correctly

### 6.2 Integration Tests

**Backend**:
- [ ] Agent responds in Urdu when user sends Urdu
- [ ] Agent responds in French when user sends French
- [ ] Agent responds in Arabic when user sends Arabic
- [ ] Agent maintains language across conversation
- [ ] Agent switches language when user switches

**Frontend**:
- [ ] Urdu messages render RTL
- [ ] Arabic messages render RTL
- [ ] English messages render LTR
- [ ] French messages render LTR
- [ ] Fonts load and apply correctly
- [ ] Mixed conversations display properly

### 6.3 Manual Testing Checklist

- [ ] Send Urdu message: "میری فہرست دکھائیں" (Show my list)
  - **Expected**: RTL alignment, Noto Nastaliq Urdu font, Urdu response
- [ ] Send Arabic message: "أرني قائمتي" (Show me my list)
  - **Expected**: RTL alignment, Noto Sans Arabic font, Arabic response
- [ ] Send French message: "Montre-moi ma liste" (Show me my list)
  - **Expected**: LTR alignment, Geist Sans font, French response
- [ ] Send English message: "Show me my tasks"
  - **Expected**: LTR alignment, Geist Sans font, English response
- [ ] Switch languages mid-conversation
  - **Expected**: Agent follows new language, proper rendering
- [ ] Test on mobile devices
  - **Expected**: RTL/LTR work on iOS Safari, Android Chrome
- [ ] Test font rendering quality
  - **Expected**: Natural Urdu script (not disjointed), clear Arabic

---

## 7. Edge Cases and Error Handling

### 7.1 Mixed-Language Text

**Scenario**: User sends message with multiple languages
**Example**: "Add task میں کل جاؤں گا tomorrow"
**Behavior**: Detect majority language by character count
**Fallback**: Default to English if equal distribution

### 7.2 Unknown/Unsupported Languages

**Scenario**: User sends message in unsupported language (e.g., Spanish, Chinese)
**Behavior**: Default to English rendering (LTR, Geist Sans)
**Agent Response**: May respond in English or attempt to match language

### 7.3 Font Loading Failure

**Scenario**: Google Fonts CDN unavailable
**Behavior**: Fallback to system fonts
**Impact**: Urdu may not render correctly without Noto Nastaliq

### 7.4 RTL Layout Issues

**Scenario**: Browser doesn't support `dir="rtl"`
**Behavior**: Text still renders (left-aligned)
**Mitigation**: Feature detection, polyfills for old browsers

---

## 8. Non-Functional Requirements

### 8.1 Performance

- **Language Detection**: < 10ms per message (client-side)
- **Font Loading**: Fonts preloaded on page load (Next.js optimization)
- **Layout Shift**: No CLS when switching languages
- **Memory**: < 5MB additional for font files

### 8.2 Accessibility

- `lang` attribute set on message elements
- Screen readers announce language changes
- RTL navigation works with keyboard (Tab order preserved)
- High contrast mode preserves readability

### 8.3 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| `dir` attribute | ✅ | ✅ | ✅ | ✅ |
| Google Fonts | ✅ | ✅ | ✅ | ✅ |
| Unicode rendering | ✅ | ✅ | ✅ | ✅ |
| RTL layout | ✅ | ✅ | ✅ | ✅ |

---

## 9. Implementation Phases

### Phase 1: Backend Polyglot Prompt ✅ COMPLETED
- [x] Update system prompt with multilingual instructions
- [x] Test agent responses in all 4 languages
- [x] Verify language detection by LLM
- [x] Verify language consistency

### Phase 2: Frontend Language Detection ✅ COMPLETED
- [x] Create `lib/languageDetection.ts` utility
- [x] Implement Unicode character range analysis
- [x] Test detection accuracy
- [x] Add TypeScript types

### Phase 3: Font Integration ✅ COMPLETED
- [x] Add Noto Nastaliq Urdu to `layout.tsx`
- [x] Configure font variables
- [x] Add font weights (400, 500, 600, 700)
- [x] Verify font loading in DevTools

### Phase 4: RTL Layout ✅ COMPLETED
- [x] Update `FloatingChatbot.tsx` with language detection
- [x] Apply `dir` attribute dynamically
- [x] Apply `fontFamily` style dynamically
- [x] Apply `textAlign` style dynamically
- [x] Test mixed-language conversations

---

## 10. Success Metrics

### Key Performance Indicators (KPIs)

- **Language Detection Accuracy**: >95% correct language identification
- **Rendering Quality**: No broken Urdu script, clear Arabic
- **User Satisfaction**: Non-English users report positive experience
- **Performance**: No noticeable lag when switching languages

### Targets (1 month post-launch)

- 10% of conversations use non-English languages
- <1% user reports of incorrect language detection
- <1% user reports of rendering issues
- 0ms additional latency for language detection

---

## 11. Dependencies

- **Google Fonts**: Noto Nastaliq Urdu, Noto Sans Arabic
- **Next.js**: Font optimization (@next/font)
- **Groq API**: LLM with multilingual support (llama-3.3-70b-versatile)
- **Unicode**: UTF-8 encoding throughout stack

---

## 12. Constraints and Assumptions

### Constraints

- Limited to 4 languages (En, Ur, Fr, Ar)
- No manual language selector (auto-detection only)
- RTL support only for Urdu and Arabic
- LLM must support multilingual responses (Groq llama-3.3-70b does)

### Assumptions

- Users will write entire messages in one language (not code-switching)
- Urdu users prefer Nastaliq script (traditional calligraphy style)
- LLM can accurately detect language from context
- Browser supports modern CSS (dir attribute, custom fonts)

---

## 13. Out of Scope

- Voice input/output for non-English languages (future)
- Additional languages beyond En, Ur, Fr, Ar (future)
- Manual language selector UI (auto-detection only)
- Translation features (user must write in target language)
- Localization of UI elements (only chat messages multilingual)
- RTL layout for entire application (only chat bubbles)

---

## 14. References

- [Unicode Standard](https://unicode.org/charts/)
- [Google Fonts: Noto Nastaliq Urdu](https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu)
- [CSS Writing Modes](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_writing_modes)
- [Next.js Font Optimization](https://nextjs.org/docs/app/building-your-application/optimizing/fonts)

---

**End of Specification**
