CREATE OR REPLACE FUNCTION get_reports_sp(p_user_id INT)
RETURNS TABLE(
    videoid INT,
    uploadDate TIMESTAMP,
    duration DECIMAL,
    status videoStatus, 
    videoname varchar(50),
    fillers_score DECIMAL,
    pause_rate_score DECIMAL,
    emotion_score DECIMAL,
    energy_score DECIMAL,
    eye_contact_score DECIMAL,
    grammar_score DECIMAL,
    total_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.videoid,
        v.uploaddate::TIMESTAMP, -- Force cast to match your TIMESTAMP return type
        v.duration::DECIMAL,
        v.status,
        v.videoname,
        vs.fillers_score::DECIMAL,
        vs.pause_rate_score::DECIMAL,
        vs.emotion_score::DECIMAL,
        vs.energy_score::DECIMAL,
        vs.eye_contact_score::DECIMAL,
        vs.grammar_score::DECIMAL,
        vs.total_score::DECIMAL
    FROM Video v
    LEFT JOIN videoScore vs ON v.videoid = vs.videoid
    WHERE v.userid = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION compare_reports_sp(v1 INT, v2 INT)
RETURNS TABLE(
    res_videoid INT,
    res_fillers_score DECIMAL,
    res_pause_rate_score DECIMAL,
    res_emotion_score DECIMAL,
    res_energy_score DECIMAL,
    res_eye_contact_score DECIMAL,
    res_grammar_score DECIMAL,
    res_total_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vs.videoid,
        vs.fillers_score::DECIMAL,
        vs.pause_rate_score::DECIMAL,
        vs.emotion_score::DECIMAL,
        vs.energy_score::DECIMAL,
        vs.eye_contact_score::DECIMAL,
        vs.grammar_score::DECIMAL,
        vs.total_score::DECIMAL
    FROM videoScore vs
    WHERE vs.videoid = v1 OR vs.videoid = v2;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_video_score_and_analysis(
    p_video_ids INT[],
    p_user_id INT
)
RETURNS JSON AS $$
DECLARE
    score_list JSONB := '[]'::JSONB;
    analysis_list JSONB := '[]'::JSONB;
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT v.videoid,
               vs.fillers_score,
               vs.pause_rate_score,
               vs.emotion_score,
               vs.energy_score,
               vs.eye_contact_score,
               vs.grammar_score,
               vs.total_score,
               va.fillers_word,
               va.rate_of_stop,
               va.emotion_analysis,
               va.energy_statistics,
               va.eye_contact,
               va.grammar_mistakes,
               va.total_score AS analysis_total_score
        FROM Video v
        LEFT JOIN videoScore vs ON vs.videoid = v.videoid
        LEFT JOIN VideoAnalysis va ON va.videoid = v.videoid
        WHERE v.userid = p_user_id
          AND v.videoid = ANY(p_video_ids)
        ORDER BY array_position(p_video_ids, v.videoid)
    LOOP
        score_list := score_list || jsonb_build_array(
            jsonb_build_object(
                'videoID', rec.videoid,
                'fillers_score', rec.fillers_score,
                'pause_rate_score', rec.pause_rate_score,
                'emotion_score', rec.emotion_score,
                'energy_score', rec.energy_score,
                'eye_contact_score', rec.eye_contact_score,
                'grammar_score', rec.grammar_score,
                'total_score', rec.total_score
            )
        );

        analysis_list := analysis_list || jsonb_build_array(
            jsonb_build_object(
                'videoID', rec.videoid,
                'fillers_Word', rec.fillers_word,
                'rate_Of_Stop', rec.rate_of_stop,
                'emotion_analysis', rec.emotion_analysis,
                'energy_Statistics', rec.energy_statistics,
                'eye_Contact', rec.eye_contact,
                'grammar_Mistakes', rec.grammar_mistakes,
                'total_Score', rec.analysis_total_score
            )
        );
    END LOOP;

    RETURN json_build_object(
        'scores', score_list,
        'analysis', analysis_list
    );
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
    p_fillers_weight DECIMAL(5,4),
    p_pause_rate_weight DECIMAL(5,4),
    p_emotion_weight DECIMAL(5,4),
    p_energy_weight DECIMAL(5,4),
    p_eye_contact_weight DECIMAL(5,4),
    p_grammar_weight DECIMAL(5,4)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_fillers_weight + p_pause_rate_weight + p_emotion_weight + p_energy_weight + p_eye_contact_weight + p_grammar_weight <> 1.0 THEN
        RETURN FALSE;
    END IF;

    UPDATE MetricWeight SET
        fillers_weight = p_fillers_weight,
        pause_rate_weight = p_pause_rate_weight,
        emotion_weight = p_emotion_weight,
        energy_weight = p_energy_weight,
        eye_contact_weight = p_eye_contact_weight,
        grammar_weight = p_grammar_weight
    WHERE userID = p_user_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION insert_metric_weight(
    p_user_id INT,
    p_fillers_weight DECIMAL(5,4),
    p_pause_rate_weight DECIMAL(5,4),
    p_emotion_weight DECIMAL(5,4),
    p_energy_weight DECIMAL(5,4),
    p_eye_contact_weight DECIMAL(5,4),
    p_grammar_weight DECIMAL(5,4)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_fillers_weight + p_pause_rate_weight + p_emotion_weight + p_energy_weight + p_eye_contact_weight + p_grammar_weight <> 1.0 THEN
        RETURN FALSE;
    END IF;

    INSERT INTO MetricWeight (
        userID,
        fillers_weight,
        pause_rate_weight,
        emotion_weight,
        energy_weight,
        eye_contact_weight,
        grammar_weight
    ) VALUES (
        p_user_id,
        p_fillers_weight,
        p_pause_rate_weight,
        p_emotion_weight,
        p_energy_weight,
        p_eye_contact_weight,
        p_grammar_weight
    );

    RETURN TRUE;
EXCEPTION WHEN unique_violation THEN
    RETURN FALSE;
END;
$$;

CREATE OR REPLACE FUNCTION insert_or_update_video_metric_weight(
    p_video_id INT,
    p_fillers_weight DECIMAL(5,4),
    p_pause_rate_weight DECIMAL(5,4),
    p_emotion_weight DECIMAL(5,4),
    p_energy_weight DECIMAL(5,4),
    p_eye_contact_weight DECIMAL(5,4),
    p_grammar_weight DECIMAL(5,4)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_fillers_weight + p_pause_rate_weight + p_emotion_weight + p_energy_weight + p_eye_contact_weight + p_grammar_weight <> 1.0 THEN
        RETURN FALSE;
    END IF;

    INSERT INTO VideoMetricWeight (
        videoID,
        fillers_weight,
        pause_rate_weight,
        emotion_weight,
        energy_weight,
        eye_contact_weight,
        grammar_weight
    ) VALUES (
        p_video_id,
        p_fillers_weight,
        p_pause_rate_weight,
        p_emotion_weight,
        p_energy_weight,
        p_eye_contact_weight,
        p_grammar_weight
    )
    ON CONFLICT (videoID) DO UPDATE SET
        fillers_weight = EXCLUDED.fillers_weight,
        pause_rate_weight = EXCLUDED.pause_rate_weight,
        emotion_weight = EXCLUDED.emotion_weight,
        energy_weight = EXCLUDED.energy_weight,
        eye_contact_weight = EXCLUDED.eye_contact_weight,
        grammar_weight = EXCLUDED.grammar_weight;

    RETURN TRUE;
EXCEPTION WHEN foreign_key_violation OR check_violation OR unique_violation THEN
    RETURN FALSE;
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
    fillers_score DECIMAL(5,2),
    pause_rate_score DECIMAL(5,2),
    emotion_score DECIMAL(5,2),
    energy_score DECIMAL(5,2),
    eye_contact_score DECIMAL(5,2),
    grammar_score DECIMAL(5,2),
    total_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vs.fillers_score, vs.pause_rate_score, vs.emotion_score, vs.energy_score,
        vs.eye_contact_score, vs.grammar_score, vs.total_score
    FROM videoScore vs
    WHERE vs.videoID = p_video_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE insert_video_scores(
    p_video_id INTEGER,
    p_fillers_score DECIMAL(5,2),
    p_pause_rate_score DECIMAL(5,2),
    p_emotion_score DECIMAL(5,2),
    p_energy_score DECIMAL(5,2),
    p_eye_contact_score DECIMAL(5,2),
    p_grammar_score DECIMAL(5,2),
    p_total_score DECIMAL(5,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO videoScore (
        videoID, fillers_score, pause_rate_score, emotion_score, energy_score,
        eye_contact_score, grammar_score, total_score
    ) VALUES (
        p_video_id, p_fillers_score, p_pause_rate_score, p_emotion_score, p_energy_score,
        p_eye_contact_score, p_grammar_score, p_total_score
    );
END;
$$;

CREATE OR REPLACE PROCEDURE insert_or_update_video_analysis(
    p_video_id INTEGER,
    p_fillers_word JSONB,
    p_rate_of_stop DECIMAL(10,4),
    p_emotion_analysis JSONB,
    p_energy_statistics JSONB,
    p_eye_contact JSONB,
    p_grammar_mistakes JSONB,
    p_total_score DECIMAL(10,4)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO VideoAnalysis (
        videoID,
        fillers_Word,
        rate_Of_Stop,
        emotion_analysis,
        energy_Statistics,
        eye_Contact,
        grammar_Mistakes,
        total_Score
    ) VALUES (
        p_video_id,
        p_fillers_word,
        p_rate_of_stop,
        p_emotion_analysis,
        p_energy_statistics,
        p_eye_contact,
        p_grammar_mistakes,
        p_total_score
    )
    ON CONFLICT (videoID) DO UPDATE SET
        fillers_Word = EXCLUDED.fillers_Word,
        rate_Of_Stop = EXCLUDED.rate_Of_Stop,
        emotion_analysis = EXCLUDED.emotion_analysis,
        energy_Statistics = EXCLUDED.energy_Statistics,
        eye_Contact = EXCLUDED.eye_Contact,
        grammar_Mistakes = EXCLUDED.grammar_Mistakes,
        total_Score = EXCLUDED.total_Score;
END;
$$;

