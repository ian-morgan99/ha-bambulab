# FTPS Testing Features

This document describes the three new button entities and three new number entities added to test and verify FTPS connectivity with Bambu Lab printers.

## Overview

These buttons are designed to help users verify that FTPS (FTP over SSL/TLS) is working correctly, which is essential for spaghetti detection and other advanced features.

The new number entities allow users to configure which image/video to retrieve and which frame to extract, enabling better testing and debugging.

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

**Description**: Finds and displays an image file (JPG, JPEG, or PNG) from the printer based on the configured index.

**What it does**:
- Scans the printer's directories (`/timelapse`, `/cache`, `/`) for image files
- Sorts images by timestamp (most recent first)
- Downloads the image at the configured index (0=latest, 1=2nd latest, etc.)
- Displays the image in a Home Assistant notification
- Shows the image path, timestamp, and index information

**Configuration**: Use the `number.<printer_name>_ftps_test_image_index` entity to select which image to retrieve (0-20).

**Use case**: Verify that image files are accessible via FTPS for spaghetti detection, and test with different images when debugging issues.

### 3. Get Last Frame

**Entity ID**: `button.<printer_name>_get_last_frame`

**Description**: Finds a video file and extracts a frame at a configurable offset from the end.

**What it does**:
- Scans the printer's directories for video files (AVI, MPG, MPEG, MP4)
- Sorts videos by timestamp (most recent first)
- Downloads the video at the configured index (0=latest, 1=2nd latest, etc.)
- Uses FFmpeg to extract a frame at the configured offset from the end of the video
- Displays the extracted frame in a Home Assistant notification
- Shows the video path, timestamp, index, and frame offset information

**Configuration**: 
- Use the `number.<printer_name>_ftps_test_video_index` entity to select which video to use (0 or higher, depending on available videos)
- Use the `number.<printer_name>_ftps_test_frame_offset` entity to set how many seconds from the end to extract the frame (1 or higher)

**Use case**: Verify that video files are accessible and that frame extraction works. This is crucial for debugging black frame issues or testing different parts of videos.

## New Number Entities

### 1. FTPS Test Video Index

**Entity ID**: `number.<printer_name>_ftps_test_video_index`

**Description**: Selects which video to use when pressing the "Get Last Frame" button.

**Range**: 0 or higher (0 = most recent video, 1 = 2nd most recent, etc.)

**Default**: 0 (latest video)

**Note**: The actual maximum depends on how many video files are available on the printer. If you request an index that doesn't exist, you'll get an appropriate error message.

### 2. FTPS Test Frame Offset

**Entity ID**: `number.<printer_name>_ftps_test_frame_offset`

**Description**: Sets how many seconds from the end of the video to extract a frame.

**Range**: 1 second or higher

**Default**: 1 second from end

**Note**: The actual maximum depends on the video duration. If you request an offset longer than the video, you'll get an appropriate error message.

**Use case**: If the last second of a video is black, increase this value to extract a frame from earlier in the video.

### 3. FTPS Test Image Index

**Entity ID**: `number.<printer_name>_ftps_test_image_index`

**Description**: Selects which image to retrieve when pressing the "Get Last Image" button.

**Range**: 0 or higher (0 = most recent image, 1 = 2nd most recent, etc.)

**Default**: 0 (latest image)

**Note**: The actual maximum depends on how many image files are available on the printer. If you request an index that doesn't exist, you'll get an appropriate error message.

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

To use these features:

1. Navigate to your Bambu Lab printer device in Home Assistant
2. Find the three new number entities under the diagnostic category to configure test parameters:
   - **FTPS Test Image Index**: Set which image to retrieve (0=latest, 1=2nd latest, etc.)
   - **FTPS Test Video Index**: Set which video to use (0=latest, 1=2nd latest, etc.)
   - **FTPS Test Frame Offset**: Set how many seconds from the end to extract a frame (1-60)
3. Find the three buttons under the diagnostic category
4. Press any button to test the corresponding functionality
5. Check your Home Assistant notifications for the results

### Example Workflows

**Testing different parts of a video:**
1. Set "FTPS Test Frame Offset" to 1 second - press "Get Last Frame" - check the result
2. If the frame is black, set "FTPS Test Frame Offset" to 5 seconds - press "Get Last Frame" again
3. Continue adjusting until you find a good frame

**Testing older files:**
1. Set "FTPS Test Video Index" to 1 to get the 2nd most recent video
2. Press "Get Last Frame" to see a frame from that video
3. Set to 2 for the 3rd most recent, and so on

## Troubleshooting

If any button fails:

1. **Check FTPS Configuration**: Ensure your printer's IP address and access code are correct
2. **Network Connectivity**: Verify that Home Assistant can reach the printer on port 990 (FTPS)
3. **Printer Permissions**: Ensure the access code has proper permissions
4. **FFmpeg Availability**: For "Get Last Frame", ensure FFmpeg is available in your Home Assistant installation
5. **Check Logs**: Look for error messages in the Home Assistant logs under the `custom_components.bambu_lab` logger

### Common Issues

**"No image files found"**
- Check if your printer has any image files in `/timelapse`, `/cache`, or `/` directories
- Try pressing the "Test FTPS" button to see what files exist
- Ensure your printer has completed at least one print with timelapse enabled

**"Only X image(s) found, cannot retrieve index Y"**
- You've set the image/video index too high
- Lower the index number to within the available range
- The notification will tell you how many files were found

**"Last frame is black"**
- The end of the video may be black/empty
- Increase the "FTPS Test Frame Offset" value to extract a frame from earlier in the video
- Try values like 5, 10, or 20 seconds from the end

**"Failed to extract frame from video"**
- Check FFmpeg is installed and accessible
- Check the video file isn't corrupted
- Try a different video by adjusting the "FTPS Test Video Index"
- Check Home Assistant logs for detailed FFmpeg error messages

## Notes

- These buttons are classified as "diagnostic" entities and may be hidden by default in some UIs
- Large videos may take some time to download and process
- The notifications include embedded images, so they may be large
- File timestamps use the printer's clock, which may not always be accurate
