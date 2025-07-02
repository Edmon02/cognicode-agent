'use client';

import { useEffect, useState } from 'react';

// Dynamically import socket.io-client only on client side
export function useSocket() {
  const [socket, setSocket] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Skip socket initialization on server-side rendering
    if (typeof window === 'undefined') {
      return;
    }

    // Dynamically import socket.io-client
    const initSocket = async () => {
      try {
        const { io } = await import('socket.io-client');
        
        // Use environment variable for backend URL with fallback to localhost
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
        
        const socketInstance = io(backendUrl, {
          transports: ['websocket'],
          autoConnect: true,
        });

        socketInstance.on('connect', () => {
          setIsConnected(true);
          console.log('Connected to CogniCode AI backend');
        });

        socketInstance.on('disconnect', () => {
          setIsConnected(false);
          console.log('Disconnected from CogniCode AI backend');
        });

        socketInstance.on('connect_error', (error: any) => {
          console.log('Connection failed:', error);
          setIsConnected(false);
          
          // Don't automatically fall back to simulation - let user know connection failed
          console.warn('Unable to connect to backend. Please ensure the backend server is running on', backendUrl);
        });

        setSocket(socketInstance);

        // Return cleanup function
        return () => {
          socketInstance.disconnect();
        };
      } catch (error) {
        console.error('Failed to load socket.io client:', error);
      }
    };

    const cleanup = initSocket();

    // Return cleanup function for useEffect
    return () => {
      cleanup?.then(cleanupFn => cleanupFn?.());
    };
  }, []);

  return { socket, isConnected };
}

function simulateBackendResponses(socket: any) {
  socket.on('analyze_code', (data: any) => {
    setTimeout(() => {
      socket.emit('analysis_complete', {
        issues: [
          {
            severity: 'warning',
            message: 'Recursive function without memoization detected',
            line: 3,
            column: 12,
            type: 'performance'
          },
          {
            severity: 'info',
            message: 'Consider using dynamic programming approach',
            line: 1,
            column: 1,
            type: 'suggestion'
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
    }, 1500);
  });

  socket.on('generate_refactoring', (data: any) => {
    setTimeout(() => {
      socket.emit('refactor_suggestions', [
        {
          title: 'Optimize with Memoization',
          description: 'Replace recursive implementation with memoized version for better performance',
          difficulty: 'medium',
          impact: 'high',
          estimated_time: '10-15 minutes',
          code: `const fibonacci = (() => {
  const memo = {};
  return function fib(n) {
    if (n in memo) return memo[n];
    if (n <= 1) return n;
    memo[n] = fib(n - 1) + fib(n - 2);
    return memo[n];
  };
})();`,
          explanation: 'This memoized version caches previously computed values, reducing time complexity from O(2^n) to O(n).'
        },
        {
          title: 'Iterative Approach',
          description: 'Convert to iterative implementation for better space complexity',
          difficulty: 'easy',
          impact: 'medium',
          estimated_time: '5-10 minutes',
          code: `function fibonacci(n) {
  if (n <= 1) return n;
  let a = 0, b = 1, temp;
  for (let i = 2; i <= n; i++) {
    temp = a + b;
    a = b;
    b = temp;
  }
  return b;
}`,
          explanation: 'Iterative approach eliminates recursion stack overhead and provides O(1) space complexity.'
        }
      ]);
    }, 1200);
  });

  socket.on('generate_tests', (data: any) => {
    setTimeout(() => {
      socket.emit('test_cases_generated', [
        {
          name: 'fibonacci base cases',
          description: 'Test base cases (0 and 1)',
          type: 'unit',
          framework: 'jest',
          code: `test('fibonacci base cases', () => {
  expect(fibonacci(0)).toBe(0);
  expect(fibonacci(1)).toBe(1);
});`,
          expected_result: 'pass'
        },
        {
          name: 'fibonacci sequence',
          description: 'Test correct sequence calculation',
          type: 'unit',
          framework: 'jest',
          code: `test('fibonacci sequence', () => {
  expect(fibonacci(5)).toBe(5);
  expect(fibonacci(8)).toBe(21);
  expect(fibonacci(10)).toBe(55);
});`,
          expected_result: 'pass'
        },
        {
          name: 'fibonacci edge cases',
          description: 'Test edge cases and error handling',
          type: 'edge_case',
          framework: 'jest',
          code: `test('fibonacci edge cases', () => {
  expect(() => fibonacci(-1)).toThrow();
  expect(fibonacci(0)).toBe(0);
  expect(typeof fibonacci(5)).toBe('number');
});`,
          expected_result: 'pass'
        }
      ]);
    }, 1800);
  });
}
