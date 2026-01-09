# Summary of Changes for FTPS and Camera Improvements

## Changes Made

### 1. Added `/ipcam` Folder to Search Paths

**Files Modified**: `custom_components/bambu_lab/pybambu/models.py`

**Changes**:
- Updated `_sync_get_last_video_frame()` to search `/ipcam` folder first, then `/timelapse`, `/cache`, and `/`
- Updated `_sync_get_last_image()` to search `/ipcam` folder first, then `/timelapse`, `/cache`, and `/`
- Prioritized `/ipcam` because it contains active recordings during prints

**Why**: The "Get Last Frame" button was retrieving old videos from `/timelapse` instead of current recordings from `/ipcam`

### 2. Improved Error Logging for FTPS

**Files Modified**: `custom_components/bambu_lab/pybambu/models.py`

**Changes**:
- Track which paths were successfully searched vs which failed
- Error messages now show: "Successfully searched: /ipcam, /timelapse, /cache (Failed to access: /)"
- Helps users understand if certain folders don't exist on their printer

**Why**: Better debugging information when folders don't exist or have permission issues

### 3. External Camera Dropdown Selector

**Files Modified**: 
- `custom_components/bambu_lab/select.py`
- `custom_components/bambu_lab/translations/en.json`

**Changes**:
- Added new `BambuLabExternalCameraSelect` entity
- Dropdown automatically populated with all available `camera.*` and `image.*` entities
- Option for "Built-in Chamber Camera" (default)
- Replaces the manual text entry with user-friendly dropdown

**Why**: Easier configuration, prevents typos in entity IDs, shows only valid camera options

### 4. Documentation Updates

**Files Modified**: `SPAGHETTI_DETECTION.md`

**Changes**:
- Updated external camera configuration section
- Changed from text entity to select entity instructions
- Added troubleshooting for dropdown issues
- Clarified that spaghetti detection runs on every layer change using selected camera

## How to Test

### Testing /ipcam Folder Access

1. Press the "Get Last Frame" button (`button.<printer_name>_get_last_frame`)
2. Check the notification for the video path
3. Check Home Assistant logs for messages like:
   - `Searching for videos in /ipcam`
   - `Successfully searched: /ipcam, /timelapse, /cache`
   - Or `Failed to access: /ipcam` if folder doesn't exist

### Testing External Camera Dropdown

1. Navigate to your Bambu Lab printer device in Home Assistant
2. Find the "Spaghetti Detection Camera" select entity
3. Click the dropdown - it should show:
   - "Built-in Chamber Camera" (default)
   - All your configured camera entities (e.g., `camera.esp32_cam`)
   - All your image entities (e.g., `image.screenshot`)
4. Select a camera and verify it's saved
5. Start a print and check that spaghetti detection uses the selected camera

### Testing Backward Compatibility

The old text entity (`text.<printer_name>_spaghetti_external_camera_entity_id`) is still present but marked as deprecated. If you had a camera configured in the text field:
- The select dropdown should respect that setting
- You can now use the dropdown instead
- The text entity will be removed in a future version

## Expected Behavior

### Active Print with External Camera

When you have an active print running with an external camera (e.g., ESP32-CAM) configured:

1. During printing, videos/images are recorded to `/ipcam` folder
2. "Get Last Frame" button retrieves the most recent file from `/ipcam` first
3. If `/ipcam` doesn't exist or is empty, falls back to `/timelapse`, then `/cache`, then `/`
4. On each layer change, spaghetti detection fetches image from selected camera (external or built-in)

### After Print Completes

1. Videos are moved from `/ipcam` to `/timelapse` folder
2. "Get Last Frame" will find the video in `/timelapse`
3. This is normal behavior - the video is no longer being written

## Notes on File Access

**Question**: Can it access files that are still open and being written?

**Answer**: Yes, FTP allows reading files that are currently being written. The printer's FTP server allows:
- Reading incomplete video files from `/ipcam` during recording
- FFmpeg can extract frames from incomplete video files
- The last frame may be within 1 second of the end of what's been written so far

## Troubleshooting

### "No video files found" with all paths listed

This means the search worked but no video files were found. Possible reasons:
1. No prints have been run yet (no timelapses created)
2. Camera recording is disabled on the printer
3. Timelapse feature is disabled in printer settings

### "Failed to access: /ipcam" in error message

This is normal if:
1. Your printer doesn't have an `/ipcam` folder (some models or firmware versions may differ)
2. The folder only exists during active recording
3. The search will continue with other folders

### Dropdown doesn't show my camera

1. Verify the camera exists: Developer Tools → States
2. Check that it's a `camera.*` or `image.*` entity
3. Restart Home Assistant if camera was just added
4. The dropdown refreshes each time you open it

## Related Files

- `custom_components/bambu_lab/pybambu/models.py` - FTPS search logic
- `custom_components/bambu_lab/select.py` - Select entities including camera dropdown
- `custom_components/bambu_lab/button.py` - "Get Last Frame" button implementation
- `custom_components/bambu_lab/translations/en.json` - UI text translations
- `SPAGHETTI_DETECTION.md` - Complete spaghetti detection documentation
