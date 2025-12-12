/**
 * Voice Commands Hook
 *
 * Provides voice-to-text and text-to-speech functionality for the Todo App.
 * Uses Web Speech API for browser-native speech recognition and synthesis.
 *
 * Features:
 * - Voice input for task creation ("create task buy milk")
 * - Voice commands for task management ("complete task 5", "delete task 3")
 * - Text-to-speech feedback for confirmations
 * - Support for Urdu and English languages
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Type definitions for Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor;
    webkitSpeechRecognition: SpeechRecognitionConstructor;
  }
}

export interface VoiceCommand {
  action: 'create' | 'complete' | 'delete' | 'update' | 'list' | 'help' | 'unknown';
  text: string;
  taskId?: number;
  taskTitle?: string;
}

export interface UseVoiceCommandsOptions {
  language?: 'en-US' | 'ur-PK';
  onCommand?: (command: VoiceCommand) => void;
  onTranscript?: (transcript: string) => void;
  autoStart?: boolean;
}

export const useVoiceCommands = ({
  language = 'en-US',
  onCommand,
  onTranscript,
  autoStart = false,
}: UseVoiceCommandsOptions = {}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthesisRef = useRef<SpeechSynthesis | null>(null);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesis = window.speechSynthesis;

    if (SpeechRecognition && speechSynthesis) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognition();
      synthesisRef.current = speechSynthesis;

      const recognition = recognitionRef.current;
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = language;

      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);

        if (onTranscript) {
          onTranscript(transcriptText);
        }

        // Parse command
        const command = parseVoiceCommand(transcriptText);
        if (onCommand) {
          onCommand(command);
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setError(event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };
    } else {
      setIsSupported(false);
      setError('Voice commands not supported in this browser');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [language, onCommand, onTranscript]);

  // Auto-start if requested
  useEffect(() => {
    if (autoStart && isSupported && !isListening) {
      startListening();
    }
  }, [autoStart, isSupported]);

  /**
   * Parse voice transcript into structured command
   */
  const parseVoiceCommand = (text: string): VoiceCommand => {
    const lowerText = text.toLowerCase().trim();

    // Create task command
    if (lowerText.startsWith('create task') || lowerText.startsWith('add task') || lowerText.startsWith('new task')) {
      const taskTitle = text.replace(/^(create|add|new) task/i, '').trim();
      return {
        action: 'create',
        text,
        taskTitle: taskTitle || 'New task',
      };
    }

    // Complete task command
    if (lowerText.includes('complete task') || lowerText.includes('finish task') || lowerText.includes('done task')) {
      const match = lowerText.match(/task\s+(\d+)/);
      const taskId = match ? parseInt(match[1], 10) : undefined;
      return {
        action: 'complete',
        text,
        taskId,
      };
    }

    // Delete task command
    if (lowerText.includes('delete task') || lowerText.includes('remove task')) {
      const match = lowerText.match(/task\s+(\d+)/);
      const taskId = match ? parseInt(match[1], 10) : undefined;
      return {
        action: 'delete',
        text,
        taskId,
      };
    }

    // List tasks command
    if (lowerText.includes('list tasks') || lowerText.includes('show tasks') || lowerText.includes('my tasks')) {
      return {
        action: 'list',
        text,
      };
    }

    // Help command
    if (lowerText.includes('help') || lowerText.includes('commands')) {
      return {
        action: 'help',
        text,
      };
    }

    // Unknown command
    return {
      action: 'unknown',
      text,
    };
  };

  /**
   * Start listening for voice input
   */
  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setError(null);
      try {
        recognitionRef.current.start();
      } catch (err) {
        setError('Failed to start voice recognition');
      }
    }
  }, [isListening]);

  /**
   * Stop listening for voice input
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  /**
   * Speak text using text-to-speech
   */
  const speak = useCallback((text: string, options?: { lang?: string; rate?: number; pitch?: number }) => {
    if (synthesisRef.current) {
      // Cancel any ongoing speech
      synthesisRef.current.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = options?.lang || language;
      utterance.rate = options?.rate || 1;
      utterance.pitch = options?.pitch || 1;

      synthesisRef.current.speak(utterance);
    }
  }, [language]);

  /**
   * Stop any ongoing speech
   */
  const stopSpeaking = useCallback(() => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
    }
  }, []);

  return {
    isListening,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
};

/**
 * Get help text for voice commands
 */
export const getVoiceCommandsHelp = (language: 'en-US' | 'ur-PK' = 'en-US'): string => {
  if (language === 'ur-PK') {
    return `
    آواز کمانڈز:
    - نیا کام بنانے کے لیے: "کام بنائیں [کام کا نام]"
    - کام مکمل کرنے کے لیے: "کام مکمل کریں [نمبر]"
    - کام حذف کرنے کے لیے: "کام حذف کریں [نمبر]"
    - تمام کام دیکھنے کے لیے: "کام دکھائیں"
    - مدد کے لیے: "مدد"
    `;
  }

  return `
  Voice Commands:
  - To create a task: "create task [task name]"
  - To complete a task: "complete task [number]"
  - To delete a task: "delete task [number]"
  - To list all tasks: "list tasks"
  - For help: "help"
  `;
};
