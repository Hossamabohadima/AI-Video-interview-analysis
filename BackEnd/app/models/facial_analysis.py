from .IAnalysisModel import IAnalysisModel, AnalysisInput
from deepface import DeepFace
import cv2
import mediapipe as mp

class FacialAnalysis(IAnalysisModel):
    def __init__(self, face_options):
        """Initialize the FacialAnalysis model.

        Args:
            face_options: Options for the face landmarker.
        """
        super().__init__("FacialAnalysis")
        self.face_options = face_options

    def _analyze_emotions(self, video_path: str) -> dict:
        """Analyze emotions from a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            dict: Dictionary with average emotion scores.
        """
        cap = cv2.VideoCapture(video_path)
        emotion_sums = {e: 0.0 for e in ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']}
        frame_count, analyzed_count = 0, 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            if frame_count % 10 == 0:
                try:
                    results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    emotions = results[0]['emotion']
                    for emotion, score in emotions.items():
                        if emotion in emotion_sums:
                            emotion_sums[emotion] += score
                    analyzed_count += 1
                except Exception:
                    pass
            frame_count += 1
        
        cap.release()
        if analyzed_count > 0:
            return {e: (s / analyzed_count) for e, s in emotion_sums.items()}
        return {e: 0.0 for e in emotion_sums}

    def _analyze_eye_contact(self, video_path: str) -> float:
        """Analyze eye contact score from a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            float: Eye contact score.
        """
        cap = cv2.VideoCapture(video_path)
        results = []
        
        # Mediapipe constants needed inside
        FaceLandmarker = mp.tasks.vision.FaceLandmarker

        with FaceLandmarker.create_from_options(self.face_options) as landmarker:
            frame_index = 0
            fps = cap.get(cv2.CAP_PROP_FPS) or 30

            while True:
                ret, frame = cap.read()
                if not ret: break

                if frame_index % 10 == 0:
                    timestamp_ms = int((frame_index / fps) * 1000)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    detection = landmarker.detect_for_video(mp_image, timestamp_ms)

                    if detection.face_blendshapes:
                        blendshapes = {b.category_name: b.score for b in detection.face_blendshapes[0]}
                        deviation = (blendshapes.get('eyeLookInLeft', 0) + blendshapes.get('eyeLookInRight', 0) +
                                     blendshapes.get('eyeLookUpLeft', 0) + blendshapes.get('eyeLookDownLeft', 0)) / 4
                        results.append(round(1 - deviation, 2))
                    else:
                        results.append(0.0)
                frame_index += 1
        
        cap.release()
        return round(sum(results) / len(results), 2) if results else 0.0

    def analyze(self, input_data: AnalysisInput) -> dict:
        """Analyze facial data from video.

        Args:
            input_data (AnalysisInput): Input data containing video_path.

        Returns:
            dict: Dictionary with face_emotions and eye_contact_score.
        """
        if not input_data.video_path:
            raise ValueError("FacialAnalysis requires input_data.video_path")

        return {
            "face_emotions": self._analyze_emotions(input_data.video_path),
            "eye_contact_score": self._analyze_eye_contact(input_data.video_path)
        }