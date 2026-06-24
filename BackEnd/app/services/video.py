import asyncio
from openai import AsyncOpenAI
from ..services.report import video_report
from ..models.IAnalysisModel import AnalysisInput
from ..schemas.video import MetricWeights, Scores
from ..models.facial_analysis import FacialAnalysis
from ..models.audio_analysis import AudioAnalysis
from ..models.text_analysis import TextAnalysis
from .video_standardize import standardize_video
from concurrent.futures import ThreadPoolExecutor
from ..db import get_db_connection
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool
import language_tool_python
import uuid
import os
import shutil
import json
import whisper
import subprocess
import mediapipe as mp
import os
from dotenv import load_dotenv
load_dotenv()


def _extract_audio_from_video(video_path: str) -> str:
    audio_folder = "audio"
    os.makedirs(audio_folder, exist_ok=True)
    audio_path = os.path.join(audio_folder, f"{uuid.uuid4()}.wav")

    try:
        subprocess.run(["ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract audio from video {video_path}: {e}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg.")

    return audio_path

def _get_video_duration(video_path: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error extracting duration from {video_path}: {e}")
        return 0.0
    except FileNotFoundError:
        print("ffprobe not found. Please install FFmpeg/ffprobe.")
        return 0.0


def _get_video_filename(video_id: int) -> str | None:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT videoName FROM Video WHERE videoID = %s", (video_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close()
        conn.close()


def _json_default(obj):
    """Convert nonstandard numeric types to JSON serializable primitives."""
    try:
        return obj.tolist()
    except Exception:
        pass
    try:
        return float(obj)
    except Exception:
        pass
    try:
        return int(obj)
    except Exception:
        pass
    try:
        return str(obj)
    except Exception:
        pass
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _normalize_json_values(obj):
    if isinstance(obj, dict):
        return {k: _normalize_json_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize_json_values(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_normalize_json_values(v) for v in obj)
    if obj is None or isinstance(obj, (str, bool, int, float)):
        return obj
    if hasattr(obj, "tolist"):
        try:
            return _normalize_json_values(obj.tolist())
        except Exception:
            pass
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")
    try:
        return float(obj)
    except Exception:
        pass
    try:
        return int(obj)
    except Exception:
        pass
    return str(obj)


def _insert_scores(video_id: int, scores: Scores, cur=None, conn=None):
    """Insert video scores using stored procedure."""
    own_conn = conn is None
    if own_conn:
        conn = get_db_connection()
        cur = conn.cursor()
    try:
        query = """
        CALL insert_video_scores(%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (
            video_id,
            scores.fillers_score,
            scores.pause_rate_score,
            scores.emotion_score,
            scores.energy_score,
            scores.eye_contact_score,
            scores.grammar_score,
            scores.total_score
        ))

        if own_conn:
            conn.commit()
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise ValueError(f"Failed to insert scores: {str(e)}")
    finally:
        if own_conn:
            cur.close()
            conn.close()


def _update_video_status(video_id: int, status: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE Video SET status = %s WHERE videoID = %s", (status, video_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to update video status: {str(e)}")
    finally:
        cur.close()
        conn.close()


def _insert_or_update_video_analysis(
    video_id: int,
    fillers_word: dict | list,
    rate_of_stop: float,
    emotion_analysis: dict,
    energy_statistics: dict,
    eye_contact: dict,
    grammar_mistakes: dict | list,
    total_score: float,
    cur=None,
    conn=None,
):
    own_conn = conn is None
    if own_conn:
        conn = get_db_connection()
        cur = conn.cursor()
    try:
        query = (
            "CALL insert_or_update_video_analysis(%s::integer, %s::jsonb, %s::numeric, %s::jsonb, "
            "%s::jsonb, %s::jsonb, %s::jsonb, %s::numeric);"
        )
        cur.execute(query, (
            video_id,
            json.dumps(fillers_word, default=_json_default),
            rate_of_stop,
            json.dumps(emotion_analysis, default=_json_default),
            json.dumps(energy_statistics, default=_json_default),
            json.dumps(eye_contact, default=_json_default),
            json.dumps(grammar_mistakes, default=_json_default),
            total_score,
        ))
        if own_conn:
            conn.commit()
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise ValueError(f"Failed to insert video analysis: {str(e)}")
    finally:
        if own_conn:
            cur.close()
            conn.close()


def scoring(facial_results: dict, audio_results: dict, text_results: dict, weights: MetricWeights, video_id: int) -> Scores:
    """Compute the final Scores object from analysis results and user weights."""

    total_words = text_results.get("total_words", 0) or 0
    filler_count = text_results.get("filler_count", 0) or 0
    filler_rate_pct = (filler_count / total_words) * 100 if total_words > 0 else 0.0
    fillers_score = max(0.0, 1.0 - (filler_rate_pct / 100.0))

    pause_rate_pct = text_results.get("pause_rate", 0.0) or 0.0
    pause_rate_score = min(max(pause_rate_pct / 100.0, 0.0)+0.1, 1.0)

    grammar_score = min(max(float(text_results.get("grammar_score", 1.0) or 1.0), 0.0), 1.0)

    emotions = facial_results.get("face_emotions", {}) or {}
    happy = float(emotions.get("happy", 0.0))
    neutral = float(emotions.get("neutral", 0.0))
    surprise = float(emotions.get("surprise", 0.0))
    angry = float(emotions.get("angry", 0.0))
    disgust = float(emotions.get("disgust", 0.0))
    fear = float(emotions.get("fear", 0.0))
    sad = float(emotions.get("sad", 0.0))

    positive = happy + neutral + 0.5 * surprise
    negative = angry + disgust + 0.8 * fear + 0.9 * sad
    raw_emotion_score = positive / (positive + negative) * 100.0 if (positive + negative) > 0 else 0.0
    emotion_pct = max(0.0, min(raw_emotion_score, 100.0))
    emotion_score = emotion_pct / 100.0

    eye_contact_raw = facial_results.get("eye_contact_score", 0.0) or 0.0
    eye_contact_score = min(max(float(eye_contact_raw), 0.0), 1.0)

    energy_stats = audio_results.get("energy_stats", {}) or {}
    avg_energy = float(energy_stats.get("average_energy", 0.0) or 0.0)
    max_energy = float(energy_stats.get("max_energy", 0.0) or 0.0)
    if max_energy > 0:
        energy_pct = (avg_energy / max_energy) * 100.0
    else:
        energy_pct = 0.0
    energy_score = min(1 - max(energy_pct / 100.0, 0.0), 1.0)

    try:
        total_score = (
            fillers_score * float(weights.fillers_weight)
            + pause_rate_score * float(weights.pause_rate_weight)
            + emotion_score * float(weights.emotion_weight)
            + energy_score * float(weights.energy_weight)
            + eye_contact_score * float(weights.eye_contact_weight)
            + grammar_score * float(weights.grammar_weight)
        )
    except Exception as e:
        print(f"Error computing total score for video {video_id}: {e}")
        components = [fillers_score, pause_rate_score, emotion_score, energy_score, eye_contact_score, grammar_score]
        total_score = sum(components) / len(components) if components else 0.0

    total_score = min(max(float(total_score), 0.0), 1.0)

    return Scores(
        fillers_score=round(float(fillers_score), 4),
        pause_rate_score=round(float(pause_rate_score), 4),
        emotion_score=round(float(emotion_score), 4),
        energy_score=round(float(energy_score), 4),
        eye_contact_score=round(float(eye_contact_score), 4),
        grammar_score=round(float(grammar_score), 4),
        total_score=round(float(total_score), 4),
        video_id=video_id
    )


def _process_video_sync(video_id: int, weights: MetricWeights | None = None, video_path: str | None = None) -> dict:
    """Process a video and return scores + report. Raises exception on failure."""
    if video_path is None:
        file_name = _get_video_filename(video_id)
        if not file_name:
            raise ValueError(f"No video found for video_id={video_id}")
        video_path = os.path.join("videos", file_name)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if weights is None:
        weights = MetricWeights()

    audio_path = None
    try:
        # 1. Load Face Landmarker configuration
        model_path = '../AI/face_landmarker.task'
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        face_options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=True,
        )

        # 2. Load Grammar Tool
        grammar_tool = None
        try:
            grammar_tool = language_tool_python.LanguageTool('en-US')
        except Exception as e:
            print(f"Warning: Failed to initialize grammar tool: {e}")

        # 3. Extract audio and transcribe
        audio_path = _extract_audio_from_video(video_path)
        
        # Use base.en for reliability (smaller, faster, avoids checksum issues)
        whisper_model = whisper.load_model("base.en")
        whisper_result = whisper_model.transcribe(audio_path, word_timestamps=True)

        # 4. Run analysis models
        facial_model = FacialAnalysis(face_options=face_options)
        audio_model = AudioAnalysis()
        text_model = TextAnalysis(grammar_tool=grammar_tool)

        analysis_input = AnalysisInput(
            audio_path=audio_path,
            video_path=video_path,
            whisper_result=whisper_result
        )

        # 5. Execute analysis in parallel using a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three tasks to the pool concurrently
            future_text = executor.submit(text_model.analyze, analysis_input)
            future_facial = executor.submit(facial_model.analyze, analysis_input)
            future_audio = executor.submit(audio_model.analyze, analysis_input)

            # Gather the results as they finish (.result() blocks until that specific thread completes)
            text_results = future_text.result()
            facial_results = future_facial.result()
            audio_results = future_audio.result()
        
        scores = scoring(facial_results, audio_results, text_results, weights, video_id=video_id)
        # 5. Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            _insert_or_update_video_analysis(
                video_id=video_id,
                fillers_word=text_results.get("fillers_word", {}),
                rate_of_stop=float(text_results.get("pause_rate", 0.0) or 0.0),
                emotion_analysis=facial_results.get("face_emotions", {}),
                energy_statistics=audio_results.get("energy_stats", {}),
                eye_contact={"score": facial_results.get("eye_contact_score", 0.0)},
                grammar_mistakes=text_results.get("grammar_mistakes", []),
                total_score=float(scores.total_score),
                cur=cur,
                conn=conn,
            )
            _insert_scores(video_id, scores, cur=cur, conn=conn)
            conn.commit()
        except Exception as e:
            print(f"Error inserting analysis results for video {video_id}: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
            
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            report = "Video analysis completed successfully. LLM report generation unavailable (API key not configured)."
        else:
            Groq_client = AsyncOpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            
 
        
        report = asyncio.run(video_report(Groq_client, scores, {
            "text_results": text_results,
            "facial_results": facial_results,
            "audio_results": audio_results
        }))
        print(f"Report generated for video {video_id}")
        return {
            "scores": scores,
            "report": report
        }

    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        # Re-raise so caller can mark as FAILED
        raise

    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


async def handle_uploaded_video(file: UploadFile, user_id: int, video_name: str, weights: MetricWeights | None = None):
    """Handle video upload, validation, and async processing."""
    folder = "videos"
    os.makedirs(folder, exist_ok=True)

    if not file.filename:
        raise ValueError("Uploaded file must have a filename")

    ext = os.path.splitext(file.filename)[1]
    unique_name = video_name + "_" + str(uuid.uuid4()) + ext
    unique_name = unique_name[:50]
    output_path = os.path.join(folder, unique_name)

    duration = 0.0
    video_id = None

    try:
        with open(output_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            duration = _get_video_duration(output_path)
        except Exception as e:
            duration = 0.0

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT add_video(%s, %s, %s, %s)",
            (unique_name, user_id, duration, "PENDING")
        )

        rec = cur.fetchone()[0]
        video_id = rec["video_id"]

        if weights is not None:
            cur.execute(
                "SELECT insert_or_update_video_metric_weight(%s::integer, %s::numeric, %s::numeric, %s::numeric, %s::numeric, %s::numeric, %s::numeric)",
                (
                    video_id,
                    weights.fillers_weight,
                    weights.pause_rate_weight,
                    weights.emotion_weight,
                    weights.energy_weight,
                    weights.eye_contact_weight,
                    weights.grammar_weight,
                )
            )
            insert_result = cur.fetchone()[0]
            if not insert_result:
                raise ValueError("Failed to persist metric weights for video")

        conn.commit()
        cur.close()
        conn.close()

        # Standardize video
        unique_standardized_path = os.path.join("videos", f"standardized_{uuid.uuid4()}.mp4")
        standardized_path = await run_in_threadpool(
            standardize_video, output_path, unique_standardized_path
        )
        
        if standardized_path and os.path.exists(standardized_path):
            try:
                os.replace(standardized_path, output_path)
            except Exception as e:
                if os.path.exists(standardized_path):
                    try:
                        os.remove(standardized_path)
                    except OSError:
                        pass
                raise ValueError(f"Failed to replace video: {str(e)}")
        else:
            raise ValueError("Video standardization failed")

        # Process video - raises exception on failure
        result = await run_in_threadpool(
            _process_video_sync,
            video_id,
            weights or MetricWeights(),
            output_path
        )
        
        # Success - mark as DONE
        _update_video_status(video_id, "DONE")
        
        return {
            "video_id": video_id,
            "file_name": unique_name,
            "duration": duration,
            "report": result["report"],
            "status": "DONE",
            "scores": result["scores"]
        }

    except Exception as e:
        # Clean up file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass

        # Mark as FAILED
        if video_id is not None:
            try:
                _update_video_status(video_id, "FAILED")
            except Exception:
                pass

        # Re-raise the original error
        raise