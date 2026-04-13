CREATE OR REPLACE PROCEDURE register_user(
    p_name VARCHAR,
    p_email VARCHAR,
    p_password TEXT,
    p_phone VARCHAR,
    p_role user_role,
    p_initial_threshold DECIMAL(5,2)
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_userid INT;
BEGIN
    -- 1. Insert into Users and get the new ID
    INSERT INTO Users (name, email, password, phoneNumber, role)
    VALUES (p_name, p_email, p_password, p_phone, p_role)
    RETURNING userid INTO new_userid;

    -- 2. Initialize Threshold
    INSERT INTO Threshold (userID, thresholdValue)
    VALUES (new_userid, p_initial_threshold);

    -- 3. Initialize MetricWeight with default 1.0 (or 0.0)
    INSERT INTO MetricWeight (userID, SpeechClarity, SpeechFluency, SpeechConfidence)
    VALUES (new_userid, 0, 1.0, 0); 

    COMMIT;
END;
$$;


CREATE OR REPLACE FUNCTION add_video(
    p_video_name VARCHAR,
    p_user_id INT,
    p_duration DECIMAL(5,2),
    p_status videoStatus
) RETURNS INT AS $$
DECLARE
    new_video_id INT;
BEGIN
    -- 1. Insert Video record
    INSERT INTO Video (VideoName, userID, duration, status)
    VALUES (p_video_name, p_user_id, p_duration, p_status)
    RETURNING videoID INTO new_video_id;

    RETURN new_video_id;
END;

$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_video_scores(p_video_id INT)
RETURNS TABLE(
    speechClarity DECIMAL(5,2),
    speechFluency DECIMAL(5,2),
    speechConfidence DECIMAL(5,2),
    speechExpressiveness DECIMAL(5,2),
    speechEngagement DECIMAL(5,2),
    facialConfidence DECIMAL(5,2),
    facialApproachability DECIMAL(5,2),
    facialEngagement DECIMAL(5,2),
    videoProfessionalism DECIMAL(5,2),
    totalScore DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        SpeechClarity, SpeechFluency, SpeechConfidence, SpeechExpressiveness, SpeechEngagement,
        FacialConfidence, FacialApproachability, FacialEngagement, VideoProfessionalism, totalScore
    FROM videoScore
    WHERE videoID = p_video_id;
END;
$$ LANGUAGE plpgsql;