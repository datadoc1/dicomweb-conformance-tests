import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const period = searchParams.get('period') || 'MONTHLY'
    
    const leaderboardEntries = await prisma.leaderboardEntry.findMany({
      where: {
        period: period as any
      },
      include: {
        vendor: {
          select: {
            name: true,
            website: true,
            description: true
          }
        }
      },
      orderBy: {
        overallRank: 'asc'
      }
    })

    // Calculate market share
    const totalTests = leaderboardEntries.reduce((sum, entry) => sum + entry.totalTestsRun, 0)
    const entriesWithMarketShare = leaderboardEntries.map(entry => ({
      ...entry,
      marketShare: totalTests > 0 ? (entry.totalTestsRun / totalTests) * 100 : 0
    }))

    return NextResponse.json({
      success: true,
      data: entriesWithMarketShare,
      period,
      totalEntries: entriesWithMarketShare.length,
      totalTests
    })
  } catch (error) {
    console.error('Error fetching leaderboard:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch leaderboard data' },
      { status: 500 }
    )
  }
}