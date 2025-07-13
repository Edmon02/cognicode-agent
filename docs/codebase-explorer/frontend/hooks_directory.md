# The `hooks/` Directory: Encapsulating Reusable Frontend Logic

Welcome to the `hooks/` directory, a place where we distill complex or reusable frontend logic into clean, manageable, and shareable pieces of code: Custom React Hooks. In React, hooks let you "hook into" React state and lifecycle features from function components. Custom hooks take this a step further by allowing us to create our own reusable stateful logic.

For CogniCode Agent, the most critical custom hook is the one responsible for managing the WebSocket connection to our backend. This is the lifeline for real-time analysis, refactoring suggestions, and test generation results.

## Core Hook We'll Dissect:

*   **`use-socket-real.ts`** (and its potential variants): This hook is the star of our real-time show, encapsulating the setup, management, and event handling for our Socket.IO connection.

Let's unravel the magic behind this crucial piece of our frontend architecture!

---

## 🔌 `use-socket-real.ts`: The Real-Time Communication Engine

The `use-socket-real.ts` hook is the heart of CogniCode Agent's real-time communication system. It encapsulates all the logic for establishing, maintaining, and interacting with the Socket.IO connection to our Python backend. By abstracting this complexity into a custom hook, we make our page components (like `app/page.tsx`) cleaner and more focused on their presentational and core application logic.

**Purpose:**
*   To initialize and manage a Socket.IO client instance.
*   To track the connection status (`isConnected`) and any connection errors (`error`).
*   To provide the `socket` instance to components that need to emit events or register listeners.
*   To handle common Socket.IO lifecycle events like `connect`, `disconnect`, `connect_error`, `reconnect`, etc., providing console logs and updating state accordingly.
*   To ensure the socket connection is properly cleaned up when the component using the hook unmounts.
*   To prevent multiple connection attempts and only run on the client-side.

Let's dive into its inner workings:

