from .IAnalysisModel import IAnalysisModel, AnalysisInput
from pyAudioAnalysis import audioBasicIO, ShortTermFeatures
import numpy as np

# helper functions for audio analysis
def calculate_speech_energy(audio_path):
    """
    Calculates energy statistics for a given audio file.

    Args:
        audio_path (str): Path to the audio file to analyze.

    Returns:
        dict: Average, Max, Min, and Std of the speech energy.
    """

    # sample_rate is the sampling rate (how many discrete numbers he capture each second) -Hz-
    # x is the actual array data for wave, numpay array (should be Hz * num of seconds)
    # audioBasicIO auto detect a good number for sampling rate (Fs) from the video
    sample_rate, audio_signal = audioBasicIO.read_audio_file(audio_path)

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

def speech_continuity(audio_path):
    """
    Estimate speech continuity quality for an audio file.

    Args:
        audio_path (str): Path to the audio file to analyze.

    Returns:
        int: Placeholder continuity score (currently not implemented).
    """
    # not implemented yet.
    return 0

# main class for audio analysis
class AudioAnalysis(IAnalysisModel):
    """
    Implements the IAnalysisModel interface to extract audio-based interview metrics.

    This class currently computes energy statistics and a placeholder continuity score.
    """
    def __init__(self):
        """
        Initialize the audio analysis model.
        """
        super().__init__("AudioAnalysis")
        self.model = None

    def analyze(self, input_data: AnalysisInput) -> dict:
        """
        Analyze an audio file for speech energy and continuity metrics.

        Args:
            input_data (AnalysisInput): Input model containing audio_path.

        Returns:
            dict: A dictionary containing computed audio metrics (energy statistics and continuity score).
        """
        if not input_data.audio_path:
            raise ValueError("AudioAnalysis requires input_data.audio_path")

        energy_stats = calculate_speech_energy(input_data.audio_path)
        continuity_score = speech_continuity(input_data.audio_path)

        return {
            "energy_stats": energy_stats,
            "continuity_score": continuity_score
        }