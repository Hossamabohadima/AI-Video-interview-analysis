import ffmpeg

def compress_video(input_path, output_path, target_bitrate="2M"):
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, video_bitrate=target_bitrate)
            .run(overwrite_output=True)
        )
        print(f"Success! Compressed video saved to: {output_path}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")

# Example usage
compress_video(r"D:\Hossam\study\Graduation project\AI-Video-interview-analysis-\DataSet\Hossam_video.mp4",
                r"D:\Hossam\study\Graduation project\AI-Video-interview-analysis-\DataSet\Hossam_video_compressed.mp4", target_bitrate="1.5M")