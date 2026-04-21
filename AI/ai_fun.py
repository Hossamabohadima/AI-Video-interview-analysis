from pyAudioAnalysis import audioBasicIO, ShortTermFeatures
from nltk.corpus import stopwords
from collections import Counter
from deepface import DeepFace
import numpy as np
import subprocess
import nltk, re
import whisper
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

def extract_words_and_text(audio_path):
    """
    Transcribes audio to get both word-level timestamps 
    and the full formatted text.
    """
    # word_timestamps=True is necessary for word-level data
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # 1. Get the full string of text
    example_text = result["text"].strip()
    
    # 2. Extract the list of word dictionaries (your original logic)
    words = []
    for seg in result["segments"]:
        for w in seg["words"]:
            words.append(w)         
    return words, example_text

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

def calculate_speech_energy(audio_output_path):
    """
    Calculates energy statistics for a given audio file.

    Args:
        audio_output_path (str): Path to the audio file to analyze.

    Returns:
        dict: Average, Max, Min, and Std of the speech energy.
    """
    # sample_rate is the sampling rate (how many discrete numbers he capture each second) -Hz-
    # x is the actual array data for wave, numpay array (should be Hz * num of seconds)
    # audioBasicIO auto detect a good number for sampling rate (Fs) from the video
    
    sample_rate, audio_signal = audioBasicIO.read_audio_file(audio_output_path)

    # pyAudioAnalysis library expect mono voice
    audio_signal = audioBasicIO.stereo_to_mono(audio_signal)
    # 50ms window, 25ms step
    # overlap to catch all features in voice

    win = int(0.050 * sample_rate)
    step = int(0.025 * sample_rate)


    # the work on the audio:
    # f_names is the names of features ['energy', 'entropy',..... etc]
    # F is 2D matrix for numeric values for each window for the features
    F, f_names = ShortTermFeatures.feature_extraction(audio_signal, sample_rate, win, step)


    # we need energy only for this task
    # extract the energy column only
    try:
        energy_idx = f_names.index('energy')
    except ValueError:
        energy_idx = 1

    # energy values
    energy_frames = F[energy_idx, :].astype(float)

    # final calculations
    stats = {
        "average_energy": float(np.mean(energy_frames)),
        "max_energy": float(np.max(energy_frames)),
        "min_energy": float(np.min(energy_frames)),
        "std_energy": float(np.std(energy_frames))
    }

    return stats

def get_word_repetition(text):
    """
    Calculates the frequency of each word in a text string,
    excluding stop words and punctuation.
    """
    if not text:
        return {}

    # lowercase all
    words = nltk.word_tokenize(text.lower())

    # keep words only (removes numbers and punctuation)
    words = [w for w in words if re.match(r'[a-z]+$', w)]

    # remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [w for w in words if w not in stop_words]

    repetition_counts = Counter(filtered_words)

    # return sorted dict
    return dict(repetition_counts.most_common())

# download necessary nltk data and load whisper model
model = whisper.load_model("medium.en")# base faster but less accurate
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

input_video = "/content/Hossam_video.mp4"
audio_output_path = "extracted_audio.wav"

# extract audio to extracted_audio.wav
subprocess.run(["ffmpeg", "-y", "-i", input_video, "-q:a", "0", "-map", "a", audio_output_path])

energy_results = calculate_speech_energy(audio_output_path)

word_list, example_text = extract_words_and_text(audio_output_path)

cap = cv2.VideoCapture(input_video)
face_emotion(cap)
repetition_data = get_word_repetition(example_text)

