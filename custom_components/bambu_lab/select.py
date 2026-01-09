"""Support for Bambu Lab through MQTT."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.select import SelectEntity

from .const import DOMAIN, LOGGER
from .pybambu.const import Features, SPEED_PROFILE
from .coordinator import BambuDataUpdateCoordinator
from .models import BambuLabEntity


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BambuLab sensor based on a config entry."""

    coordinator: BambuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.get_model().has_full_printer_data:
        return
    
    LOGGER.debug("SELECT::async_setup_entry")
    entities = []
    
    # Unsure if hybrid mode also blocks speed control.
    if not coordinator.get_model().print_fun.mqtt_signature_required:
        entities.append(BambuLabSpeedSelect(coordinator))
    
    # Add external camera select for spaghetti detection
    entities.append(BambuLabExternalCameraSelect(coordinator, hass))
    
    async_add_entities(entities)


class BambuLabSpeedSelect(BambuLabEntity, SelectEntity):
    """Speed select options."""

    _attr_icon = "mdi:speedometer"
    _attr_translation_key = "printing_speed"

    def __init__(self, coordinator: BambuDataUpdateCoordinator) -> None:
        """Initialize Speed Select."""
        super().__init__(coordinator=coordinator)
        printer = self.coordinator.get_model().info
        self._attr_unique_id = f"{printer.serial}_Speed"
        self._attr_options = [
            speed for i, speed in SPEED_PROFILE.items()
        ]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.get_model().print_job.gcode_state == 'RUNNING'

    @property
    def current_option(self) -> str:
        """Return the current selected live override."""
        return self.coordinator.get_model().speed.name

    async def async_select_option(self, option: str) -> None:
        """Set print speed."""
        self.coordinator.get_model().speed.SetSpeed(option)


class BambuLabExternalCameraSelect(BambuLabEntity, SelectEntity):
    """External camera select for spaghetti detection."""

    _attr_icon = "mdi:camera-plus"
    _attr_translation_key = "spaghetti_external_camera"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: BambuDataUpdateCoordinator, hass: HomeAssistant) -> None:
        """Initialize External Camera Select."""
        super().__init__(coordinator=coordinator)
        self._hass = hass
        printer = self.coordinator.get_model().info
        self._attr_unique_id = f"{printer.serial}_external_camera"
        
        # Start with minimal options - will be populated lazily
        self._attr_options = ["Built-in Chamber Camera"]
        self._options_loaded = False

    def _update_options(self) -> None:
        """Update the list of available camera options."""
        # Get all camera and image entities from Home Assistant
        camera_entities = []
        if self._hass and self._hass.states:
            for state in self._hass.states.async_all():
                if state.domain in ["camera", "image"]:
                    camera_entities.append(state.entity_id)
        
        # Sort camera entities and prepend built-in option
        self._attr_options = ["Built-in Chamber Camera"] + sorted(camera_entities)
        self._options_loaded = True

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        # Lazy load options on first access
        if not self._options_loaded:
            self._update_options()
        return self._attr_options

    @property
    def current_option(self) -> str:
        """Return the current selected camera."""
        external_camera = self.coordinator.get_model().spaghetti_detector.external_camera_entity_id
        if external_camera:
            return external_camera
        return "Built-in Chamber Camera"

    async def async_select_option(self, option: str) -> None:
        """Set the external camera."""
        if option == "Built-in Chamber Camera":
            # Clear external camera to use built-in
            self.coordinator.get_model().spaghetti_detector.set_external_camera_entity_id("")
        else:
            # Set the selected camera entity
            self.coordinator.get_model().spaghetti_detector.set_external_camera_entity_id(option)
        
        self.async_write_ha_state()