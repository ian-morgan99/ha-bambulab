"""Support for Bambu Lab text entities."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.text import (
    TextEntity,
    TextEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    LOGGER,
)

from .coordinator import BambuDataUpdateCoordinator
from .models import BambuLabEntity


@dataclass
class BambuLabTextEntityDescriptionMixin:
    """Mixin for required keys."""
    value_fn: Callable[..., str]
    set_value_fn: Callable[..., Awaitable[None]]


@dataclass
class BambuLabTextEntityDescription(TextEntityDescription, BambuLabTextEntityDescriptionMixin):
    """Text entity description for Bambu Lab."""


SPAGHETTI_DETECTION_TEXT: tuple[BambuLabTextEntityDescription, ...] = (
    BambuLabTextEntityDescription(
        key="spaghetti_external_camera_entity_id",
        translation_key="spaghetti_external_camera_entity_id",
        icon="mdi:camera-plus",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda self: self.coordinator.get_model().spaghetti_detector.external_camera_entity_id,
        set_value_fn=lambda self, value: self.coordinator.get_model().spaghetti_detector.set_external_camera_entity_id(value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bambu Lab text entities."""
    coordinator: BambuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.get_model().has_full_printer_data:
        return

    LOGGER.debug("TEXT::async_setup_entry")

    entities = []
    for description in SPAGHETTI_DETECTION_TEXT:
        entities.append(BambuLabTextEntity(coordinator, description))

    async_add_entities(entities)


class BambuLabTextEntity(BambuLabEntity, TextEntity):
    """Bambu Lab text entity."""

    entity_description: BambuLabTextEntityDescription

    def __init__(
        self,
        coordinator: BambuDataUpdateCoordinator,
        description: BambuLabTextEntityDescription,
    ) -> None:
        """Initialize the text entity."""
        self.entity_description = description
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"{coordinator.get_model().info.serial}_{description.key}"

    @property
    def native_value(self) -> str:
        """Return the current value."""
        return self.entity_description.value_fn(self)

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        await self.entity_description.set_value_fn(self, value)
        self.async_write_ha_state()
