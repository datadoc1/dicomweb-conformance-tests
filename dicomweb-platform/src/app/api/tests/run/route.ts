import { NextRequest, NextResponse } from 'next/server';
import { executeDicomTests, saveTestResultsToSupabase } from '@/lib/test-executor';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      pacsUrl,
      username,
      password,
      protocols,
      timeout,
      verbose,
      isPublic,
      organization,
      contactName,
      contactEmail
    } = body;

    // Validate required fields
    if (!pacsUrl) {
      return NextResponse.json({
        error: 'PACS URL is required'
      }, { status: 400 });
    }

    if (!protocols || protocols.length === 0) {
      return NextResponse.json({
        error: 'At least one protocol must be specified'
      }, { status: 400 });
    }

    // Create test configuration
    const testConfig = {
      pacsUrl,
      username,
      password,
      protocols: protocols || ['QIDO', 'WADO', 'STOW'],
      timeout: timeout || 30,
      verbose: verbose || false,
      isPublic: isPublic !== false, // Default to true
      organization,
      contactName,
      contactEmail,
      saveToSupabase: true // Enable Supabase saving
    };

    // Generate a test run ID
    const testRunId = `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Start test execution in background (async) and save results
    setTimeout(async () => {
      try {
        // Execute the tests
        const result = await executeDicomTests(testConfig);
        console.log('Test execution completed for:', testRunId);
        
        // Save results to Supabase
        const saveResult = await saveTestResultsToSupabase(testConfig, result);
        console.log('Results saved to Supabase:', saveResult);
        
        if (!saveResult.success) {
          console.error('Failed to save test results:', saveResult.error);
        }
      } catch (error) {
        console.error('Test execution failed:', error);
      }
    }, 100);

    // Return immediate response with test run ID
    return NextResponse.json({
      success: true,
      testRunId,
      status: 'RUNNING',
      message: 'Test execution started. Use the testRunId to check status.',
      config: {
        pacsUrl,
        protocols: testConfig.protocols,
        timeout: testConfig.timeout,
        isPublic: testConfig.isPublic
      },
      estimatedTime: '2-5 minutes'
    });

  } catch (error: any) {
    console.error('Test execution error:', error);
    return NextResponse.json({
      error: error.message || 'Test execution failed'
    }, { status: 500 });
  }
}