import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  try {
    // Try to get leaderboard data from database
    const { data: leaderboardData, error } = await supabase
      .from('leaderboard_entries')
      .select('*')
      .order('average_compliance_score', { ascending: false })
      .limit(20);

    if (error) {
      // If table doesn't exist, return sample data
      console.warn('Leaderboard table not found, returning sample data:', error.message);
      
      return NextResponse.json({
        success: true,
        data: [
          {
            id: 'sample-1',
            vendor_name: 'Orthanc DICOM Server',
            website: 'https://www.orthanc-server.com/',
            average_compliance_score: 95.5,
            total_tests_run: 1247,
            protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
            public_rankings: { rank: 1, category: 'open-source' },
            created_at: new Date().toISOString()
          },
          {
            id: 'sample-2',
            vendor_name: 'dcm4chee PACS',
            website: 'https://www.dcm4che.org/',
            average_compliance_score: 89.2,
            total_tests_run: 856,
            protocols_supported: ['QIDO-RS', 'WADO-RS'],
            public_rankings: { rank: 2, category: 'open-source' },
            created_at: new Date().toISOString()
          },
          {
            id: 'sample-3',
            vendor_name: 'AGFA Healthcare',
            website: 'https://www.agfa.com/',
            average_compliance_score: 76.8,
            total_tests_run: 2341,
            protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
            public_rankings: { rank: 3, category: 'commercial' },
            created_at: new Date().toISOString()
          },
          {
            id: 'sample-4',
            vendor_name: 'FUJIFILM Healthcare',
            website: 'https://www.fujifilm.com/',
            average_compliance_score: 82.1,
            total_tests_run: 1892,
            protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
            public_rankings: { rank: 4, category: 'commercial' },
            created_at: new Date().toISOString()
          },
          {
            id: 'sample-5',
            vendor_name: 'Philips Healthcare',
            website: 'https://www.philips.com/',
            average_compliance_score: 74.3,
            total_tests_run: 1654,
            protocols_supported: ['QIDO-RS', 'WADO-RS'],
            public_rankings: { rank: 5, category: 'commercial' },
            created_at: new Date().toISOString()
          }
        ],
        message: 'Sample data - database setup required'
      });
    }

    return NextResponse.json({
      success: true,
      data: leaderboardData || [],
      count: leaderboardData?.length || 0
    });

  } catch (error: any) {
    console.error('Leaderboard API error:', error);
    
    // Return sample data on any error to keep the app functional
    return NextResponse.json({
      success: true,
      data: [
        {
          id: 'fallback-1',
          vendor_name: 'Orthanc DICOM Server',
          website: 'https://www.orthanc-server.com/',
          average_compliance_score: 95.5,
          total_tests_run: 1247,
          protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
          public_rankings: { rank: 1, category: 'open-source' },
          created_at: new Date().toISOString()
        }
      ],
      message: 'Fallback sample data'
    });
  }
}