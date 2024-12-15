from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from .const import (
    DOMAIN, VT_PRICE, MT_PRICE, TAX,
    BLOK_1_CONS_PRICE, BLOK_2_CONS_PRICE, BLOK_3_CONS_PRICE, BLOK_4_CONS_PRICE, BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE, BLOK_2_TAR_PRICE, BLOK_3_TAR_PRICE, BLOK_4_TAR_PRICE, BLOK_5_TAR_PRICE
)

def friendly_name_from_id(name: str) -> str:
    return name.replace("_", " ").title()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    device_identifiers = data["device_identifiers"]


    to_create = [
        (VT_PRICE, data["vt_price_initial"]),
        (MT_PRICE, data["mt_price_initial"]),
        (TAX, data["tax_initial"]),

        (BLOK_1_CONS_PRICE, data["blok_1_consumption_price_initial"]),
        (BLOK_2_CONS_PRICE, data["blok_2_consumption_price_initial"]),
        (BLOK_3_CONS_PRICE, data["blok_3_consumption_price_initial"]),
        (BLOK_4_CONS_PRICE, data["blok_4_consumption_price_initial"]),
        (BLOK_5_CONS_PRICE, data["blok_5_consumption_price_initial"]),

        (BLOK_1_TAR_PRICE, data["blok_1_tariff_price_initial"]),
        (BLOK_2_TAR_PRICE, data["blok_2_tariff_price_initial"]),
        (BLOK_3_TAR_PRICE, data["blok_3_tariff_price_initial"]),
        (BLOK_4_TAR_PRICE, data["blok_4_tariff_price_initial"]),
        (BLOK_5_TAR_PRICE, data["blok_5_tariff_price_initial"])
    ]

    entities = [
        EnergyCostNumber(entry, name, initial, device_identifiers)
        for name, initial in to_create
    ]

    async_add_entities(entities, True)

class EnergyCostNumber(NumberEntity, RestoreEntity):
    def __init__(self, entry: ConfigEntry, name: str, initial_value: float, device_identifiers):
        self._entry = entry
        self._name_id = name
        self._initial_value = initial_value
        self._state = None  # Will set on async_added_to_hass
        self._device_identifiers = device_identifiers

        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._attr_name = friendly_name_from_id(name)
        self._attr_mode = NumberMode.BOX
        self._attr_min_value = 0.0
        self._attr_max_value = 10.0
        self._attr_step = 0.0001

        # Don't set self._state here; wait for restore or fallback to initial value in async_added_to_hass

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
    def state(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {self._device_identifiers},
            "name": "Energy & Tariff Costs",
            "manufacturer": "Energy & Tariff Costs",
            "model": "Beta",
        }

    async def async_set_value(self, value: float):
        self._state = value
        self.async_write_ha_state()
