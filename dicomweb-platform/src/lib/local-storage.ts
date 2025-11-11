// Local SQLite storage for testing DICOMweb platform
// This provides a simple way to store test results without requiring Supabase
import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';

export interface LocalTestResult {
  id: string;
  testName: string;
  protocol: 'QIDO' | 'WADO' | 'STOW';
  status: 'PASS' | 'FAIL' | 'SKIP';
  message: string;
  responseTime: number;
  dicomSection?: string;
  classification?: string;
  requirement?: string;
  timestamp: string;
}

export interface LocalTestRun {
  id: string;
  pacsUrl: string;
  startTime: string;
  endTime?: string;
  status: 'RUNNING' | 'COMPLETED' | 'FAILED';
  protocols: string[];
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  complianceScore: number;
  conformanceLevel: string;
  testResults: LocalTestResult[];
  shareToken?: string;
  createdAt: string;
}

// Simple in-memory storage for local testing
const localStorage = new Map<string, LocalTestRun>();

// Test results storage
const testResultsStorage = new Map<string, LocalTestResult[]>();

export class LocalStorageService {
  // Save a test run
  static saveTestRun(testRun: Omit<LocalTestRun, 'id' | 'createdAt'>): string {
    const id = randomUUID();
    const createdAt = new Date().toISOString();
    
    const fullTestRun: LocalTestRun = {
      ...testRun,
      id,
      createdAt,
    };
    
    localStorage.set(id, fullTestRun);
    testResultsStorage.set(id, testRun.testResults);
    
    return id;
  }

  // Get a test run by ID
  static getTestRun(id: string): LocalTestRun | null {
    return localStorage.get(id) || null;
  }

  // Get test results for a run
  static getTestResults(testRunId: string): LocalTestResult[] {
    return testResultsStorage.get(testRunId) || [];
  }

  // Update test run status
  static updateTestRun(id: string, updates: Partial<LocalTestRun>): void {
    const existing = localStorage.get(id);
    if (existing) {
      const updated = { ...existing, ...updates };
      localStorage.set(id, updated);
    }
  }

  // List all test runs (for debugging)
  static listTestRuns(): LocalTestRun[] {
    return Array.from(localStorage.values()).sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  // Clear all data (for testing)
  static clear(): void {
    localStorage.clear();
    testResultsStorage.clear();
  }
}