```typescript
// hooks/use-socket-real.ts
'use client'; // 1. This hook is for client-side usage only

import { useEffect, useState, useRef } from 'react';
// Note: 'socket.io-client' is dynamically imported later

// 2. The custom hook definition
export function useSocket() {
  // 3. State variables to manage socket instance, connection status, and errors
  const [socket, setSocket] = useState<any>(null); // Holds the socket.io client instance
  const [isConnected, setIsConnected] = useState(false); // True if connected, false otherwise
  const [error, setError] = useState<string | null>(null); // Stores any connection error messages

  // 4. useRef to track if a connection attempt has already been made
  // This helps prevent multiple connections if the hook re-runs.
  const connectionAttempted = useRef(false);

  // 5. useEffect: The core logic for socket initialization and event handling
  useEffect(() => {
    // 6. Guard: Skip socket initialization on server-side rendering (SSR)
    if (typeof window === 'undefined') {
      return; // Socket.IO client only works in the browser
    }

    // 7. Guard: Prevent multiple connection attempts if already tried
    if (connectionAttempted.current) {
      return;
    }
    connectionAttempted.current = true; // Mark that an attempt is now being made

    // 8. Asynchronous function to initialize the socket
    const initSocket = async () => {
      try {
        // 9. Dynamically import 'socket.io-client'
        // This can help with bundle splitting and ensures it's only loaded client-side.
        const { io } = await import('socket.io-client');

        // 10. Determine backend URL from environment variable or fallback
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        // Note: The fallback was 'http://localhost:5000' in page.tsx's .env example.
        // Using 8000 here as per the hook's code. Consistency check needed for actual project.

        console.log('🔌 Connecting to CogniCode backend at:', backendUrl);

        // 11. Initial delay: A small grace period for the backend to be ready,
        // especially in local development when frontend and backend start simultaneously.
        await new Promise(resolve => setTimeout(resolve, 1000));

        // 12. Create the socket instance with specific configurations
        const socketInstance = io(backendUrl, {
          transports: ['websocket', 'polling'], // Preferred transports
          autoConnect: true, // Connect automatically on creation
          reconnection: true, // Enable auto-reconnection
          reconnectionAttempts: 10, // Max number of reconnection attempts
          reconnectionDelay: 2000, // Initial delay before retrying (ms)
          reconnectionDelayMax: 10000, // Max delay between retries (ms)
          timeout: 20000, // Connection timeout (ms)
          forceNew: false, // Whether to create a new connection if one already exists for the namespace
          upgrade: true, // Whether to attempt upgrading the transport (e.g., from polling to websocket)
        });

        // 13. Registering listeners for standard Socket.IO events
        socketInstance.on('connect', () => {
          setIsConnected(true);
          setError(null); // Clear any previous errors
          console.log('✅ Connected to CogniCode AI backend at', backendUrl);
          console.log('📡 Socket ID:', socketInstance.id);
        });

        socketInstance.on('connected', (data) => { // Custom 'connected' event from our backend
          console.log('🎯 Received backend confirmation:', data);
        });

        socketInstance.on('disconnect', (reason) => {
          setIsConnected(false);
          console.log('❌ Disconnected from CogniCode AI backend:', reason);
          // Important: Don't treat intentional disconnects as errors that persist in UI
          if (reason === 'io server disconnect' || reason === 'io client disconnect') {
            setError(null); // Clear error if it was a clean disconnect
          }
          // If it's an unexpected disconnect, an error might be set by 'connect_error'
        });

        socketInstance.on('connect_error', (err: any) => {
          const errorMsg = err?.message || 'Connection failed';
          console.error('⚠️ Connection error:', err);
          setError(errorMsg); // Set the error state
          setIsConnected(false);
        });

        // Generic 'error' event from the socket library itself (less common for connection issues)
        socketInstance.on('error', (err: any) => {
          let errorMsg = 'Socket error';
          if (typeof err === 'string') errorMsg = err;
          else if (err?.message) errorMsg = err.message;
          else if (typeof err === 'object') errorMsg = JSON.stringify(err);

          console.error('❌ Socket error:', err);
          setError(errorMsg);
          // isConnected might already be false due to connect_error or disconnect
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

        // 14. Update the state with the created socket instance
        setSocket(socketInstance);

        // 15. Return a cleanup function for this async effect
        return () => {
          console.log('🧹 Cleaning up socket connection (from initSocket async scope)');
          if (socketInstance?.connected) {
            socketInstance.disconnect(); // Disconnect if still connected
          }
        };
      } catch (err) { // Catch errors during dynamic import or initial io() call
        const errorMsg = `Failed to initialize socket: ${err}`;
        console.error('❌', errorMsg);
        setError(errorMsg);
        setIsConnected(false);
      }
    };

    // 16. Call the async initSocket function
    const cleanupPromise = initSocket();

    // 17. useEffect cleanup function: This runs when the component using the hook unmounts.
    // It ensures that the cleanup function returned by initSocket (if any) is called.
    return () => {
      // Since initSocket is async, it returns a Promise that resolves to the cleanup function.
      // We need to handle this promise.
      cleanupPromise?.then(cleanupFnFromAsync => {
        if (cleanupFnFromAsync) {
          cleanupFnFromAsync();
        }
      });
      // Also, as a fallback or if the promise didn't resolve to a function
      if (socket && socket.connected) { // Access socket from state directly for cleanup
          console.log('🧹 Cleaning up socket connection (from useEffect direct cleanup)');
          socket.disconnect();
      }
      connectionAttempted.current = false; // Reset for potential future re-mounts (e.g., in HMR)
    };
  }, [socket]); // 18. Dependency array for useEffect. Re-run if `socket` state changes.
                // Consider if this dependency is truly needed or if `[]` is more appropriate
                // given `connectionAttempted.current` guard. If `socket` is in dep array,
                // and `setSocket` is called, it will re-run. The `connectionAttempted` ref
                // aims to prevent re-initialization. Usually, for one-time setup, `[]` is used.
                // However, if `socket` could be externally nulled and needs re-init, this might be intentional.
                // For this hook's purpose (single, persistent connection), `[]` is likely more correct
                // with the `connectionAttempted.current` guard.

  // 19. Return the socket instance, connection status, and any error
  return { socket, isConnected, error };
}
```

