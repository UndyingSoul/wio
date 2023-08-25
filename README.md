# Wio - Web Image Optimizer

Wio (Web Image Optimizer) is a Python script designed to optimize images for the web by reducing their size or dimensions. It supports various image formats and offers configuration options through a settings file. This README guide will help you understand how to set up and use Wio effectively.

## Features

- Converts images to different formats (webp, avif, or original)
- Adjusts the quality of the images
- Preserves or removes metadata from images
- Can keep or delete original files after conversion
- Supports batch processing of images

## Table of Contents

- [Wio - Web Image Optimizer](#wio---web-image-optimizer)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Options](#options)
    - [Examples](#examples)
  - [Notes](#notes)

## Installation

1. Clone this repository or download the Python script.

2. Install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before using Wio, you can customize its behavior using the `config/settings.json` file. This file allows you to control the logging levels and modes. Make sure to adjust the settings according to your preferences.

- `logToFile`: Set to `true` to enable logging to the file named `latest.log`.

- `loggingLevel`: Choose from DEBUG, INFO, WARNING, ERROR, or CRITICAL. This sets the logging level for console output. File logging is always in DEBUG mode.

## Usage

To use Wio, open a terminal and navigate to the directory containing the script. You can run the script with various command-line arguments to control the conversion process.

```bash
python wio.py [options] input_paths
```

### Options

- `--version`, `-v`: Display the script's version.

- `--extensions`, `-e`: Specify the image file extensions to convert. Default: jpg, jpeg, png, gif.

- `--format`, `-f`: Choose the format to convert images to: webp, avif, or original. Default: avif.

- `--quality`, `-q`: Set the quality of the conversion (0-100). Default: 70.

- `--keep-originals`, `-o`: Keep the original files after conversion.

- `--keep-metadata`, `-m`: Keep metadata on the converted images.

- `--dry-run`, `-d`: Perform a dry run without actually converting images.

### Examples

1. Convert all jpg and png images in a directory to avif format with 80% quality, keeping originals:

   ```bash
   python wio.py -e jpg png -f avif -q 80 -o /path/to/images
   ```

2. Convert a single image to webp format with 90% quality and keep metadata:

   ```bash
   python wio.py -f webp -q 90 -m image.jpg
   ```

3. Convert all images in a directory to their original formats, keeping metadata and original files:

   ```bash
   python wio.py -f original -m -o /path/to/images
   ```

4. Perform a dry run on a directory to see what conversions would take place:

   ```bash
   python wio.py -d /path/to/images
   ```

## Notes

- You can customize the supported image formats and their corresponding plugins by modifying the `SUPPORTED_FORMATS` dictionary in the script.

- The script uses asynchronous programming for faster processing. This might require Python 3.7 or higher.

- Make sure the necessary packages are installed from the `requirements.txt` file.

- Before using Wio on a large number of images, consider making backups to avoid accidental data loss.

- Wio is provided as-is and may be subject to changes or updates. Always check for the latest version and release notes.

---

Feel free to contribute to this open-source project or report issues on the [GitHub repository](https://github.com/UndyingSoul/wio). Your feedback and contributions are greatly appreciated!