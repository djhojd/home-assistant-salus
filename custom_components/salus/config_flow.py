"""Config flow for Salus Smart Home integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol
from pyit600.exceptions import IT600AuthenticationError, IT600ConnectionError
from pyit600.gateway import IT600Gateway

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_EUID, DEFAULT_EUID, DOMAIN

_LOGGER = logging.getLogger(__name__)

EUID_REGEX = re.compile(r"^[0-9a-fA-F]{16}$")


def validate_euid(euid: str) -> bool:
    """Validate EUID format."""
    return bool(EUID_REGEX.match(euid))


class SalusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Salus Smart Home."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            euid = user_input.get(CONF_EUID, DEFAULT_EUID)

            # Validate EUID format
            if not validate_euid(euid):
                errors["euid"] = "invalid_euid"
            else:
                # Try to connect to the gateway
                try:
                    gateway = IT600Gateway(host=host, euid=euid)
                    await gateway.connect()
                    await gateway.close()

                    # Check if already configured
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Salus Gateway ({host})",
                        data={
                            CONF_HOST: host,
                            CONF_EUID: euid,
                        },
                    )

                except IT600AuthenticationError:
                    errors["base"] = "invalid_euid"
                except IT600ConnectionError:
                    errors["base"] = "cannot_connect"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception during connection")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_EUID, default=DEFAULT_EUID): str,
                }
            ),
            errors=errors,
        )
