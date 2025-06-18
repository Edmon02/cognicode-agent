'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RefactorSuggestion } from '@/types/analysis';
import { Zap, Code, TrendingUp, Check, ArrowRight } from 'lucide-react';
import CodeEditor from './code-editor';
import { useState } from 'react';

interface RefactorPanelProps {
  suggestions: RefactorSuggestion[];
  onApplySuggestion?: (suggestion: RefactorSuggestion) => void;
}

const IMPROVEMENT_ICONS = {
  performance: TrendingUp,
  readability: Code,
  maintainability: Zap,
};

export default function RefactorPanel({ suggestions, onApplySuggestion }: RefactorPanelProps) {
  const [selectedSuggestion, setSelectedSuggestion] = useState<RefactorSuggestion | null>(null);

  if (suggestions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Refactoring Suggestions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Zap className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No refactoring suggestions available</p>
            <p className="text-sm mt-2">Run code analysis first to get intelligent refactoring suggestions</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Refactoring Suggestions</span>
            <Badge variant="secondary">{suggestions.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-80">
            <div className="p-4 space-y-4">
              {suggestions.map((suggestion, index) => {
                const Icon = IMPROVEMENT_ICONS[suggestion.type] || Code;
                
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedSuggestion === suggestion
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                        : 'hover:bg-muted/50'
                    }`}
                    onClick={() => setSelectedSuggestion(suggestion)}
                  >
                    <div className="flex items-start space-x-3">
                      <Icon className="h-4 w-4 mt-0.5 text-blue-600" />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="outline" className="capitalize">
                            {suggestion.type}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            Line {suggestion.lineStart}-{suggestion.lineEnd}
                          </span>
                        </div>
                        <p className="font-medium mb-2">{suggestion.description}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>Impact: {suggestion.impact}</span>
                            <span>Confidence: {suggestion.confidence}%</span>
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedSuggestion(suggestion);
                              }}
                            >
                              <ArrowRight className="h-3 w-3 mr-1" />
                              Preview
                            </Button>
                            <Button
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                onApplySuggestion?.(suggestion);
                              }}
                            >
                              <Check className="h-3 w-3 mr-1" />
                              Apply
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {selectedSuggestion && (
        <Card>
          <CardHeader>
            <CardTitle>Code Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="before" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="before">Before</TabsTrigger>
                <TabsTrigger value="after">After</TabsTrigger>
              </TabsList>
              <TabsContent value="before" className="mt-4">
                <CodeEditor
                  value={selectedSuggestion.originalCode}
                  onChange={() => {}}
                  language="javascript"
                  onLanguageChange={() => {}}
                  readOnly
                />
              </TabsContent>
              <TabsContent value="after" className="mt-4">
                <CodeEditor
                  value={selectedSuggestion.refactoredCode}
                  onChange={() => {}}
                  language="javascript"
                  onLanguageChange={() => {}}
                  readOnly
                />
                <div className="mt-4 p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                  <p className="text-sm font-medium text-green-800 dark:text-green-200">
                    Expected Benefits:
                  </p>
                  <ul className="text-sm text-green-700 dark:text-green-300 mt-1 list-disc list-inside">
                    {selectedSuggestion.benefits.map((benefit, index) => (
                      <li key={index}>{benefit}</li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}