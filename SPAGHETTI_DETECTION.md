# Spaghetti Detection Feature

This document describes the comprehensive spaghetti detection feature that monitors your 3D prints for failures using edge-based image analysis.

## Overview

The spaghetti detection system analyzes chamber images during printing to detect potential print failures such as:
- **Spaghetti**: Thin, chaotic filament structures from failed adhesion
- **Detached prints**: Loss of bed adhesion causing the print to move
- **Mid-air extrusion**: Printer continuing to extrude when print has failed

The system uses edge detection algorithms to identify sudden changes in the print structure that indicate failures.

## Components

### 1. Test Button: "Test Spaghetti Detection"

**Entity ID**: `button.<printer_name>_test_spaghetti_detection`

**Purpose**: Manually test the edge detection algorithm on a video frame from FTPS.

**What it does**:
1. Retrieves a video frame using the configured FTPS test parameters (video index and frame offset)
2. Analyzes the frame using edge detection algorithms
3. Calculates edge density metrics
4. Displays comprehensive results in a Home Assistant notification

**Output includes**:
- Edge density value (0.0 to 1.0)
- Edge pixel count and percentage
- Image dimensions
- Visual interpretation guidelines
- The analyzed frame image

**Use case**: Validate that edge detection works correctly and understand what "normal" edge density looks like for your printer and prints.

### 2. Sensors

#### Spaghetti Detection Status
**Entity ID**: `sensor.<printer_name>_spaghetti_detection_status`

**Values**:
- `disabled`: Detection is turned off via the switch
- `inactive`: Detection is enabled but no print is running
- `monitoring`: Actively monitoring a print in progress
- `alert`: Potential failure detected

**Attributes**:
- `enabled`: Whether detection is globally enabled
- `monitoring_active`: Whether currently monitoring a print
- `alert_triggered`: Whether an alert has been triggered

#### Spaghetti Edge Density
**Entity ID**: `sensor.<printer_name>_spaghetti_edge_density`

**Value**: Current edge density (0.0 to 1.0)

**Attributes**:
- `average_edge_density`: Average across all monitored layers
- `rate_of_change`: Current rate of change in edge density
- `history_size`: Number of layers in history
- `current_layer`: Current layer number
- `total_layers`: Total layers in the print

**Interpretation**:
- **< 0.05**: Few edges, simple or empty scene
- **0.05-0.15**: Typical print with clean edges (normal range)
- **0.15-0.25**: Complex structure or potential early issues
- **> 0.25**: High likelihood of spaghetti or major failure

#### Spaghetti Test Result
**Entity ID**: `sensor.<printer_name>_spaghetti_test_result`

**Value**: Edge density from the last manual test, or "No test run"

**Attributes**: All metrics from the last test analysis

### 3. Configuration Number Entities

#### Spaghetti Edge Density Threshold
**Entity ID**: `number.<printer_name>_spaghetti_edge_density_threshold`

**Range**: 0.0 to 1.0 (default: 0.15)

**Purpose**: Set the threshold for detecting abnormal edge density increases from baseline.

A value of 0.15 means a 15% increase in edge density from the baseline will trigger an alert.

#### Spaghetti Rate Threshold
**Entity ID**: `number.<printer_name>_spaghetti_rate_threshold`

**Range**: 0.0 to 1.0 (default: 0.10)

**Purpose**: Set the threshold for rate of change detection.

A value of 0.10 means a 10% increase in edge density over the rate window will trigger an alert.

#### Spaghetti Rate Window Size
**Entity ID**: `number.<printer_name>_spaghetti_rate_window_size`

**Range**: 3 to 20 layers (default: 5)

**Purpose**: Set how many recent layers to analyze when calculating rate of change.

A larger window is more stable but slower to detect issues. A smaller window is more sensitive but may have false positives.

### 4. Spaghetti Detection Switch

**Entity ID**: `switch.<printer_name>_spaghetti_detection`

**Purpose**: Enable or disable spaghetti detection monitoring.

When enabled, monitoring will automatically start when a print begins and stop when it ends.

## How It Works

### Manual Testing (Phase 1)

