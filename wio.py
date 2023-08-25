import time
import os
import argparse
import asyncio
from PIL import Image
from PIL import ImageOps
from colorama import Fore, Back

# Supported formats
from PIL import JpegImagePlugin
from PIL import PngImagePlugin
from PIL import GifImagePlugin
from PIL import WebPImagePlugin
from PIL import BmpImagePlugin
from PIL import BlpImagePlugin
from PIL import TiffImagePlugin
from pillow_avif import AvifImagePlugin

# Setup Logging
import utils.Logger
import logging
utils.Logger.setup_logging()
log = logging.getLogger(__name__)

#Constants
#version number
VERSION = "1.0"

#welcome message
WELCOME_MESSAGE = f"""__        _____ ___  
\ \      / /_ _/ _ \ 
 \ \ /\ / / | | | | |
  \ V  V /  | | |_| |
   \_/\_/  |___\___/ 
Web Image Optimizer
Made with ❤️ by UndyingSoul
GitHub: https://github.com/UndyingSoul/wio
    """

# Supported image formats and their corresponding Pillow plugins
SUPPORTED_FORMATS = {
    "jpg": JpegImagePlugin.JpegImageFile,
    "jpeg": JpegImagePlugin.JpegImageFile,
    "png": PngImagePlugin.PngImageFile,
    "gif": GifImagePlugin.GifImageFile,
    "webp": WebPImagePlugin.WebPImageFile,
    "bmp": BmpImagePlugin.BmpImageFile,
    "blp": BlpImagePlugin.BlpImageFile,
    "tiff": TiffImagePlugin.TiffImageFile,
    "avif": AvifImagePlugin.AvifImageFile,
}

human_readable_bools = ('no','yes')

def range_arg_type(astr, min=0, max=100):
    value = int(astr)
    if min <= value <= max:
        return value
    else:
        raise argparse.ArgumentTypeError(f"value not in range {min}-{max}")

def size_of_file_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def generate_output_path(input_path, format, keep_originals, save_as_original_format):
    directory, filename = os.path.split(input_path)
    filename, ext = os.path.splitext(filename)
    
    if save_as_original_format:
        new_ext = ext if not keep_originals else "_wio" + ext
    else:
        new_ext = + ext

    output_path = os.path.join(directory, filename + new_ext)
    return output_path

# Function to convert an image to the specified format and quality
async def convert_image(input_path, output_path, format, quality, keep_metadata, keep_originals, save_as_original_format, resize=False):
    log.debug(f"Converting image {input_path}")
    try:
        with Image.open(input_path) as img:
            img = ImageOps.exif_transpose(img)  # Fix orientation if applicable
            
            if resize:
                width, height = img.size
                new_width = int(width * (quality / 100))
                new_height = int(height * (quality / 100))
                img = img.resize((new_width, new_height), Image.LANCZOS)

            exif_data = img.info.get('exif')  # Get exif data
            exif_kwargs = {'exif': exif_data} if exif_data and keep_metadata else {}

            if save_as_original_format:
                output_path = generate_output_path(input_path, format, keep_originals, save_as_original_format)

            if resize:
                img.save(output_path, format=format, quality=95, subsampling=0, **exif_kwargs)
            else:
                img.save(output_path, format=format, quality=quality, **exif_kwargs)
            return True
    except Exception as e:
        log.error(f"Could not convert {input_path}")
        log.debug(e)
        return False

