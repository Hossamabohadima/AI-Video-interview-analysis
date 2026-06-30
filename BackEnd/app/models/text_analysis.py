from pydoc import text
from .IAnalysisModel import IAnalysisModel, AnalysisInput
import language_tool_python

class TextAnalysis(IAnalysisModel):
    """
    Implements the IAnalysisModel interface to analyze text-related metrics from Whisper results.

    This class computes various speech metrics such as clarity, fluency, confidence, and engagement
    based on the provided Whisper transcription results.
    """

    def __init__(self, grammar_tool=None):
        """
        Initialize the TextAnalysis model.
        
        Args:
            grammar_tool (optional): Injected LanguageTool instance. If None, initializes a new one.
        """
        super().__init__("TextAnalysis")
        self.model = None
        if grammar_tool is not None:
            self.grammar_tool = grammar_tool
        else:
            try:
                self.grammar_tool = language_tool_python.LanguageTool('en-US')
            except Exception as e:
                print(f"Warning: Failed to initialize grammar tool: {e}")
                self.grammar_tool = None

    def _extract_words_and_text(self,whisper_result):
        """
        Extracts the full text and a list of word dictionaries from Hugging Face Whisper results.
    
        Args:
            whisper_result (dict): The result dictionary from HF pipeline transcription.
    
        Returns:
            tuple: (words_only, full_text) where words_only is a list of chunks and full_text is the stripped text.
        """
        # Get the full string of text safely
        full_text = whisper_result.get("text", "").strip()
        
        # Extract the list of word/chunk dictionaries
        words_only = whisper_result.get("chunks", [])
             
        return words_only, full_text


    def _grammar_mistakes(self,full_text):
        """
        Calculate grammar mistakes in the full text.
    
        Args:
            full_text (str): The full text transcript.
    
        Returns:
            tuple: (mistakes_list, grammar_score, num_errors, word_count)
        """
        if not full_text:
            return [], 100.0, 0, 0
        
        if self.grammar_tool is None:
            return [], 100.0, 0, len(full_text.split())
        
        matches = self.grammar_tool.check(full_text)
        mistakes = []
        
        for match in matches:
            # Include GRAMMAR, TYPOS, and MISC to capture spoken anomalies accurately
            target_categories = {'GRAMMAR', 'TYPOS', 'MISC', 'CONFUSED_WORDS'}
            if match.category in target_categories:
                mistakes.append({
                    "category": match.category,
                    "error_message": match.message,
                    "incorrect_text": match.context,
                    "suggestions": match.replacements[:3]  # Top 3 suggestions
                })
                
        num_errors = len(mistakes)
        word_count = max(len(full_text.split()), 1)
    
        # Scoring out of 100 for evaluation consistency 
        grammar_score = max(0.0, 100.0 - (num_errors / word_count * 100))
        
        return mistakes, grammar_score, num_errors, word_count
    def _pause_quality_score(self, words, min_threshold=0.25, ideal_min=0.4, ideal_max=0.8):
        """
        Calculate the percentage of pauses that fall within the ideal natural range (around 0.6s).
        // ratio according to https://pmc.ncbi.nlm.nih.gov/articles/PMC8874014/
        
        Args:
            words (list): List of word dictionaries with 'start' and 'end' timestamps.
            min_threshold (float): Minimum gap to be considered a pause (ignores phonetic stops).
            ideal_min (float): Lower bound of a natural-sounding pause.
            ideal_max (float): Upper bound of a natural-sounding pause.
        
        Returns:
            float: Percentage of pauses that are considered "ideal" (0 to 100).
        """
        if not words or len(words) < 2:
            return 0.0
            
        real_pauses = []
        ideal_pauses = []
        
        for i in range(len(words)-1):
            gap = words[i+1]['start'] - words[i]['end']
            
            # 2. Use the DETECTOR (0.25s) to filter out mechanical mouth movements
            if gap > min_threshold:  
                real_pauses.append(gap)
                
                # 3. Use the GRADER zone (0.4s to 0.8s, centered on 0.6s) to evaluate quality
                if ideal_min <= gap <= ideal_max:
                    ideal_pauses.append(gap)
                    
        # If they never paused, they get a 0 score for natural pacing
        if not real_pauses:
            return 0.0
            
        # 4. Calculate the score: what percentage of their pauses were "perfect"?
        quality_score = (len(ideal_pauses) / len(real_pauses)) * 100
        
        return round(quality_score, 2)

 

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

    def analyze(self, input_data: AnalysisInput) -> dict:
        """
        Analyze the Whisper result to compute text-related metrics.

        Args:
            input_data (AnalysisInput): Input model containing whisper_result.

        Returns:
            dict: A dictionary containing computed metrics like  pause_rate, etc.
        """
        if not input_data.whisper_result:
            raise ValueError("TextAnalysis requires input_data.whisper_result")

        whisper_result = input_data.whisper_result
        words, full_text = self._extract_words_and_text(whisper_result)
        pause_rate_val = self._pause_quality_score(words)
        total_words, filler_count = self._count_fillers(words)
        grammar_mistakes, grammar_score, num_errors, word_count = self._grammar_mistakes(full_text)
 
        return {
            "pause_rate": pause_rate_val,
            "total_words": total_words,
            "filler_count": filler_count,
            "grammar_errors_count": len(grammar_mistakes),
            "grammar_errors_details": grammar_mistakes,
            "grammar_score": grammar_score
        }
