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
END;
$$;


CREATE OR REPLACE FUNCTION add_video(
    p_video_name VARCHAR,
    p_user_id INT,
    p_duration DECIMAL(5,2),
    p_status videoStatus
) 
RETURNS JSON AS $$
DECLARE
    v_id INT;
    v_status videoStatus;
BEGIN
    INSERT INTO Video (VideoName, userID, duration, status)
    VALUES (p_video_name, p_user_id, p_duration, p_status)
    RETURNING videoID, status INTO v_id, v_status;

    RETURN json_build_object(
        'video_id', v_id,
        'status', v_status
    );
END;
$$ LANGUAGE plpgsql;