from BackEnd.app.schemas.video import MetricWeights, Scores
from BackEnd.app.models.IAnalysisModel import IAnalysisModel, AnalysisInput
from BackEnd.app.models.facial_analysis import FacialAnalysis
from BackEnd.app.models.audio_analysis import AudioAnalysis
from BackEnd.app.models.text_analysis import TextAnalysis
from db import get_db_connection
from fastapi import UploadFile
import uuid
import os
import shutil
import json
import cv2
import whisper
import subprocess


def _extract_audio_from_video(video_path: str) -> str:
    audio_folder = "audio"
    os.makedirs(audio_folder, exist_ok=True)
    audio_path = os.path.join(audio_folder, f"{uuid.uuid4()}.wav")

    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_path])

    return audio_path

def _get_video_duration(video_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


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
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO videoScore (
                videoID, SpeechClarity, SpeechFluency, SpeechConfidence, SpeechExpressiveness, SpeechEngagement,
                FacialConfidence, FacialApproachability, FacialEngagement, VideoProfessionalism, totalScore
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                video_id, scores.speechClarity, scores.speechFluency, scores.speechConfidence,
                scores.speechExpressiveness, scores.speechEngagement, scores.facialConfidence,
                scores.facialApproachability, scores.facialEngagement, scores.videoProfessionalism,
                scores.totalScore
            )
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def scoring(facial_results: dict, audio_results: dict, text_results: dict, weights: MetricWeights) -> Scores:
    # to be discussed
    # return Scores()
    pass


def handle_uploaded_video(file: UploadFile, user_id: int, video_name: str):
    folder = "videos"
    os.makedirs(folder, exist_ok=True)

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

        try:
            scores = process_video(video_id, video_path=output_path)
            _insert_scores(video_id, scores)
            status = "PROCESSED"
        except Exception as e:
            print(f"Video processing failed for video_id={video_id}: {e}")
            status = "PENDING"
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


def process_video(video_id: int, weights: MetricWeights | None = None, video_path: str | None = None) -> Scores | None:
    if video_path is None:
        file_name = _get_video_filename(video_id)
        if not file_name:
            raise ValueError(f"No video found for video_id={video_id}")
        video_path = os.path.join("videos", file_name)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if weights is None:
        weights = MetricWeights()

    # handle inputs
    audio_path = _extract_audio_from_video(video_path)
    whisper_model = whisper.load_model("medium.en")
    whisper_result = whisper_model.transcribe(audio_path, word_timestamps=True)


    try:
        facial_model = FacialAnalysis()
        audio_model = AudioAnalysis()
        text_model = TextAnalysis()


        text_results = text_model.analyze(AnalysisInput(whisper_result=whisper_result))
        facial_results = facial_model.analyze(AnalysisInput(video_path=video_path))
        audio_results = audio_model.analyze(AnalysisInput(audio_path=audio_path))

        scores = scoring(facial_results, audio_results, text_results, weights)

        return scores
    finally:
        if os.path.exists(audio_path):
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