# Function to process a single image file
async def process_file(file_path, format, quality, keep_originals, keep_metadata, index, total, resize=False):
    directory, filename = os.path.split(file_path)
    filename, ext = os.path.splitext(filename)
    save_as_original_format = False
    
    if format == "original":
        save_as_original_format = True
        format = ext[1:]
        if format == "jpg":
            format = "jpeg" # dumb, but necessary edge case
            
        
        output_path = generate_output_path(file_path, format, keep_originals, save_as_original_format)
        if not format:
            log.critical(f"Invalid extension for file {output_path}")
            return
    else:
        output_path = os.path.join(directory, filename + "." + format)
        
    file_path_size = os.stat(file_path).st_size
    if await convert_image(file_path, output_path, format, quality, keep_metadata, keep_originals, save_as_original_format, resize):
        output_path_size = os.stat(output_path).st_size
        space_saved_percent = int((1-(output_path_size/file_path_size))*100)
        space_saved = f"({space_saved_percent}% smaller)" if space_saved_percent > -1 else f"{Fore.BLACK}{Back.WHITE}({abs(space_saved_percent)}% larger){Fore.RESET}{Back.RESET}"
        if not keep_originals and not save_as_original_format:  # Optionally delete the original file
            log.info(f"Deleting file {file_path}")
            os.remove(file_path)
        log.info(f"{index+1}/{total} ({int(((index+1)/total)*100)}%) - Converted {file_path}[{size_of_file_fmt(file_path_size)}] to {output_path}[{size_of_file_fmt(output_path_size)}] {space_saved}")

# Main function that handles command line arguments and orchestrates the conversion process
def main():
    # Arguments
    parser = argparse.ArgumentParser(description="Web Image optimizer/converter")
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f"{parser.prog} v.{VERSION}",
    )
    parser.add_argument(
        "input_paths",
        nargs="+",
        help="Input file(s) or directory(s)",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        nargs="*",
        choices=SUPPORTED_FORMATS,
        default=["jpg", "jpeg", "png", "gif"],
        help="File extensions to convert",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["webp", "avif"],
        default="avif",
        help="Format to convert the images to",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=range_arg_type,
        metavar="[0-100]",
        default=70,
        help="Quality of the conversion (0-100)",
    )
    parser.add_argument(
        "--resize",
        "-r",
        action="store_true",
        help="Resize images instead of optimizing them",
    )
    parser.add_argument(
        "--keep-originals",
        "-o",
        action="store_true",
        help="Keep original files after conversion",
    )
    parser.add_argument(
        "--keep-metadata",
        "-m",
        action="store_true",
        help="Keep metadata on the converted images",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Do a dry run (no images converted)",
    )
    args = parser.parse_args()

    print(WELCOME_MESSAGE)

    # Register additional image format encoders and decoders
    if args.format == "webp":
        Image.register_encoder("webp", WebPImagePlugin.WebPImageFile)
        Image.register_decoder("webp", WebPImagePlugin.WebPImageFile)

    if args.format == "avif":
        Image.register_decoder("avif", AvifImagePlugin.AvifImageFile)

    # Create a list of image files to be converted
    file_list = []
    for path in args.input_paths:
        if os.path.isdir(path):
            log.debug(f"{path} is directory, finding files in directory")
            for root, _, files in os.walk(path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in args.extensions):
                        log.debug(f"File found {os.path.join(root, file)}")
                        file_list.append(os.path.join(root, file))
        elif os.path.isfile(path) and any(path.lower().endswith(ext) for ext in args.extensions):
            log.debug(f"{path} is file")
            file_list.append(path)
        else:
            log.error(f"Unsupported image or directory {path}")

    if not file_list:
        log.error("No valid files specified. Exiting.")
        raise SystemExit(0)
    
    log.info(f"Converting {len(file_list)} files to the following parameters\n" + 
             f" * Format: {args.format}\n" + 
             f" * Quality: {args.quality}%\n" +
             f" * Resize Images: {human_readable_bools[args.resize]}\n" +
             f" * Keeping Originals: {human_readable_bools[args.keep_originals]}\n" + 
             f" * Keeping Metadata: {human_readable_bools[args.keep_metadata]}")
    
    log.log(logging.HEADER, "File Conversion")

    start_time = time.time()
    
    for index, file_path in enumerate(file_list):
        if args.dry_run:
            log.info(f"Will convert {file_path}")
            continue
        asyncio.run(process_file(file_path, args.format, args.quality, args.keep_originals, args.keep_metadata, index, len(file_list), resize=args.resize))
    

    seconds = time.time() - start_time
    timer = f"Time Taken: {time.strftime('%H:%M:%S', time.gmtime(seconds))}" if start_time else ""
    log.log(logging.COMPLETION, f"Done. {timer}")

if __name__ == "__main__":
    main()
