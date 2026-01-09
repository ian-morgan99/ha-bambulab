from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription, NumberDeviceClass, NumberMode
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    LOGGER,
    Options,
)

from .coordinator import BambuDataUpdateCoordinator
from .models import BambuLabEntity
from .pybambu.const import Features, TempEnum


@dataclass
class BambuLabNumberEntityDescriptionMixin:
    """Mixin for required keys."""
    value_fn: Callable[..., any]
    set_value_fn: Callable[..., Awaitable[None]]

@dataclass
class BambuLabNumberEntityDescription(NumberEntityDescription, BambuLabNumberEntityDescriptionMixin):
    """Sensor entity description for Bambu Lab."""


NUMBERS: tuple[BambuLabNumberEntityDescription, ...] = (
    BambuLabNumberEntityDescription(
        key="target_nozzle_temperature",
        translation_key="target_nozzle_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:printer-3d-nozzle",
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=320, # TODO: Determine by actual printer model
        native_step=1,
        value_fn=lambda self: self.coordinator.get_model().temperature.active_nozzle_target_temperature,
        set_value_fn=lambda self, value: self.coordinator.get_model().temperature.set_target_temp(TempEnum.NOZZLE, value),
    ),
    BambuLabNumberEntityDescription(
        key="target_bed_temperature",
        translation_key="target_bed_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=120,  # TODO: Determine by actual printer model and voltage
        native_step=1,
        value_fn=lambda self: self.coordinator.get_model().temperature.target_bed_temp,
        set_value_fn=lambda self, value: self.coordinator.get_model().temperature.set_target_temp(TempEnum.HEATBED, value),
    ),
)

# FTPS test parameter numbers (diagnostic)
FTPS_TEST_NUMBERS: tuple[BambuLabNumberEntityDescription, ...] = (
    BambuLabNumberEntityDescription(
        key="ftps_test_video_index",
        translation_key="ftps_test_video_index",
        icon="mdi:video",
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().print_job.ftps_test_video_index,
        set_value_fn=lambda self, value: setattr(self.coordinator.get_model().print_job, 'ftps_test_video_index', int(value)),
    ),
    BambuLabNumberEntityDescription(
        key="ftps_test_frame_offset",
        translation_key="ftps_test_frame_offset",
        icon="mdi:timer",
        mode=NumberMode.BOX,
        native_min_value=1,
        native_max_value=60,
        native_step=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().print_job.ftps_test_frame_offset,
        set_value_fn=lambda self, value: setattr(self.coordinator.get_model().print_job, 'ftps_test_frame_offset', int(value)),
    ),
    BambuLabNumberEntityDescription(
        key="ftps_test_image_index",
        translation_key="ftps_test_image_index",
        icon="mdi:image",
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().print_job.ftps_test_image_index,
        set_value_fn=lambda self, value: setattr(self.coordinator.get_model().print_job, 'ftps_test_image_index', int(value)),
    ),
)

# Spaghetti detection configuration numbers (diagnostic)
SPAGHETTI_DETECTION_NUMBERS: tuple[BambuLabNumberEntityDescription, ...] = (
    BambuLabNumberEntityDescription(
        key="spaghetti_edge_density_threshold",
        translation_key="spaghetti_edge_density_threshold",
        icon="mdi:gauge",
        mode=NumberMode.BOX,
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.01,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().spaghetti_detector.edge_density_threshold,
        set_value_fn=lambda self, value: self.coordinator.get_model().spaghetti_detector.set_edge_density_threshold(float(value)),
    ),
    BambuLabNumberEntityDescription(
        key="spaghetti_rate_threshold",
        translation_key="spaghetti_rate_threshold",
        icon="mdi:speedometer",
        mode=NumberMode.BOX,
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.01,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().spaghetti_detector.rate_threshold,
        set_value_fn=lambda self, value: self.coordinator.get_model().spaghetti_detector.set_rate_threshold(float(value)),
    ),
    BambuLabNumberEntityDescription(
        key="spaghetti_rate_window_size",
        translation_key="spaghetti_rate_window_size",
        icon="mdi:window-maximize",
        mode=NumberMode.BOX,
        native_min_value=3,
        native_max_value=20,
        native_step=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda self: self.coordinator.get_model().spaghetti_detector.rate_window_size,
        set_value_fn=lambda self, value: self.coordinator.get_model().spaghetti_detector.set_rate_window_size(int(value)),
    ),
    BambuLabNumberEntityDescription(
        key="spaghetti_pause_layer_threshold",
        translation_key="spaghetti_pause_layer_threshold",
        icon="mdi:layers",
        mode=NumberMode.BOX,
        native_min_value=1,
        native_max_value=20,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda self: self.coordinator.get_model().spaghetti_detector.pause_layer_threshold,
        set_value_fn=lambda self, value: self.coordinator.get_model().spaghetti_detector.set_pause_layer_threshold(int(value)),
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:

    coordinator: BambuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.get_model().has_full_printer_data:
        return
        
    LOGGER.debug("NUMBER::async_setup_entry")

    entities = []
    
    # Add FTPS test numbers (always available for diagnostics)
    for description in FTPS_TEST_NUMBERS:
        entities.append(BambuLabNumber(coordinator, description, entry))
    
    # Add spaghetti detection configuration numbers (always available for diagnostics)
    for description in SPAGHETTI_DETECTION_NUMBERS:
        entities.append(BambuLabNumber(coordinator, description, entry))
    
    # Add temperature control numbers if not blocked
    if not coordinator.get_model().info.is_hybrid_mode_blocking and not coordinator.get_model().print_fun.mqtt_signature_required:
        for description in NUMBERS:
            entities.append(BambuLabNumber(coordinator, description, entry))
    
    async_add_entities(entities)

    LOGGER.debug("NUMBER::async_setup_entry DONE")


class BambuLabNumber(BambuLabEntity, NumberEntity):
    """ Defined the Number"""
    entity_description: BambuLabNumberEntityDescription

    def __init__(
            self,
            coordinator: BambuDataUpdateCoordinator,
            description: BambuLabNumberEntityDescription,
            config_entry: ConfigEntry
    ) -> None:
        """Initialize the number."""
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.data['serial']}_{description.key}"
        self._attr_native_value = description.value_fn(self)

        super().__init__(coordinator=coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self.entity_description.value_fn(self)

    async def async_set_native_value(self, value: float) -> None:
        self.entity_description.set_value_fn(self, round(value))
