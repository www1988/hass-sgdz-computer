"""The SGDZ Computer Control integration."""
from __future__ import annotations

import logging
import json
import urllib.parse
import voluptuous as vol
import requests

from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
    DEFAULT_NAME,
    PLATFORMS,
    DEVICE_LIST_API_URL,
)

_LOGGER = logging.getLogger(__name__)

class SGDZComputerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SGDZ Computer Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # 验证账号密码并获取设备列表
                devices = await self.hass.async_add_executor_job(
                    self._get_device_list,
                    user_input[CONF_ACCOUNT],
                    user_input[CONF_PASSWORD],
                )
                
                if devices:
                    # 保存账号密码，进入设备选择步骤
                    self._account = user_input[CONF_ACCOUNT]
                    self._password = user_input[CONF_PASSWORD]
                    self._devices = devices
                    return await self.async_step_select_device()
                else:
                    errors["base"] = "no_devices"
            except Exception as ex:
                _LOGGER.error("Failed to connect: %s", ex)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCOUNT): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_device(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle device selection."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME],
                data={
                    CONF_ACCOUNT: self._account,
                    CONF_PASSWORD: self._password,
                    CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                },
            )

        device_names = [device["deviceName"] for device in self._devices]
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME): vol.In(device_names),
                }
            ),
            errors=errors,
        )

    def _get_device_list(self, account: str, password: str) -> list:
        """Get device list from API."""
        try:
            payload = {
                "sgdz_account": account,
                "sgdz_password": password,
                "type": "1"
            }
            
            encoded_data = urllib.parse.quote(json.dumps(payload))
            response = requests.post(DEVICE_LIST_API_URL, data=encoded_data)
            result = response.json()
            
            return result.get("deviceslist", [])
        except Exception as ex:
            _LOGGER.error("Error getting device list: %s", ex)
            raise

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SGDZ Computer Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok 