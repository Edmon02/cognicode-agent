'use client';

import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Copy, Download } from 'lucide-react';
import { useTheme } from 'next-themes';
import { toast } from 'sonner';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  onLanguageChange: (language: string) => void;
  readOnly?: boolean;
}

const SUPPORTED_LANGUAGES = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'csharp', label: 'C#' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
];

export default function CodeEditor({ 
  value, 
  onChange, 
  language, 
  onLanguageChange, 
  readOnly = false 
}: CodeEditorProps) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      toast.success('Code copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy code');
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([value], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `code.${language === 'javascript' ? 'js' : language === 'typescript' ? 'ts' : language === 'python' ? 'py' : 'txt'}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Code downloaded!');
  };

  if (!mounted) {
    return (
      <div className="h-96 bg-muted animate-pulse rounded-md flex items-center justify-center">
        <span className="text-muted-foreground">Loading editor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
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
        
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
        </div>
      </div>

      <div className="border rounded-md overflow-hidden">
        <Editor
          height="400px"
          language={language}
          value={value}
          onChange={(value) => onChange(value || '')}
          theme={theme === 'dark' ? 'vs-dark' : 'light'}
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            wordWrap: 'on',
            automaticLayout: true,
            scrollBeyondLastLine: false,
            tabSize: 2,
            insertSpaces: true,
            bracketPairColorization: { enabled: true },
            formatOnPaste: true,
            formatOnType: true,
          }}
        />
      </div>
    </div>
  );
}