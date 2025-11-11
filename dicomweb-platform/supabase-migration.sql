-- Create test_runs table for DICOMweb conformance testing results
CREATE TABLE IF NOT EXISTS public.test_runs (
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
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS test_runs_created_at_idx ON public.test_runs(created_at);
CREATE INDEX IF NOT EXISTS test_runs_pacs_url_idx ON public.test_runs(pacs_url);
CREATE INDEX IF NOT EXISTS test_runs_is_public_idx ON public.test_runs(is_public);

-- Create test_results table for individual test results
CREATE TABLE IF NOT EXISTS public.test_results (
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
);

-- Create indexes for test results
CREATE INDEX IF NOT EXISTS test_results_test_run_id_idx ON public.test_results(test_run_id);
CREATE INDEX IF NOT EXISTS test_results_protocol_idx ON public.test_results(protocol);
CREATE INDEX IF NOT EXISTS test_results_status_idx ON public.test_results(status);

-- Create leaderboard_entries table for vendor rankings
CREATE TABLE IF NOT EXISTS public.leaderboard_entries (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL,
  vendor_name text NOT NULL,
  website text,
  average_compliance_score real DEFAULT 0,
  total_tests_run integer DEFAULT 0,
  protocols_supported text[] DEFAULT '{}',
  public_rankings jsonb DEFAULT '{}'
);

-- Create indexes for leaderboard
CREATE INDEX IF NOT EXISTS leaderboard_entries_vendor_name_idx ON public.leaderboard_entries(vendor_name);
CREATE INDEX IF NOT EXISTS leaderboard_entries_compliance_idx ON public.leaderboard_entries(average_compliance_score);

-- Create sharing_links table for result sharing
CREATE TABLE IF NOT EXISTS public.sharing_links (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  test_run_id uuid REFERENCES public.test_runs(id) ON DELETE CASCADE,
  share_token text UNIQUE NOT NULL,
  is_active boolean DEFAULT true,
  social_media_shared boolean DEFAULT false,
  shared_at timestamp with time zone
);

-- Create indexes for sharing
CREATE INDEX IF NOT EXISTS sharing_links_token_idx ON public.sharing_links(share_token);
CREATE INDEX IF NOT EXISTS sharing_links_active_idx ON public.sharing_links(is_active);

-- Enable RLS (Row Level Security)
ALTER TABLE public.test_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leaderboard_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sharing_links ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public access to results
CREATE POLICY "Public can view public test runs" ON public.test_runs
  FOR SELECT USING (is_public = true);

CREATE POLICY "Public can view all test results for public runs" ON public.test_results
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.test_runs 
      WHERE test_runs.id = test_results.test_run_id 
      AND test_runs.is_public = true
    )
  );

CREATE POLICY "Public can view leaderboard entries" ON public.leaderboard_entries
  FOR SELECT USING (true);

CREATE POLICY "Public can view active sharing links" ON public.sharing_links
  FOR SELECT USING (is_active = true);

-- Allow authenticated users to create test runs
CREATE POLICY "Authenticated users can create test runs" ON public.test_runs
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow inserting test results for existing test runs
CREATE POLICY "Users can insert results for their runs" ON public.test_results
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.test_runs 
      WHERE test_runs.id = test_results.test_run_id
    )
  );

-- Allow updating leaderboard entries (for admin/system)
CREATE POLICY "Service role can manage leaderboard" ON public.leaderboard_entries
  FOR ALL USING (auth.role() = 'service_role');

-- Allow creating sharing links
CREATE POLICY "Service role can manage sharing links" ON public.sharing_links
  FOR ALL USING (auth.role() = 'service_role');