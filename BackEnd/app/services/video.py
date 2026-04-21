from ..models.IAnalysisModel import IAnalysisModel, AnalysisInput
from ..schemas.video import MetricWeights, Scores
from ..models.facial_analysis import FacialAnalysis
from ..models.audio_analysis import AudioAnalysis
from ..models.text_analysis import TextAnalysis
from video_standardize import standardize_video
from db import get_db_connection
from fastapi import UploadFile
import uuid
import os
import shutil
import json
import whisper
import subprocess


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
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.callproc('insert_video_scores', (
            video_id, 
            scores.speechClarity, 
            scores.speechFluency, 
            scores.speechConfidence,
            scores.speechExpressiveness, 
            scores.speechEngagement, 
            scores.facialConfidence,
            scores.facialApproachability, 
            scores.facialEngagement, 
            scores.videoProfessionalism,
            scores.totalScore
        ))
        conn.commit()
    except Exception as e:
        print(f"Error inserting scores for video_id {video_id}: {e}")
        raise
    finally:
        cur.close()  # type: ignore
        conn.close() # type: ignore


def scoring(facial_results: dict, audio_results: dict, text_results: dict, weights: MetricWeights) -> Scores:
    # placeholder implementation: compute scores based on results and weights
    # for now, return default Scores with zeros ----- to be discussed and implemented later
    return Scores(
        speechClarity=0.0,
        speechFluency=0.0,
        speechConfidence=0.0,
        speechExpressiveness=0.0,
        speechEngagement=0.0,
        facialConfidence=0.0,
        facialApproachability=0.0,
        facialEngagement=0.0,
        videoProfessionalism=0.0,
        totalScore=0.0
    )


def handle_uploaded_video(file: UploadFile, user_id: int, video_name: str):
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
            print("Error extracting duration:", e)
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

        # Standardize the video before sending to processing
        unique_standardized_path = os.path.join("videos", f"standardized_{uuid.uuid4()}.mp4")
        standardized_path = standardize_video(output_path, unique_standardized_path)
        if standardized_path and os.path.exists(standardized_path):
            try:
                os.replace(standardized_path, output_path)
            except Exception as e:
                print(f"Error replacing standardized video: {e}")
                if os.path.exists(standardized_path):
                    try:
                        os.remove(standardized_path)
                    except OSError:
                        pass
                raise
        else:
            raise ValueError("Standardization failed: no output file produced")

        scores = process_video(video_id, video_path=output_path)
        if scores is None:
            raise RuntimeError(f"Failed to process video {video_id}")
        _insert_scores(video_id, scores)
        status = "PROCESSED"
        return {
            "video_id": video_id,
            "file_name": unique_name,
            "duration": duration,
            "status": status
        }

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e


def process_video(video_id: int, weights: MetricWeights | None = None, video_path: str | None = None) -> Scores:
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
        # handle inputs
        audio_path = _extract_audio_from_video(video_path)
        whisper_model = whisper.load_model("medium.en")  # type: ignore
        whisper_result = whisper_model.transcribe(audio_path, word_timestamps=True)

        facial_model = FacialAnalysis()
        audio_model = AudioAnalysis()
        text_model = TextAnalysis()

        text_results = text_model.analyze(AnalysisInput(whisper_result=whisper_result))
        facial_results = facial_model.analyze(AnalysisInput(video_path=video_path))
        audio_results = audio_model.analyze(AnalysisInput(audio_path=audio_path))

        scores = scoring(facial_results, audio_results, text_results, weights)
        return scores
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        # Return default scores to prevent crash
        return Scores(
            speechClarity=0.0,
            speechFluency=0.0,
            speechConfidence=0.0,
            speechExpressiveness=0.0,
            speechEngagement=0.0,
            facialConfidence=0.0,
            facialApproachability=0.0,
            facialEngagement=0.0,
            videoProfessionalism=0.0,
            totalScore=0.0
        )
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


def add_analysis_model(model: IAnalysisModel):
    # logic?
    # return None
    pass

def get_scores(video_id: int) -> Scores | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM get_video_scores(%s)", (video_id,))
        row = cursor.fetchone()
        if row:
            return Scores(
                speechClarity=row[0],
                speechFluency=row[1],
                speechConfidence=row[2],
                speechExpressiveness=row[3],
                speechEngagement=row[4],
                facialConfidence=row[5],
                facialApproachability=row[6],
                facialEngagement=row[7],
                videoProfessionalism=row[8],
                totalScore=row[9]
            )
        return None
    finally:
        cursor.close()
        conn.close()