1. **Configure FTPS Test Parameters**:
   - Set `number.<printer_name>_ftps_test_video_index` to select which video (0=latest)
   - Set `number.<printer_name>_ftps_test_frame_offset` to choose frame position (seconds from end)

2. **Run Test**:
   - Press `button.<printer_name>_test_spaghetti_detection`
   - Wait for the notification with results

3. **Interpret Results**:
   - Check the edge density value
   - Compare against interpretation guidelines
   - View the analyzed frame to see what was detected

4. **Compare Across Images**:
   - Adjust the video index or frame offset
   - Run the test again
   - Compare edge density values between different frames

### Automatic Monitoring (Phase 3)

1. **Enable Detection**:
   - Turn on `switch.<printer_name>_spaghetti_detection`

2. **Configure Thresholds** (optional):
   - Adjust `number.<printer_name>_spaghetti_edge_density_threshold`
   - Adjust `number.<printer_name>_spaghetti_rate_threshold`
   - Adjust `number.<printer_name>_spaghetti_rate_window_size`

3. **Start a Print**:
   - Monitoring automatically starts when print begins
   - Status changes to "monitoring"

4. **During Print**:
   - On each layer change, the chamber image is analyzed
   - Edge density is calculated and stored in history
   - Rate of change is monitored
   - `sensor.<printer_name>_spaghetti_edge_density` updates with each layer

5. **Alert Conditions**:
   - If edge density exceeds threshold from baseline: ALERT
   - If rate of change exceeds threshold over window: ALERT
   - Status changes to "alert"
   - `event_spaghetti_detected` is fired (can be used in automations)

6. **Print End**:
   - Monitoring automatically stops when print finishes/fails/cancels
   - History is preserved until next print

## Detection Algorithm

The system uses a multi-stage approach:

### Edge Detection
1. Chamber image is converted to grayscale
2. Image is resized to 640px max dimension (for performance)
3. PIL's FIND_EDGES filter is applied
4. Edges are thresholded (pixels > 30 intensity)
5. Edge density = edge_pixels / total_pixels

### Baseline Tracking
- First few layers establish a baseline edge density
- Baseline is updated every 5 layers (configurable)
- Compares current density to baseline

### Rate of Change Detection
- Maintains history of edge density per layer (last 50 layers)
- Calculates rate over a sliding window (default 5 layers)
- Detects sudden increases that indicate rapid structure changes

### Alert Logic
An alert is triggered when either:
1. **Baseline anomaly**: Current density increased > 15% from baseline
2. **Sudden growth**: Frame-to-frame change > 25%
3. **Rate anomaly**: Rate of change over window > 10%

Alerts have a cooldown period (3 layers) to prevent spam.

## Automations

### Example: Send Notification on Detection

```yaml
automation:
  - alias: "Bambu Lab Spaghetti Detected"
    trigger:
      - platform: event
        event_type: bambu_lab
        event_data:
          type: event_spaghetti_detected
    action:
      - service: notify.mobile_app
        data:
          title: "Print Failure Detected!"
          message: "Possible spaghetti on {{ trigger.event.data.device.name }}"
          data:
            tag: "bambu_spaghetti"
            priority: high
```

### Example: Pause Print on Detection

```yaml
automation:
  - alias: "Pause Print on Spaghetti"
    trigger:
      - platform: state
        entity_id: sensor.bambu_lab_p1p_spaghetti_detection_status
        to: "alert"
    action:
      - service: button.press
        target:
          entity_id: button.bambu_lab_p1p_pause
```

### Example: Monitor Edge Density Trend

```yaml
automation:
  - alias: "High Edge Density Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bambu_lab_p1p_spaghetti_edge_density
        above: 0.20
    condition:
      - condition: state
        entity_id: sensor.bambu_lab_p1p_spaghetti_detection_status
        state: "monitoring"
    action:
      - service: notify.mobile_app
        data:
          title: "High Edge Density"
          message: "Edge density is {{ states('sensor.bambu_lab_p1p_spaghetti_edge_density') }}, watch for issues"
```

## Tuning Guide

### Getting Started

1. **Run Initial Tests**:
   - Use the test button on known good prints
   - Note typical edge density values (usually 0.05-0.15)
   - Test on images of failed prints if available

