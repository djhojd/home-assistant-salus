"""Data update coordinator for Salus Smart Home."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import async_timeout
from pyit600.exceptions import IT600AuthenticationError, IT600ConnectionError
from pyit600.gateway import IT600Gateway

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SalusDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Salus data from the gateway."""

    def __init__(self, hass: HomeAssistant, host: str, euid: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._host = host
        self._euid = euid
        self._gateway: IT600Gateway | None = None

    @property
    def gateway(self) -> IT600Gateway | None:
        """Return the gateway instance."""
        return self._gateway

    async def _async_setup(self) -> None:
        """Set up the coordinator - called during first refresh."""
        _LOGGER.debug("Connecting to Salus gateway at %s", self._host)
        self._gateway = IT600Gateway(host=self._host, euid=self._euid)
        try:
            await self._gateway.connect()
            _LOGGER.debug("Successfully connected to Salus gateway")
        except IT600AuthenticationError as err:
            raise ConfigEntryAuthFailed("Authentication failed - check EUID") from err
        except IT600ConnectionError as err:
            raise UpdateFailed(f"Failed to connect to gateway: {err}") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the gateway."""
        if self._gateway is None:
            await self._async_setup()

        try:
            async with async_timeout.timeout(30):
                await self._gateway.poll_status()

                # Gather all device data
                climate_devices = self._gateway.get_climate_devices()

                _LOGGER.debug("Polled %d climate devices", len(climate_devices))

                return {
                    "climate": climate_devices,
                }

        except IT600AuthenticationError as err:
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except IT600ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with gateway: {err}") from err

    async def async_close(self) -> None:
        """Close the gateway connection."""
        if self._gateway is not None:
            await self._gateway.close()
            self._gateway = None
            _LOGGER.debug("Closed connection to Salus gateway")

    async def async_set_temperature(self, device_id: str, temperature: float) -> None:
        """Set the target temperature for a device."""
        if self._gateway is None:
            raise UpdateFailed("Gateway not connected")

        try:
            await self._gateway.set_climate_device_temperature(device_id, temperature)
            # Request an immediate refresh after setting temperature
            await self.async_request_refresh()
        except Exception as err:
            raise UpdateFailed(f"Failed to set temperature: {err}") from err

    async def async_set_hvac_mode(self, device_id: str, hvac_mode: str) -> None:
        """Set the HVAC mode for a device."""
        if self._gateway is None:
            raise UpdateFailed("Gateway not connected")

        try:
            await self._gateway.set_climate_device_mode(device_id, hvac_mode)
            await self.async_request_refresh()
        except Exception as err:
            raise UpdateFailed(f"Failed to set HVAC mode: {err}") from err

    async def async_set_preset_mode(self, device_id: str, preset_mode: str) -> None:
        """Set the preset mode for a device."""
        if self._gateway is None:
            raise UpdateFailed("Gateway not connected")

        try:
            await self._gateway.set_climate_device_preset(device_id, preset_mode)
            await self.async_request_refresh()
        except Exception as err:
            raise UpdateFailed(f"Failed to set preset mode: {err}") from err