**Deconstructing the `useSocket` Hook:**

1.  **`'use client';`**: Essential, as this hook manages client-side WebSocket connections and uses React's client-side hooks.

2.  **`export function useSocket() { ... }`**: The definition of our custom hook. Components can call `useSocket()` to get access to its returned values.

3.  **State Variables (`useState`)**:
    *   `socket`: Stores the actual Socket.IO client instance once it's created. Initialized to `null`. The type `any` is used here; a more specific type from `socket.io-client` (like `Socket`) would be better for type safety.
    *   `isConnected`: A boolean flag indicating the current connection status. This is useful for UI elements to show, for example, a "Connected" or "Disconnected" status.
    *   `error`: A string or `null`, holding any error message related to the socket connection.

4.  **`connectionAttempted = useRef(false);`**: A `useRef` hook is used here. Unlike `useState`, changing a `ref`'s `.current` value does not trigger a re-render. This `ref` acts as an instance variable to ensure that the socket initialization logic runs only once, even if the component using the hook re-renders for other reasons.

5.  **`useEffect(() => { ... }, [socket]);`**: This is where the main action happens. The `useEffect` hook is used for side effects, and connecting to a WebSocket server is definitely a side effect.
    *   The dependency array `[socket]` means this effect will re-run if the `socket` state variable itself changes. This is a bit unusual for a setup effect that should run once. Typically, for one-time setup, an empty dependency array `[]` is used, and the `connectionAttempted.current` ref handles the "run once" logic. If `socket` is in the dependency array, then calling `setSocket(socketInstance)` inside this effect *will* cause it to run again. The `connectionAttempted.current` check is crucial to prevent re-creating the socket in such a loop. A more standard approach might be to use `[]` as the dependency array if the intent is truly a one-time setup per component mount.

6.  **Server-Side Rendering Guard (`if (typeof window === 'undefined')`)**: Socket.IO client library is browser-specific. This check prevents the socket initialization code from running during server-side rendering (SSR) in Next.js, where `window` is not defined.

7.  **Multiple Attempts Guard (`if (connectionAttempted.current)`)**: This check, using the `useRef` variable, ensures that `initSocket` is only called once per lifecycle of the hook's usage in a component.

8.  **`initSocket = async () => { ... }`**: An asynchronous function to handle the socket setup. This is `async` because dynamic `import()` is asynchronous.

9.  **Dynamic Import (`await import('socket.io-client')`)**: The `socket.io-client` library is imported dynamically. This means it's only loaded into the browser's memory when `initSocket` is actually called. This can be good for initial page load performance, as the library isn't part of the main JavaScript bundle if the socket isn't immediately needed or if this hook isn't used on every page.

10. **Backend URL (`process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'`)**: The hook tries to get the backend URL from a Next.js public environment variable (`NEXT_PUBLIC_BACKEND_URL`). If it's not set, it falls back to `http://localhost:8000`. *It's worth noting that the `page.tsx` and main README mentioned `http://localhost:5000` for the backend. This discrepancy should be resolved in a real project for consistency.*

11. **Initial Delay (`await new Promise(resolve => setTimeout(resolve, 1000));`)**: A 1-second delay is introduced before attempting to connect. This can be a pragmatic workaround in local development where the frontend might try to connect before the backend server is fully up and running.

