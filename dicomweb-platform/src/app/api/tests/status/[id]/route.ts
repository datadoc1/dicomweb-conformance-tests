import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Fix: await params in Next.js 13+
    const { id } = await params;
    
    const { data: testRun, error } = await supabase
      .from('test_runs')
      .select('*')
      .eq('id', id)
      .single();

    if (error || !testRun) {
      return NextResponse.json(
        { error: 'Test run not found' },
        { status: 404 }
      );
    }

    // If test is still running, just return status
    if (testRun.status === 'running') {
      return NextResponse.json({
        id: testRun.id,
        status: testRun.status,
        startTime: testRun.start_time,
        message: 'Test is currently running...',
      });
    }

    // Get test results
    const { data: testResults } = await supabase
      .from('test_results')
      .select('*')
      .eq('test_run_id', testRun.id);

    // Return complete results for completed tests
    return NextResponse.json({
      id: testRun.id,
      status: testRun.status,
      pacsUrl: testRun.pacs_url,
      startTime: testRun.start_time,
      endTime: testRun.end_time,
      totalTests: testRun.total_tests,
      passedTests: testRun.passed_tests,
      failedTests: testRun.failed_tests,
      skippedTests: testRun.skipped_tests,
      complianceScore: testRun.compliance_score,
      conformanceLevel: testRun.conformance_level,
      averageResponseTime: testRun.average_response_time,
      maxResponseTime: testRun.max_response_time,
      minResponseTime: testRun.min_response_time,
      totalDuration: testRun.total_duration,
      shareToken: testRun.share_token,
      testResults: (testResults || []).map(result => ({
        testName: result.test_name,
        protocol: result.protocol,
        status: result.status,
        message: result.message,
        responseTime: result.response_time,
        dicomSection: result.dicom_section,
        classification: result.classification,
        requirement: result.requirement,
      })),
      recommendations: [], // Recommendations table not implemented yet
    });
  } catch (error) {
    console.error('Error fetching test status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch test status' },
      { status: 500 }
    );
  }
}