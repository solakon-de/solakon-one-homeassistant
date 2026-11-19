from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class ReadFailed(HomeAssistantError):
    """Error to indicate that no register could be read."""
