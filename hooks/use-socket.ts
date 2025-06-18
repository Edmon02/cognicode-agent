'use client';

import { useEffect, useState } from 'react';

export function useSocket() {
  const [socket, setSocket] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Skip on server-side or during build
    if (typeof window === 'undefined' || typeof document === 'undefined') return;

    // Simple mock socket for demo purposes
    const callbacks: Record<string, (data: any) => void> = {};
    
    const mockSocket = {
      emit: (event: string, data: any) => {
        console.log('Mock socket emit:', event, data);
        
        // Simulate responses
        setTimeout(() => {
          if (event === 'analyze_code') {
            mockSocket.trigger('analysis_complete', {
              issues: [
                {
                  severity: 'warning',
                  message: 'Recursive function without memoization detected',
                  line: 3,
                  column: 12,
                  type: 'performance'
                }
              ],
              metrics: {
                complexity: 8,
                maintainability: 7.5,
                performance: 6.2,
                security: 9.1
              },
              suggestions: [
                'Add input validation',
                'Implement memoization for better performance',
                'Add error handling for edge cases'
              ]
            });
          }
        }, 1500);
      },
      on: (event: string, callback: (data: any) => void) => {
        // Store callbacks for mock responses
        callbacks[event] = callback;
      },
      off: (event: string) => {
        delete callbacks[event];
      },
      trigger: (event: string, data: any) => {
        if (callbacks[event]) {
          callbacks[event](data);
        }
      }
    };

    // Simulate connection
    setTimeout(() => {
      setIsConnected(true);
      setSocket(mockSocket);
    }, 1000);

    return () => {
      setIsConnected(false);
      setSocket(null);
    };
  }, []);

  return { socket, isConnected };
}
