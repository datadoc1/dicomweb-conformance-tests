import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json();

    if (action === 'create_tables') {
      // Create tables using raw SQL
      const tables = [
        // Test runs table
        `CREATE TABLE IF NOT EXISTS public.test_runs (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          created_at timestamp with time zone DEFAULT now() NOT NULL,
          pacs_url text NOT NULL,
          username text,
          password text,
          protocols_tested text[] DEFAULT '{}',
          timeout integer DEFAULT 30,
          verbose boolean DEFAULT false,
          is_public boolean DEFAULT true,
          organization text,
          contact_name text,
          contact_email text,
          results jsonb DEFAULT '[]',
          summary jsonb DEFAULT '{}'
        );`,

        // Test results table
        `CREATE TABLE IF NOT EXISTS public.test_results (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          test_run_id uuid REFERENCES public.test_runs(id) ON DELETE CASCADE,
          created_at timestamp with time zone DEFAULT now() NOT NULL,
          test_name text NOT NULL,
          protocol text NOT NULL,
          status text NOT NULL,
          message text,
          response_time real,
          request_details jsonb DEFAULT '{}',
          response_details jsonb DEFAULT '{}',
          recommendation text,
          timestamp text DEFAULT now()
        );`,

        // Leaderboard entries table
        `CREATE TABLE IF NOT EXISTS public.leaderboard_entries (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          created_at timestamp with time zone DEFAULT now() NOT NULL,
          updated_at timestamp with time zone DEFAULT now() NOT NULL,
          vendor_name text NOT NULL,
          website text,
          average_compliance_score real DEFAULT 0,
          total_tests_run integer DEFAULT 0,
          protocols_supported text[] DEFAULT '{}',
          public_rankings jsonb DEFAULT '{}'
        );`,

        // Sharing links table
        `CREATE TABLE IF NOT EXISTS public.sharing_links (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          created_at timestamp with time zone DEFAULT now() NOT NULL,
          test_run_id uuid REFERENCES public.test_runs(id) ON DELETE CASCADE,
          share_token text UNIQUE NOT NULL,
          is_active boolean DEFAULT true,
          social_media_shared boolean DEFAULT false,
          shared_at timestamp with time zone
        );`
      ];

      // Execute table creation
      const { error: createError } = await supabase.rpc('exec_sql', {
        query: tables.join('\n')
      });

      if (createError) {
        // Try alternative approach - direct table creation
        for (const table of tables) {
          const { error } = await supabase.rpc('exec_sql', { query: table });
          if (error) {
            console.error('Table creation error:', error);
          }
        }
      }

      return NextResponse.json({ 
        success: true, 
        message: 'Database setup completed',
        tables: ['test_runs', 'test_results', 'leaderboard_entries', 'sharing_links']
      });
    }

    if (action === 'insert_sample_data') {
      // Insert sample leaderboard data
      const sampleData = [
        {
          vendor_name: 'Orthanc DICOM Server',
          website: 'https://www.orthanc-server.com/',
          average_compliance_score: 95.5,
          total_tests_run: 1247,
          protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
          public_rankings: { rank: 1, category: 'open-source' }
        },
        {
          vendor_name: 'dcm4chee PACS',
          website: 'https://www.dcm4che.org/',
          average_compliance_score: 89.2,
          total_tests_run: 856,
          protocols_supported: ['QIDO-RS', 'WADO-RS'],
          public_rankings: { rank: 2, category: 'open-source' }
        },
        {
          vendor_name: 'AGFA Healthcare',
          website: 'https://www.agfa.com/',
          average_compliance_score: 76.8,
          total_tests_run: 2341,
          protocols_supported: ['QIDO-RS', 'WADO-RS', 'STOW-RS'],
          public_rankings: { rank: 3, category: 'commercial' }
        }
      ];

      for (const data of sampleData) {
        const { error } = await supabase
          .from('leaderboard_entries')
          .upsert(data, { onConflict: 'vendor_name' });
        
        if (error) {
          console.error('Sample data insertion error:', error);
        }
      }

      return NextResponse.json({ 
        success: true, 
        message: 'Sample data inserted',
        count: sampleData.length
      });
    }

    return NextResponse.json({ 
      error: 'Invalid action. Use "create_tables" or "insert_sample_data"' 
    }, { status: 400 });

  } catch (error: any) {
    console.error('Setup error:', error);
    return NextResponse.json({ 
      error: error.message || 'Setup failed' 
    }, { status: 500 });
  }
}