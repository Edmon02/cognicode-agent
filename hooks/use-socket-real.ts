'use client';

import { useEffect, useState, useRef } from 'react';

// Real socket.io implementation that connects to the backend
export function useSocket() {
  const [socket, setSocket] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const connectionAttempted = useRef(false);

  useEffect(() => {
    // Skip socket initialization on server-side rendering
    if (typeof window === 'undefined') {
      return;
    }

    // Prevent multiple connection attempts
    if (connectionAttempted.current) {
      return;
    }

    connectionAttempted.current = true;

    // Add delay to ensure backend is ready
    const initSocket = async () => {
      try {
        const { io } = await import('socket.io-client');
        
        // Use environment variable for backend URL with fallback to localhost
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        
        console.log('🔌 Connecting to CogniCode backend at:', backendUrl);
        
        // Add initial delay to let backend start up
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const socketInstance = io(backendUrl, {
          transports: ['websocket', 'polling'],
          autoConnect: true,
          reconnection: true,
          reconnectionAttempts: 10,
          reconnectionDelay: 2000,
          reconnectionDelayMax: 10000,
          timeout: 20000,
          forceNew: false,
          upgrade: true,
        });

        socketInstance.on('connect', () => {
          setIsConnected(true);
          setError(null);
          console.log('✅ Connected to CogniCode AI backend at', backendUrl);
          console.log('📡 Socket ID:', socketInstance.id);
        });

        socketInstance.on('connected', (data) => {
          console.log('🎯 Received backend confirmation:', data);
        });

        socketInstance.on('disconnect', (reason) => {
          setIsConnected(false);
          console.log('❌ Disconnected from CogniCode AI backend:', reason);
          // Don't treat normal disconnects as errors
          if (reason === 'io server disconnect' || reason === 'io client disconnect') {
            setError(null);
          }
        });

        socketInstance.on('connect_error', (error: any) => {
          const errorMsg = error?.message || 'Connection failed';
          console.error('⚠️ Connection error:', error);
          setError(errorMsg);
          setIsConnected(false);
        });

        socketInstance.on('error', (error: any) => {
          let errorMsg = 'Socket error';
          
          if (typeof error === 'string') {
            errorMsg = error;
          } else if (error?.message) {
            errorMsg = error.message;
          } else if (typeof error === 'object') {
            errorMsg = JSON.stringify(error);
          }
          
          console.error('❌ Socket error:', error);
          setError(errorMsg);
        });

        socketInstance.on('reconnect', (attemptNumber) => {
          console.log('🔄 Reconnected to backend on attempt', attemptNumber);
          setIsConnected(true);
          setError(null);
        });

        socketInstance.on('reconnect_failed', () => {
          const errorMsg = 'Failed to reconnect after maximum attempts';
          console.error('💥', errorMsg);
          setError(errorMsg);
          setIsConnected(false);
        });

        setSocket(socketInstance);

        // Return cleanup function
        return () => {
          console.log('🧹 Cleaning up socket connection');
          if (socketInstance?.connected) {
            socketInstance.disconnect();
          }
        };
      } catch (error) {
        const errorMsg = `Failed to initialize socket: ${error}`;
        console.error('❌', errorMsg);
        setError(errorMsg);
        setIsConnected(false);
      }
    };

    const cleanup = initSocket();

    // Return cleanup function for useEffect
    return () => {
      cleanup?.then(cleanupFn => cleanupFn?.());
    };
  }, []);

  return { socket, isConnected, error };
}
