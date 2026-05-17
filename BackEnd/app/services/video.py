from ..models.IAnalysisModel import IAnalysisModel, AnalysisInput
from ..schemas.video import MetricWeights, Scores
from ..models.facial_analysis import FacialAnalysis
from ..models.audio_analysis import AudioAnalysis
from ..models.text_analysis import TextAnalysis
from .video_standardize import standardize_video
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
import torch
import mediapipe as mp
import asyncio


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


def _insert_scores(video_id: int, scores: Scores):
    """Insert video scores using stored procedure."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
       # Using cur.execute with the CALL keyword
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

        # Crucial: Don't forget to commit if you aren't using an autocommit connection
        # conn.commit()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to insert scores: {str(e)}")
    finally:
        cur.close()
        conn.close()


def scoring(facial_results: dict, audio_results: dict, text_results: dict, weights: MetricWeights, video_id: int) -> Scores:
    """Compute the final Scores object from analysis results and user weights.

    All returned scores are normalized to the range 0.0 - 1.0 to match schema expectations. The total_score is a weighted average of the individual metrics, also normalized to 0.0 - 1.0.
    """
    # Text-based metrics
    total_words = text_results.get("total_words", 0) or 0
    filler_count = text_results.get("filler_count", 0) or 0
    # filler rate in percent
    filler_rate_pct = (filler_count / total_words) * 100 if total_words > 0 else 0.0
    # fewer fillers => higher score (1.0 is best, 0.0 is worst)
    fillers_score = max(0.0, 1.0 - (filler_rate_pct / 100.0))

    # Pause / rate-of-stop: text_results should provide a pause quality percent (0-100)
    pause_rate_pct = text_results.get("pause_rate", 0.0) or 0.0
    pause_rate_score = min(max(pause_rate_pct / 100.0, 0.0), 1.0)

    # Grammar: text_results returns grammar_score already normalized to 0.0 - 1.0
    grammar_score = min(max(float(text_results.get("grammar_score", 1.0) or 1.0), 0.0), 1.0)

    # Facial emotions: Averages DeepFace from facial_results["face_emotions"]
    emotions = facial_results.get("face_emotions", {}) or {}
    # normalize missing keys to 0
    happy = float(emotions.get("happy", 0.0))
    neutral = float(emotions.get("neutral", 0.0))
    surprise = float(emotions.get("surprise", 0.0))
    angry = float(emotions.get("angry", 0.0))
    disgust = float(emotions.get("disgust", 0.0))
    fear = float(emotions.get("fear", 0.0))
    sad = float(emotions.get("sad", 0.0))

    # the emotion score is a simple weighted combination of positive vs negative emotions, normalized to 0..1
    positive = happy + neutral + 0.5 * surprise
    negative = angry + disgust + fear + sad
    raw_emotion_score = positive - negative

    # ensure emotion score is between 0 and 100 before normalizing to 0..1
    emotion_pct = max(0.0, min(raw_emotion_score, 100.0))
    emotion_score = emotion_pct / 100.0

    # Eye contact: facial_results provides a 0..1 score from the analyzer
    eye_contact_raw = facial_results.get("eye_contact_score", 0.0) or 0.0
    eye_contact_score = min(max(float(eye_contact_raw), 0.0), 1.0)

    # Energy: use average / max to compute relative energy percentage
    energy_stats = audio_results.get("energy_stats", {}) or {}
    avg_energy = float(energy_stats.get("average_energy", 0.0) or 0.0)
    max_energy = float(energy_stats.get("max_energy", 0.0) or 0.0)
    if max_energy > 0:
        energy_pct = (avg_energy / max_energy) * 100.0
    else:
        energy_pct = 0.0
    energy_score = min(max(energy_pct / 100.0, 0.0), 1.0)

    # Compute weighted total_score (weights expected 0..1)
    try:
        total_score = (
            fillers_score * float(weights.fillers_weight)
            + pause_rate_score * float(weights.pause_rate_weight)
            + emotion_score * float(weights.emotion_weight)
            + energy_score * float(weights.energy_weight)
            + eye_contact_score * float(weights.eye_contact_weight)
            + grammar_score * float(weights.grammar_weight)
        )
    except Exception:
        # If weights are missing or invalid, back to equal weighting
        components = [fillers_score, pause_rate_score, emotion_score, energy_score, eye_contact_score, grammar_score]
        total_score = sum(components) / len(components) if components else 0.0

    # Clamp final total to 0..1
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

def _process_video_sync(video_id: int, weights: MetricWeights | None = None, video_path: str | None = None) -> Scores:
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
        # 1. Load dependencies for model initialization
        # Load Face Landmarker configuration
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

        # Load Grammar Tool for text analysis (handle grammar_mistakes dependencies)
        grammar_tool = None
        try:
            grammar_tool = language_tool_python.LanguageTool('en-US')
        except ImportError:
            print("Warning: language-tool-python not installed. Grammar analysis will be skipped.")
        except Exception as e:
            print(f"Warning: Failed to initialize grammar tool: {e}")

        # 2. Extract raw data (Audio and Transcription)
        audio_path = _extract_audio_from_video(video_path)
        whisper_model = whisper.load_model("medium.en")  # type: ignore
        whisper_result = whisper_model.transcribe(audio_path, word_timestamps=True)

        # 3. Instantiate models with injected dependencies
        facial_model = FacialAnalysis(face_options=face_options)
        audio_model = AudioAnalysis()
        text_model = TextAnalysis(grammar_tool=grammar_tool)

        # 4. Create unified input object
        analysis_input = AnalysisInput(
            audio_path=audio_path,
            video_path=video_path,
            whisper_result=whisper_result
        )

        # 5. Execute analysis via the standardized interface
        text_results = text_model.analyze(analysis_input)
        facial_results = facial_model.analyze(analysis_input)
        audio_results = audio_model.analyze(analysis_input)

        scores = scoring(facial_results, audio_results, text_results, weights, video_id=video_id)
        return scores

    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        # Return default scores to prevent crash
        return Scores(
            video_id=video_id,
            fillers_score=0.0,
            pause_rate_score=0.0,
            emotion_score=0.0,
            energy_score=0.0,
            eye_contact_score=0.0,
            grammar_score=0.0,
            total_score=0.0,
        )
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
    output_path = os.path.join(folder, unique_name)

    duration = 0.0

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
                "SELECT insert_or_update_video_metric_weight(%s, %s, %s, %s, %s, %s, %s)",
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

        # Run video standardization in thread pool (CPU-intensive)
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

        # Run video processing in thread pool (CPU-intensive)
        scores = await run_in_threadpool(
            _process_video_sync,
            video_id,
            weights or MetricWeights(),
            output_path
        )
        
        if scores is None:
            raise RuntimeError(f"Failed to process video {video_id}")
        
        _insert_scores(video_id, scores)
        
        return {
            "video_id": video_id,
            "file_name": unique_name,
            "duration": duration,
            "status": "PROCESSED"
        }

    except Exception as e:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        raise


async def process_video(video_id: int, weights: MetricWeights | None = None, video_path: str | None = None) -> Scores:
    """Asynchronously process video using thread pool for CPU-intensive operations."""
    if video_path is None:
        file_name = _get_video_filename(video_id)
        if not file_name:
            raise ValueError(f"No video found for video_id={video_id}")
        video_path = os.path.join("videos", file_name)

    if weights is None:
        weights = MetricWeights()

    return await run_in_threadpool(_process_video_sync, video_id, weights, video_path)