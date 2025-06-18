'use client';

import { Button } from '@/components/ui/button';
import { Moon, Sun, Github, Brain } from 'lucide-react';
import { useTheme } from 'next-themes';
import Link from 'next/link';

export default function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-6 w-6 text-blue-600" />
            <span className="text-xl font-bold">CogniCode Agent</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link href="https://github.com/Edmon02/cognicode-agent" target="_blank">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Github className="h-4 w-4" />
                <span>GitHub</span>
              </Button>
            </Link>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}