2. **Monitor a Few Prints**:
   - Enable detection and watch `sensor.<printer_name>_spaghetti_edge_density`
   - Observe how edge density changes throughout the print
   - Check the rate_of_change attribute

3. **Adjust Thresholds**:
   - If getting false positives: Increase thresholds
   - If missing real failures: Decrease thresholds
   - If detection is too fast: Increase rate window size
   - If detection is too slow: Decrease rate window size

### Threshold Guidelines

**Conservative (fewer false alarms)**:
- Edge Density Threshold: 0.20-0.25
- Rate Threshold: 0.15-0.20
- Rate Window: 7-10 layers

**Balanced (default)**:
- Edge Density Threshold: 0.15
- Rate Threshold: 0.10
- Rate Window: 5 layers

**Aggressive (catch issues early)**:
- Edge Density Threshold: 0.10-0.12
- Rate Threshold: 0.08
- Rate Window: 3-4 layers

### Print Type Considerations

Different print types have different characteristics:

**Simple Geometric Prints** (cubes, cylinders):
- Lower baseline edge density (0.03-0.08)
- Use lower thresholds

**Complex Detailed Prints** (figurines, mechanical parts):
- Higher baseline edge density (0.08-0.15)
- Use higher thresholds or rely more on rate detection

**Vase Mode**:
- Very low edge density (0.02-0.05)
- Use aggressive rate detection

## Troubleshooting

### "No chamber image available" in logs

**Cause**: The chamber image sensor is not providing data.

**Solution**:
1. Ensure you have a compatible printer (P1P, P1S, A1, A1 Mini)
2. Verify `switch.<printer_name>_imagecamera` is enabled
3. Check that the camera is functioning properly

### False positives at layer changes

**Cause**: Legitimate structure changes triggering alerts.

**Solution**:
1. Increase `spaghetti_edge_density_threshold`
2. Increase `spaghetti_rate_window_size` for more stability
3. Monitor the edge density during normal prints to understand patterns

### Missing actual failures

**Cause**: Thresholds too high or failure type not detectable.

**Solution**:
1. Decrease thresholds
2. Use the test button on images of the failure to see if edge density changed
3. Some failures (internal voids, weak adhesion) may not be detectable

### High system load

**Cause**: Image analysis on every layer change.

**Solution**:
1. Image processing is optimized (resized to 640px)
2. Runs in the event loop without blocking
3. If still concerned, monitor system resources

## Technical Details

### Image Processing

- **Input**: JPEG image from `ChamberImage` (typically 1920x1080)
- **Resize**: Scaled to max 640px dimension (maintains aspect ratio)
- **Filter**: PIL's ImageFilter.FIND_EDGES (Sobel-like operator)
- **Threshold**: Binary threshold at intensity 30
- **Output**: Edge density ratio (0.0 to 1.0)

### Performance

- **Processing time**: ~50-200ms per image (depending on hardware)
- **Memory**: Minimal, images are not stored (only metrics)
- **History**: Last 50 layers (configurable via `_max_history_size`)

## External Camera Support

If the built-in printer camera is not sufficient quality for spaghetti detection, you can configure an external camera to use instead.

### Configuration

**Entity ID**: `select.<printer_name>_external_camera`

**Purpose**: Select a Home Assistant camera or image entity to use for spaghetti detection instead of the built-in chamber camera.

**How to configure**:

1. Set up your external camera in Home Assistant (e.g., ESP32-CAM, USB camera, IP camera)
2. Ensure the camera has a clear view of the print bed
3. Navigate to the Bambu Lab printer device in Home Assistant
4. Find the "Spaghetti Detection Camera" select entity
5. Choose from the dropdown:
   - **Built-in Chamber Camera** (default) - Uses the printer's internal camera
   - Any configured camera or image entity from your Home Assistant installation
6. The dropdown automatically includes all available `camera.*` and `image.*` entities

### Supported Entity Types

- **Camera entities** (`camera.*`): Standard camera entities with live image feeds
- **Image entities** (`image.*`): Static image entities that update periodically

### How it Works

When an external camera is selected:

