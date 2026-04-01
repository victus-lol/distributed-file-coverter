import os
import subprocess


def convert(input_path, target_format):
    """
    Convert video files using ffmpeg.
    Supports: mp4→gif, mp4→avi, avi→mp4, mp4→webm, etc.
    Requires ffmpeg installed: sudo apt install ffmpeg
    """
    target_format = target_format.lower().strip('.')
    base = os.path.splitext(input_path)[0]
    output_path = f"{base}_converted.{target_format}"

    if target_format == 'gif':
        # Better quality GIF using palette
        palette_path = f"{base}_palette.png"
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "fps=10,scale=320:-1:flags=lanczos,palettegen",
            palette_path
        ], check=True, capture_output=True)
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-i", palette_path,
            "-filter_complex", "fps=10,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse",
            output_path
        ], check=True, capture_output=True)
        os.remove(palette_path)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, output_path
        ], check=True, capture_output=True)

    print(f"[VIDEO CONVERTER] {input_path} → {output_path}")
    return output_path


def can_handle(input_path, target_format):
    video_inputs = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
    video_outputs = {'mp4', 'avi', 'gif', 'webm', 'mov', 'mkv'}
    ext = os.path.splitext(input_path)[1].lower().strip('.')
    return ext in video_inputs and target_format.lower() in video_outputs