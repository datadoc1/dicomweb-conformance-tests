// Supabase integration for DICOMweb test results
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'https://fakomdpruvqbxcsgeoez.supabase.co';
const supabaseKey = process.env.SUPABASE_PUBLISHABLE_KEY || 'sb_publishable_SuYRFMWlNBIFztRIqvsWmA_hKZN0G3y';

// Create Supabase client for server-side operations
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: false
  }
});

// Test result interface matching Python TestResult structure
export interface TestResultData {
  test_name: string;
  protocol: 'QIDO' | 'WADO' | 'STOW';
  status: 'PASS' | 'FAIL' | 'SKIP';
  message: string;
  response_time: number;
  request_details: any;
  response_details: any;
  timestamp: string;
  recommendation?: string;
}

// Test run interface
export interface TestRunData {
  pacs_url: string;
  username?: string;
  password?: string;
  protocols_tested: string[];
  timeout: number;
  verbose: boolean;
  is_public: boolean;
  organization?: string;
  contact_name?: string;
  contact_email?: string;
  results: TestResultData[];
  summary: {
    total_tests: number;
    passed_tests: number;
    failed_tests: number;
    skipped_tests: number;
    compliance_score: number;
    conformance_level: string;
    average_response_time: number;
    max_response_time: number;
    min_response_time: number;
    total_duration: number;
  };
}

