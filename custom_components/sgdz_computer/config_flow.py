"""Config flow for SGDZ Computer Control integration."""
from __future__ import annotations

import logging
import json
import urllib.parse
import voluptuous as vol
import requests

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
    DEFAULT_NAME,
    DEVICE_LIST_API_URL,
)

_LOGGER = logging.getLogger(__name__)

class SGDZComputerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
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
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 直接发送 JSON 数据
            response = requests.post(
                DEVICE_LIST_API_URL,
                json=payload,  # 使用 json 参数而不是 data
                headers=headers,
                timeout=10
            )
            
            # URL 解码响应内容
            decoded_response = urllib.parse.unquote(response.text)
            _LOGGER.debug("Decoded Response: %s", decoded_response)
            
            # 解析 JSON
            result = json.loads(decoded_response)
            _LOGGER.debug("API Response: %s", result)

            devices = result.get("deviceslist", [])
            if not devices:
                _LOGGER.warning("No devices found in response: %s", result)
            
            return devices

        except Exception as ex:
            _LOGGER.error("Error getting device list: %s", ex)
            _LOGGER.debug("Request payload: %s", payload)
            raise