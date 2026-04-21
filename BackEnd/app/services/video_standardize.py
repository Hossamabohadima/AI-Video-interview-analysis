import subprocess
import os


def run_ffmpeg_command(command):
    """Helper to run ffmpeg command"""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(result)
    #result is a obj, which has returncode, stdout, and stderr
    if result.returncode != 0:
        raise Exception(f"FFmpeg Error: {result.stderr.decode()}")
    return True


"""
-y  --> to overwrite output file if it already exists
-i input_path  --> specify the input video file path
-vf "scale=-2:480"  --> set the video filter to scale the video to a height of 480 pixels while maintaining the aspect ratio(16:9 or 4:3)
-r 30  --> set the frame rate to 30 frames per second
-c:v libx264  --> use the H.264 video codec for encoding
-crf 23  --> (Constant Rate Factor) controls the quality and size of the output video (higher = smaller)
-preset medium  --> use a medium encoding preset for a balance between speed and compression (smaller file size)
-c:a aac  --> use the AAC audio codec for encoding
-b:a 128k  --> set the audio bitrate to 128 kbps for compression
rgb24  --> specify the pixel format to RGB24, 8 bits per channel, 3 channels (R, G, B)
ac 1  --> set the audio channel layout to mono (1 channel)
-ar 44100  --> set the audio sample rate to 44.1 kHz

"""

def _set_resolution(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "scale=-2:480",
        output_path
    ]
    run_ffmpeg_command(command)


def _set_framerate(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-r", "30",
        output_path
    ]
    run_ffmpeg_command(command)


def _convert_to_mp4(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-crf", "23",        
        "-preset", "medium",   
        "-c:a", "aac",
        "-b:a", "128k",       
        output_path
    ]
    run_ffmpeg_command(command)


def _convert_to_rgb(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "format=rgb24",
        output_path
    ]
    run_ffmpeg_command(command)


def _convert_audio_to_mono(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        output_path
    ]
    run_ffmpeg_command(command)


def _set_audio_samplerate(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "44100",
        output_path
    ]
    run_ffmpeg_command(command)


def standardize_video(input_file, output_file="final_output.mp4"):
    temp1 = "temp1.mp4"
    temp2 = "temp2.mp4"
    temp3 = "temp3.mp4"
    temp4 = "temp4.mp4"
    temp5 = "temp5.mp4"

    _set_resolution(input_file, temp1)
    _set_framerate(temp1, temp2)
    _convert_to_rgb(temp2, temp3)
    _convert_audio_to_mono(temp3, temp4)
    _set_audio_samplerate(temp4, temp5)
    _convert_to_mp4(temp5, output_file)

    for f in [temp1, temp2, temp3, temp4, temp5]:
        if os.path.exists(f):
            os.remove(f)

    # print("Done")
    return output_file
