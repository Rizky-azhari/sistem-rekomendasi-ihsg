-- Migration: Authentication & RBAC tables (user_profiles, activity_logs, reports)
-- Compatible with Supabase Auth (auth.users)

-- 1. Create user_profiles table linked to auth.users
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'USER' CHECK (role IN ('ADMIN', 'USER')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast role & email lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON public.user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- 2. Create activity_logs table for audit trail
CREATE TABLE IF NOT EXISTS public.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    user_email VARCHAR(255),
    role VARCHAR(20),
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for activity logs
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON public.activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON public.activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON public.activity_logs(action);

-- 3. Create reports table for stock analysis reports
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    symbol VARCHAR(20),
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) DEFAULT 'TECHNICAL_ANALYSIS',
    recommendation VARCHAR(20),
    target_price NUMERIC(15, 2),
    stop_loss NUMERIC(15, 2),
    content TEXT,
    summary JSONB DEFAULT '{}'::jsonb,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for reports
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON public.reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_symbol ON public.reports(symbol);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON public.reports(user_id);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policies for user_profiles
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
CREATE POLICY "Users can read own profile"
    ON public.user_profiles
    FOR SELECT
    TO authenticated
    USING ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS "Admins can read all profiles" ON public.user_profiles;
CREATE POLICY "Admins can read all profiles"
    ON public.user_profiles
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = (SELECT auth.uid()) AND role = 'ADMIN'
        )
    );

DROP POLICY IF EXISTS "Admins can update all profiles" ON public.user_profiles;
CREATE POLICY "Admins can update all profiles"
    ON public.user_profiles
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = (SELECT auth.uid()) AND role = 'ADMIN'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = (SELECT auth.uid()) AND role = 'ADMIN'
        )
    );

-- 6. RLS Policies for activity_logs
DROP POLICY IF EXISTS "Authenticated can insert activity logs" ON public.activity_logs;
CREATE POLICY "Authenticated can insert activity logs"
    ON public.activity_logs
    FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

DROP POLICY IF EXISTS "Admins can view all activity logs" ON public.activity_logs;
CREATE POLICY "Admins can view all activity logs"
    ON public.activity_logs
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = (SELECT auth.uid()) AND role = 'ADMIN'
        )
    );

-- 7. RLS Policies for reports
DROP POLICY IF EXISTS "Anyone authenticated can view public reports" ON public.reports;
CREATE POLICY "Anyone authenticated can view public reports"
    ON public.reports
    FOR SELECT
    TO authenticated
    USING (is_public = TRUE OR (SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Authenticated users can insert reports" ON public.reports;
CREATE POLICY "Authenticated users can insert reports"
    ON public.reports
    FOR INSERT
    TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Authors and admins can delete reports" ON public.reports;
CREATE POLICY "Authors and admins can delete reports"
    ON public.reports
    FOR DELETE
    TO authenticated
    USING (
        (SELECT auth.uid()) = user_id OR
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = (SELECT auth.uid()) AND role = 'ADMIN'
        )
    );

-- 8. Table Grants
GRANT ALL ON TABLE public.user_profiles TO authenticated, service_role, postgres;
GRANT ALL ON TABLE public.activity_logs TO authenticated, service_role, postgres;
GRANT ALL ON TABLE public.reports TO authenticated, service_role, postgres;
GRANT SELECT ON TABLE public.user_profiles TO anon;
GRANT SELECT ON TABLE public.reports TO anon;
