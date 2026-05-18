CREATE OR REPLACE FUNCTION get_reports_sp(p_user_id INT)
RETURNS TABLE(
    videoid INT,
    uploadDate TIMESTAMP,
    duration DECIMAL,
    status videoStatus, 
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
    SELECT 
        v.videoid,
        v.uploaddate::TIMESTAMP, -- Force cast to match your TIMESTAMP return type
        v.duration::DECIMAL,
        v.status,
        v.videoname,
        vs.speechclarity::DECIMAL,
        vs.speechfluency::DECIMAL,
        vs.speechconfidence::DECIMAL,
        vs.speechexpressiveness::DECIMAL,
        vs.speechengagement::DECIMAL,
        vs.facialconfidence::DECIMAL,
        vs.facialapproachability::DECIMAL,
        vs.facialengagement::DECIMAL,
        vs.videoprofessionalism::DECIMAL,
        vs.totalscore::DECIMAL
    FROM Video v
    LEFT JOIN videoScore vs ON v.videoid = vs.videoid
    WHERE v.userid = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION compare_reports_sp(p_video_ids INT[])
RETURNS TABLE(
    res_videoid INT,
    res_SpeechClarity DECIMAL,
    res_SpeechFluency DECIMAL,
    res_SpeechConfidence DECIMAL,
    res_SpeechExpressiveness DECIMAL,
    res_SpeechEngagement DECIMAL,
    res_FacialConfidence DECIMAL,
    res_FacialApproachability DECIMAL,
    res_FacialEngagement DECIMAL,
    res_VideoProfessionalism DECIMAL,
    res_totalScore DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vs.videoid,
        vs.SpeechClarity::DECIMAL,
        vs.SpeechFluency::DECIMAL,
        vs.SpeechConfidence::DECIMAL,
        vs.SpeechExpressiveness::DECIMAL,
        vs.SpeechEngagement::DECIMAL,
        vs.FacialConfidence::DECIMAL,
        vs.FacialApproachability::DECIMAL,
        vs.FacialEngagement::DECIMAL,
        vs.VideoProfessionalism::DECIMAL,
        vs.totalScore::DECIMAL
    FROM videoScore vs
    WHERE vs.videoid = ANY(p_video_ids)
    ORDER BY array_position(p_video_ids, vs.videoid);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_threshold_score(
    p_user_id INT,
    p_score FLOAT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE threshold
    SET thresholdvalue = p_score
    WHERE userid = p_user_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION set_weights_fn(
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
RETURNS BOOLEAN
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

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
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

--not checked yet
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



CREATE OR REPLACE FUNCTION login_user_sp(p_email TEXT, p_password TEXT)
RETURNS TABLE(userid INT, name TEXT, role user_role, password TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT u.userid, u.name::TEXT, u.role, u.password
    FROM Users u
    WHERE u.email = p_email;
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


CREATE OR REPLACE PROCEDURE insert_video_scores(
    p_video_id INTEGER,
    p_speechClarity DECIMAL(5,2),
    p_speechFluency DECIMAL(5,2),
    p_speechConfidence DECIMAL(5,2),
    p_speechExpressiveness DECIMAL(5,2),
    p_speechEngagement DECIMAL(5,2),
    p_facialConfidence DECIMAL(5,2),
    p_facialApproachability DECIMAL(5,2),
    p_facialEngagement DECIMAL(5,2),
    p_videoProfessionalism DECIMAL(5,2),
    p_totalScore DECIMAL(5,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO videoScore (
        videoID, SpeechClarity, SpeechFluency, SpeechConfidence, SpeechExpressiveness, SpeechEngagement,
        FacialConfidence, FacialApproachability, FacialEngagement, VideoProfessionalism, totalScore
    ) VALUES (
        p_video_id, p_speechClarity, p_speechFluency, p_speechConfidence, p_speechExpressiveness, p_speechEngagement,
        p_facialConfidence, p_facialApproachability, p_facialEngagement, p_videoProfessionalism, p_totalScore
    );
END;
$$;