import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET() {
  try {
    // Test database connection
    const vendors = await prisma.vendor.findMany()
    const testRuns = await prisma.testRun.findMany()
    
    return NextResponse.json({
      success: true,
      message: 'Database connection successful',
      data: {
        vendors: vendors.length,
        testRuns: testRuns.length
      }
    })
  } catch (error) {
    console.error('Database connection error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Database connection failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}