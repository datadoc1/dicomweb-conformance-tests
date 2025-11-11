import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  try {
    // Test database connection
    const { data: vendors, error: vendorsError } = await supabase
      .from('leaderboard_entries')
      .select('vendor_name')
    
    const { data: testRuns, error: testRunsError } = await supabase
      .from('test_runs')
      .select('id')
    
    if (vendorsError) {
      throw vendorsError
    }
    if (testRunsError) {
      throw testRunsError
    }
    
    return NextResponse.json({
      success: true,
      message: 'Database connection successful',
      data: {
        vendors: vendors?.length || 0,
        testRuns: testRuns?.length || 0
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