import { spawn } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { loadDicomMapping } from './dicom-mapping';
import { SupabaseTestService } from './supabase';
import { vendorIdentifier, VendorMatch } from './vendor-identification';

export interface TestExecutionConfig {
  pacsUrl: string;
  username?: string;
  password?: string;
  protocols: string[];
  timeout: number;
  verbose: boolean;
  saveToSupabase?: boolean;
  isPublic?: boolean;
  organization?: string;
  contactName?: string;
  contactEmail?: string;
}

export interface TestResult {
  testId: string;
  testName: string;
  protocol: 'QIDO' | 'WADO' | 'STOW';
  status: 'PASS' | 'FAIL' | 'SKIP';
  message: string;
  responseTime: number;
  dicomSection?: string;
  requirement?: 'SHALL' | 'SHOULD' | 'MAY';
  classification?: 'mandatory' | 'recommended' | 'optional';
  requestDetails?: any;
  responseDetails?: any;
  recommendation?: string;
}

export interface TestExecutionResult {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  complianceScore: number;
  conformanceLevel: string;
  averageResponseTime: number;
  maxResponseTime: number;
  minResponseTime: number;
  totalDuration: number;
  testResults: TestResult[];
  recommendations: Recommendation[];
  vendorInfo?: {
    name: string;
    website: string;
    confidence: number;
    recommendations: string[];
  };
}

export interface Recommendation {
  category: 'COMPLIANCE' | 'PERFORMANCE' | 'SECURITY' | 'INTEGRATION' | 'BEST_PRACTICES';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  actionableSteps?: string;
  referenceUrl?: string;
}

export async function executeDicomTests(
  config: TestExecutionConfig
): Promise<TestExecutionResult> {
  const startTime = Date.now();
  
  // Create temporary config file for Python test runner
  const configPath = join(process.cwd(), 'temp-test-config.json');
  writeFileSync(configPath, JSON.stringify({
    pacsUrl: config.pacsUrl,
    username: config.username,
    password: config.password,
    protocols: config.protocols,
    timeout: config.timeout,
    verbose: config.verbose,
  }, null, 2));

  try {
    // Execute the existing Python test framework
    const result = await runPythonTests(config);
    
    // Identify the vendor using HTTP headers
    const vendorMatches = await identifyVendor(config.pacsUrl);
    let vendorInfo = undefined;
    
    if (vendorMatches && vendorMatches.length > 0) {
      const bestMatch = vendorMatches[0];
      const vendorRecommendations = vendorIdentifier.getVendorRecommendations(
        bestMatch.vendor, 
        result.testResults
      );
      
      vendorInfo = {
        name: bestMatch.vendor.name,
        website: bestMatch.vendor.website,
        confidence: bestMatch.confidence,
        recommendations: vendorRecommendations
      };
    }
    
    const endTime = Date.now();
    const totalDuration = (endTime - startTime) / 1000;
    
    return {
      ...result,
      totalDuration,
      vendorInfo,
    };
  } finally {
    // Clean up temp config file
    try {
      // Remove the temporary config file
    } catch (error) {
      console.warn('Failed to clean up temp config file:', error);
    }
  }
}

// Save test results to Supabase
export async function saveTestResultsToSupabase(
  config: TestExecutionConfig,
  result: TestExecutionResult
): Promise<{ success: boolean; testRunId?: string; error?: string }> {
  if (!config.saveToSupabase) {
    return { success: false, error: 'Supabase saving not enabled' };
  }

  // Convert TestResult format to SupabaseTestService format
  const supabaseTestData: any = {
    pacs_url: config.pacsUrl,
    username: config.username,
    password: config.password,
    protocols_tested: config.protocols,
    timeout: config.timeout,
    verbose: config.verbose,
    is_public: config.isPublic || false,
    organization: config.organization,
    contact_name: config.contactName,
    contact_email: config.contactEmail,
    results: result.testResults.map(tr => ({
      test_name: tr.testName,
      protocol: tr.protocol,
      status: tr.status,
      message: tr.message,
      response_time: tr.responseTime,
      request_details: tr.requestDetails || {},
      response_details: tr.responseDetails || {},
      timestamp: new Date().toISOString(),
      recommendation: tr.recommendation,
    })),
    summary: {
      total_tests: result.totalTests,
      passed_tests: result.passedTests,
      failed_tests: result.failedTests,
      skipped_tests: result.skippedTests,
      compliance_score: result.complianceScore,
      conformance_level: result.conformanceLevel,
      average_response_time: result.averageResponseTime,
      max_response_time: result.maxResponseTime,
      min_response_time: result.minResponseTime,
      total_duration: result.totalDuration,
    }
  };

  return await SupabaseTestService.saveTestResults(supabaseTestData);
}

