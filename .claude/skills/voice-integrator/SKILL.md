---
name: voice-integrator
description: Integrate Speech-to-Text functionality into Next.js ChatKit applications using the browser's native SpeechRecognition API. Use when: (1) Adding voice input to ChatKit chat interfaces, (2) Implementing speech-to-text for message inputs, (3) Enabling voice recording in chat applications, (4) Creating voice-enabled messaging features with real-time transcription, or (5) Building accessible voice input controls for web chat. Provides production-ready React hooks, components, and integration patterns with proper error handling and browser compatibility.
---

# Voice Integrator

Integrate voice input functionality into Next.js ChatKit applications using the browser's native Web Speech API.

## Quick Start

### Step 1: Copy Asset Templates

Copy these templates from the skill's `assets/` directory to your project:

- `useVoiceInput.tsx` → Your hooks directory (e.g., `src/hooks/`)
- `VoiceInputButton.tsx` → Your components directory (e.g., `src/components/`)
- `ChatKitVoiceIntegration.example.tsx` → Reference for integration patterns

### Step 2: Integrate with ChatKit

**Basic Integration Pattern:**

```tsx
import { VoiceInputButton } from '@/components/VoiceInputButton';

function ChatInput() {
  const [message, setMessage] = useState('');

  const handleVoiceTranscript = (transcript: string) => {
    // Append voice transcript to input
    setMessage(prev => prev ? `${prev} ${transcript}` : transcript);
  };

  return (
    <div className="input-wrapper">
      <input
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="Type or speak..."
      />
      <VoiceInputButton
        onTranscript={handleVoiceTranscript}
        language="en-US"
      />
    </div>
  );
}
```

### Step 3: Position Voice Button

Place the voice button **inside the ChatKit input area** as an adornment or sibling:

```css
.input-wrapper {
  position: relative;
}

.voice-button-wrapper {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}
```

## Quality Criteria

Ensure implementations meet these requirements:

### 1. Browser Compatibility

The hook automatically checks for browser support:

```tsx
const { isSupported } = useVoiceInput();

// Button only renders if supported
if (!isSupported) return null;
```

Checks for both `window.SpeechRecognition` and `window.webkitSpeechRecognition`.

### 2. User Feedback

Visual indicators show recording state:

- **Listening**: Pulsing red button with "Listening..." text
- **Idle**: Gray microphone icon
- **Error**: Error message displayed below button

Implemented with CSS animations:

```css
.listening {
  animation: pulse 1.5s ease-in-out infinite;
  background-color: #ef4444;
}
```

### 3. ChatKit Integration

Transcript automatically populates the input field via `onTranscript` callback:

```tsx
const handleVoiceTranscript = (transcript: string) => {
  setInputValue(transcript); // Direct replacement
  // OR
  setInputValue(prev => `${prev} ${transcript}`); // Append mode
};
```

### 4. Error Handling

Graceful handling of microphone permission denials:

```tsx
const { error } = useVoiceInput({
  onError: (errorMessage) => {
    console.error('Voice input error:', errorMessage);
    // Show user-friendly error message
  }
});
```

**Common error states:**
- `not-allowed` / `permission-denied`: Microphone access blocked
- `no-speech`: No speech detected
- `network`: Network error
- `aborted`: Recognition aborted

## Hook API

### `useVoiceInput(options)`

**Options:**
- `language?: string` - Recognition language (default: 'en-US')
- `continuous?: boolean` - Continuous recognition mode (default: false)
- `interimResults?: boolean` - Show interim results (default: true)
- `onTranscriptChange?: (transcript: string) => void` - Callback for transcript updates
- `onError?: (error: string) => void` - Callback for errors

**Returns:**
- `transcript: string` - Current transcript text
- `isListening: boolean` - Whether actively listening
- `isSupported: boolean` - Browser compatibility check
- `error: string | null` - Current error message
- `startListening: () => void` - Start voice recognition
- `stopListening: () => void` - Stop voice recognition
- `resetTranscript: () => void` - Clear transcript

## Component API

### `VoiceInputButton`

**Props:**
- `onTranscript: (text: string) => void` - **Required**. Callback receiving transcribed text
- `language?: string` - Recognition language (default: 'en-US')
- `className?: string` - Container className
- `buttonClassName?: string` - Button className
- `listeningClassName?: string` - Additional className when listening

## Language Support

Change recognition language:

```tsx
<VoiceInputButton
  onTranscript={handleTranscript}
  language="es-ES" // Spanish
/>
```

**Common language codes:**
- `en-US` - English (United States)
- `en-GB` - English (United Kingdom)
- `es-ES` - Spanish (Spain)
- `fr-FR` - French (France)
- `de-DE` - German (Germany)
- `ar-SA` - Arabic (Saudi Arabia)
- `ur-PK` - Urdu (Pakistan)

## Advanced Patterns

### Continuous Recognition Mode

For longer transcriptions:

```tsx
const { transcript, startListening, stopListening } = useVoiceInput({
  continuous: true,
  interimResults: true,
});
```

### Custom Styling

Override default styles:

```tsx
<VoiceInputButton
  onTranscript={handleTranscript}
  buttonClassName="my-custom-button"
  listeningClassName="my-listening-state"
/>
```

### Manual Control

Use the hook directly for custom UI:

```tsx
const { isListening, startListening, stopListening, transcript } = useVoiceInput();

<button onClick={isListening ? stopListening : startListening}>
  {isListening ? 'Stop' : 'Start'} Recording
</button>
```

## Troubleshooting

### Button Not Appearing

- Check browser compatibility: Chrome, Edge, Safari support Web Speech API
- Firefox has limited support; consider feature detection

### Microphone Permission Issues

- HTTPS required for microphone access (localhost exempt)
- User must explicitly grant permission
- Show clear error message via `error` state

### Transcript Not Updating Input

- Ensure `onTranscript` callback properly updates state
- Check for controlled vs uncontrolled input conflicts
- Verify transcript is being passed correctly

## Best Practices

1. **Browser Compatibility**: Always check `isSupported` before rendering
2. **User Privacy**: Clearly indicate when microphone is active
3. **Error Messages**: Display user-friendly error messages
4. **HTTPS**: Deploy on HTTPS for production (required for microphone access)
5. **Accessibility**: Include proper ARIA labels and roles
6. **Visual Feedback**: Show clear listening state with animations
7. **Positioning**: Place voice button where users expect it (input area)

## Constraints

- **Native API Only**: No external libraries required
- **Standard React Hooks**: Uses useState, useEffect, useRef, useCallback
- **TypeScript**: Full type safety with TypeScript support
- **Browser API**: Requires modern browser with SpeechRecognition API
- **HTTPS**: Microphone access requires secure context (except localhost)

## Reference Files

All implementation code is in `assets/`:
- `useVoiceInput.tsx` - React hook with full SpeechRecognition API integration
- `VoiceInputButton.tsx` - Pre-built voice button component with styling
- `ChatKitVoiceIntegration.example.tsx` - Complete integration examples
