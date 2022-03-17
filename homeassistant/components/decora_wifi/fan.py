"""Interfaces with the myLeviton API for Decora Smart WiFi products."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import BaseDecoraWifiEntity, EntityTypes, _setup_platform

_LOGGER = logging.getLogger(__name__)


class DecoraWifiFanController(BaseDecoraWifiEntity, FanEntity):
    """Encapsulates functionality specific to Decora WiFi fan controllers."""

    PERCENTAGE_ATTRIB_KEY = "brightness"

    @property
    def speed_count(self) -> int:
        """Return the number of supported non-zero speeds."""

        return 4

    @property
    def supported_features(self) -> int:
        """Return supported features."""

        if self._switch.canSetLevel:
            return SUPPORT_SET_SPEED
        return 0

    @property
    def percentage(self) -> int:
        """Return the current percentage."""

        return int(self._switch.brightness)

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Turn the fan on."""

        attribs: dict[str, Any] = {"power": "ON"}

        if percentage is not None:
            attribs[self.PERCENTAGE_ATTRIB_KEY] = self._get_valid_percentage(percentage)

        try:
            self._switch.update_attributes(attribs)
        except ValueError:
            _LOGGER.error("Failed to turn on myLeviton switch")

    def set_percentage(self, percentage: int) -> None:
        """Update the fan's speed."""

        percentage = self._get_valid_percentage(percentage)
        if percentage == 0:
            self.turn_off()
        else:
            self.turn_on(percentage=percentage)

    def _get_valid_percentage(self, percentage: int) -> int:
        """Get the nearest valid fan speed."""

        return int(self.percentage_step * round(percentage / self.percentage_step))


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decora fan controllers."""

    await hass.async_add_executor_job(
        _setup_platform,
        EntityTypes.FAN,
        DecoraWifiFanController,
        hass,
        config_entry,
        async_add_entities,
    )