export class SupabaseTestService {
  // Save test results to Supabase
  static async saveTestResults(testRunData: TestRunData): Promise<{ success: boolean; testRunId?: string; error?: string }> {
    try {
      // First, try to identify or create vendor and PACS
      const vendorId = await this.identifyOrCreateVendor(testRunData.pacs_url);
      const pacsId = await this.identifyOrCreatePACS(vendorId, testRunData.pacs_url);

      // Calculate compliance score and conformance level
      const { compliance_score, conformance_level } = this.calculateComplianceScore(testRunData.summary);

      // Create test run record
      const { data: testRun, error: testRunError } = await supabase
        .from('test_runs')
        .insert({
          pacs_id: pacsId,
          run_identifier: this.generateRunIdentifier(),
          status: 'COMPLETED',
          start_time: new Date().toISOString(),
          end_time: new Date().toISOString(),
          protocols_tested: testRunData.protocols_tested.join(','),
          timeout: testRunData.timeout,
          verbose: testRunData.verbose,
          total_tests: testRunData.summary.total_tests,
          passed_tests: testRunData.summary.passed_tests,
          failed_tests: testRunData.summary.failed_tests,
          skipped_tests: testRunData.summary.skipped_tests,
          compliance_score: compliance_score,
          conformance_level: conformance_level,
          average_response_time: testRunData.summary.average_response_time,
          max_response_time: testRunData.summary.max_response_time,
          min_response_time: testRunData.summary.min_response_time,
          total_duration: testRunData.summary.total_duration,
          is_public: testRunData.is_public,
          share_token: testRunData.is_public ? this.generateShareToken() : null,
          contact_email: testRunData.contact_email,
          organization: testRunData.organization,
          contact_name: testRunData.contact_name,
        })
        .select()
        .single();

      if (testRunError) {
        console.error('Error creating test run:', testRunError);
        return { success: false, error: `Failed to create test run: ${testRunError.message}` };
      }

      // Save individual test results
      const testResults = testRunData.results.map(result => ({
        test_run_id: testRun.id,
        test_name: result.test_name,
        protocol: result.protocol,
        status: result.status,
        message: result.message,
        response_time: result.response_time,
        request_details: result.request_details,
        response_details: result.response_details,
        timestamp: result.timestamp,
        recommendation: result.recommendation,
      }));

      const { error: resultsError } = await supabase
        .from('test_results')
        .insert(testResults);

      if (resultsError) {
        console.error('Error saving test results:', resultsError);
        return { success: false, error: `Failed to save test results: ${resultsError.message}` };
      }

      return { success: true, testRunId: testRun.id };

    } catch (error) {
      console.error('Unexpected error saving test results:', error);
      return { success: false, error: `Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
  }

  // Parse Python test output into structured data
  static parsePythonTestOutput(output: string): TestRunData | null {
    try {
      // Try to extract JSON data from Python output
      // The Python script typically outputs JSON results
      const jsonMatch = output.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        console.warn('No JSON data found in Python output');
        return null;
      }

      const testData = JSON.parse(jsonMatch[0]);
      
      // Parse the test results structure
      const testResults: TestResultData[] = [];
      let totalTests = 0, passedTests = 0, failedTests = 0, skippedTests = 0;
      let totalResponseTime = 0, maxResponseTime = 0, minResponseTime = Infinity;
      let protocols: Set<string> = new Set();

      if (testData.test_results && Array.isArray(testData.test_results)) {
        for (const result of testData.test_results) {
          testResults.push({
            test_name: result.test_name || 'Unknown Test',
            protocol: (result.protocol || 'QIDO').toUpperCase(),
            status: result.status || 'FAIL',
            message: result.message || 'No message',
            response_time: result.response_time || 0,
            request_details: result.request_details || {},
            response_details: result.response_details || {},
            timestamp: result.timestamp || new Date().toISOString(),
            recommendation: result.recommendation,
          });

          totalTests++;
          if (result.status === 'PASS') passedTests++;
          else if (result.status === 'FAIL') failedTests++;
          else if (result.status === 'SKIP') skippedTests++;

          const responseTime = result.response_time || 0;
          totalResponseTime += responseTime;
          maxResponseTime = Math.max(maxResponseTime, responseTime);
          minResponseTime = Math.min(minResponseTime, responseTime);
          protocols.add(result.protocol);
        }
      }

      // Calculate metrics
      const complianceScore = totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
      const averageResponseTime = totalTests > 0 ? totalResponseTime / totalTests : 0;
      const conformanceLevel = complianceScore >= 90 ? 'CONFORMANT' :
                              complianceScore >= 75 ? 'MOSTLY_CONFORMANT' :
                              complianceScore >= 50 ? 'PARTIALLY_CONFORMANT' :
                              'NON_CONFORMANT';

      return {
        pacs_url: testData.pacs_url || 'unknown',
        protocols_tested: Array.from(protocols),
        timeout: testData.timeout || 30,
        verbose: testData.verbose || false,
        is_public: testData.is_public || false,
        results: testResults,
        summary: {
          total_tests: totalTests,
          passed_tests: passedTests,
          failed_tests: failedTests,
          skipped_tests: skippedTests,
          compliance_score: complianceScore,
          conformance_level: conformanceLevel,
          average_response_time: averageResponseTime,
          max_response_time: maxResponseTime === Infinity ? 0 : maxResponseTime,
          min_response_time: minResponseTime === Infinity ? 0 : minResponseTime,
          total_duration: testData.total_duration || 0,
        }
      };
    } catch (error) {
      console.error('Error parsing Python test output:', error);
      return null;
    }
  }

  // Calculate compliance score and conformance level
  private static calculateComplianceScore(summary: TestRunData['summary']): { compliance_score: number; conformance_level: string } {
    const score = summary.compliance_score;
    const level = score >= 90 ? 'CONFORMANT' :
                  score >= 75 ? 'MOSTLY_CONFORMANT' :
                  score >= 50 ? 'PARTIALLY_CONFORMANT' :
                  'NON_CONFORMANT';
    
    return { compliance_score: score, conformance_level: level };
  }

  // Identify or create vendor based on PACS URL
  private static async identifyOrCreateVendor(pacsUrl: string): Promise<string> {
    // Simple heuristic: extract domain from URL to guess vendor
    const domain = new URL(pacsUrl).hostname;
    let vendorName = 'Unknown Vendor';
    
    // Known PACS vendors by domain pattern
    if (domain.includes('ge.com') || domain.includes('gehealthcare')) {
      vendorName = 'GE Healthcare';
    } else if (domain.includes('philips.com') || domain.includes('philips')) {
      vendorName = 'Philips Healthcare';
    } else if (domain.includes('agfa.com') || domain.includes('agfa')) {
      vendorName = 'AGFA HealthCare';
    } else if (domain.includes('fujifilm.com') || domain.includes('fuji')) {
      vendorName = 'FUJIFILM Healthcare';
    }

    // Try to find existing vendor
    const { data: existingVendor } = await supabase
      .from('vendors')
      .select('id')
      .eq('name', vendorName)
      .single();

    if (existingVendor) {
      return existingVendor.id;
    }

    // Create new vendor
    const { data: newVendor, error } = await supabase
      .from('vendors')
      .insert({
        name: vendorName,
        website: domain.startsWith('www.') ? `https://${domain}` : `https://www.${domain}`,
        description: `${vendorName} PACS system`
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating vendor:', error);
      // Return a default vendor ID or handle error
      return 'default-vendor-id';
    }

    return newVendor.id;
  }

  // Identify or create PACS record
  private static async identifyOrCreatePACS(vendorId: string, endpointUrl: string): Promise<string> {
    // Try to find existing PACS
    const { data: existingPACS } = await supabase
      .from('pacs')
      .select('id')
      .eq('vendor_id', vendorId)
      .eq('endpoint_url', endpointUrl)
      .single();

    if (existingPACS) {
      return existingPACS.id;
    }

    // Create new PACS
    const { data: newPACS, error } = await supabase
      .from('pacs')
      .insert({
        vendor_id: vendorId,
        name: `PACS at ${new URL(endpointUrl).hostname}`,
        endpoint_url: endpointUrl,
        version: 'Unknown',
        is_active: true,
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating PACS:', error);
      return 'default-pacs-id';
    }

    return newPACS.id;
  }

  // Generate unique run identifier
  private static generateRunIdentifier(): string {
    return `run_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
  }

  // Generate share token for public results
  private static generateShareToken(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }
}