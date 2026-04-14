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
    userID int PRIMARY KEY REFERENCES Users(userid) ON DELETE CASCADE,
   SpeechClarity DECIMAL(5,2) default 0,
   SpeechFluency DECIMAL(5,2) default 0,
   SpeechConfidence DECIMAL(5,2) default 0,
   SpeechExpressiveness DECIMAL(5,2) default 0,
   SpeechEngagement DECIMAL(5,2) default 0,
   FacialConfidence DECIMAL(5,2) default 0,
   FacialApproachability DECIMAL(5,2) default 0,
   FacialEngagement DECIMAL(5,2) default 0,
   VideoProfessionalism DECIMAL(5,2) default 0
    CONSTRAINT metric_score_limit 
    CHECK (SpeechClarity + SpeechFluency + SpeechConfidence + SpeechExpressiveness + SpeechEngagement + FacialConfidence + FacialApproachability + FacialEngagement + VideoProfessionalism = 1.0)

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
CREATE   TABLE videoScore (
    videoID int PRIMARY KEY REFERENCES Video(videoID) ON DELETE CASCADE,
   SpeechClarity DECIMAL(5,2) default 0,
   SpeechFluency DECIMAL(5,2) default 0,
   SpeechConfidence DECIMAL(5,2) default 0,
   SpeechExpressiveness DECIMAL(5,2) default 0,
   SpeechEngagement DECIMAL(5,2) default 0,
   FacialConfidence DECIMAL(5,2) default 0,
   FacialApproachability DECIMAL(5,2) default 0,
   FacialEngagement DECIMAL(5,2) default 0,
   VideoProfessionalism DECIMAL(5,2) default 0,
   totalScore DECIMAL(5,2) default 0,
    CONSTRAINT score_limit 
    CHECK (totalScore >= 0 AND totalScore <= 100)
   ); 