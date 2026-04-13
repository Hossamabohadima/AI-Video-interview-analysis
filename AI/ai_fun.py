import whisper
from deepface import DeepFace
import cv2

def face_emotion(cap):
    print("Processing video... this may take a minute.")
    
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
                print ("analyzed_count:",analyzed_count)

            except Exception as e:
                print(f"Error occurred at frame {frame_count}: {e}")

        frame_count += 1

    cap.release()
    
    # Calculate average emotion scores
    if analyzed_count > 0:
        average_emotions = {emotion: (score / analyzed_count) for emotion, score in emotion_sums.items()}
    else:
        average_emotions = {emotion: 0.0 for emotion in emotion_sums}

    print("Done!")
    return average_emotions

def extract_words(audio_path):
    """Transcribe audio and extract word-level timestamps.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        list: List of word dictionaries with timestamps.
    """
    result = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for seg in result["segments"]:
        for w in seg["words"]:
            words.append(w)
    return words

def speech_rate(words):
    """Calculate speech rate in words per minute (WPM).
    
    Args:
        words (list): List of word dictionaries with 'start' and 'end' timestamps.
    
    Returns:
        float: Speech rate in words per minute.
    """
    duration = words[-1]['end'] - words[0]['start']
    total_words = len(words)
    return float(total_words / (duration / 60))

def pause_rate(words):
    """
    Calculate pause rate as the average duration of pauses per second of speech.
    
    Args:
        words (list): List of word dictionaries with 'start' and 'end' timestamps.
    
    Returns:
        float: Pause rate in seconds of pause per second of speech.
    """
    duration = words[-1]['end'] - words[0]['start']
    pauses = []
    for i in range(len(words)-1):
        gap = words[i+1]['start'] - words[i]['end']
        if gap > 1.0:  
            pauses.append(gap)
    return sum(pauses) / duration if pauses else 0

def count_fillers(words,    fillers = ["um", "uh", "like", "you know", "ah", "ahh", "oh", "hmm", "er", "mm", "mmm", "uhm", "huh", "eh", "uhhh", "so", "actually", "basically", "right", "well", "you see", "I mean", "kind of", "sort of"]):
    """
    Count total words and filler words in the transcript.\n
    aegs:        words (list): List of word dictionaries with 'word' key.
        fillers (list): List of filler words to count.
    Returns:
        tuple: (total_words, filler_count) 
    """
    total_words = len(words)
    filler_count = sum(1 for w in words if w["word"].lower() in fillers)
    return total_words, filler_count

# base faster but less accurate
model = whisper.load_model("medium.en")
input_video = "/content/Hossam_video.mp4"
cap = cv2.VideoCapture(input_video)
face_emotion(cap)