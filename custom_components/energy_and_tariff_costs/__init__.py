# __init__.py

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from .const import (
    DOMAIN,
    VT_PRICE,
    MT_PRICE,
    TAX,
    ADDITIONAL_PRICE,
    BLOK_1_CONS_PRICE,
    BLOK_2_CONS_PRICE,
    BLOK_3_CONS_PRICE,
    BLOK_4_CONS_PRICE,
    BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE,
    BLOK_2_TAR_PRICE,
    BLOK_3_TAR_PRICE,
    BLOK_4_TAR_PRICE,
    BLOK_5_TAR_PRICE,
    VT_PRICE_INITIAL,
    MT_PRICE_INITIAL,
    TAX_INITIAL,
    ADDITIONAL_PRICE_INITIAL,
    BLOK_1_CONS_PRICE_INITIAL,
    BLOK_2_CONS_PRICE_INITIAL,
    BLOK_3_CONS_PRICE_INITIAL,
    BLOK_4_CONS_PRICE_INITIAL,
    BLOK_5_CONS_PRICE_INITIAL,
    BLOK_1_TAR_PRICE_INITIAL,
    BLOK_2_TAR_PRICE_INITIAL,
    BLOK_3_TAR_PRICE_INITIAL,
    BLOK_4_TAR_PRICE_INITIAL,
    BLOK_5_TAR_PRICE_INITIAL,
)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_registry = dr.async_get(hass)
    identifiers = (DOMAIN, entry.entry_id)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={identifiers},
        name="Energy & Tariff Costs",
        manufacturer="Energy & Tariff Costs",
        model="Beta"
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_identifiers": identifiers,
        VT_PRICE: VT_PRICE_INITIAL,
        MT_PRICE: MT_PRICE_INITIAL,
        TAX: TAX_INITIAL,
        ADDITIONAL_PRICE: ADDITIONAL_PRICE_INITIAL,

        BLOK_1_CONS_PRICE: BLOK_1_CONS_PRICE_INITIAL,
        BLOK_2_CONS_PRICE: BLOK_2_CONS_PRICE_INITIAL,
        BLOK_3_CONS_PRICE: BLOK_3_CONS_PRICE_INITIAL,
        BLOK_4_CONS_PRICE: BLOK_4_CONS_PRICE_INITIAL,
        BLOK_5_CONS_PRICE: BLOK_5_CONS_PRICE_INITIAL,

        BLOK_1_TAR_PRICE: BLOK_1_TAR_PRICE_INITIAL,
        BLOK_2_TAR_PRICE: BLOK_2_TAR_PRICE_INITIAL,
        BLOK_3_TAR_PRICE: BLOK_3_TAR_PRICE_INITIAL,
        BLOK_4_TAR_PRICE: BLOK_4_TAR_PRICE_INITIAL,
        BLOK_5_TAR_PRICE: BLOK_5_TAR_PRICE_INITIAL,
    }

    await hass.config_entries.async_forward_entry_setup(entry, "number")
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "number")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
