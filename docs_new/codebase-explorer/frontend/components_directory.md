# The `components/` Directory: Building Blocks of the UI

Welcome to the workshop of our frontend – the `components/` directory! If `app/page.tsx` is the main stage production, then the files in `components/` are the individual actors, props, and set pieces that bring the show to life. This directory is home to reusable React components that make up the user interface of CogniCode Agent.

We follow a common pattern:
*   **`components/ui/`**: This sub-directory typically houses general-purpose UI primitives, often sourced from `shadcn/ui` (like Button, Card, Dialog, Tabs). These are foundational elements, styled and ready to be composed into more complex structures. We'll acknowledge their use but focus our deep dive on application-specific components.
*   **`components/*.tsx` (root of `components/`)**: These are custom components tailored specifically for CogniCode Agent's functionality. Examples include the code editor itself, panels for displaying analysis results, and the application header.

Our exploration here will focus on a few core, application-specific components to understand how they are built, how they manage their state, and how they interact with the rest of the application.

## Core Components We'll Dissect:

1.  **`code-editor.tsx`**: The interactive canvas where users input their code. Understanding its integration with the Monaco Editor is key.
2.  **`analysis-panel.tsx`**: The component responsible for displaying the detailed results from the Linter Agent.
3.  **`header.tsx`**: The application's main header, likely handling navigation, branding, and global actions or status indicators.

Let's get under the hood of these crucial UI building blocks!

*(Detailed walkthroughs for selected components will follow.)*

---

## ⌨️ `code-editor.tsx`: The Developer's Canvas

The `CodeEditor` component is arguably one of the most critical pieces of our frontend. It provides the interactive text area where users write or paste their code for analysis. This component leverages the powerful `@monaco-editor/react` library, which brings the core engine of Visual Studio Code's editor directly into our React application.

**Purpose:**
*   To provide a feature-rich code editing experience.
*   To allow users to select the programming language for syntax highlighting and analysis.
*   To manage the code input as state and communicate changes back to the parent component (`app/page.tsx`).
*   To offer utility actions like copying the code to the clipboard and downloading it as a file.
*   To adapt its theme based on the application's light/dark mode.

Let's look at its structure and key functionalities:

