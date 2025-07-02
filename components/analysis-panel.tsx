'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { CodeAnalysis, Issue } from '@/types/analysis';
import { AlertTriangle, CheckCircle, XCircle, Info, Zap } from 'lucide-react';

interface AnalysisPanelProps {
  analysis: CodeAnalysis | null;
  isLoading: boolean;
}

const SEVERITY_ICONS = {
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  suggestion: Zap,
};

const SEVERITY_COLORS = {
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
  suggestion: 'text-purple-500',
};

export default function AnalysisPanel({ analysis, isLoading }: AnalysisPanelProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analyzing Code...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm text-muted-foreground">Running AI analysis agents...</span>
            </div>
            <Progress value={75} className="w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Code Analysis</CardTitle>
        </CardHeader>
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

  // Safely extract data with fallbacks
  const issues = analysis.issues || [];
  const metrics = analysis.metrics || {
    complexity: 0,
    maintainability: 10,
    linesOfCode: 0,
    codeQualityScore: 10
  };
  const functions = analysis.functions || [];
  
  const errorCount = issues.filter(i => i.severity === 'error').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;
  const infoCount = issues.filter(i => i.severity === 'info').length;

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Analysis Summary</span>
            {issues.length === 0 && (
              <CheckCircle className="h-5 w-5 text-green-500" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-500">{errorCount}</div>
              <div className="text-sm text-muted-foreground">Errors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-500">{warningCount}</div>
              <div className="text-sm text-muted-foreground">Warnings</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-500">{infoCount}</div>
              <div className="text-sm text-muted-foreground">Info</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-500">{metrics.codeQualityScore || 10}</div>
              <div className="text-sm text-muted-foreground">Quality Score</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Metrics Card */}
      <Card>
        <CardHeader>
          <CardTitle>Code Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex justify-between text-sm">
                <span>Complexity</span>
                <span>{metrics.complexity || 0}/10</span>
              </div>
              <Progress value={(metrics.complexity || 0) * 10} className="mt-1" />
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Maintainability</span>
                <span>{metrics.maintainability || 10}/10</span>
              </div>
              <Progress value={(metrics.maintainability || 10) * 10} className="mt-1" />
            </div>
          </div>
          <Separator className="my-4" />
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>Lines of Code: <span className="font-medium">{metrics.linesOfCode || 0}</span></div>
            {(functions && functions.length) > 0 && (
              <div>Functions: <span className="font-medium">{functions.length}</span></div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Issues Card */}
      <Card>
        <CardHeader>
          <CardTitle>Issues Found</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {issues.length === 0 ? (
            <div className="p-6 text-center text-muted-foreground">
              <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
              <p className="font-medium">No issues found!</p>
              <p className="text-sm">Your code looks great.</p>
            </div>
          ) : (
            <ScrollArea className="h-80">
              <div className="p-4 space-y-4">
                {issues.map((issue, index) => {
                  const Icon = SEVERITY_ICONS[issue.severity];
                  const colorClass = SEVERITY_COLORS[issue.severity];

                  return (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg border">
                      <Icon className={`h-4 w-4 mt-0.5 ${colorClass}`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <Badge variant={issue.severity === 'error' ? 'destructive' : 'secondary'}>
                            {issue.severity}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            Line {issue.line}
                          </span>
                        </div>
                        <p className="font-medium mt-1">{issue.message}</p>
                        {issue.suggestion && (
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