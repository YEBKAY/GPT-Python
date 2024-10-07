import os
import sys
import subprocess

def convert_flac_to_opus(input_dir, output_dir):
    """Recursively convert FLAC files from input_dir to Opus in output_dir, preserving directory structure."""
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.flac'):
                flac_file = os.path.join(root, filename)
                # Determine relative path to maintain folder structure
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                os.makedirs(output_subdir, exist_ok=True)
                opus_filename = os.path.splitext(filename)[0] + '.opus'
                opus_file = os.path.join(output_subdir, opus_filename)
                cmd = [
                    'ffmpeg',
                    '-i', flac_file,
                    '-c:a', 'libopus',
                    '-b:a', '128k',  # Adjust the bitrate as needed
                    opus_file
                ]
                print(f'Converting: {flac_file} to {opus_file}')
                try:
                    subprocess.run(cmd, check=True)
                except subprocess.CalledProcessError as e:
                    print(f'Error converting {flac_file}: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python flac_to_opus.py input_directory output_directory')
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f'The input directory {input_dir} does not exist.')
        sys.exit(1)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    convert_flac_to_opus(input_dir, output_dir)