```typescript
// components/code-editor.tsx
'use client'; // 1. Client component, as it uses hooks and browser APIs

import { useState, useEffect } from 'react'; // React hooks for state and side effects
import Editor from '@monaco-editor/react'; // 2. The star: Monaco Editor component
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'; // 3. Shadcn/ui Select component
import { Button } from '@/components/ui/button'; // Shadcn/ui Button
import { Copy, Download } from 'lucide-react'; // Icons for buttons
import { useTheme } from 'next-themes'; // 4. Hook to access current theme (light/dark)
import { toast } from 'sonner'; // For notifications

// 5. Props interface for type safety and clarity
interface CodeEditorProps {
  value: string; // Current code content (controlled component)
  onChange: (value: string) => void; // Callback when code changes
  language: string; // Current selected language
  onLanguageChange: (language: string) => void; // Callback when language changes
  readOnly?: boolean; // Optional: to make the editor read-only
}

// 6. List of supported languages for the dropdown
const SUPPORTED_LANGUAGES = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  // ... other languages (Python, Java, C++, C#, Go, Rust)
];

// 7. The CodeEditor component definition
export default function CodeEditorComponent({ // Renamed to avoid conflict with imported Editor
  value,
  onChange,
  language,
  onLanguageChange,
  readOnly = false
}: CodeEditorProps) {
  const { theme } = useTheme(); // 8. Get current theme ('light' or 'dark')
  const [mounted, setMounted] = useState(false); // 9. State to track if component is mounted

  // 10. useEffect to set mounted to true after initial render
  // This helps prevent hydration mismatches with theme-dependent editor rendering
  useEffect(() => {
    setMounted(true);
  }, []);

  // 11. Handler to copy code to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value); // Uses browser Clipboard API
      toast.success('Code copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy code');
    }
  };

  // 12. Handler to download code as a file
  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([value], { type: 'text/plain' }); // Create a text blob
    element.href = URL.createObjectURL(file); // Create a URL for the blob
    // Determine file extension based on language
    element.download = `code.${language === 'javascript' ? 'js' : language === 'typescript' ? 'ts' : language === 'python' ? 'py' : 'txt'}`;
    document.body.appendChild(element); // Temporarily add to DOM
    element.click(); // Programmatically click to trigger download
    document.body.removeChild(element); // Clean up
    toast.success('Code downloaded!');
  };

  // 13. Conditional rendering: Show a loading state until the component is mounted
  // This is important because the Monaco editor might not render correctly
  // on the server or before the theme is determined.
  if (!mounted) {
    return (
      <div className="h-96 bg-muted animate-pulse rounded-md flex items-center justify-center">
        <span className="text-muted-foreground">Loading editor...</span>
      </div>
    );
  }

  // 14. Main component JSX
  return (
    <div className="space-y-4"> {/* Outer container with spacing */}
      {/* Top bar: Language selector and action buttons */}
      <div className="flex items-center justify-between">
        {/* Language Selector Dropdown */}
        <Select value={language} onValueChange={onLanguageChange}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Select language" />
          </SelectTrigger>
          <SelectContent>
            {SUPPORTED_LANGUAGES.map((lang) => (
              <SelectItem key={lang.value} value={lang.value}>
                {lang.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Action Buttons: Copy and Download */}
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="h-4 w-4 mr-2" /> Copy
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" /> Download
          </Button>
        </div>
      </div>

      {/* The Monaco Editor instance itself, wrapped in a bordered div */}
      <div className="border rounded-md overflow-hidden">
        <Editor
          height="400px" // Fixed height for the editor
          language={language} // Sets syntax highlighting and editor features for the language
          value={value} // The code content (controlled input)
          onChange={(currentCodeValue) => onChange(currentCodeValue || '')} // Callback for code changes
          theme={theme === 'dark' ? 'vs-dark' : 'light'} // Adapts editor theme to app theme
          options={{ // 15. Configuration options for Monaco Editor
            readOnly, // Is the editor read-only?
            minimap: { enabled: false }, // We've disabled the minimap
            fontSize: 14,
            lineNumbers: 'on', // Show line numbers
            wordWrap: 'on', // Wrap long lines
            automaticLayout: true, // Adjust layout automatically on container resize
            scrollBeyondLastLine: false, // Don't allow scrolling past the last line
            tabSize: 2, // Standard 2 spaces for tabs
            insertSpaces: true, // Insert spaces when tab is pressed
            bracketPairColorization: { enabled: true }, // Colorize matching brackets
            formatOnPaste: true, // Automatically format code on paste
            formatOnType: true, // Automatically format code as user types (language-dependent)
          }}
        />
      </div>
    </div>
  );
}
```

**Narrative & Deeper Dive:**

1.  **`'use client';`**: This component is a "Client Component" because it uses React hooks (`useState`, `useEffect`) and interacts with browser APIs (like `navigator.clipboard` and `document.createElement` for download). The Monaco editor itself is also a client-side library.

2.  **`@monaco-editor/react`**: This is the core dependency that brings the Monaco Editor into our React app. It provides the `<Editor />` component that we use.

3.  **`@/components/ui/select`**: We use a `Select` component (from `shadcn/ui`) to allow users to choose the programming language. This is a good example of composing UI primitives.

4.  **`next-themes`**: The `useTheme` hook allows the editor to match the application's current theme (light or dark), providing a consistent user experience.

5.  **`CodeEditorProps` Interface**: Defines the contract for this component.
    *   `value` and `onChange`: Make it a controlled component, meaning its content is managed by state in the parent (`app/page.tsx`).
    *   `language` and `onLanguageChange`: Similar control for the selected language.
    *   `readOnly`: An optional prop to disable editing, which could be useful for displaying code snippets that shouldn't be modified.

