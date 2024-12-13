"""Support for SGDZ Computer Control switches."""
from __future__ import annotations

import logging
import json
import urllib.parse
import requests
from datetime import timedelta

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
    API_URL,
    DEVICE_LIST_API_URL,
    VALUE_SHUTDOWN,
    VALUE_STARTUP,
    VALUE_FORCE_SHUTDOWN,
    VALUE_FORCE_RESTART,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SGDZ Computer Control switch."""
    config = config_entry.data
    
    platform = entity_platform.async_get_current_platform()

    # 注册服务
    platform.async_register_entity_service(
        "force_shutdown",
        {},
        "async_force_shutdown",
    )

    platform.async_register_entity_service(
        "force_restart",
        {},
        "async_force_restart",
    )
    
    async_add_entities(
        [
            SGDZComputerSwitch(
                config[CONF_ACCOUNT],
                config[CONF_PASSWORD],
                config[CONF_DEVICE_NAME],
            )
        ],
        True,
    )

class SGDZComputerSwitch(SwitchEntity):
    """Representation of a SGDZ Computer Control switch."""

    def __init__(self, account, password, device_name):
        """Initialize the switch."""
        self._account = account
        self._password = password
        self._device_name = device_name
        self._is_on = False
        self._available = True
        self._attr_unique_id = f"{DOMAIN}_{account}_{device_name}"
        self._attr_name = device_name

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._attr_name,
            "manufacturer": "松果电子",
            "model": "Computer Control",
        }

    @property
    def name(self):
        """Return the name of the switch."""
        return self._attr_name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._is_on

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "device_name": self._device_name,
            "account": self._account,
            "status": "online" if self._available else "offline",
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if not self._available:
            return "mdi:desktop-classic-off"
        return "mdi:desktop-classic" if self._is_on else "mdi:desktop-classic-off"

    def _send_request(self, value: str) -> bool:
        """Send request to the API."""
        try:
            payload = {
                "sgdz_account": self._account,
                "sgdz_password": self._password,
                "device_name": self._device_name,
                "value": str(value)
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # URL 解码响应内容
            decoded_response = urllib.parse.unquote(response.text)
            _LOGGER.debug("Decoded Response: %s", decoded_response)
            
            # 解析 JSON
            result = json.loads(decoded_response)
            _LOGGER.debug("API Response: %s", result)
            
            status = result.get("status")
            if status == "0":
                return True
            elif status == "-2":
                _LOGGER.error("Authentication failed: Invalid account or password")
                self._available = False
            elif status == "-3":
                _LOGGER.error("Device not found: %s", self._device_name)
                self._available = False
            elif status == "2":
                _LOGGER.warning("Device is offline")
                self._available = False
            return False
            
        except Exception as e:
            _LOGGER.error("Error sending request: %s", str(e))
            self._available = False
            return False

    def _get_device_status(self) -> bool:
        """Get device status from device list API."""
        try:
            payload = {
                "sgdz_account": self._account,
                "sgdz_password": self._password,
                "type": "1"
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                DEVICE_LIST_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # URL 解码响应内容
            decoded_response = urllib.parse.unquote(response.text)
            result = json.loads(decoded_response)
            
            devices = result.get("deviceslist", [])
            for device in devices:
                if device.get("deviceName") == self._device_name:
                    status = device.get("status")
                    self._available = status != 2  # 如果状态为2则设备离线
                    self._is_on = status == 1  # 1表示开机
                    return True
            return False
        except Exception as e:
            _LOGGER.error("Error getting device status: %s", str(e))
            self._available = False
            return False

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        result = await self.hass.async_add_executor_job(
            self._send_request, VALUE_STARTUP
        )
        if result:
            self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        result = await self.hass.async_add_executor_job(
            self._send_request, VALUE_SHUTDOWN
        )
        if result:
            self._is_on = False

    async def async_update(self):
        """Update the switch status."""
        await self.hass.async_add_executor_job(self._get_device_status)

    async def async_force_shutdown(self):
        """Force shutdown the computer."""
        await self.hass.async_add_executor_job(
            self._send_request, VALUE_FORCE_SHUTDOWN
        )

    async def async_force_restart(self):
        """Force restart the computer."""
        await self.hass.async_add_executor_job(
            self._send_request, VALUE_FORCE_RESTART
        )

    def _fire_status_event(self, old_status, new_status):
        """Fire event when status changes."""
        self.hass.bus.fire(
            f"{DOMAIN}_status_change",
            {
                "entity_id": self.entity_id,
                "old_status": old_status,
                "new_status": new_status,
                "device_name": self._device_name,
            }
        )