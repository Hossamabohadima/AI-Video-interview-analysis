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


CREATE OR REPLACE PROCEDURE set_threshold_score(
    p_user_id INT,
    p_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE threshold
    SET thresholdvalue = p_score
    WHERE userid = p_user_id;
END;
$$;

CREATE OR REPLACE FUNCTION login_user_sp(p_email TEXT, p_password TEXT)
RETURNS TABLE(userid INT, name TEXT, role user_role) AS $$
BEGIN
    RETURN QUERY
    SELECT u.userid, u.name, u.role
    FROM Users u
    WHERE u.email = p_email AND u.password = p_password;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_reports_sp(p_user_id INT)
RETURNS TABLE(
    videoid INT,
    videoname varchar(50),
    SpeechClarity DECIMAL,
    SpeechFluency DECIMAL,
    SpeechConfidence DECIMAL,
    SpeechExpressiveness DECIMAL,
    SpeechEngagement DECIMAL,
    FacialConfidence DECIMAL,
    FacialApproachability DECIMAL,
    FacialEngagement DECIMAL,
    VideoProfessionalism DECIMAL,
    totalScore DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT v.videoid, v.videoname,
           vs.SpeechClarity, vs.SpeechFluency, vs.SpeechConfidence,
           vs.SpeechExpressiveness, vs.SpeechEngagement,
           vs.FacialConfidence, vs.FacialApproachability,
           vs.FacialEngagement, vs.VideoProfessionalism,
           vs.totalScore
    FROM Video v
    LEFT JOIN videoScore vs ON v.videoid = vs.videoid
    WHERE v.userid = p_user_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION compare_reports_sp(v1 INT, v2 INT)
RETURNS TABLE(
    videoid INT,
    SpeechClarity DECIMAL,
    SpeechFluency DECIMAL,
    SpeechConfidence DECIMAL,
    SpeechExpressiveness DECIMAL,
    SpeechEngagement DECIMAL,
    FacialConfidence DECIMAL,
    FacialApproachability DECIMAL,
    FacialEngagement DECIMAL,
    VideoProfessionalism DECIMAL,
    totalScore DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM videoScore
    WHERE videoScore.videoid = v1 OR videoid = v2;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE set_weights_sp(
    p_user_id INT,
    p_SpeechClarity DECIMAL,
    p_SpeechFluency DECIMAL,
    p_SpeechConfidence DECIMAL,
    p_SpeechExpressiveness DECIMAL,
    p_SpeechEngagement DECIMAL,
    p_FacialConfidence DECIMAL,
    p_FacialApproachability DECIMAL,
    p_FacialEngagement DECIMAL,
    p_VideoProfessionalism DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE MetricWeight SET
        SpeechClarity = p_SpeechClarity,
        SpeechFluency = p_SpeechFluency,
        SpeechConfidence = p_SpeechConfidence,
        SpeechExpressiveness = p_SpeechExpressiveness,
        SpeechEngagement = p_SpeechEngagement,
        FacialConfidence = p_FacialConfidence,
        FacialApproachability = p_FacialApproachability,
        FacialEngagement = p_FacialEngagement,
        VideoProfessionalism = p_VideoProfessionalism
    WHERE userID = p_user_id;
END;
$$;