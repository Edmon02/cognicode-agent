export interface Issue {
  severity: 'error' | 'warning' | 'info' | 'suggestion';
  message: string;
  line: number;
  column?: number;
  suggestion?: string;
  rule?: string;
}

export interface CodeMetrics {
  complexity: number;
  maintainability: number;
  codeQualityScore: number;
  linesOfCode: number;
  cyclomaticComplexity?: number;
  testCoverage?: number;
}

export interface FunctionInfo {
  name: string;
  startLine: number;
  endLine: number;
  complexity: number;
  parameters?: string[];
  returnType?: string;
}

export interface CodeAnalysis {
  issues: Issue[];
  metrics: CodeMetrics;
  functions: FunctionInfo[];
  timestamp: number;
}

export interface RefactorSuggestion {
  type: 'performance' | 'readability' | 'maintainability';
  description: string;
  originalCode: string;
  refactoredCode: string;
  lineStart: number;
  lineEnd: number;
  impact: 'low' | 'medium' | 'high';
  confidence: number;
  benefits: string[];
  estimatedTimeSeconds?: number;
}

export interface TestCase {
  name: string;
  description: string;
  type: 'unit' | 'integration' | 'e2e';
  code: string;
  expectedResult: 'pass' | 'fail';
  testData?: any;
  framework?: 'jest' | 'mocha' | 'vitest';
}

export interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'error';
  lastRun?: number;
  capabilities: string[];
}

export interface AnalysisSession {
  id: string;
  code: string;
  language: string;
  startTime: number;
  endTime?: number;
  analysis?: CodeAnalysis;
  refactorSuggestions?: RefactorSuggestion[];
  testCases?: TestCase[];
}