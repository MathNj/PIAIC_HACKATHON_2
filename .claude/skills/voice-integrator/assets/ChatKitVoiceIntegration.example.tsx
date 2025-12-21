import React, { useState, useRef, useEffect } from 'react';
import { VoiceInputButton } from './VoiceInputButton';

/**
 * Example integration of voice input with ChatKit
 * This demonstrates how to add voice input functionality to ChatKit's message input
 */

export const ChatKitVoiceIntegration: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Handle voice transcript and update the input field
  const handleVoiceTranscript = (transcript: string) => {
    setInputValue((prev) => {
      // Append transcript to existing value with a space if there's content
      const newValue = prev ? `${prev} ${transcript}` : transcript;
      return newValue.trim();
    });

    // Focus the input after receiving transcript
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Handle sending the message
  const handleSend = () => {
    if (!inputValue.trim()) return;

    // TODO: Replace with your ChatKit send message logic
    console.log('Sending message:', inputValue);

    // Clear input after sending
    setInputValue('');
  };

  // Handle Enter key to send
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatkit-container">
      {/* Message input area with voice button */}
      <div className="message-input-container">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message or use voice input..."
            className="message-input"
          />

          {/* Voice Input Button - positioned inside the input area */}
          <div className="voice-button-wrapper">
            <VoiceInputButton
              onTranscript={handleVoiceTranscript}
              language="en-US"
              buttonClassName="chatkit-voice-button"
            />
          </div>
        </div>

        <button onClick={handleSend} className="send-button">
          Send
        </button>
      </div>

      <style jsx>{`
        .chatkit-container {
          width: 100%;
          max-width: 800px;
          margin: 0 auto;
        }

        .message-input-container {
          display: flex;
          gap: 8px;
          padding: 16px;
          background-color: #ffffff;
          border-top: 1px solid #e5e7eb;
        }

        .input-wrapper {
          position: relative;
          flex: 1;
          display: flex;
          align-items: center;
        }

        .message-input {
          width: 100%;
          padding: 12px 60px 12px 16px; /* Extra padding on right for voice button */
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .message-input:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .voice-button-wrapper {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
        }

        .send-button {
          padding: 12px 24px;
          background-color: #3b82f6;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .send-button:hover {
          background-color: #2563eb;
        }

        .send-button:disabled {
          background-color: #9ca3af;
          cursor: not-allowed;
        }

        /* Custom styling for voice button in ChatKit context */
        :global(.chatkit-voice-button) {
          padding: 6px;
          min-width: unset;
          background-color: transparent;
        }

        :global(.chatkit-voice-button:hover) {
          background-color: #f3f4f6;
        }

        :global(.chatkit-voice-button.listening) {
          background-color: #fef2f2;
        }
      `}</style>
    </div>
  );
};

/**
 * Alternative: Functional component approach with custom input handling
 * Use this pattern if you need more control over the ChatKit input
 */

export const ChatKitVoiceWithCustomInput: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [currentInput, setCurrentInput] = useState('');

  const handleVoiceInput = (transcript: string) => {
    // Option 1: Replace current input with transcript
    setCurrentInput(transcript);

    // Option 2: Append to current input
    // setCurrentInput(prev => prev ? `${prev} ${transcript}` : transcript);
  };

  const sendMessage = () => {
    if (!currentInput.trim()) return;

    setMessages((prev) => [...prev, currentInput]);
    setCurrentInput('');
  };

  return (
    <div>
      {/* Your ChatKit messages display */}
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx}>{msg}</div>
        ))}
      </div>

      {/* Input with integrated voice button */}
      <div className="input-container">
        <input
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)}
          placeholder="Type or speak your message..."
        />
        <VoiceInputButton onTranscript={handleVoiceInput} />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatKitVoiceIntegration;
