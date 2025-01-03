from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from .const import (
    DOMAIN, VT_PRICE, MT_PRICE, TAX,
    BLOK_1_CONS_PRICE, BLOK_2_CONS_PRICE, BLOK_3_CONS_PRICE, BLOK_4_CONS_PRICE, BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE, BLOK_2_TAR_PRICE, BLOK_3_TAR_PRICE, BLOK_4_TAR_PRICE, BLOK_5_TAR_PRICE
)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_registry = dr.async_get(hass)
    identifiers = (DOMAIN, entry.entry_id)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={identifiers},
        name="Energy Costs Device",
        manufacturer="Test Manufacturer",
        model="Test Model"
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_identifiers": identifiers,
        "vt_price_initial": 0.084000,
        "mt_price_initial": 0.070000,
        "tax_initial": 22.0,
        "additional_price_initial": 1.96,

        "blok_1_consumption_price_initial": 0.019580,
        "blok_2_consumption_price_initial": 0.018440,
        "blok_3_consumption_price_initial": 0.018370,
        "blok_4_consumption_price_initial": 0.018380,
        "blok_5_consumption_price_initial": 0.0,

        "blok_1_tariff_price_initial": 3.613240,
        "blok_2_tariff_price_initial": 0.882400,
        "blok_3_tariff_price_initial": 0.191370,
        "blok_4_tariff_price_initial": 0.013160,
        "blok_5_tariff_price_initial": 0.0,
    }

    await hass.config_entries.async_forward_entry_setup(entry, "number")
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "number")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
