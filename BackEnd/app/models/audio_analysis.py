from .IAnalysisModel import IAnalysisModel, AnalysisInput
from pyAudioAnalysis import audioBasicIO, ShortTermFeatures
import numpy as np

class AudioAnalysis(IAnalysisModel):
    def __init__(self):
        """Initialize the AudioAnalysis model.

        Args:
            vad_model: The VAD model for speech detection.
            get_speech_timestamps: Function to get speech timestamps.
        """
        super().__init__("AudioAnalysis")


    def _calculate_speech_energy(self, audio_path: str) -> dict:
        """Calculate speech energy statistics from an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            dict: Dictionary containing average_energy, max_energy, min_energy, std_energy.
        """
        sample_rate, audio_signal = audioBasicIO.read_audio_file(audio_path)
        audio_signal = audioBasicIO.stereo_to_mono(audio_signal)
        
        win = int(0.050 * sample_rate)
        step = int(0.025 * sample_rate)

        F, f_names = ShortTermFeatures.feature_extraction(audio_signal, sample_rate, win, step)

        try:
            energy_idx = f_names.index('energy')
        except ValueError:
            energy_idx = 1

        energy_frames = F[energy_idx, :].astype(float)

        return {
            "average_energy": float(np.mean(energy_frames)),
            "max_energy": float(np.max(energy_frames)),
            "min_energy": float(np.min(energy_frames)),
            "std_energy": float(np.std(energy_frames))
        }

    def analyze(self, input_data: AnalysisInput) -> dict:
        """Analyze audio data for energy and continuity.

        Args:
            input_data (AnalysisInput): Input data containing audio_path.

        Returns:
            dict: Dictionary with energy_stats and continuity_score.
        """
        if not input_data.audio_path:
            raise ValueError("AudioAnalysis requires input_data.audio_path")

        energy_stats = self._calculate_speech_energy(input_data.audio_path)

        return {
            "energy_stats": energy_stats,
        }