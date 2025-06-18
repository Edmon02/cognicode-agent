'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function useSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
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

    socketInstance.on('connect_error', (error) => {
      console.log('Connection failed:', error);
      setIsConnected(false);
      
      // For demo purposes, simulate connection after delay
      setTimeout(() => {
        setIsConnected(true);
        simulateBackendResponses(socketInstance);
      }, 2000);
    });

    setSocket(socketInstance);

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
    };
  }, []);

  return { socket, isConnected };
}

// Demo function to simulate backend AI responses
function simulateBackendResponses(socket: Socket) {
  socket.on('analyze_code', (data) => {
    console.log('Analyzing code:', data);
    
    // Simulate analysis progress
    let progress = 0;
    const progressInterval = setInterval(() => {
      progress += 25;
      socket.emit('analysis_progress', progress);
      
      if (progress >= 100) {
        clearInterval(progressInterval);
        
        // Simulate analysis results
        setTimeout(() => {
          socket.emit('analysis_complete', {
            issues: [
              {
                severity: 'warning',
                message: 'Function has exponential time complexity',
                line: 3,
                suggestion: 'Consider using memoization to improve performance'
              },
              {
                severity: 'info',
                message: 'Consider adding type annotations',
                line: 1,
                suggestion: 'Add JSDoc or TypeScript types for better code documentation'
              }
            ],
            metrics: {
              complexity: 7,
              maintainability: 6,
              codeQualityScore: 75,
              linesOfCode: 6
            },
            functions: [
              {
                name: 'fibonacci',
                startLine: 1,
                endLine: 4,
                complexity: 7
              }
            ]
          });
        }, 500);
      }
    }, 200);
  });

  socket.on('generate_refactoring', (data) => {
    console.log('Generating refactoring:', data);
    
    setTimeout(() => {
      socket.emit('refactor_suggestions', [
        {
          type: 'performance',
          description: 'Optimize recursive fibonacci with memoization',
          originalCode: data.code,
          refactoredCode: `const fibonacciMemo = (() => {
  const cache = {};
  return function fibonacci(n) {
    if (n in cache) return cache[n];
    if (n <= 1) return n;
    cache[n] = fibonacci(n - 1) + fibonacci(n - 2);
    return cache[n];
  };
})();

// Example usage
console.log(fibonacciMemo(10));`,
          lineStart: 1,
          lineEnd: 4,
          impact: 'high',
          confidence: 95,
          benefits: [
            'Reduces time complexity from O(2^n) to O(n)',
            'Eliminates redundant calculations',
            'Improves performance for large inputs'
          ]
        }
      ]);
    }, 1000);
  });

  socket.on('generate_tests', (data) => {
    console.log('Generating tests:', data);
    
    setTimeout(() => {
      socket.emit('test_cases_generated', [
        {
          name: 'should return 0 for fibonacci(0)',
          description: 'Test base case where n is 0',
          type: 'unit',
          code: `test('fibonacci(0) should return 0', () => {
  expect(fibonacci(0)).toBe(0);
});`,
          expectedResult: 'pass',
          testData: { input: 0, expected: 0 }
        },
        {
          name: 'should return 1 for fibonacci(1)',
          description: 'Test base case where n is 1',
          type: 'unit',
          code: `test('fibonacci(1) should return 1', () => {
  expect(fibonacci(1)).toBe(1);
});`,
          expectedResult: 'pass',
          testData: { input: 1, expected: 1 }
        },
        {
          name: 'should calculate fibonacci sequence correctly',
          description: 'Test recursive calculation for various inputs',
          type: 'unit',
          code: `test('fibonacci sequence calculation', () => {
  expect(fibonacci(5)).toBe(5);
  expect(fibonacci(8)).toBe(21);
  expect(fibonacci(10)).toBe(55);
});`,
          expectedResult: 'pass',
          testData: { 
            inputs: [5, 8, 10], 
            expected: [5, 21, 55] 
          }
        }
      ]);
    }, 1500);
  });
}