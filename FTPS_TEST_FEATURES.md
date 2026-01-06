# FTPS Testing Features

This document describes the three new button entities added to test and verify FTPS connectivity with Bambu Lab printers.

## Overview

These buttons are designed to help users verify that FTPS (FTP over SSL/TLS) is working correctly, which is essential for spaghetti detection and other advanced features.

## New Button Entities

### 1. Test FTPS

**Entity ID**: `button.<printer_name>_test_ftps`

**Description**: Tests the FTPS connection to the printer and lists the root directory.

**What it does**:
- Establishes an FTPS connection to the printer
- Lists all files and directories in the root directory
- Displays the results in a Home Assistant notification

**Use case**: Quick verification that FTPS connectivity is working properly.

### 2. Get Last Image

**Entity ID**: `button.<printer_name>_get_last_image`

**Description**: Finds and displays the most recent image file (JPG, JPEG, or PNG) from the printer.

**What it does**:
- Scans the printer's directories (`/timelapse`, `/cache`, `/`) for image files
- Identifies the most recently modified image based on timestamp
- Downloads the image and displays it in a Home Assistant notification
- Shows the image path and timestamp

**Use case**: Verify that image files are accessible via FTPS for spaghetti detection.

### 3. Get Last Frame

**Entity ID**: `button.<printer_name>_get_last_frame`

**Description**: Finds the latest video file and extracts its last frame.

**What it does**:
- Scans the printer's directories for video files (AVI, MPG, MPEG, MP4)
- Identifies the most recently modified video
- Downloads the video and uses FFmpeg to extract the last frame
- Displays the extracted frame in a Home Assistant notification
- Shows the video path and timestamp

**Use case**: Verify that video files are accessible and that frame extraction works, which is crucial for spaghetti detection during layer changes.

## Technical Details

### Dependencies

- **FFmpeg**: Required for video frame extraction (Get Last Frame button)
  - Already listed as a dependency in the integration's `manifest.json`
  - Home Assistant typically includes FFmpeg by default

### Implementation

The buttons use the following approach:

1. **Async Operations**: All FTP operations are run in an executor to avoid blocking the Home Assistant event loop
2. **Error Handling**: Comprehensive error handling with user-friendly error messages
3. **Notifications**: Results are displayed using Home Assistant's `persistent_notification` service
4. **Image Display**: Images are encoded as base64 and embedded directly in notifications using data URIs

### File Search Paths

The buttons search in the following directories on the printer:
- `/timelapse` - Contains timelapse videos and related files
- `/cache` - Contains cached files including some prints and images
- `/` - Root directory as a fallback

### Supported File Types

**Images**: `.jpg`, `.jpeg`, `.png`
**Videos**: `.avi`, `.mpg`, `.mpeg`, `.mp4`

## Future Integration with Spaghetti Detection

These functions provide the foundation for implementing spaghetti detection:

1. **FTPS Verification**: Ensures the connection is working
2. **Image Access**: Confirms that layer images can be retrieved
3. **Frame Extraction**: Demonstrates the ability to extract frames from video at specific points

For full spaghetti detection, the integration will need to:
- Capture frames at layer changes
- Compare frames using image analysis
- Detect anomalies that indicate print failures
- Trigger alerts when spaghetti is detected

## Usage

To use these buttons:

1. Navigate to your Bambu Lab printer device in Home Assistant
2. Find the three new buttons under the diagnostic category
3. Press any button to test the corresponding functionality
4. Check your Home Assistant notifications for the results

## Troubleshooting

If any button fails:

1. **Check FTPS Configuration**: Ensure your printer's IP address and access code are correct
2. **Network Connectivity**: Verify that Home Assistant can reach the printer on port 990 (FTPS)
3. **Printer Permissions**: Ensure the access code has proper permissions
4. **FFmpeg Availability**: For "Get Last Frame", ensure FFmpeg is available in your Home Assistant installation
5. **Check Logs**: Look for error messages in the Home Assistant logs under the `custom_components.bambu_lab` logger

## Notes

- These buttons are classified as "diagnostic" entities and may be hidden by default in some UIs
- Large videos may take some time to download and process
- The notifications include embedded images, so they may be large
- File timestamps use the printer's clock, which may not always be accurate
