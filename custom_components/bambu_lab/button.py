import base64
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, LOGGER
from .models import BambuLabEntity
from .pybambu.commands import PAUSE, RESUME, STOP, BUZZER_SET_SILENT, BUZZER_SET_ALARM, BUZZER_SET_BEEPING
from .pybambu.const import Features

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .coordinator import BambuDataUpdateCoordinator

# Maximum number of directory entries to display in FTPS test notification
MAX_DISPLAYED_FILES = 20

PAUSE_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="pause",
    icon="mdi:pause",
    translation_key="pause",
    entity_category=EntityCategory.CONFIG,
)
RESUME_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="resume",
    icon="mdi:play",
    translation_key="resume",
    entity_category=EntityCategory.CONFIG,
)
STOP_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="stop",
    icon="mdi:stop",
    translation_key="stop",
    entity_category=EntityCategory.CONFIG,
)
FORCE_REFRESH_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="refresh",
    icon="mdi:refresh",
    translation_key="refresh",
    entity_category=EntityCategory.DIAGNOSTIC,
)

# There is no reliable way to obtain state of the buzzer, so it is better to expose as buttons
# Also, there are 3 possible states, therefore, it cannot be fully exposed by switch
BUZZER_SILENCE_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="buzzer_silence",
    icon="mdi:alarm-light-off-outline",
    translation_key="buzzer_silence",
    entity_category=EntityCategory.CONFIG,
)
BUZZER_FIRE_ALARM_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="buzzer_fire_alarm",
    icon="mdi:alarm-light",
    translation_key="buzzer_fire_alarm",
    entity_category=EntityCategory.CONFIG,
)
BUZZER_BEEPING_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="buzzer_beeping",
    icon="mdi:alarm-light-outline",
    translation_key="buzzer_beeping",
    entity_category=EntityCategory.CONFIG,
)

TEST_FTPS_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="test_ftps",
    icon="mdi:file-check",
    translation_key="test_ftps",
    entity_category=EntityCategory.DIAGNOSTIC,
)

GET_LAST_IMAGE_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="get_last_image",
    icon="mdi:image",
    translation_key="get_last_image",
    entity_category=EntityCategory.DIAGNOSTIC,
)

GET_LAST_FRAME_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="get_last_frame",
    icon="mdi:video-image",
    translation_key="get_last_frame",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:

    coordinator: BambuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.get_model().has_full_printer_data:
        return

    LOGGER.debug(f"BUTTON::async_setup_entry")

    # Unsure if hybrid model blocks this control.
    if not coordinator.get_model().print_fun.mqtt_signature_required:
        buttons = [
            BambuLabPauseButton(coordinator, entry),
            BambuLabResumeButton(coordinator, entry),
            BambuLabStopButton(coordinator, entry),
            BambuLabRefreshButton(coordinator, entry),
            BambuLabTestFTPSButton(coordinator, entry),
            BambuLabGetLastImageButton(coordinator, entry),
            BambuLabGetLastFrameButton(coordinator, entry)
        ]

        if coordinator.get_model().supports_feature(Features.FIRE_ALARM_BUZZER):
            buttons += [
                BambuLabBuzzerSilenceButton(coordinator, entry),
                BambuLabBuzzerFireAlarmButton(coordinator, entry),
                BambuLabBuzzerBeepingButton(coordinator, entry)
            ]

        async_add_entities(buttons)


