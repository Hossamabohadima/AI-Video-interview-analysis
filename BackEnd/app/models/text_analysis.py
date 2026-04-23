from .IAnalysisModel import IAnalysisModel, AnalysisInput
from nltk.corpus import stopwords
from collections import Counter
import nltk
import re

class TextAnalysis(IAnalysisModel):
    """
    Implements the IAnalysisModel interface to analyze text-related metrics from Whisper results.

    This class computes various speech metrics such as clarity, fluency, confidence, and engagement
    based on the provided Whisper transcription results.
    """

    def __init__(self):
        """
        Initialize the TextAnalysis model.
        """
        super().__init__("TextAnalysis")
        self.model = None

    def _extract_words_and_text(self, whisper_result):
        """
        Extracts the full text and a list of word dictionaries from Whisper results.

        Args:
            whisper_result (dict): The result dictionary from Whisper transcription.

        Returns:
            tuple: (words_only, full_text) where words_only is a list of word dicts and full_text is the stripped text.
        """
        # 1. Get the full string of text
        full_text = whisper_result["text"].strip()
        
        # 2. Extract the list of word dictionaries
        words_only = []
        for seg in whisper_result["segments"]:
            for w in seg["words"]:
                words_only.append(w)         
        return words_only, full_text

    def _speech_rate(self, words):
        """Calculate speech rate in words per minute (WPM).
        
        Args:
            words (list): List of word dictionaries with 'start' and 'end' timestamps.
        
        Returns:
            float: Speech rate in words per minute.
        """
        duration = words[-1]['end'] - words[0]['start']
        total_words = len(words)
        return float(total_words / (duration / 60))

    def _pause_rate(self, words):
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

    def _count_fillers(self, words, fillers=["um", "uh", "like", "you know", "ah", "ahh", "oh", "hmm", "er", "mm", "mmm", "uhm", "huh", "eh", "uhhh", "so", "actually", "basically", "right", "well", "you see", "I mean", "kind of", "sort of"]):
        """
        Count total words and filler words in the transcript.

        Args:
            words (list): List of word dictionaries with 'word' key.
            fillers (list): List of filler words to count.

        Returns:
            tuple: (total_words, filler_count)
        """
        total_words = len(words)
        filler_count = sum(1 for w in words if w["word"].lower() in fillers)
        return total_words, filler_count

    def _get_word_repetition(self, full_text):
        """
        Calculates the frequency of each word in a text string, excluding stop words and punctuation.

        Args:
            full_text (str): The full text transcript.

        Returns:
            dict: A dictionary with words as keys and their frequencies as values, sorted by frequency.
        """
        if not full_text:
            return {}

        # lowercase all
        words = nltk.word_tokenize(full_text.lower())

        # keep words only (removes numbers and punctuation)
        words = [w for w in words if re.match(r'[a-z]+$', w)]

        # remove stop words
        stop_words = set(stopwords.words('english'))
        filtered_words = [w for w in words if w not in stop_words]

        repetition_counts = Counter(filtered_words)

        # return sorted dict
        return dict(repetition_counts.most_common())

    def _grammar_mistakes(self, full_text):
        """
        Calculate the number of grammar mistakes in the full text.

        Args:
            full_text (str): The full text transcript.

        Returns:
            int: Number of grammar mistakes (currently not implemented).
        """
        # not implemented yet.
        return 0

    def analyze(self, input_data: AnalysisInput) -> dict:
        """
        Analyze the Whisper result to compute text-related metrics.

        Args:
            input_data (AnalysisInput): Input model containing whisper_result.

        Returns:
            dict: A dictionary containing computed metrics like speech_rate, pause_rate, etc.
        """
        if not input_data.whisper_result:
            raise ValueError("TextAnalysis requires input_data.whisper_result")

        whisper_result = input_data.whisper_result
        words, full_text = self._extract_words_and_text(whisper_result)
        speech_rate_val = self._speech_rate(words)
        pause_rate_val = self._pause_rate(words)
        total_words, filler_count = self._count_fillers(words)
        repetition = self._get_word_repetition(full_text)
        grammar_errors = self._grammar_mistakes(full_text)
 
        return {
            "speech_rate": speech_rate_val,
            "pause_rate": pause_rate_val,
            "total_words": total_words,
            "filler_count": filler_count,
            "word_repetition": repetition,
            "grammar_errors": grammar_errors
        }