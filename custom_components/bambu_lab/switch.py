from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, LOGGER, Options
from .models import BambuLabEntity
from .pybambu.const import Features

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)

from .coordinator import BambuDataUpdateCoordinator


AIRDUCT_MODE_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="airduct_mode",
    icon="mdi:air-filter",
    translation_key="airduct_mode",
    entity_category=EntityCategory.CONFIG,
)

PROMPT_SOUND_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="prompt_sound",
    icon="mdi:audio",
    translation_key="prompt_sound",
    entity_category=EntityCategory.CONFIG,
)

CAMERA_SWITCH_DESCRIPION = SwitchEntityDescription(
    key="camera",
    icon="mdi:refresh-auto",
    translation_key="camera",
    entity_category=EntityCategory.CONFIG,
)

CAMERA_IMAGE_SENSOR_DESCRIPION = SwitchEntityDescription(
    key="imagecamera",
    icon="mdi:refresh-auto",
    translation_key="imagecamera",
    entity_category=EntityCategory.CONFIG,
)

FTP_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="ftp",
    icon="mdi:folder-network",
    translation_key="ftp",
    entity_category=EntityCategory.CONFIG,
)

SPAGHETTI_DETECTION_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="spaghetti_detection",
    icon="mdi:alert-octagon",
    translation_key="spaghetti_detection",
    entity_category=EntityCategory.CONFIG,
)

INCOGNITO_MODE_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="incognito_mode",
    icon="mdi:incognito",
    translation_key="incognito_mode",
    entity_category=EntityCategory.CONFIG,
)

FTPS_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="ftps",
    icon="mdi:folder-network",
    translation_key="ftps",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    
    coordinator: BambuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.get_model().has_full_printer_data:
        return
    
    LOGGER.debug(f"SWITCH::async_setup_entry")

    # A camera is always present so the switch to turn it on and off should be always present.
    async_add_entities([BambuLabCameraSwitch(coordinator, entry)])

    # Add FTPS and Incognito Mode switches (always present)
    async_add_entities([BambuLabFTPSSwitch(coordinator, entry)])
    async_add_entities([BambuLabIncognitoModeSwitch(coordinator, entry)])

    if coordinator.get_model().supports_feature(Features.CAMERA_IMAGE):
        async_add_entities([BambuLabCameraImageSwitch(coordinator, entry)])
        async_add_entities([BambuLabSpaghettiDetectionSwitch(coordinator, entry)])

    if not coordinator.get_model().print_fun.mqtt_signature_required:
        if coordinator.get_model().supports_feature(Features.PROMPT_SOUND):
                async_add_entities([BambuLabPromptSoundSwitch(coordinator, entry)])
    
        if coordinator.get_model().supports_feature(Features.AIRDUCT_MODE):
            async_add_entities([BambuLabPromptAirductModeSwitch(coordinator, entry)])


