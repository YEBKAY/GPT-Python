#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os

def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("ffmpeg is not installed or not in PATH.")
        sys.exit(1)

def convert_to_opus(input_file, output_file):
    """Convert the input media file to an OPUS file."""
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:a', 'libopus',
        '-b:a', '128k',  # Set audio bitrate (adjust as needed)
        '-vn',           # Disable video recording
        output_file
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Converted {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting {input_file}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert any media file to OPUS using ffmpeg")
    parser.add_argument('input', help='Input media file')
    parser.add_argument('output', nargs='?', help='Output OPUS file')
    args = parser.parse_args()

    input_file = args.input
    if not os.path.isfile(input_file):
        print(f"Input file '{input_file}' does not exist.")
        sys.exit(1)

    if args.output:
        output_file = args.output
    else:
        base, _ = os.path.splitext(input_file)
        output_file = base + '.opus'

    check_ffmpeg()
    convert_to_opus(input_file, output_file)

if __name__ == "__main__":
    main()
