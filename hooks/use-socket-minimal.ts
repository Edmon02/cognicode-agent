'use client';

import { useEffect, useState } from 'react';

export function useSocket() {
  const [socket, setSocket] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Skip on server-side
    if (typeof window === 'undefined') return;

    // Simulate connection status for demo
    const timeout = setTimeout(() => {
      setIsConnected(true);
      // Create a mock socket object
      setSocket({
        emit: (event: string, data: any) => {
          console.log('Socket emit:', event, data);
        },
        on: (event: string, callback: (data: any) => void) => {
          console.log('Socket on:', event);
          // Handle mock responses
          if (event === 'analyze_code') {
            setTimeout(() => {
              callback({
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
                }
              });
            }, 1500);
          }
        }
      });
    }, 1000);

    return () => clearTimeout(timeout);
  }, []);

  return { socket, isConnected };
}