class BambuLabSwitch(BambuLabEntity, SwitchEntity):
    """Base BambuLab Switch"""

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        """Initialise a Switch."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{config_entry.data['serial']}_{self.entity_description.key}"
        )
        self._attr_is_on = False


class BambuLabCameraSwitch(BambuLabSwitch):
    """BambuLab Refresh data Switch"""

    entity_description = CAMERA_SWITCH_DESCRIPION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_is_on = self.coordinator.get_option_enabled(Options.CAMERA)

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:video" if self.is_on else "mdi:video-off"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the camera."""
        self._attr_is_on = True
        await self.coordinator.set_option_enabled(Options.CAMERA, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the camera."""
        self._attr_is_on = False
        await self.coordinator.set_option_enabled(Options.CAMERA, False)


class BambuLabCameraImageSwitch(BambuLabSwitch):
    """BambuLab Refresh data Switch"""

    entity_description = CAMERA_IMAGE_SENSOR_DESCRIPION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_is_on = self.coordinator.get_option_enabled(Options.IMAGECAMERA)

    @property
    def available(self) -> bool:
        return self.coordinator.get_option_enabled(Options.CAMERA)

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:image" if self.is_on else "mdi:video"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the camera."""
        self._attr_is_on = True
        await self.coordinator.set_option_enabled(Options.IMAGECAMERA, self._attr_is_on)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the camera."""
        self._attr_is_on = False
        await self.coordinator.set_option_enabled(Options.IMAGECAMERA, self._attr_is_on)


class BambuLabPromptSoundSwitch(BambuLabSwitch):
    """BambuLab Refresh data Switch"""

    entity_description = PROMPT_SOUND_SWITCH_DESCRIPTION

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:volume-high" if self.is_on else "mdi:volume-off"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.coordinator.get_model().home_flag.xcam_prompt_sound

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable A1 / H2D sound."""
        self.coordinator.get_model().info.set_prompt_sound(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable A1 / H2D sound."""
        self.coordinator.get_model().info.set_prompt_sound(False)



class BambuLabPromptAirductModeSwitch(BambuLabSwitch):
    """BambuLab Refresh data Switch"""

    entity_description = AIRDUCT_MODE_SWITCH_DESCRIPTION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_is_on = self.coordinator.get_model().info.airduct_mode == 0 
        
    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        # the filter icon looks like it's letting air in, so we use that for the cooling mode.
        return "mdi:air-filter" if self.is_on else "mdi:hvac"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.coordinator.get_model().info.airduct_mode == 0  # Cooling mode so outside air goes in

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable Cooling."""
        self.coordinator.get_model().info.set_airduct_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Enable Heating/Filter Mode."""
        self.coordinator.get_model().info.set_airduct_mode(False)


class BambuLabSpaghettiDetectionSwitch(BambuLabSwitch):
    """BambuLab Spaghetti Detection Switch"""

    entity_description = SPAGHETTI_DETECTION_SWITCH_DESCRIPTION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        try:
            self._attr_is_on = self.coordinator.get_model().spaghetti_detector.is_enabled
        except AttributeError as e:
            LOGGER.warning(f"Spaghetti detector not available: {e}")
            self._attr_is_on = True
        except Exception as e:
            LOGGER.error(f"Unexpected error initializing spaghetti detector switch: {e}", exc_info=True)
            self._attr_is_on = True
        
    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:eye-check" if self.is_on else "mdi:eye-off"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        try:
            return self.coordinator.get_model().spaghetti_detector.is_enabled
        except AttributeError:
            return self._attr_is_on
        except Exception as e:
            LOGGER.error(f"Unexpected error checking spaghetti detector state: {e}", exc_info=True)
            return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable spaghetti detection."""
        try:
            self.coordinator.get_model().spaghetti_detector.enable()
            self._attr_is_on = True
            self.async_write_ha_state()
        except AttributeError as e:
            LOGGER.error(f"Spaghetti detector not available: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error enabling spaghetti detection: {e}", exc_info=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable spaghetti detection."""
        try:
            self.coordinator.get_model().spaghetti_detector.disable()
            self._attr_is_on = False
            self.async_write_ha_state()
        except AttributeError as e:
            LOGGER.error(f"Spaghetti detector not available: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error disabling spaghetti detection: {e}", exc_info=True)


class BambuLabFTPSSwitch(BambuLabSwitch):
    """BambuLab FTPS Enable Switch"""

    entity_description = FTPS_SWITCH_DESCRIPTION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_is_on = self.coordinator.get_option_enabled(Options.FTPS)

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:folder-network" if self.is_on else "mdi:folder-network-outline"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable FTPS."""
        self._attr_is_on = True
        await self.coordinator.set_option_enabled(Options.FTPS, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable FTPS."""
        self._attr_is_on = False
        await self.coordinator.set_option_enabled(Options.FTPS, False)


class BambuLabIncognitoModeSwitch(BambuLabSwitch):
    """BambuLab Incognito Mode Switch"""

    entity_description = INCOGNITO_MODE_SWITCH_DESCRIPTION

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            config_entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, config_entry)
        self._attr_is_on = self.coordinator.get_option_enabled(Options.INCOGNITO_MODE)

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return "mdi:incognito" if self.is_on else "mdi:incognito-off"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable incognito mode."""
        self._attr_is_on = True
        await self.coordinator.set_option_enabled(Options.INCOGNITO_MODE, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable incognito mode."""
        self._attr_is_on = False
        await self.coordinator.set_option_enabled(Options.INCOGNITO_MODE, False)

