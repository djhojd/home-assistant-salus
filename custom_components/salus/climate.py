"""Climate platform for Salus Smart Home integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SalusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Map pyit600 HVAC modes to Home Assistant
HVAC_MODE_MAP = {
    "heat": HVACMode.HEAT,
    "off": HVACMode.OFF,
    "auto": HVACMode.AUTO,
}

HVAC_MODE_REVERSE_MAP = {v: k for k, v in HVAC_MODE_MAP.items()}

# Map pyit600 HVAC actions to Home Assistant
HVAC_ACTION_MAP = {
    "heating": HVACAction.HEATING,
    "idle": HVACAction.IDLE,
    "off": HVACAction.OFF,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Salus climate entities from a config entry."""
    coordinator: SalusDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    climate_devices = coordinator.data.get("climate", {})

    entities = [
        SalusClimateEntity(coordinator, device_id, entry.entry_id)
        for device_id in climate_devices
    ]

    _LOGGER.debug("Adding %d climate entities", len(entities))
    async_add_entities(entities)


class SalusClimateEntity(CoordinatorEntity[SalusDataUpdateCoordinator], ClimateEntity):
    """Representation of a Salus thermostat."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
    )

    def __init__(
        self,
        coordinator: SalusDataUpdateCoordinator,
        device_id: str,
        entry_id: str,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._attr_unique_id = f"{entry_id}_{device_id}"

    @property
    def _device_data(self):
        """Get the current device data from coordinator."""
        return self.coordinator.data.get("climate", {}).get(self._device_id)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        device = self._device_data
        return device is not None and device.available

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        device = self._device_data
        if device:
            return device.name
        return f"Salus {self._device_id}"

    @property
    def device_info(self):
        """Return device information."""
        device = self._device_data
        name = device.name if device else f"Salus {self._device_id}"
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": name,
            "manufacturer": "Salus",
            "model": "IT600 Thermostat",
        }

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        device = self._device_data
        if device:
            return device.current_temperature
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        device = self._device_data
        if device:
            return device.target_temperature
        return None

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        device = self._device_data
        if device and hasattr(device, "min_temp"):
            return device.min_temp
        return 5.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        device = self._device_data
        if device and hasattr(device, "max_temp"):
            return device.max_temp
        return 35.0

    @property
    def target_temperature_step(self) -> float:
        """Return the temperature step."""
        return 0.5

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        device = self._device_data
        if device and hasattr(device, "hvac_mode"):
            return HVAC_MODE_MAP.get(device.hvac_mode, HVACMode.HEAT)
        return HVACMode.HEAT

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC modes."""
        return [HVACMode.HEAT, HVACMode.OFF]

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        device = self._device_data
        if device and hasattr(device, "hvac_action"):
            return HVAC_ACTION_MAP.get(device.hvac_action, HVACAction.IDLE)
        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        device = self._device_data
        if device and hasattr(device, "preset_mode"):
            return device.preset_mode
        return None

    @property
    def preset_modes(self) -> list[str] | None:
        """Return the list of available preset modes."""
        # Common preset modes for Salus thermostats
        return ["Permanent Hold", "Follow Schedule", "Off"]

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        _LOGGER.debug(
            "Setting temperature for %s to %s", self._device_id, temperature
        )
        await self.coordinator.async_set_temperature(self._device_id, temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        mode = HVAC_MODE_REVERSE_MAP.get(hvac_mode)
        if mode is None:
            _LOGGER.warning("Unsupported HVAC mode: %s", hvac_mode)
            return

        _LOGGER.debug("Setting HVAC mode for %s to %s", self._device_id, mode)
        await self.coordinator.async_set_hvac_mode(self._device_id, mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        _LOGGER.debug("Setting preset mode for %s to %s", self._device_id, preset_mode)
        await self.coordinator.async_set_preset_mode(self._device_id, preset_mode)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
