'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TestCase } from '@/types/analysis';
import { TestTube, Copy, Download, CheckCircle, XCircle } from 'lucide-react';
import CodeEditor from './code-editor';
import { toast } from 'sonner';

interface TestGenPanelProps {
  testCases: TestCase[];
}

export default function TestGenPanel({ testCases }: TestGenPanelProps) {
  const handleCopyTests = async () => {
    const allTests = testCases.map(test => test.code).join('\n\n');
    try {
      await navigator.clipboard.writeText(allTests);
      toast.success('All tests copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy tests');
    }
  };

  const handleDownloadTests = () => {
    const allTests = testCases.map(test => test.code).join('\n\n');
    const element = document.createElement('a');
    const file = new Blob([allTests], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'generated-tests.test.js';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('Test file downloaded!');
  };

  if (testCases.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Unit Test Generation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <TestTube className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No unit tests generated yet</p>
            <p className="text-sm mt-2">Analyze your code first, then generate comprehensive unit tests</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const passedTests = testCases.filter(test => test.expectedResult === 'pass').length;
  const failedTests = testCases.filter(test => test.expectedResult === 'fail').length;

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TestTube className="h-5 w-5" />
              <span>Generated Unit Tests</span>
              <Badge variant="secondary">{testCases.length}</Badge>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={handleCopyTests}>
                <Copy className="h-4 w-4 mr-2" />
                Copy All
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownloadTests}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{testCases.length}</div>
              <div className="text-sm text-muted-foreground">Total Tests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-500">{passedTests}</div>
              <div className="text-sm text-muted-foreground">Expected Pass</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-500">{failedTests}</div>
              <div className="text-sm text-muted-foreground">Expected Fail</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Test Cases */}
      <Card>
        <CardHeader>
          <CardTitle>Test Cases</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Tabs defaultValue="list" className="w-full">
            <div className="px-4 pt-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="list">Test List</TabsTrigger>
                <TabsTrigger value="full">Full Test Suite</TabsTrigger>
              </TabsList>
            </div>
            
            <TabsContent value="list" className="mt-4">
              <ScrollArea className="h-80">
                <div className="p-4 space-y-4">
                  {testCases.map((testCase, index) => (
                    <div key={index} className="p-4 rounded-lg border">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{testCase.name}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {testCase.description}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{testCase.type}</Badge>
                          {testCase.expectedResult === 'pass' ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-muted rounded-md p-3">
                        <pre className="text-xs font-mono overflow-x-auto">
                          <code>{testCase.code}</code>
                        </pre>
                      </div>
                      
                      {testCase.testData && (
                        <div className="mt-3">
                          <h5 className="text-sm font-medium mb-2">Test Data:</h5>
                          <div className="bg-blue-50 dark:bg-blue-950 rounded-md p-2">
                            <pre className="text-xs font-mono">
                              <code>{JSON.stringify(testCase.testData, null, 2)}</code>
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="full" className="mt-4">
              <div className="p-4">
                <CodeEditor
                  value={testCases.map(test => test.code).join('\n\n')}
                  onChange={() => {}}
                  language="javascript"
                  onLanguageChange={() => {}}
                  readOnly
                />
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}