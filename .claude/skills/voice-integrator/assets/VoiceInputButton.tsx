import React, { useEffect } from 'react';
import { useVoiceInput } from './useVoiceInput';

export interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  language?: string;
  className?: string;
  buttonClassName?: string;
  listeningClassName?: string;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  language = 'en-US',
  className = '',
  buttonClassName = '',
  listeningClassName = '',
}) => {
  const {
    transcript,
    isListening,
    isSupported,
    error,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoiceInput({
    language,
    continuous: false,
    interimResults: true,
  });

  // Update parent component when transcript changes
  useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  // Handle button click
  const handleClick = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening();
    }
  };

  // Don't render if browser doesn't support speech recognition
  if (!isSupported) {
    return null;
  }

  return (
    <div className={`voice-input-container ${className}`}>
      <button
        type="button"
        onClick={handleClick}
        className={`voice-input-button ${buttonClassName} ${
          isListening ? `listening ${listeningClassName}` : ''
        }`}
        aria-label={isListening ? 'Stop recording' : 'Start voice input'}
        title={isListening ? 'Stop recording' : 'Start voice input'}
      >
        {/* Microphone Icon SVG */}
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={isListening ? 'mic-icon listening' : 'mic-icon'}
        >
          <path
            d="M12 14C13.66 14 15 12.66 15 11V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V11C9 12.66 10.34 14 12 14Z"
            fill="currentColor"
          />
          <path
            d="M17 11C17 13.76 14.76 16 12 16C9.24 16 7 13.76 7 11H5C5 14.53 7.61 17.43 11 17.92V21H13V17.92C16.39 17.43 19 14.53 19 11H17Z"
            fill="currentColor"
          />
        </svg>

        {/* Visual feedback when listening */}
        {isListening && (
          <span className="listening-indicator" aria-live="polite">
            Listening...
          </span>
        )}
      </button>

      {/* Error message display */}
      {error && (
        <div className="voice-input-error" role="alert">
          {error}
        </div>
      )}

      <style jsx>{`
        .voice-input-container {
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .voice-input-button {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          border: none;
          background-color: #f3f4f6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          color: #374151;
        }

        .voice-input-button:hover {
          background-color: #e5e7eb;
        }

        .voice-input-button:active {
          transform: scale(0.95);
        }

        .voice-input-button.listening {
          background-color: #ef4444;
          color: white;
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.7;
          }
        }

        .mic-icon {
          transition: transform 0.2s ease;
        }

        .mic-icon.listening {
          animation: micPulse 1s ease-in-out infinite;
        }

        @keyframes micPulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.1);
          }
        }

        .listening-indicator {
          font-size: 12px;
          font-weight: 500;
        }

        .voice-input-error {
          position: absolute;
          bottom: -24px;
          left: 0;
          font-size: 12px;
          color: #ef4444;
          white-space: nowrap;
        }
      `}</style>
    </div>
  );
};

export default VoiceInputButton;
