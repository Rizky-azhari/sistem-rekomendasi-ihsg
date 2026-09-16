-- Migration: Google OAuth Profiles & Automatic First-Admin Trigger
-- Compatible with Supabase Auth (auth.users)

-- 1. Create profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast role lookup
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

-- 2. Create function to automatically assign role (First user -> admin, subsequent -> user)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
    admin_count INT;
    assigned_role TEXT;
    meta JSONB;
    u_full_name TEXT;
    u_avatar TEXT;
BEGIN
    -- Check if an admin already exists in profiles
    SELECT COUNT(*) INTO admin_count FROM public.profiles WHERE role = 'admin';

    IF admin_count = 0 THEN
        assigned_role := 'admin';
    ELSE
        assigned_role := 'user';
    END IF;

    meta := NEW.raw_user_meta_data;
    u_full_name := COALESCE(meta->>'full_name', meta->>'name', split_part(NEW.email, '@', 1));
    u_avatar := COALESCE(meta->>'avatar_url', meta->>'picture', '');

    -- Insert into profiles
    INSERT INTO public.profiles (id, email, full_name, avatar_url, role, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        u_full_name,
        u_avatar,
        assigned_role,
        NOW()
    )
    ON CONFLICT (id) DO UPDATE
    SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, public.profiles.full_name),
        avatar_url = COALESCE(EXCLUDED.avatar_url, public.profiles.avatar_url);

    RETURN NEW;
END;
$$;

-- 3. Create Trigger AFTER INSERT ON auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 5. RLS Policies
DROP POLICY IF EXISTS "Profiles are viewable by authenticated users" ON public.profiles;
CREATE POLICY "Profiles are viewable by authenticated users"
    ON public.profiles
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "Profiles are viewable by anon" ON public.profiles;
CREATE POLICY "Profiles are viewable by anon"
    ON public.profiles
    FOR SELECT
    TO anon
    USING (true);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING ((SELECT auth.uid()) = id)
    WITH CHECK ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS "Admins can update any profile" ON public.profiles;
CREATE POLICY "Admins can update any profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = (SELECT auth.uid()) AND role = 'admin'
        )
    );

-- 6. Table Grants
GRANT ALL ON TABLE public.profiles TO authenticated, service_role, postgres;
GRANT SELECT ON TABLE public.profiles TO anon;