async function runPythonTests(
  config: TestExecutionConfig
): Promise<Omit<TestExecutionResult, 'totalDuration'>> {
  return new Promise((resolve, reject) => {
    // Use the process.cwd() which should be the dicomweb-platform root
    // then navigate to the project root where run_tests.py exists
    const scriptPath = join(process.cwd(), '..', 'run_tests.py');
    
    // Build command arguments
    const args = [
      scriptPath,
      '--pacs-url', config.pacsUrl,
      '--protocols', config.protocols.join(','),
      '--timeout', config.timeout.toString(),
      '--output-format', 'json',
      '--quiet'
    ];

    if (config.username) {
      args.push('--username', config.username);
    }
    if (config.password) {
      args.push('--password', config.password);
    }
    if (config.verbose) {
      args.push('--verbose');
    }

    console.log('Executing Python tests:', args.join(' '));

    const pythonProcess = spawn('python', args, {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout?.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr?.on('data', (data) => {
      stderr += data.toString();
      console.error('Python test stderr:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          // Parse the JSON output
          const lines = stdout.trim().split('\n');
          const jsonLine = lines.find(line => line.startsWith('{'));
          
          if (!jsonLine) {
            throw new Error('No JSON output found in test results');
          }
          
          const testData = JSON.parse(jsonLine);
          const convertedResults = convertTestResults(testData);
          resolve(convertedResults);
        } catch (error) {
          console.error('Failed to parse test results:', error);
          console.error('stdout:', stdout);
          reject(new Error(`Failed to parse test results: ${error}`));
        }
      } else {
        console.error('Python tests failed with code:', code);
        console.error('stderr:', stderr);
        reject(new Error(`Python tests failed with exit code ${code}: ${stderr}`));
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      reject(new Error(`Failed to start test execution: ${error}`));
    });

    // Set timeout
    setTimeout(() => {
      pythonProcess.kill();
      reject(new Error('Test execution timeout'));
    }, config.timeout * 1000 * 2); // Double the configured timeout
  });
}

function convertTestResults(testData: any): Omit<TestExecutionResult, 'totalDuration'> {
  // Load DICOM mapping for test traceability
  const dicomMapping = loadDicomMapping();
  
  const testResults: TestResult[] = [];
  let totalResponseTime = 0;
  let maxResponseTime = 0;
  let minResponseTime = Infinity;
  
  // Convert individual test results
  for (const [protocol, results] of Object.entries(testData.test_results_by_protocol || {})) {
    for (const result of (results as any[])) {
      const testId = result.test_name?.replace(/\s+/g, '_').toUpperCase();
      const mapping = dicomMapping.tests[testId];
      
      const convertedResult: TestResult = {
        testId: testId || result.test_name,
        testName: result.test_name,
        protocol: protocol as 'QIDO' | 'WADO' | 'STOW',
        status: result.status,
        message: result.message,
        responseTime: result.response_time || 0,
        dicomSection: mapping?.dicom_section,
        requirement: mapping?.requirement,
        classification: mapping?.classification,
        requestDetails: result.request_details,
        responseDetails: result.response_details,
        recommendation: result.recommendation,
      };
      
      testResults.push(convertedResult);
      
      // Track response times
      if (result.response_time) {
        totalResponseTime += result.response_time;
        maxResponseTime = Math.max(maxResponseTime, result.response_time);
        minResponseTime = Math.min(minResponseTime, result.response_time);
      }
    }
  }

  // Calculate summary statistics
  const totalTests = testResults.length;
  const passedTests = testResults.filter(r => r.status === 'PASS').length;
  const failedTests = testResults.filter(r => r.status === 'FAIL').length;
  const skippedTests = testResults.filter(r => r.status === 'SKIP').length;
  
  const complianceScore = totalTests > 0 
    ? (passedTests / (totalTests - skippedTests)) * 100 
    : 0;
  
  const conformanceLevel = determineConformanceLevel(complianceScore);
  const averageResponseTime = totalTests > 0 ? totalResponseTime / totalTests : 0;
  
  // Generate recommendations based on results
  const recommendations = generateRecommendations(testResults, complianceScore);
  
  return {
    totalTests,
    passedTests,
    failedTests,
    skippedTests,
    complianceScore,
    conformanceLevel,
    averageResponseTime,
    maxResponseTime: maxResponseTime === 0 ? 0 : maxResponseTime,
    minResponseTime: minResponseTime === Infinity ? 0 : minResponseTime,
    testResults,
    recommendations,
  };
}

function determineConformanceLevel(score: number): string {
  if (score >= 90) return 'EXCELLENT';
  if (score >= 75) return 'GOOD';
  if (score >= 60) return 'ACCEPTABLE';
  if (score >= 40) return 'POOR';
  return 'NON_COMPLIANT';
}

function generateRecommendations(testResults: TestResult[], complianceScore: number): Recommendation[] {
  const recommendations: Recommendation[] = [];
  
  // High-level recommendations based on overall score
  if (complianceScore < 60) {
    recommendations.push({
      category: 'COMPLIANCE',
      priority: 'CRITICAL',
      title: 'Urgent DICOMweb Compliance Issues',
      description: 'Your PACS system has significant DICOMweb compliance gaps that require immediate attention.',
      actionableSteps: '1. Review failed test results\n2. Contact vendor support\n3. Schedule compliance assessment',
      referenceUrl: 'https://www.dicomstandard.org/using/dicomweb/',
    });
  }
  
  // Protocol-specific recommendations
  const failedByProtocol = testResults.reduce((acc, result) => {
    if (result.status === 'FAIL') {
      acc[result.protocol] = (acc[result.protocol] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);
  
  for (const [protocol, count] of Object.entries(failedByProtocol)) {
    if (count > 3) {
      recommendations.push({
        category: 'COMPLIANCE',
        priority: 'HIGH',
        title: `${protocol}-RS Implementation Issues`,
        description: `Your ${protocol}-RS implementation has ${count} failures. This protocol is essential for DICOMweb compliance.`,
        actionableSteps: `1. Review ${protocol}-RS specific test failures\n2. Verify endpoint URLs and authentication\n3. Check server configuration\n4. Update PACS software if needed`,
        referenceUrl: `https://www.dicomstandard.org/dicomweb/${protocol.toLowerCase()}-rs/`,
      });
    }
  }
  
  // Performance recommendations
  const slowTests = testResults.filter(r => r.responseTime > 2.0);
  if (slowTests.length > 0) {
    recommendations.push({
      category: 'PERFORMANCE',
      priority: 'MEDIUM',
      title: 'Performance Optimization Needed',
      description: `${slowTests.length} tests showed response times > 2 seconds. This may impact clinical workflows.`,
      actionableSteps: '1. Check network latency\n2. Optimize database queries\n3. Implement caching\n4. Review server resources',
    });
  }
  
  return recommendations;
}

// Vendor identification function
async function identifyVendor(pacsUrl: string): Promise<VendorMatch[] | null> {
  try {
    // Make a simple HEAD request to get server headers
    const response = await fetch(pacsUrl, {
      method: 'HEAD',
      headers: {
        'User-Agent': 'DICOMweb-Tester/1.0'
      }
    });
    
    if (!response.ok) {
      console.log(`Failed to fetch headers from ${pacsUrl}: ${response.status}`);
      return null;
    }
    
    // Extract headers and server info
    const headers: { [key: string]: string } = {};
    response.headers.forEach((value, key) => {
      headers[key.toLowerCase()] = value;
    });
    
    // Identify vendor using the vendor identifier
    const vendorMatches = await vendorIdentifier.identifyVendor(pacsUrl, {
      headers,
      server: response.headers.get('server') || undefined,
      statusCode: response.status,
    });
    
    return vendorMatches;
  } catch (error) {
    console.warn('Vendor identification failed:', error);
    return null;
  }
}