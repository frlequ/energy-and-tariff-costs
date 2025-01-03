from homeassistant import config_entries
from .const import DOMAIN

class EnergyCostsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Costs."""
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user")
        return self.async_create_entry(title="Energy Costs", data={})
