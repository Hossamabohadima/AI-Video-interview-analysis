-- ============================================================
-- InterviewMe Database Schema - Complete (Original + Updates)
-- ============================================================

-- 1. Create the custom types
CREATE TYPE user_role AS ENUM ('USER', 'RECRUITER');
CREATE TYPE videoStatus AS ENUM ('DONE', 'FAILED', 'PENDING');

-- 2. Create Users table
CREATE TABLE Users (
    userid SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    createdDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phoneNumber VARCHAR(20), 
    role user_role NOT NULL 
);

-- 3. Create Threshold table
CREATE TABLE Threshold (
    userID int PRIMARY KEY REFERENCES Users(userid) ON DELETE CASCADE,
    thresholdValue DECIMAL(5,2) NOT NULL
);

-- 4. Create Video table
CREATE TABLE Video (
    videoID SERIAL PRIMARY KEY,
    VideoName VARCHAR(50) NOT NULL,
    userID int REFERENCES Users(userid) ON DELETE CASCADE,
    uploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration DECIMAL(5,2),
    status videoStatus NOT NULL 
);

-- 5. Create VideoMetricWeight table for per-video weight storage
CREATE TABLE VideoMetricWeight (
    videoID INT PRIMARY KEY REFERENCES Video(videoID) ON DELETE CASCADE,
    fillers_weight DECIMAL(5,4) NOT NULL,
    pause_rate_weight DECIMAL(5,4) NOT NULL,
    emotion_weight DECIMAL(5,4) NOT NULL,
    energy_weight DECIMAL(5,4) NOT NULL,
    eye_contact_weight DECIMAL(5,4) NOT NULL,
    grammar_weight DECIMAL(5,4) NOT NULL,
    CONSTRAINT video_metric_weight_sum CHECK (
        fillers_weight +
        pause_rate_weight +
        emotion_weight +
        energy_weight +
        eye_contact_weight +
        grammar_weight = 1.0
    )
);

-- 6. Create videoScore table
CREATE TABLE videoScore (
    videoID INT PRIMARY KEY REFERENCES Video(videoID) ON DELETE CASCADE,
    fillers_score DECIMAL(5,2) DEFAULT 0,
    pause_rate_score DECIMAL(5,2) DEFAULT 0,
    emotion_score DECIMAL(5,2) DEFAULT 0,
    energy_score DECIMAL(5,2) DEFAULT 0,
    eye_contact_score DECIMAL(5,2) DEFAULT 0,
    grammar_score DECIMAL(5,2) DEFAULT 0,
    total_score DECIMAL(5,2) DEFAULT 0,
    CONSTRAINT score_limit 
    CHECK (total_score >= 0 AND total_score <= 100)
);
   
-- 7. Create videoAnalysis table
CREATE TABLE VideoAnalysis (
    videoID INT PRIMARY KEY REFERENCES Video(videoID) ON DELETE CASCADE,
    fillers_Word JSONB,
    rate_Of_Stop DECIMAL(10,4), 
    emotion_analysis JSONB,
    energy_Statistics JSONB,
    eye_Contact       JSONB,
    grammar_Mistakes JSONB,
    total_Score DECIMAL(10,4)
);

-- ============================================================
-- NEW: Password Reset & Token Blacklist Tables
-- ============================================================

-- 8. Create password_reset_tokens table for secure password reset flow
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(userid) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id)
);

-- Index for fast token lookup
CREATE INDEX IF NOT EXISTS idx_reset_tokens_hash ON password_reset_tokens(token_hash);

-- 9. Create token_blacklist table for logout functionality
-- (In production with Redis, this table can be omitted)
CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    token_jti TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_blacklist_jti ON token_blacklist(token_jti);
CREATE INDEX IF NOT EXISTS idx_blacklist_expires ON token_blacklist(expires_at);