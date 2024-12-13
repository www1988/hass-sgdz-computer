"""Constants for the SGDZ Computer Control integration."""
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    Platform,
)

DOMAIN = "sgdz_computer"

CONF_ACCOUNT = "sgdz_account"
CONF_PASSWORD = "sgdz_password"
CONF_DEVICE_NAME = "device_name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "Computer"
API_URL = "https://songguoyun.topwd.top/Esp_Api_new.php"
DEVICE_LIST_API_URL = "https://songguoyun.topwd.top/Esp_Api_advance.php"
DEFAULT_SCAN_INTERVAL = 30

# Value constants
VALUE_SHUTDOWN = 0
VALUE_STARTUP = 1
VALUE_FORCE_RESTART = 2
VALUE_CHECK_STATUS = 11
VALUE_FORCE_SHUTDOWN = 14

PLATFORMS = [Platform.SWITCH] 