6.  **`SUPPORTED_LANGUAGES`**: An array of objects defining the languages available in the dropdown. This makes it easy to add or remove languages.

7.  **Component Name `CodeEditorComponent`**: The component is named `CodeEditorComponent` in the implementation to avoid a naming collision with the imported `Editor` from `@monaco-editor/react`. This is a common pattern.

8.  **`const { theme } = useTheme();`**: Retrieves the current theme string (e.g., "dark", "light", or "system").

9.  **`mounted` State**: The `mounted` state (and its `useEffect`) is a common trick to deal with potential hydration issues when a component's rendering depends on client-side information (like the theme) that might not be available or accurate during server-side rendering. By only rendering the full editor `if (mounted)`, we ensure it renders correctly after the client-side environment is fully established.

10. **`useEffect(() => { setMounted(true); }, []);`**: This effect runs once after the component mounts on the client, setting `mounted` to `true`. The empty dependency array `[]` ensures it only runs once.

11. **`handleCopy` Function**:
    *   Uses the `navigator.clipboard.writeText()` browser API to copy the current editor content to the clipboard. This is a modern, asynchronous API.
    *   Provides user feedback using `toast.success` or `toast.error`.

12. **`handleDownload` Function**:
    *   A clever way to trigger a file download in the browser:
        *   Creates an `<a>` (anchor) element programmatically.
        *   Creates a `Blob` (Binary Large Object) containing the code text.
        *   Generates an object URL for this blob using `URL.createObjectURL()`.
        *   Sets the `href` of the anchor to this URL and the `download` attribute to a filename (with an extension based on the selected language).
        *   Appends the anchor to the `document.body`, simulates a click on it, and then removes it. This dance triggers the browser's download mechanism.

13. **Loading State (`if (!mounted)`)**: Before the component is fully mounted (and the theme is reliably known), it displays a simple loading skeleton (an animated pulsing box). This improves the perceived performance and prevents the editor from flashing or rendering incorrectly initially.

14. **Main JSX Structure**:
    *   The top section contains the language `Select` dropdown and the "Copy" / "Download" `Button`s, arranged using flexbox for layout.
    *   The `<Editor />` component itself is wrapped in a `div` with `border rounded-md overflow-hidden` classes to give it a neat, contained appearance.

15. **`<Editor />` Component & Options**: This is where the Monaco magic happens.
    *   `height`: Sets a fixed height for the editor.
    *   `language`: Passed from props, controls syntax highlighting and language-specific features.
    *   `value`: The code content, making it a controlled component.
    *   `onChange`: Callback function that updates the parent's state with the new code. The `value || ''` ensures we always pass a string.
    *   `theme`: Dynamically set to `'vs-dark'` if the app theme is dark, otherwise `'light'`. Monaco has its own theme names.
    *   **`options` Prop**: This is a rich configuration object for Monaco:
        *   `readOnly`: Makes the editor non-editable if true.
        *   `minimap: { enabled: false }`: Hides the code minimap. A design choice for simplicity here.
        *   `fontSize`, `lineNumbers`, `wordWrap`: Basic editor appearance and behavior.
        *   `automaticLayout: true`: Essential for responsive design; the editor will adjust if its container resizes.
        *   `scrollBeyondLastLine: false`: Prevents scrolling past the end of the code.
        *   `tabSize: 2`, `insertSpaces: true`: Common code formatting preferences.
        *   `bracketPairColorization: { enabled: true }`: A very helpful feature for visualizing matching brackets.
        *   `formatOnPaste: true`, `formatOnType: true`: Enables automatic code formatting, which can significantly improve code consistency (though its effectiveness depends on the language services available in Monaco for the current language).

**In summary, `components/code-editor.tsx` is a well-crafted component that encapsulates the Monaco Editor, provides essential user controls for language selection and code actions, and thoughtfully handles client-side rendering considerations like theming and loading states. It acts as the primary input gateway for the entire application.**

