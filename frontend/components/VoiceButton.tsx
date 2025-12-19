/**
 * Voice Button Component
 *
 * Provides a floating action button for voice commands.
 * Integrates with useVoiceCommands hook for speech recognition.
 */

'use client';

import { useState, useEffect } from 'react';
import { useVoiceCommands, getVoiceCommandsHelp, type VoiceCommand } from '@/lib/hooks/useVoiceCommands';

interface VoiceButtonProps {
  language?: 'en-US' | 'ur-PK';
  onCreateTask?: (title: string) => void;
  onCompleteTask?: (taskId: number) => void;
  onDeleteTask?: (taskId: number) => void;
  onListTasks?: () => void;
}

export default function VoiceButton({
  language = 'en-US',
  onCreateTask,
  onCompleteTask,
  onDeleteTask,
  onListTasks,
}: VoiceButtonProps) {
  const [showHelp, setShowHelp] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleCommand = (command: VoiceCommand) => {
    console.log('Voice command received:', command);

    switch (command.action) {
      case 'create':
        if (command.taskTitle && onCreateTask) {
          onCreateTask(command.taskTitle);
          speak(`Task created: ${command.taskTitle}`);
          setFeedback(`✅ Created: ${command.taskTitle}`);
        }
        break;

      case 'complete':
        if (command.taskId && onCompleteTask) {
          onCompleteTask(command.taskId);
          speak(`Task ${command.taskId} marked as complete`);
          setFeedback(`✅ Completed task ${command.taskId}`);
        } else {
          speak('Please specify a task number to complete');
          setFeedback('❌ Missing task number');
        }
        break;

      case 'delete':
        if (command.taskId && onDeleteTask) {
          onDeleteTask(command.taskId);
          speak(`Task ${command.taskId} deleted`);
          setFeedback(`🗑️ Deleted task ${command.taskId}`);
        } else {
          speak('Please specify a task number to delete');
          setFeedback('❌ Missing task number');
        }
        break;

      case 'list':
        if (onListTasks) {
          onListTasks();
          speak('Showing all tasks');
          setFeedback('📋 Listing tasks');
        }
        break;

      case 'help':
        setShowHelp(true);
        speak(getVoiceCommandsHelp(language));
        setFeedback('ℹ️ Showing help');
        break;

      case 'unknown':
        speak('Command not recognized. Say help for available commands.');
        setFeedback('❓ Unknown command');
        break;
    }

    // Clear feedback after 3 seconds
    setTimeout(() => setFeedback(null), 3000);
  };

  const { isListening, transcript, isSupported, error, startListening, stopListening, speak } = useVoiceCommands({
    language,
    onCommand: handleCommand,
  });

  // Auto-close help after 10 seconds
  useEffect(() => {
    if (showHelp) {
      const timer = setTimeout(() => setShowHelp(false), 10000);
      return () => clearTimeout(timer);
    }
  }, [showHelp]);

  if (!isSupported) {
    return (
      <div className="fixed bottom-24 right-8 z-50">
        <div className="bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-4 py-2 rounded-lg text-sm">
          Voice commands not supported in this browser
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Voice Button */}
      <button
        onClick={() => (isListening ? stopListening() : startListening())}
        className={`fixed bottom-8 right-8 z-50 p-4 rounded-full shadow-lg transition-all duration-300 ${
          isListening
            ? 'bg-red-500 hover:bg-red-600 scale-110 animate-pulse'
            : 'bg-blue-500 hover:bg-blue-600'
        } text-white`}
        title={isListening ? 'Stop listening' : 'Start voice command'}
      >
        {isListening ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
            />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        )}
      </button>

      {/* Transcript Display */}
      {isListening && (
        <div className="fixed bottom-24 right-8 z-50 bg-white dark:bg-gray-800 px-4 py-3 rounded-lg shadow-lg max-w-xs">
          <p className="text-sm text-gray-600 dark:text-gray-300">Listening...</p>
          {transcript && (
            <p className="text-sm font-medium text-gray-900 dark:text-white mt-1">{transcript}</p>
          )}
        </div>
      )}

      {/* Feedback Display */}
      {feedback && !isListening && (
        <div className="fixed bottom-24 right-8 z-50 bg-white dark:bg-gray-800 px-4 py-3 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 dark:text-white">{feedback}</p>
        </div>
      )}

      {/* Error Display */}
      {error && !isListening && (
        <div className="fixed bottom-24 right-8 z-50 bg-red-100 dark:bg-red-900 px-4 py-3 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-red-800 dark:text-red-200">Error: {error}</p>
        </div>
      )}

      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Voice Commands Help</h2>
              <button
                onClick={() => setShowHelp(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
              {language === 'ur-PK' ? (
                <>
                  <div>
                    <p className="font-semibold mb-1">نیا کام بنانے کے لیے:</p>
                    <p className="text-gray-600 dark:text-gray-400 font-urdu">
                      &quot;کام بنائیں دودھ خریدیں&quot;
                    </p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">کام مکمل کرنے کے لیے:</p>
                    <p className="text-gray-600 dark:text-gray-400 font-urdu">&quot;کام مکمل کریں 5&quot;</p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">کام حذف کرنے کے لیے:</p>
                    <p className="text-gray-600 dark:text-gray-400 font-urdu">&quot;کام حذف کریں 3&quot;</p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">تمام کام دیکھنے کے لیے:</p>
                    <p className="text-gray-600 dark:text-gray-400 font-urdu">&quot;کام دکھائیں&quot;</p>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <p className="font-semibold mb-1">To create a task:</p>
                    <p className="text-gray-600 dark:text-gray-400">&quot;create task buy milk&quot;</p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">To complete a task:</p>
                    <p className="text-gray-600 dark:text-gray-400">&quot;complete task 5&quot;</p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">To delete a task:</p>
                    <p className="text-gray-600 dark:text-gray-400">&quot;delete task 3&quot;</p>
                  </div>
                  <div>
                    <p className="font-semibold mb-1">To list all tasks:</p>
                    <p className="text-gray-600 dark:text-gray-400">&quot;list tasks&quot;</p>
                  </div>
                </>
              )}
            </div>

            <div className="mt-6">
              <button
                onClick={() => setShowHelp(false)}
                className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
              >
                {language === 'ur-PK' ? 'بند کریں' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
