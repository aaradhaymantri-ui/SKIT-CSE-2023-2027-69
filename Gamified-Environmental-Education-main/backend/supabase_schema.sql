-- ================================================================
-- Supabase Schema for EcoQuest / Gamified Environmental Education
-- Paste and execute this script in Supabase Dashboard -> SQL Editor
-- ================================================================

-- 1. Create the Users table
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    roll_number VARCHAR(50),
    school VARCHAR(100),
    class_name VARCHAR(50),
    password_hash VARCHAR(256),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Optional Leaderboard / Scores Table (for gamified quizzes & games)
CREATE TABLE IF NOT EXISTS public.leaderboard (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(100) REFERENCES public.users(email) ON DELETE CASCADE,
    student_name VARCHAR(100),
    score INTEGER DEFAULT 0,
    eco_points INTEGER DEFAULT 0,
    game_name VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Enable Row Level Security (RLS) for data protection
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leaderboard ENABLE ROW LEVEL SECURITY;

-- 4. Policies for 'users' table
-- Allow users to sign up (insert record)
CREATE POLICY "Allow public insert to users" ON public.users
    FOR INSERT
    WITH CHECK (true);

-- Allow reading user profile data
CREATE POLICY "Allow select on users" ON public.users
    FOR SELECT
    USING (true);

-- 5. Policies for 'leaderboard' table
CREATE POLICY "Allow public read leaderboard" ON public.leaderboard
    FOR SELECT
    USING (true);

CREATE POLICY "Allow authenticated insert/update leaderboard" ON public.leaderboard
    FOR ALL
    USING (true)
    WITH CHECK (true);
