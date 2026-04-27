from ..models.IAnalysisModel import IAnalysisModel, AnalysisInput
from ..schemas.video import MetricWeights, Scores
from ..models.facial_analysis import FacialAnalysis
from ..models.audio_analysis import AudioAnalysis
from ..models.text_analysis import TextAnalysis
from .video_standardize import standardize_video
from ..db import get_db_connection
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool
import uuid
import os
import shutil
import json
# import whisper
import subprocess
# import torch
# import mediapipe as mp
# import asyncio


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
        CALL insert_video_scores(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (
        video_id,
        scores.speech_clarity,
        scores.speech_fluency,
        scores.speech_confidence,
        scores.speech_expressiveness,
        scores.speech_engagement,
        scores.facial_confidence,
        scores.facial_approachability,
        scores.facial_engagement,
        scores.video_professionalism,
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


def scoring(facial_results: dict, audio_results: dict, text_results: dict, weights: MetricWeights) -> Scores:
    # DISCUSSION NOTE: Scoring computation logic needs to be finalized in next meeting
    return Scores(
        speech_clarity=0.0,
        speech_fluency=0.0,
        speech_confidence=0.0,
        speech_expressiveness=0.0,
        speech_engagement=0.0,
        facial_confidence=0.0,
        facial_approachability=0.0,
        facial_engagement=0.0,
        video_professionalism=0.0,
        total_score=0.0,
        video_id=0
    )


def _process_video_sync(video_id: int, weights: MetricWeights, video_path: str) -> Scores:
    """Synchronous video processing - runs in thread pool."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if weights is None:
        weights = MetricWeights()

    audio_path = None
    try:
        # DISCUSSION NOTE: Video processing orchestration needs refinement
        # Current implementation is a placeholder; actual analysis pipeline TBD
        return Scores(
            speech_clarity=0.0,
            speech_fluency=0.0,
            speech_confidence=0.0,
            speech_expressiveness=0.0,
            speech_engagement=0.0,
            facial_confidence=0.0,
            facial_approachability=0.0,
            facial_engagement=0.0,
            video_professionalism=0.0,
            total_score=0.0,
            video_id=video_id
        )
    except Exception as e:
        raise RuntimeError(f"Video processing failed: {str(e)}")
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


async def handle_uploaded_video(file: UploadFile, user_id: int, video_name: str):
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
        conn.commit()
        cur.close()
        conn.close()

        video_id = rec["video_id"]

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
            _process_video_sync, video_id, MetricWeights(), output_path
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