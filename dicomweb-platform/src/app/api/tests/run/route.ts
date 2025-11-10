import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { executeDicomTests } from '@/lib/test-executor';
import { generateTestIdentifier } from '@/lib/utils/identifiers';
import { nanoid } from 'nanoid';

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
      contactEmail,
    } = body;

    // Validate required fields
    if (!pacsUrl || !protocols || protocols.length === 0) {
      return NextResponse.json(
        { error: 'PACS URL and protocols are required' },
        { status: 400 }
      );
    }

    // Create or find PACS system
    const pacs = await prisma.pACS.upsert({
      where: { endpointUrl: pacsUrl },
      update: {
        name: organization ? `${organization} PACS` : 'Unknown PACS',
        updatedAt: new Date(),
      },
      create: {
        name: organization ? `${organization} PACS` : 'Unknown PACS',
        endpointUrl: pacsUrl,
        isPublic: isPublic || false,
      },
    });

    // Create test run record
    const runIdentifier = generateTestIdentifier();
    const testRun = await prisma.testRun.create({
      data: {
        pacsId: pacs.id,
        runIdentifier,
        status: 'RUNNING',
        protocolsTested: protocols.join(','),
        timeout,
        verbose,
        isPublic,
        organization,
        contactName,
        contactEmail,
        startTime: new Date(),
      },
    });

    // Execute tests in background
    executeTestInBackground(testRun.id, {
      pacsUrl,
      username,
      password,
      protocols,
      timeout,
      verbose,
    }).catch(console.error);

    return NextResponse.json({
      success: true,
      testRunId: testRun.id,
      runIdentifier: testRun.runIdentifier,
      message: 'Test started successfully',
    });
  } catch (error) {
    console.error('Test execution error:', error);
    return NextResponse.json(
      { error: 'Failed to start test execution' },
      { status: 500 }
    );
  }
}

async function executeTestInBackground(
  testRunId: string,
  config: {
    pacsUrl: string;
    username?: string;
    password?: string;
    protocols: string[];
    timeout: number;
    verbose: boolean;
  }
) {
  try {
    console.log(`Starting test execution for run ${testRunId}`);
    
    // Execute DICOM tests using our test executor
    const results = await executeDicomTests(config);
    
    // Update test run with results
    await prisma.testRun.update({
      where: { id: testRunId },
      data: {
        status: 'COMPLETED',
        endTime: new Date(),
        totalTests: results.totalTests,
        passedTests: results.passedTests,
        failedTests: results.failedTests,
        skippedTests: results.skippedTests,
        complianceScore: results.complianceScore,
        conformanceLevel: results.conformanceLevel,
        averageResponseTime: results.averageResponseTime,
        maxResponseTime: results.maxResponseTime,
        minResponseTime: results.minResponseTime,
        totalDuration: results.totalDuration,
        // Generate share token if public
        ...(config.isPublic && {
          shareToken: nanoid(10),
          sharedAt: new Date(),
        }),
      },
    });

    // Store individual test results
    for (const testResult of results.testResults) {
      await prisma.testResult.create({
        data: {
          testRunId,
          testId: testResult.testId,
          testName: testResult.testName,
          protocol: testResult.protocol,
          status: testResult.status,
          message: testResult.message,
          responseTime: testResult.responseTime,
          dicomSection: testResult.dicomSection,
          requirement: testResult.requirement,
          classification: testResult.classification,
          requestDetails: testResult.requestDetails,
          responseDetails: testResult.responseDetails,
          recommendation: testResult.recommendation,
        },
      });
    }

    // Generate recommendations
    for (const recommendation of results.recommendations) {
      await prisma.recommendation.create({
        data: {
          testRunId,
          category: recommendation.category,
          priority: recommendation.priority,
          title: recommendation.title,
          description: recommendation.description,
          actionableSteps: recommendation.actionableSteps,
          referenceUrl: recommendation.referenceUrl,
        },
      });
    }

    console.log(`Test execution completed for run ${testRunId}`);
  } catch (error) {
    console.error(`Test execution failed for run ${testRunId}:`, error);
    
    // Mark test run as failed
    await prisma.testRun.update({
      where: { id: testRunId },
      data: {
        status: 'FAILED',
        endTime: new Date(),
      },
    });
  }
}