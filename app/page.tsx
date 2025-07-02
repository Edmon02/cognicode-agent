'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import CodeEditor from '@/components/code-editor';
import AnalysisPanel from '@/components/analysis-panel';
import RefactorPanel from '@/components/refactor-panel';
import TestGenPanel from '@/components/testgen-panel';
import Header from '@/components/header';
import { useSocket } from '@/hooks/use-socket-real';
import { CodeAnalysis, RefactorSuggestion, TestCase } from '@/types/analysis';
import { Play, Zap, TestTube, Code2, Brain, Shield } from 'lucide-react';
import { toast } from 'sonner';

export default function Home() {
  const [code, setCode] = useState<string>(`function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Example usage
console.log(fibonacci(10));`);
  
  const [language, setLanguage] = useState<string>('javascript');
  const [analysis, setAnalysis] = useState<CodeAnalysis | null>(null);
  const [refactorSuggestions, setRefactorSuggestions] = useState<RefactorSuggestion[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisMessage, setAnalysisMessage] = useState('');

  const { socket, isConnected, error } = useSocket();

  // Show connection status
  useEffect(() => {
    if (error) {
      // Only show error if it's a meaningful error message
      if (error !== 'Connection failed' || !isConnected) {
        toast.error(`Connection issue: ${error}`);
      }
    } else if (isConnected) {
      toast.success('Connected to CogniCode AI backend');
    }
  }, [isConnected, error]);

  // Handle socket events
  useEffect(() => {
    if (!socket) return;

    socket.on('analysis_complete', (data: CodeAnalysis) => {
      console.log('📊 Analysis complete:', data);
      setAnalysis(data);
      setIsAnalyzing(false);
      setAnalysisProgress(100);
      toast.success('Code analysis complete!');
    });

    socket.on('refactor_suggestions', (data: RefactorSuggestion[]) => {
      console.log('🔄 Refactor suggestions:', data);
      setRefactorSuggestions(data);
      toast.success('Refactoring suggestions generated!');
    });

    socket.on('test_cases_generated', (data: TestCase[]) => {
      console.log('🧪 Test cases generated:', data);
      setTestCases(data);
      toast.success('Unit tests generated!');
    });

    socket.on('analysis_progress', (data: any) => {
      console.log('📈 Progress data:', data);
      
      // Handle both object and number formats
      if (typeof data === 'object' && data !== null) {
        if (typeof data.progress === 'number') {
          setAnalysisProgress(data.progress);
        }
        if (typeof data.message === 'string') {
          setAnalysisMessage(data.message);
        }
      } else if (typeof data === 'number') {
        setAnalysisProgress(data);
        setAnalysisMessage('');
      }
    });

    socket.on('error', (error: any) => {
      console.error('❌ Socket error:', error);
      
      let errorMessage = 'Unknown error occurred';
      if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        errorMessage = error.message || JSON.stringify(error);
      }
      
      toast.error(`Error: ${errorMessage}`);
      setIsAnalyzing(false);
    });

    return () => {
      socket.off('analysis_complete');
      socket.off('refactor_suggestions');
      socket.off('test_cases_generated');
      socket.off('analysis_progress');
      socket.off('error');
    };
  }, [socket]);

  const analyzeCode = useCallback(() => {
    if (!socket || !code.trim()) {
      toast.error('Please enter some code to analyze');
      return;
    }

    console.log('🔬 Starting analysis for code:', code.substring(0, 100) + '...');
    console.log('📡 Language:', language);
    console.log('🔌 Socket connected:', isConnected);

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisMessage('Initializing...');
    setAnalysis(null);
    setRefactorSuggestions([]);
    setTestCases([]);

    socket.emit('analyze_code', {
      code,
      language,
      timestamp: Date.now()
    });

    toast.info('Starting code analysis...');
  }, [socket, code, language, isConnected]);

  const generateRefactoring = useCallback(() => {
    if (!socket || !code.trim()) {
      toast.error('Please enter some code to refactor');
      return;
    }

    socket.emit('generate_refactoring', {
      code,
      language,
      analysis: analysis ? analysis.issues : []
    });

    toast.info('Generating refactoring suggestions...');
  }, [socket, code, language, analysis]);

  const generateTests = useCallback(() => {
    if (!socket || !code.trim()) {
      toast.error('Please enter some code to generate tests for');
      return;
    }

    socket.emit('generate_tests', {
      code,
      language,
      functions: analysis?.functions || []
    });

    toast.info('Generating unit tests...');
  }, [socket, code, language, analysis]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <Header isConnected={isConnected} connectionError={error} />
      
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              CogniCode Agent
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Multi-agent AI system for real-time code analysis, intelligent refactoring, and automated test generation
          </p>
          <div className="flex items-center justify-center space-x-4 mt-6">
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-green-600" />
              <span className="text-sm text-muted-foreground">Privacy-First</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-yellow-600" />
              <span className="text-sm text-muted-foreground">Real-time</span>
            </div>
            <div className="flex items-center space-x-2">
              <Code2 className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-muted-foreground">Multi-language</span>
            </div>
          </div>
        </div>

        {/* Connection Status */}
        <Card className="w-full">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected to AI Agents' : 'Disconnected from AI Agents'}
                </span>
              </div>
              {isAnalyzing && (
                <div className="flex items-center space-x-2">
                  <Progress value={analysisProgress} className="w-32" />
                  <span className="text-sm text-muted-foreground">{analysisProgress}%</span>
                  {analysisMessage && (
                    <span className="text-xs text-muted-foreground ml-2">{analysisMessage}</span>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Code Editor Section */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <Code2 className="h-5 w-5" />
                    <span>Code Editor</span>
                  </CardTitle>
                  <div className="flex space-x-2">
                    <Button 
                      onClick={analyzeCode} 
                      disabled={isAnalyzing || !isConnected}
                      className="flex items-center space-x-2"
                    >
                      <Play className="h-4 w-4" />
                      <span>Analyze</span>
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CodeEditor
                  value={code}
                  onChange={setCode}
                  language={language}
                  onLanguageChange={setLanguage}
                />
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <Button 
                    variant="outline" 
                    onClick={generateRefactoring}
                    disabled={!isConnected || !analysis}
                    className="flex items-center space-x-2"
                  >
                    <Zap className="h-4 w-4" />
                    <span>Refactor</span>
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={generateTests}
                    disabled={!isConnected || !analysis}
                    className="flex items-center space-x-2"
                  >
                    <TestTube className="h-4 w-4" />
                    <span>Generate Tests</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Results Section */}
          <div>
            <Tabs defaultValue="analysis" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="analysis" className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>Analysis</span>
                  {analysis && analysis.issues.length > 0 && (
                    <Badge variant="destructive" className="ml-1">
                      {analysis.issues.length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="refactor" className="flex items-center space-x-2">
                  <Zap className="h-4 w-4" />
                  <span>Refactor</span>
                  {refactorSuggestions.length > 0 && (
                    <Badge variant="secondary" className="ml-1">
                      {refactorSuggestions.length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="tests" className="flex items-center space-x-2">
                  <TestTube className="h-4 w-4" />
                  <span>Tests</span>
                  {testCases.length > 0 && (
                    <Badge variant="secondary" className="ml-1">
                      {testCases.length}
                    </Badge>
                  )}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="analysis" className="mt-6">
                <AnalysisPanel 
                  analysis={analysis} 
                  isLoading={isAnalyzing}
                />
              </TabsContent>

              <TabsContent value="refactor" className="mt-6">
                <RefactorPanel 
                  suggestions={refactorSuggestions}
                  onApplySuggestion={(suggestion) => {
                    setCode(suggestion.refactoredCode);
                    toast.success('Refactoring applied!');
                  }}
                />
              </TabsContent>

              <TabsContent value="tests" className="mt-6">
                <TestGenPanel testCases={testCases} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  );
}