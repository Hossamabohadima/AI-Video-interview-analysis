from .IAnalysisModel import IAnalysisModel, AnalysisInput
from deepface import DeepFace
import cv2

# helper functions for facial analysis

def face_emotion(cap):
    """
    Analyze facial emotions in a video capture by sampling frames and averaging detected scores.

    Args:
        cap: An OpenCV video capture object opened for the target video.

    Returns:
        dict: Average emotion scores across analyzed frames, keyed by emotion label.
    """
    
    # Initialize dictionary to store the sum of emotion scores
    emotion_sums = {
        'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 
        'happy': 0.0, 'sad': 0.0, 'surprise': 0.0, 'neutral': 0.0
    }
    
    frame_count = 0
    analyzed_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Analyze every 10th frame to speed things up
        if frame_count % 10 == 0:
            try:
                # DeepFace.analyze returns a list (in case of multiple faces)
                # enforce_detection=False prevents the code from crashing if no face is found
                results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                
                # Assume we are tracking the primary face (index 0)
                emotions = results[0]['emotion']
                
                for emotion, score in emotions.items():
                    if emotion in emotion_sums:
                        emotion_sums[emotion] += score
                
                analyzed_count += 1

            except Exception as e:
                print(f"Error analyzing frame {frame_count}: {e}") # is this is right to print??

        frame_count += 1

    cap.release()
    
    # Calculate average emotion scores
    if analyzed_count > 0:
        average_emotions = {emotion: (score / analyzed_count) for emotion, score in emotion_sums.items()}
    else:
        average_emotions = {emotion: 0.0 for emotion in emotion_sums}

    return average_emotions

def eye_contact():
    """
    Estimate eye contact quality from a video stream.

    Returns:
        int: A placeholder eye contact score (currently not implemented).
    """
    # not implemented yet.
    return 0

# main class for facial analysis
class FacialAnalysis(IAnalysisModel):
    """
    Implements facial analysis to extract emotions and eye-contact metrics from a video.
    """
    def __init__(self):
        """
        Initialize the facial analysis model.
        """
        super().__init__("FacialAnalysis")
        self.model = None

    def analyze(self, input_data: AnalysisInput) -> dict:
        """
        Analyze a video file for facial emotion and eye contact metrics.

        Args:
            input_data (AnalysisInput): Input model containing video_path.

        Returns:
            dict: A dictionary containing computed facial metrics (emotion distribution and eye contact score).
        """
        if not input_data.video_path:
            raise ValueError("FacialAnalysis requires input_data.video_path")

        cap = cv2.VideoCapture(input_data.video_path)
        face_emotions = face_emotion(cap)
        eye_contact_score = eye_contact()

        return {
            "face_emotions": face_emotions,
            "eye_contact_score": eye_contact_score
        }