import os
import sys
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

def convert_file(input_file, output_file):
    """Convert a single audio file to Opus format."""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:a', 'libopus',
        '-b:a', '128k',  # Adjust the bitrate as needed
        output_file
    ]
    print(f'Converting: {input_file} to {output_file}')
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f'Error converting {input_file}: {e}')

def collect_audio_files(input_dir, output_dir):
    """Collect all audio files and their corresponding output paths, skipping existing output files."""
    audio_extensions = ('.flac', '.mp3', '.wav', '.aac', '.m4a', '.ogg', '.wma', '.alac', '.aiff', '.ape')
    audio_files = []
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(audio_extensions):
                input_file = os.path.join(root, filename)
                # Determine relative path to maintain folder structure
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                os.makedirs(output_subdir, exist_ok=True)
                opus_filename = os.path.splitext(filename)[0] + '.opus'
                output_file = os.path.join(output_subdir, opus_filename)
                if not os.path.exists(output_file):
                    audio_files.append((input_file, output_file))
                else:
                    print(f'Skipping existing file: {output_file}')
    return audio_files

def convert_audio_to_opus_multiprocess(input_dir, output_dir, max_workers=None):
    """Convert audio files to Opus format using multiprocessing."""
    audio_files = collect_audio_files(input_dir, output_dir)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_file, input_file, output_file): (input_file, output_file)
            for input_file, output_file in audio_files
        }
        for future in as_completed(future_to_file):
            input_file, _ = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                print(f'Error converting {input_file}: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python audio_to_opus.py input_directory output_directory')
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f'The input directory {input_dir} does not exist.')
        sys.exit(1)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    convert_audio_to_opus_multiprocess(input_dir, output_dir)