12. **Socket Instance Creation (`const socketInstance = io(...)`)**: This is where the actual Socket.IO client is created.
    *   `transports: ['websocket', 'polling']`: Specifies the preferred connection methods. It will try WebSocket first, then fall back to HTTP long-polling if WebSockets aren't available.
    *   `autoConnect: true`: The client will attempt to connect as soon as it's instantiated.
    *   `reconnection: true`, `reconnectionAttempts`, `reconnectionDelay`, `reconnectionDelayMax`: These options configure the automatic reconnection behavior if the connection drops. The client will try to reconnect up to 10 times, with increasing delays between attempts.
    *   `timeout`: How long to wait for a connection before timing out.
    *   `forceNew: false`: If `true`, it would create a new connection every time, even if one already exists for that URL/namespace. `false` allows reusing connections.
    *   `upgrade: true`: Allows the transport to be upgraded (e.g., from polling to WebSocket).

13. **Standard Event Listeners**: The hook sets up listeners for common Socket.IO events:
    *   `connect`: Fired when the connection is successfully established. Sets `isConnected` to `true` and clears errors.
    *   `connected`: This appears to be a custom event emitted by the backend upon successful connection, used here for logging.
    *   `disconnect`: Fired when the connection is lost. Sets `isConnected` to `false`. It thoughtfully clears the `error` state if the disconnect was intentional (client or server initiated it).
    *   `connect_error`: Fired if the initial connection attempt fails. Sets an error message and `isConnected` to `false`.
    *   `error`: A generic error event from the socket library. Sets an error message.
    *   `reconnect`: Fired upon successful reconnection.
    *   `reconnect_failed`: Fired if all reconnection attempts fail.

14. **`setSocket(socketInstance);`**: The newly created `socketInstance` is stored in the component's state. This makes the `socket` object available to the component using the hook.

15. **Cleanup Function from `initSocket`**: The `initSocket` function itself returns a cleanup function. This inner cleanup function is designed to be called if `initSocket` completes and later the main `useEffect` needs to clean up *this specific instance* of the socket. It disconnects the `socketInstance` if it's connected.

16. **`const cleanupPromise = initSocket();`**: Calls the async setup function.

17. **`useEffect` Cleanup Function**: This is the main cleanup logic for the `useEffect` hook.
    *   It handles the promise returned by `initSocket` to correctly call the nested cleanup function.
    *   It also includes a fallback cleanup that directly accesses the `socket` from the state to disconnect if needed. This part might be a bit redundant if the promise handling is solid but acts as a safeguard.
    *   `connectionAttempted.current = false;`: Resets the ref. This is important if the component could unmount and then remount later (e.g., due to Hot Module Replacement in development, or conditional rendering).

18. **Dependency Array `[socket]`**: As discussed in point #5, having `socket` in the dependency array of the main `useEffect` while also setting `socket` within that effect, and relying on `connectionAttempted.current` to prevent re-runs, is a complex pattern. A simpler approach for a one-time setup is often `useEffect(() => { /* setup */ return () => { /* cleanup */ }; }, [])` with the `useRef` guard inside. The current setup might be trying to handle a very specific edge case or could be simplified.

19. **Return Value (`{ socket, isConnected, error }`)**: The hook exposes the `socket` instance, the `isConnected` boolean, and any `error` string. Components using this hook can destructure these values to interact with the socket and react to its state.

**In essence, `use-socket-real.ts` is a robust custom hook that abstracts the complexities of Socket.IO client management. It handles initialization, connection state, errors, reconnections, and cleanup, providing a simple and reactive interface for components to use real-time communication.** It demonstrates careful consideration for client-side execution, preventing multiple initializations, and managing the socket lifecycle. The dynamic import of `socket.io-client` and the initial delay are practical touches for real-world applications.

---
Return to: [Frontend Overview](README.md) | [Hooks Directory Overview](#the-hooks-directory-encapsulating-reusable-frontend-logic)
Next: [The `lib/` Directory: Frontend Utilities & Helpers](./lib_directory.md)
