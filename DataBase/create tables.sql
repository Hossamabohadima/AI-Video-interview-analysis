-- 1. Create the custom type 
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
-- 4. Create MetricWeight table
CREATE TABLE MetricWeight (
    userID INT PRIMARY KEY REFERENCES Users(userid) ON DELETE CASCADE,
    fillers_weight DECIMAL(5,4) DEFAULT 0,
    pause_rate_weight DECIMAL(5,4) DEFAULT 0,
    emotion_weight DECIMAL(5,4) DEFAULT 0,
    energy_weight DECIMAL(5,4) DEFAULT 0,
    eye_contact_weight DECIMAL(5,4) DEFAULT 0,
    grammar_weight DECIMAL(5,4) DEFAULT 0,

    CONSTRAINT metric_score_limit CHECK (
        fillers_weight +
        pause_rate_weight +
        emotion_weight +
        energy_weight +
        eye_contact_weight +
        grammar_weight = 1.0
    )
);
-- 5. Create Video table
CREATE TABLE Video (
    videoID SERIAL PRIMARY KEY,
    VideoName VARCHAR(50) NOT NULL,
    userID int REFERENCES Users(userid) ON DELETE CASCADE,
    uploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration DECIMAL(5,2) ,
    status videoStatus NOT NULL 
);
-- 6. Create videoScore table
-- CREATE TABLE videoScore (
--     videoID INT PRIMARY KEY REFERENCES Video(videoID) ON DELETE CASCADE,
--     fillers_score DECIMAL(5,2) DEFAULT 0,
--     pause_rate_score DECIMAL(5,2) DEFAULT 0,
--     emotion_score DECIMAL(5,2) DEFAULT 0,
--     energy_score DECIMAL(5,2) DEFAULT 0,
--     eye_contact_score DECIMAL(5,2) DEFAULT 0,
--     grammar_score DECIMAL(5,2) DEFAULT 0,
--     total_score DECIMAL(5,2) DEFAULT 0,
--     CONSTRAINT score_limit 
--     CHECK (total_score >= 0 AND total_score <= 100)
-- );
   
   
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