import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const testRun = await prisma.testRun.findUnique({
      where: { id: params.id },
      include: {
        pacs: true,
        testResults: true,
        recommendations: true,
      },
    });

    if (!testRun) {
      return NextResponse.json(
        { error: 'Test run not found' },
        { status: 404 }
      );
    }

    // If test is still running, just return status
    if (testRun.status === 'RUNNING') {
      return NextResponse.json({
        id: testRun.id,
        status: testRun.status,
        startTime: testRun.startTime,
        message: 'Test is currently running...',
      });
    }

    // Return complete results for completed tests
    return NextResponse.json({
      id: testRun.id,
      status: testRun.status,
      pacsUrl: testRun.pacs.endpointUrl,
      startTime: testRun.startTime,
      endTime: testRun.endTime,
      totalTests: testRun.totalTests,
      passedTests: testRun.passedTests,
      failedTests: testRun.failedTests,
      skippedTests: testRun.skippedTests,
      complianceScore: testRun.complianceScore,
      conformanceLevel: testRun.conformanceLevel,
      averageResponseTime: testRun.averageResponseTime,
      maxResponseTime: testRun.maxResponseTime,
      minResponseTime: testRun.minResponseTime,
      totalDuration: testRun.totalDuration,
      shareToken: testRun.shareToken,
      testResults: testRun.testResults.map(result => ({
        testName: result.testName,
        protocol: result.protocol,
        status: result.status,
        message: result.message,
        responseTime: result.responseTime,
        dicomSection: result.dicomSection,
        classification: result.classification,
        requirement: result.requirement,
      })),
      recommendations: testRun.recommendations.map(rec => ({
        category: rec.category,
        priority: rec.priority,
        title: rec.title,
        description: rec.description,
        actionableSteps: rec.actionableSteps,
        referenceUrl: rec.referenceUrl,
      })),
    });
  } catch (error) {
    console.error('Error fetching test status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch test status' },
      { status: 500 }
    );
  }
}