class BambuLabButton(BambuLabEntity, ButtonEntity):
    """Base BambuLab Button"""

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        """Initialise a button."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{config_entry.data['serial']}_{self.entity_description.key}"
        )


class BambuLabPauseButton(BambuLabButton):
    """BambuLab Print Pause Button"""

    entity_description = PAUSE_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        """Return if the button is available"""
        if self.coordinator.data.print_job.gcode_state == "RUNNING":
            return True
        return False

    async def async_press(self) -> None:
        """ Pause the Print on button press"""
        self.coordinator.client.publish(PAUSE)


class BambuLabResumeButton(BambuLabButton):
    """BambuLab Print Resume Button"""

    entity_description = RESUME_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        """Return if the button is available"""
        if self.coordinator.data.print_job.gcode_state == "PAUSE":
            return True
        return False

    async def async_press(self) -> None:
        """ Pause the Print on button press"""
        self.coordinator.client.publish(RESUME)


class BambuLabStopButton(BambuLabButton):
    """BambuLab Print Stop Button"""

    entity_description = STOP_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        """Return if the button is available"""
        if self.coordinator.data.print_job.gcode_state == "RUNNING" or self.coordinator.data.print_job.gcode_state == "PAUSE":
            return True
        return False

    async def async_press(self) -> None:
        """ Stop the Print on button press"""
        self.coordinator.client.publish(STOP)


class BambuLabRefreshButton(BambuLabButton):
    """BambuLab Refresh data Button"""

    entity_description = FORCE_REFRESH_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        return True

    async def async_press(self) -> None:
        """ Force refresh MQTT info"""
        await self.coordinator.client.refresh()

class BambuLabBuzzerSilenceButton(BambuLabButton):
    """BambuLab Buzzer Silence Button"""

    entity_description = BUZZER_SILENCE_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """ Pause the Print on button press"""
        self.coordinator.client.publish(BUZZER_SET_SILENT)

class BambuLabBuzzerFireAlarmButton(BambuLabButton):
    """BambuLab Buzzer Fire Alarm Button"""

    entity_description = BUZZER_FIRE_ALARM_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """ Pause the Print on button press"""
        self.coordinator.client.publish(BUZZER_SET_ALARM)

class BambuLabBuzzerBeepingButton(BambuLabButton):
    """BambuLab Buzzer Beeping Button"""

    entity_description = BUZZER_BEEPING_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """ Pause the Print on button press"""
        self.coordinator.client.publish(BUZZER_SET_BEEPING)

class BambuLabTestFTPSButton(BambuLabButton):
    """BambuLab Test FTPS Button"""

    entity_description = TEST_FTPS_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """Test FTPS connection and list root directory."""
        result = await self.coordinator.data.print_job.async_test_ftps_connection()
        
        if result["success"]:
            file_list = "\n".join(result["files"][:MAX_DISPLAYED_FILES])
            if len(result["files"]) > MAX_DISPLAYED_FILES:
                file_list += f"\n... and {len(result['files']) - MAX_DISPLAYED_FILES} more files"
            
            message = f"**FTPS Connection Successful**\n\nRoot Directory Listing:\n```\n{file_list}\n```"
        else:
            message = f"**FTPS Connection Failed**\n\n{result['message']}"
        
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "FTPS Test Result",
                "message": message,
                "notification_id": f"bambu_ftps_test_{self.coordinator.data.info.serial}"
            }
        )

class BambuLabGetLastImageButton(BambuLabButton):
    """BambuLab Get Last Image Button"""

    entity_description = GET_LAST_IMAGE_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """Find and display the most recent image file."""
        result = await self.coordinator.data.print_job.async_get_last_image()
        
        if result["success"] and result["image_data"]:
            # Convert image data to base64 for display in notification
            image_base64 = base64.b64encode(result["image_data"]).decode('utf-8')
            
            # Determine MIME type from file extension
            _, ext = os.path.splitext(result['image_path'].lower())
            mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png"
            
            message = f"""**Latest Image Found**

Path: `{result['image_path']}`
Timestamp: {result.get('timestamp', 'Unknown')}
Image Index: {result.get('image_index', 0)} of {result.get('total_images', 'unknown')}

![Image](data:{mime_type};base64,{image_base64})
"""
        else:
            message = f"**No Image Found**\n\n{result['message']}"
        
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Last Image Result",
                "message": message,
                "notification_id": f"bambu_last_image_{self.coordinator.data.info.serial}"
            }
        )

class BambuLabGetLastFrameButton(BambuLabButton):
    """BambuLab Get Last Frame Button"""

    entity_description = GET_LAST_FRAME_BUTTON_DESCRIPTION

    async def async_press(self) -> None:
        """Extract and display the last frame from the latest video."""
        result = await self.coordinator.data.print_job.async_get_last_video_frame()
        
        if result["success"] and result["image_data"]:
            # Convert image data to base64 for display in notification
            image_base64 = base64.b64encode(result["image_data"]).decode('utf-8')
            
            message = f"""**Last Video Frame Extracted**

Video: `{result['video_path']}`
Timestamp: {result.get('timestamp', 'Unknown')}
Video Index: {result.get('video_index', 0)} of {result.get('total_videos', 'unknown')}
Frame Offset: {result.get('frame_offset', 1)} seconds from end

![Frame](data:image/jpeg;base64,{image_base64})
"""
        else:
            message = f"**Frame Extraction Failed**\n\n{result['message']}"
        
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Last Video Frame",
                "message": message,
                "notification_id": f"bambu_last_frame_{self.coordinator.data.info.serial}"
            }
        )

