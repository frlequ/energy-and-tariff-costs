# number.py

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from .const import (
    DOMAIN, INITIALS, VT_PRICE, MT_PRICE, TAX, ADDITIONAL_PRICE,
    BLOK_1_CONS_PRICE, BLOK_2_CONS_PRICE, BLOK_3_CONS_PRICE, BLOK_4_CONS_PRICE, BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE, BLOK_2_TAR_PRICE, BLOK_3_TAR_PRICE, BLOK_4_TAR_PRICE, BLOK_5_TAR_PRICE
)

def friendly_name_from_id(name: str) -> str:
    return name.replace("_", " ").title()

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    data = hass.data[DOMAIN][entry.entry_id]
    device_identifiers = data["device_identifiers"]

    to_create = [
        (VT_PRICE, data[VT_PRICE]),
        (MT_PRICE, data[MT_PRICE]),
        (TAX, data[TAX]),
        (ADDITIONAL_PRICE, data[ADDITIONAL_PRICE]),
        (BLOK_1_CONS_PRICE, data[BLOK_1_CONS_PRICE]),
        (BLOK_2_CONS_PRICE, data[BLOK_2_CONS_PRICE]),
        (BLOK_3_CONS_PRICE, data[BLOK_3_CONS_PRICE]),
        (BLOK_4_CONS_PRICE, data[BLOK_4_CONS_PRICE]),
        (BLOK_5_CONS_PRICE, data[BLOK_5_CONS_PRICE]),
        (BLOK_1_TAR_PRICE, data[BLOK_1_TAR_PRICE]),
        (BLOK_2_TAR_PRICE, data[BLOK_2_TAR_PRICE]),
        (BLOK_3_TAR_PRICE, data[BLOK_3_TAR_PRICE]),
        (BLOK_4_TAR_PRICE, data[BLOK_4_TAR_PRICE]),
        (BLOK_5_TAR_PRICE, data[BLOK_5_TAR_PRICE]),
    ]

    entities = [
        EnergyCostNumber(entry, name, initial, device_identifiers)
        for name, initial in to_create
    ]

    async_add_entities(entities, True)

class EnergyCostNumber(NumberEntity, RestoreEntity):
    def __init__(
        self,
        entry: ConfigEntry,
        name: str,
        initial_value: float,
        device_identifiers
    ):
        self._entry = entry
        self._name_id = name
        self.entity_id = f"number.{INITIALS}_{name}"
        self._initial_value = initial_value
        self._state = None  # Will set on async_added_to_hass
        self._device_identifiers = device_identifiers

        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._attr_name = friendly_name_from_id(name)
        self._attr_mode = NumberMode.BOX
        self._attr_min_value = 0.0
        self._attr_max_value = 10.0
        self._attr_step = 0.0001
        self._attr_icon = "mdi:currency-eur"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # Try to restore the previous state
        old_state = await self.async_get_last_state()
        if old_state and old_state.state not in (None, "unknown", "unavailable"):
            try:
                self._state = float(old_state.state)
            except ValueError:
                self._state = self._initial_value
        else:
            # No old state, use initial value
            self._state = self._initial_value

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {self._device_identifiers},
            "name": "Energy & Tariff Costs",
            "manufacturer": "Energy & Tariff Costs",
            "model": "Beta",
        }

    async def async_set_native_value(self, value: float):
        """Set the new value."""
        self._state = value
        self.async_write_ha_state()
        # Here you can add any additional logic needed when the value is set,
        # such as updating `hass.data` or interacting with other components.

    # Optional: If you prefer to use async_set_value instead of async_set_native_value
    async def async_set_value(self, value: float):
        """Set the new value."""
        await self.async_set_native_value(value)