---
Return to: [Frontend Overview](README.md) | [Components Directory Overview](#the-components-directory-building-blocks-of-the-ui)
Next Component: [`analysis-panel.tsx`](#-analysis-paneltsx-displaying-ai-insights)

---

## 📊 `analysis-panel.tsx`: Displaying AI Insights

The `AnalysisPanel` component is responsible for rendering the findings of the Linter Agent. It takes the structured analysis data, which includes issues, code metrics, and identified functions, and presents it to the user in a clear, organized, and easily digestible format. This component is crucial for translating the raw AI output into actionable insights for the developer.

**Purpose:**
*   To display a summary of the code analysis, including counts of errors, warnings, and a quality score.
*   To present detailed code metrics like complexity and maintainability.
*   To list all identified issues (errors, warnings, info, suggestions) with their severity, message, line number, and any suggested fixes.
*   To provide a loading state while analysis is in progress.
*   To show an informative message if no analysis has been run or if no issues are found.

Let's examine its implementation:

```typescript
// components/analysis-panel.tsx
'use client'; // Client component due to conditional rendering and UI logic

// Shadcn/ui and Lucide icon imports
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { CodeAnalysis, Issue } from '@/types/analysis'; // Type definitions for analysis data
import { AlertTriangle, CheckCircle, XCircle, Info, Zap } from 'lucide-react'; // Icons

// Props interface for the component
interface AnalysisPanelProps {
  analysis: CodeAnalysis | null; // The analysis data object, or null if no analysis
  isLoading: boolean; // Boolean to indicate if analysis is in progress
}

// 1. Mapping severity levels to icons and colors for visual cues
const SEVERITY_ICONS = {
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  suggestion: Zap, // Assuming 'suggestion' is a possible severity
};

const SEVERITY_COLORS = {
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
  suggestion: 'text-purple-500',
};

export default function AnalysisPanel({ analysis, isLoading }: AnalysisPanelProps) {
  // 2. Loading State: Display a spinner and progress if isLoading is true
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Analyzing Code...</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm text-muted-foreground">Running AI analysis agents...</span>
            </div>
            {/* Progress bar might be controlled by a more granular progress state in a real scenario */}
            <Progress value={75} className="w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  // 3. No Analysis Data State: Prompt user to start analysis
  if (!analysis) {
    return (
      <Card>
        <CardHeader><CardTitle>Code Analysis</CardTitle></CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Info className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Click "Analyze" to start code analysis</p>
            <p className="text-sm mt-2">AI agents will check for bugs, style issues, and performance optimizations</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 4. Data Extraction and Preparation:
  // Safely access nested data with fallbacks to prevent runtime errors if parts of 'analysis' are missing.
  const issues = analysis.issues || [];
  const metrics = analysis.metrics || {
    complexity: 0, maintainability: 10, linesOfCode: 0, codeQualityScore: 10 // Default structure
  };
  const functions = analysis.functions || [];

  // Calculate counts for summary display
  const errorCount = issues.filter(i => i.severity === 'error').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;
  const infoCount = issues.filter(i => i.severity === 'info').length; // Or other severities

  // 5. Main JSX for displaying analysis results
  return (
    <div className="space-y-6"> {/* Outer container for spacing between cards */}
      {/* Summary Card: Overview of errors, warnings, info, and quality score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Analysis Summary</span>
            {/* Green checkmark if no issues are found */}
            {issues.length === 0 && (
              <CheckCircle className="h-5 w-5 text-green-500" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Display error, warning, info counts and quality score */}
            <div className="text-center">
              <div className="text-2xl font-bold text-red-500">{errorCount}</div>
              <div className="text-sm text-muted-foreground">Errors</div>
            </div>
            {/* ... similar divs for warnings, info, and quality score ... */}
            <div className="text-center">
              <div className="text-2xl font-bold text-green-500">{metrics.codeQualityScore || 10}</div>
              <div className="text-sm text-muted-foreground">Quality Score</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metrics Card: Detailed code metrics like complexity and maintainability */}
      <Card>
        <CardHeader><CardTitle>Code Metrics</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div> {/* Complexity Metric */}
              <div className="flex justify-between text-sm">
                <span>Complexity</span>
                <span>{metrics.complexity || 0}/10</span> {/* Display as score out of 10 */}
              </div>
              <Progress value={(metrics.complexity || 0) * 10} className="mt-1" />
            </div>
            <div> {/* Maintainability Metric */}
              <div className="flex justify-between text-sm">
                <span>Maintainability</span>
                <span>{metrics.maintainability || 10}/10</span>
              </div>
              <Progress value={(metrics.maintainability || 10) * 10} className="mt-1" />
            </div>
          </div>
          <Separator className="my-4" /> {/* Visual separator */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>Lines of Code: <span className="font-medium">{metrics.linesOfCode || 0}</span></div>
            {(functions && functions.length) > 0 && ( // Conditionally display function count
              <div>Functions: <span className="font-medium">{functions.length}</span></div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Issues Card: List of all identified issues */}
      <Card>
        <CardHeader><CardTitle>Issues Found</CardTitle></CardHeader>
        <CardContent className="p-0"> {/* Remove padding for full-width ScrollArea */}
          {issues.length === 0 ? (
            // Message when no issues are found
            <div className="p-6 text-center text-muted-foreground">
              <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
              <p className="font-medium">No issues found!</p>
              <p className="text-sm">Your code looks great.</p>
            </div>
          ) : (
            // Scrollable area for listing issues
            <ScrollArea className="h-80">
              <div className="p-4 space-y-4">
                {issues.map((issue: Issue, index: number) => { // Type annotation for issue
                  const Icon = SEVERITY_ICONS[issue.severity] || Info; // Fallback icon
                  const colorClass = SEVERITY_COLORS[issue.severity] || 'text-gray-500'; // Fallback color

                  return (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg border">
                      <Icon className={`h-4 w-4 mt-0.5 ${colorClass}`} /> {/* Severity icon */}
                      <div className="flex-1 min-w-0"> {/* Ensures content wraps */}
                        <div className="flex items-center space-x-2">
                          <Badge variant={issue.severity === 'error' ? 'destructive' : 'secondary'}>
                            {issue.severity} {/* Severity badge */}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            Line {issue.line} {/* Line number of the issue */}
                          </span>
                        </div>
                        <p className="font-medium mt-1">{issue.message}</p> {/* Issue message */}
                        {issue.suggestion && ( // Conditionally display suggestion
                          <p className="text-sm text-muted-foreground mt-1">
                            💡 {issue.suggestion}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Key Aspects and Narrative:**

1.  **Visual Indicators (`SEVERITY_ICONS`, `SEVERITY_COLORS`):** The component predefines mappings for issue severities to specific icons (from `lucide-react`) and text colors. This is a great way to provide immediate visual cues to the user about the nature of an issue – errors are red with an X, warnings yellow with a triangle, etc. It makes the list of issues much easier to scan.

2.  **Loading State (`if (isLoading)`):** When the parent component (`app/page.tsx`) indicates that analysis is in progress (`isLoading={true}`), this panel displays a user-friendly loading message with a spinner and a progress bar. This manages user expectation and provides feedback that the system is working. The progress bar here is illustrative; a more sophisticated implementation might get granular progress from the backend.

3.  **Empty/Initial State (`if (!analysis)`):** If no analysis data is available (e.g., the user hasn't run an analysis yet), the panel shows an informative message prompting the user to click "Analyze." This guides new users.

4.  **Safe Data Handling (`analysis.issues || []`):** The component defensively accesses properties of the `analysis` object. For instance, `analysis.issues || []` ensures that if `analysis.issues` is undefined or null, it defaults to an empty array, preventing runtime errors when trying to `.map()` or `.filter()` it. Similar defaults are provided for `metrics` and `functions`. This makes the component robust against partially formed analysis data.

5.  **Structured Display with Cards:** The analysis results are broken down into logical sections using `Card` components from `shadcn/ui`:
    *   **Summary Card:** Gives a quick overview – total errors, warnings, info, and an overall "Quality Score." The immediate green `CheckCircle` icon if `issues.length === 0` is a nice positive reinforcement.
    *   **Metrics Card:** Displays quantitative data like "Complexity" and "Maintainability" (often presented as scores out of 10 with `Progress` bars) and "Lines of Code" / "Functions."
    *   **Issues Card:** This is where the detailed list of identified problems appears.

6.  **Issue Rendering (`issues.map`)**:
    *   If there are issues, they are rendered within a `ScrollArea` to handle potentially long lists without making the page excessively long.
    *   Each issue is displayed with its severity icon, severity badge, line number, a descriptive message, and any available suggestion. The layout uses flexbox to align these elements neatly.
    *   The use of `min-w-0` on a flex child is a common trick to ensure text wrapping works correctly within flex layouts.

7.  **Clarity and Readability:** The use of icons, badges, varying font weights, and muted text for secondary information (like line numbers or suggestions) all contribute to making the analysis results easier to parse and understand.

**In essence, `AnalysisPanel.tsx` serves as the primary diagnostic screen for the developer. It takes potentially complex data from the AI backend and transforms it into a structured, visually intuitive, and actionable report, helping the user quickly understand the state of their code.**

---
Return to: [Frontend Overview](README.md) | [Components Directory Overview](#the-components-directory-building-blocks-of-the-ui)
Next Component: [`header.tsx`](#-headertsx-the-applications-command-bar)

---

## 🔝 `header.tsx`: The Application's Command Bar

The `Header` component sits at the top of our application, providing consistent branding, navigation, global actions (like theme toggling), and important status information (like backend connectivity). It's the user's constant point of reference as they interact with CogniCode Agent.

**Purpose:**
*   Display the application name and logo/icon.
*   Provide a visual indicator of the backend connection status.
*   Offer quick access to external links (like the GitHub repository).
*   Allow users to toggle between light and dark themes.

Let's see how it's constructed:

```typescript
// components/header.tsx
'use client'; // Client component for theme toggling and dynamic status

// UI imports from shadcn/ui and lucide-react for icons
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Moon, Sun, Github, Brain, Wifi, WifiOff } from 'lucide-react';
import { useTheme } from 'next-themes'; // Hook for theme management
import Link from 'next/link'; // Next.js Link component for client-side navigation

// 1. Props interface for the Header
interface HeaderProps {
  isConnected?: boolean; // Optional: current backend connection status
  connectionError?: string | null; // Optional: any connection error message
}

// 2. The Header component definition
export default function Header({ isConnected = false, connectionError }: HeaderProps) {
  // 3. useTheme hook to get current theme and function to set theme
  const { theme, setTheme } = useTheme();

  return (
    // 4. Semantic <header> element with styling for border, background, and blur effect
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-4"> {/* Centered container with padding */}
        <div className="flex items-center justify-between"> {/* Flexbox for layout */}

          {/* Left Section: App Name and Connection Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2"> {/* App name and icon */}
              <Brain className="h-6 w-6 text-blue-600" />
              <span className="text-xl font-bold">CogniCode Agent</span>
            </div>

            {/* Connection Status Indicator Badge */}
            <Badge
              variant={isConnected ? "default" : "destructive"} // Changes color based on status
              className="flex items-center space-x-1"
            >
              {isConnected ? ( // Conditional rendering for connected state
                <>
                  <Wifi className="h-3 w-3" />
                  <span>Connected</span>
                </>
              ) : ( // Conditional rendering for disconnected state
                <>
                  <WifiOff className="h-3 w-3" />
                  <span>Disconnected</span>
                </>
              )}
            </Badge>
            {/* Future enhancement: Display connectionError tooltip on the badge if present */}
          </div>

          {/* Right Section: GitHub Link and Theme Toggle Button */}
          <div className="flex items-center space-x-4">
            {/* GitHub Link */}
            <Link href="https://github.com/Edmon02/cognicode-agent" target="_blank">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Github className="h-4 w-4" />
                <span>GitHub</span>
              </Button>
            </Link>

            {/* Theme Toggle Button */}
            <Button
              variant="ghost" // Ghost variant for a less intrusive look
              size="sm" // Smaller button size
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} // Toggle logic
            >
              {/* Sun icon for light mode, transitions out in dark mode */}
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              {/* Moon icon for dark mode, transitions in in dark mode */}
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span> {/* Accessibility text */}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
```

**Journey Through the Header:**

1.  **`HeaderProps` Interface**: Defines the props this component accepts.
    *   `isConnected`: A boolean (defaulting to `false`) passed down from `app/page.tsx` to indicate the WebSocket connection status.
    *   `connectionError`: A string or null, also from the parent, to potentially display connection error details (though not explicitly used in the current JSX, it's good practice to pass it if available for future enhancements like tooltips).

2.  **Component Definition**: `Header({ isConnected = false, connectionError }: HeaderProps)` receives these props.

3.  **`useTheme()` Hook**: This hook from `next-themes` is essential for theme functionality. It provides:
    *   `theme`: The current active theme string (e.g., "light", "dark").
    *   `setTheme`: A function to change the current theme.

4.  **Styling the `<header>`**:
    *   `border-b`: Adds a bottom border.
    *   `bg-background/95`: Sets the background color using the CSS variable `--background` (defined in `globals.css` for theming) with 95% opacity.
    *   `backdrop-blur supports-[backdrop-filter]:bg-background/60`: This creates a "frosted glass" effect. If the browser supports `backdrop-filter`, it applies a blur and sets the background to the `--background` color with 60% opacity. This is a common technique for modern sticky headers.

5.  **Layout Structure**: Inside the `<header>`, a `container` div centers content with `mx-auto`. The main content of the header is arranged in a flexbox (`flex items-center justify-between`) to position items on the left and right.

6.  **Left Section - Branding & Status**:
    *   **App Name & Icon**: Displays the "CogniCode Agent" name alongside a `Brain` icon from `lucide-react`, providing clear branding.
    *   **Connection Status `Badge`**: This is a dynamic element.
        *   The `variant` of the `Badge` changes based on `isConnected` (`default` for connected, `destructive` for disconnected), providing an immediate color cue (e.g., green/blue for connected, red for disconnected, depending on theme).
        *   It conditionally renders a `Wifi` icon and "Connected" text or a `WifiOff` icon and "Disconnected" text. This gives users at-a-glance information about the crucial backend link.

7.  **Right Section - Actions**:
    *   **GitHub Link**: Uses the Next.js `<Link>` component for client-side navigation (though `target="_blank"` makes it open in a new tab, so standard `<a>` would also work here). It's styled as a ghost `Button` with a `Github` icon.
    *   **Theme Toggle `Button`**:
        *   `onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}`: Simple yet effective logic to toggle between 'light' and 'dark' themes. If the current theme is 'light', it sets it to 'dark', and vice-versa.
        *   **Icon Animation**: It cleverly uses two icons (`Sun` and `Moon`) and Tailwind CSS transition/transform classes (`rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0` for the Sun, and similar for the Moon). This creates a neat animation where the Sun icon is visible in light mode and rotates/scales out when switching to dark mode, while the Moon icon does the opposite. The `absolute` positioning on the Moon icon allows them to occupy the same space for a smooth transition.
        *   `<span className="sr-only">Toggle theme</span>`: Important for accessibility, providing a text description for screen readers as the button itself only contains icons.

**The `Header` component is a compact yet vital part of the UI. It successfully combines branding, crucial status information, and global user actions like theme switching into a persistent and aesthetically pleasing bar at the top of the application.** It demonstrates good use of conditional rendering for status, icon-based actions, and the power of `next-themes` for theme management.

---
Return to: [Frontend Overview](README.md) | [Components Directory Overview](#the-components-directory-building-blocks-of-the-ui)
Next: [The `hooks/` Directory](./hooks_directory.md)