1. **On layer change**: Instead of using the built-in chamber image, the system fetches the current image from the specified external entity
2. **Image analysis**: The external image is processed through the same edge detection algorithm
3. **Detection**: All spaghetti detection features work identically (thresholds, rate monitoring, alerts)

**Note**: The spaghetti detection algorithm runs on every layer change during printing, using whichever camera is selected (built-in or external).

### Best Practices

1. **Camera positioning**: Position the external camera to have a similar view angle to the built-in camera for best results
2. **Lighting**: Ensure consistent lighting on the print bed (the external camera may not benefit from the chamber lights)
3. **Image quality**: Higher resolution cameras generally provide better detection accuracy
4. **Update frequency**: Ensure your camera updates frequently enough to capture layer changes (typically every few seconds is sufficient)

### Example Setup

#### ESP32-CAM Example

```yaml
# configuration.yaml
camera:
  - platform: mjpeg
    name: "3D Printer External Camera"
    mjpeg_url: http://192.168.1.100:81/stream
```

Then select `camera.3d_printer_external_camera` from the dropdown.

#### Generic IP Camera Example

```yaml
# configuration.yaml
camera:
  - platform: generic
    name: "Printer Bed Camera"
    still_image_url: http://192.168.1.101/snapshot.jpg
    stream_source: rtsp://192.168.1.101:554/stream
```

Then select `camera.printer_bed_camera` from the dropdown.

### Troubleshooting External Camera

#### Camera not appearing in dropdown

**Cause**: The camera may not be properly configured or loaded in Home Assistant.

**Solution**:
1. Check that the camera entity exists in Developer Tools → States
2. Verify the camera is online and functioning
3. Restart Home Assistant if the camera was just added
4. The dropdown refreshes when you open it, so it will show newly added cameras

#### "External camera entity not found" in logs

**Cause**: The entity ID selected no longer exists or was removed.

**Solution**:
1. Check the entity ID is correct in Home Assistant (Developer Tools → States)
2. Verify the camera is online and functioning
3. Select a different camera from the dropdown or revert to "Built-in Chamber Camera"

#### "External camera entity is not a camera or image entity" in logs

**Cause**: The selected entity is not a camera or image type.

**Solution**:
1. The dropdown should only show valid camera and image entities
2. If you see this error, the entity may have changed type after being selected
3. Select a different camera from the dropdown or revert to "Built-in Chamber Camera"

#### No images being analyzed from external camera

**Cause**: Camera may not be updating or accessible.

**Solution**:
1. View the camera feed in Home Assistant to confirm it's working
2. Check Home Assistant logs for errors fetching images
3. Verify the camera updates frequently enough (check last_changed in Developer Tools → States)

### Technical Details

- **Image Format**: Accepts any image format supported by PIL/Pillow (JPEG, PNG, etc.)
- **Async Fetching**: Image retrieval is asynchronous and doesn't block the MQTT thread
- **Error Handling**: If external camera fetch fails, layer change is skipped (no fallback to built-in camera)
- **Performance**: External camera fetching adds ~50-500ms depending on camera response time

### Limitations

1. **Camera Support**: Works with built-in chamber camera (P1P, P1S, A1, A1 Mini) or any configured external camera entity
2. **Layer-based**: Only analyzes on layer changes, not continuous
3. **Edge-based**: Detects structural changes, not all failure types
4. **Lighting Dependent**: Consistent lighting recommended for best results
5. **Post-failure**: Detects after failure started, cannot predict

## Future Enhancements

Potential improvements for future versions:

1. **Machine Learning**: Train on failed vs successful prints
2. **Multi-metric Analysis**: Combine edge density with other indicators
3. **Predictive**: Analyze trends to predict failures before they occur
4. **Adaptive Thresholds**: Automatically adjust based on print history
5. **Region of Interest**: Focus on specific areas of the build plate
6. **Confidence Score**: Probability-based alerts rather than binary

## Support

For issues, questions, or feedback:
1. Check Home Assistant logs under `custom_components.bambu_lab`
2. Review edge density values from test runs
3. Report issues on the GitHub repository with:
   - Log excerpts
   - Edge density values
   - Images of the print (if possible)
   - Printer model and firmware version
