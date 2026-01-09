# Summary of Changes for FTPS and Camera Improvements

## ⚠️ IMPORTANT: Installation Instructions

**After updating to this branch, you MUST restart Home Assistant for the changes to take effect.**

The Python code changes will not be loaded until Home Assistant is restarted. Simply reloading the integration is not sufficient.

### How to Restart Home Assistant:
1. Go to Developer Tools → Services
2. Search for "Homeassistant: Restart"
3. Click "Call Service"
4. Wait for Home Assistant to come back online

**Or use the command line:**
```bash
ha core restart
```

## Changes Made

### 1. Dynamic FTP Directory Discovery

**Files Modified**: `custom_components/bambu_lab/pybambu/models.py`

**Changes**:
- Added `_discover_ftp_directories()` function to automatically detect available folders on the FTP server
- Replaced hardcoded search paths with dynamic discovery
- Updated `_sync_get_last_video_frame()` to use discovered directories
- Updated `_sync_get_last_image()` to use discovered directories
- Maintains intelligent priority order: `/ipcam`, `/image`, `/timelapse`, `/cache`, then `/`
- Only searches directories that actually exist on the printer

**Why**: 
- Different printer models and firmware versions have different folder structures
- Hardcoded paths would fail on printers that don't have certain folders
- Dynamic discovery adapts to any printer configuration
- The "Get Last Frame" button was retrieving old videos from `/timelapse` instead of current recordings from `/ipcam`
- PNG files stored in `/image` folder were not being found

**How it works**:
1. When searching for images/videos, first queries FTP root directory
2. Identifies which known folders exist (`/ipcam`, `/image`, `/timelapse`, `/cache`)
3. Creates search path list with only existing folders, in priority order
4. Falls back to root `/` directory if no known folders found
5. Logs discovered directories for debugging

### 2. Improved Error Logging for FTPS

**Files Modified**: `custom_components/bambu_lab/pybambu/models.py`

**Changes**:
- Track which paths were successfully searched vs which failed
- Error messages now show: "Successfully searched: /ipcam, /timelapse, /cache (Failed to access: /)"
- Helps users understand if certain folders don't exist on their printer

**Why**: Better debugging information when folders don't exist or have permission issues

**Understanding the New Error Messages**:
- Old: `No image files found in /timelapse, /cache, /`
- New: `No image files found in /ipcam, /image, /timelapse (Failed to access: /cache)`
- The new message shows:
  - Which paths were successfully searched (folders that exist and were readable)
  - Which paths failed to access (folders that don't exist or had permission issues)
  - Only discovered folders are included in the search
- If you still see the old message format, you need to restart Home Assistant

### 3. External Camera Dropdown Selector

**Files Modified**: 
- `custom_components/bambu_lab/select.py`
- `custom_components/bambu_lab/translations/en.json`

**Changes**:
- Added new `BambuLabExternalCameraSelect` entity
- Dropdown automatically populated with all available `camera.*` and `image.*` entities (lazy-loaded for performance)
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

### Testing Dynamic Directory Discovery

1. Press the "Get Last Frame" button (`button.<printer_name>_get_last_frame`)
2. Check the notification for the video path
3. Check Home Assistant logs for messages like:
   - `Discovered FTP directory: /ipcam`
   - `Discovered FTP directory: /image`
   - `FTP directory search order: ['/ipcam', '/image', '/timelapse', '/cache', '/']`
   - `Searching for videos in /ipcam`
   - `Successfully searched: /ipcam, /image, /timelapse`
   - Or `Failed to access: /cache` if folder doesn't exist
4. The discovered directories will vary based on your printer model and firmware

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

1. FTP directory discovery runs first to detect available folders
2. During printing, videos/images are recorded to `/ipcam` and/or `/image` folders (if they exist)
3. "Get Last Frame" button searches discovered folders in priority order (typically: `/ipcam` → `/image` → `/timelapse` → `/cache` → `/`)
4. Retrieves the most recent file from the first discovered folder that has matching files
5. On each layer change, spaghetti detection fetches image from selected camera (external or built-in)

### After Print Completes

1. Videos are typically moved from `/ipcam` to `/timelapse` folder (printer behavior varies)
2. Images may remain in `/image` folder or be archived to `/timelapse`
3. "Get Last Frame" will find the video in whichever folder it currently exists
4. This is normal behavior - discovery adapts to where files are located

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
