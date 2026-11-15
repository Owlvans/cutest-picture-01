"""
cutest-picture-01 v4 entry: Bubble Trouble.
A baby fennec fox with huge ears blowing an oversized pink bubblegum bubble,
eyes squeezed shut, bubble about to pop.
"""

import hashlib
import os
import sys

def parse_jpeg_dimensions(data):
    if not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
        raise ValueError("Invalid JPEG SOI/EOI markers")
    i = 2
    while i < len(data) - 1:
        while i < len(data) and data[i] == 0xff:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xd8, 0xd9, 0x01) or (0xd0 <= marker <= 0xd7):
            continue
        if i + 2 > len(data):
            raise ValueError("Unexpected end of JPEG data")
        length = int.from_bytes(data[i:i+2], 'big')
        if length < 2 or i + length > len(data):
            raise ValueError("Invalid JPEG segment length")
        if 0xc0 <= marker <= 0xcf and marker not in (0xc4, 0xc8, 0xcc):
            if length < 7 or i + 7 > len(data):
                raise ValueError("SOF segment too short")
            height = int.from_bytes(data[i+3:i+5], 'big')
            width = int.from_bytes(data[i+5:i+7], 'big')
            return width, height
        i += length
    raise ValueError("No Start-Of-Frame (SOF) marker found in JPEG")

def parse_png_dimensions(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError("Invalid PNG signature")
    if len(data) < 24:
        raise ValueError("PNG file too short for IHDR")
    length = int.from_bytes(data[8:12], 'big')
    if length != 13 or data[12:16] != b'IHDR':
        raise ValueError("First PNG chunk is not IHDR")
    width = int.from_bytes(data[16:20], 'big')
    height = int.from_bytes(data[20:24], 'big')
    return width, height

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pic_path = os.path.join(script_dir, 'picture.jpg')

    if not os.path.exists(pic_path):
        print(f"Error: picture.jpg does not exist at {pic_path}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(pic_path)
    if file_size > 1048576:
        print(f"Error: picture.jpg size ({file_size} bytes) exceeds maximum allowed (1048576 bytes)", file=sys.stderr)
        sys.exit(1)

    try:
        with open(pic_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading picture.jpg: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        width, height = parse_jpeg_dimensions(data)
    except Exception:
        try:
            width, height = parse_png_dimensions(data)
        except Exception as e:
            print(f"Error: picture.jpg is not a valid JPEG or PNG image: {e}", file=sys.stderr)
            sys.exit(1)

    if width <= 0 or height <= 0 or width > 1024 or height > 1024:
        print(f"Error: Invalid dimensions {width}x{height} (must be between 1 and 1024)", file=sys.stderr)
        sys.exit(1)

    digest = hashlib.sha256(data).hexdigest()

    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory {out_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = os.path.join(out_dir, 'entry.png')
    try:
        with open(out_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        print(f"Error writing output file {out_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Bubble Trouble {width}x{height} {file_size} {digest}")

if __name__ == '__main__':
    main()
