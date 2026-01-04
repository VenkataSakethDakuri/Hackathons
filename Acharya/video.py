import subprocess
import imageio_ffmpeg as ffmpeg

def speed_up_video(input_file, output_file, speed_factor):
    # 1. Get the path to the FFmpeg executable automatically
    ffmpeg_exe = ffmpeg.get_ffmpeg_exe()

    # 2. Calculate the video timestamp scale (Inverse of speed)
    # If speed is 1.15, PTS must be 1/1.15 (0.869)
    video_scale = 1 / speed_factor
    
    # 3. Build the command
    # [0:v]setpts=PTS/1.15[v] -> Speeds up visual
    # [0:a]atempo=1.15[a]     -> Speeds up audio BUT keeps pitch same
    cmd = [
        ffmpeg_exe,
        "-i", input_file,
        "-filter_complex", 
        f"[0:v]setpts={video_scale}*PTS[v];[0:a]atempo={speed_factor}[a]",
        "-map", "[v]",
        "-map", "[a]",
        output_file,
        "-y" # Overwrite if exists
    ]

    print(f"Processing video at {speed_factor}x speed...")
    subprocess.run(cmd)
    print("Done!")


if __name__ == "__main__":
    speed_up_video("Final_Version.mp4", "output_fast.mp4", 1.15)