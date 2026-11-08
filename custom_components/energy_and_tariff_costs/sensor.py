# sensor.py

import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Tuple

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import statistic_during_period
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, INITIALS, VT_PRICE, MT_PRICE, TAX, ADDITIONAL_PRICE, CONTRIB_PRICE,
    BLOK_1_CONS_PRICE, BLOK_2_CONS_PRICE, BLOK_3_CONS_PRICE, BLOK_4_CONS_PRICE, BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE, BLOK_2_TAR_PRICE, BLOK_3_TAR_PRICE, BLOK_4_TAR_PRICE, BLOK_5_TAR_PRICE,
    MOJELEKTRO_PEAK, MOJELEKTRO_OFFPEAK,
    MOJELEKTRO_BLOK_1, MOJELEKTRO_BLOK_2, MOJELEKTRO_BLOK_3, MOJELEKTRO_BLOK_4, MOJELEKTRO_BLOK_5,
    MOJELEKTRO_DAILY_BLOK_1, MOJELEKTRO_DAILY_BLOK_2, MOJELEKTRO_DAILY_BLOK_3, MOJELEKTRO_DAILY_BLOK_4, MOJELEKTRO_DAILY_BLOK_5
)


SCAN_INTERVAL = timedelta(hours=1)

DAILY_SENSOR_PREFIX = "sensor.moj_elektro_daily_input_"

# Months in the "higher season" (winter) of the network tariff calendar.
# Winter bills blocks 1-4, the lower season (summer) bills blocks 2-5.
WINTER_MONTHS = {11, 12, 1, 2}

_LOGGER = logging.getLogger(__name__)


def friendly_name_from_id(name: str) -> str:
    """Convert an entity ID to a friendly name."""
    return name.replace("_", " ").title()


def billing_window(now: Optional[datetime] = None) -> Tuple[datetime, datetime, datetime]:
    """Return (reference_date, start, end) of the billing month whose data is arriving now.

    Moj Elektro delivers day D's data on day D+1 (around 06:00), and the
    monthly peak/offpeak sensors roll over on the 2nd. So:
      * the month being billed is the month of (now - 1 day),
      * its block data arrives from the 2nd of that month 00:00
        until the 2nd of the next month 00:00.
    Example: at 1 Oct 07:00 this returns September, window 2 Sep 00:00 - now,
    which already includes 30 Sep's data.
    """
    now = now or dt_util.now()
    ref = now - timedelta(days=1)
    month_start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (month_start + timedelta(days=32)).replace(day=1)
    start = month_start + timedelta(days=1)
    end = min(now, next_month_start + timedelta(days=1))
    return ref, start, end


def active_blocks(now: Optional[datetime] = None) -> set:
    """Return which network-tariff blocks are billed for the current billing month."""
    ref, _, _ = billing_window(now)
    if ref.month in WINTER_MONTHS:
        return {1, 2, 3, 4}
    return {2, 3, 4, 5}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    """Set up sensors from a config entry."""
    _LOGGER.debug("Setting up entry for domain %s with entry ID %s", DOMAIN, entry.entry_id)
    data = hass.data[DOMAIN][entry.entry_id]
    device_identifiers = data["device_identifiers"]

    # Energy (supplier) cost sensors
    vt_sensor = SimpleCostSensor(
        hass, entry, "energy_high_tariff_cost", device_identifiers,
        consumption_sensor=MOJELEKTRO_PEAK, price_name=VT_PRICE, tax_name=TAX,
        cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
    )
    mt_sensor = SimpleCostSensor(
        hass, entry, "energy_low_tariff_cost", device_identifiers,
        consumption_sensor=MOJELEKTRO_OFFPEAK, price_name=MT_PRICE, tax_name=TAX,
        cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
    )

    # Network tariff (agreed power) sensors. All 5 blocks are always created;
    # TotalCostSensor decides which ones are billed this month.
    tariff_definitions = [
        ("blok_1_tariff_cost", MOJELEKTRO_BLOK_1, BLOK_1_TAR_PRICE),
        ("blok_2_tariff_cost", MOJELEKTRO_BLOK_2, BLOK_2_TAR_PRICE),
        ("blok_3_tariff_cost", MOJELEKTRO_BLOK_3, BLOK_3_TAR_PRICE),
        ("blok_4_tariff_cost", MOJELEKTRO_BLOK_4, BLOK_4_TAR_PRICE),
        ("blok_5_tariff_cost", MOJELEKTRO_BLOK_5, BLOK_5_TAR_PRICE),
    ]
    tariff_sensors = [
        SimpleCostSensor(
            hass, entry, name, device_identifiers,
            consumption_sensor=consumption_sensor, price_name=price_name, tax_name=TAX,
            cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
        ) for (name, consumption_sensor, price_name) in tariff_definitions
    ]

    # Network consumption sensors (monthly kWh per block, from statistics)
    consumption_defs = [
        ("blok_1_consumption_cost", MOJELEKTRO_DAILY_BLOK_1, BLOK_1_CONS_PRICE),
        ("blok_2_consumption_cost", MOJELEKTRO_DAILY_BLOK_2, BLOK_2_CONS_PRICE),
        ("blok_3_consumption_cost", MOJELEKTRO_DAILY_BLOK_3, BLOK_3_CONS_PRICE),
        ("blok_4_consumption_cost", MOJELEKTRO_DAILY_BLOK_4, BLOK_4_CONS_PRICE),
        ("blok_5_consumption_cost", MOJELEKTRO_DAILY_BLOK_5, BLOK_5_CONS_PRICE),
    ]
    consumption_sensors = [
        SimpleCostSensor(
            hass, entry, name, device_identifiers,
            consumption_sensor=daily_sensor, price_name=price_name, tax_name=TAX,
            cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
        ) for (name, daily_sensor, price_name) in consumption_defs
    ]

    # Fixed monthly costs (OVE/SPTE + monthly fee - discounts)
    additional_cost_sensor = AdditionalCostSensor(
        hass, entry, "additional_cost", device_identifiers,
        price_name=ADDITIONAL_PRICE, tax_name=TAX
    )

    # Per-kWh contributions on total consumption (market operator,
    # energy efficiency, excise)
    contributions_sensor = ContributionsCostSensor(
        hass, entry, "contributions_cost", device_identifiers,
        consumption_sensors=[MOJELEKTRO_PEAK, MOJELEKTRO_OFFPEAK],
        price_name=CONTRIB_PRICE, tax_name=TAX
    )

    # Sensors that are ALWAYS included in the total, regardless of season
    always_sensors = [vt_sensor, mt_sensor, additional_cost_sensor, contributions_sensor]

    # Block sensors tagged with their block number (1-5)
    block_sensors = [
        (1, tariff_sensors[0]), (2, tariff_sensors[1]), (3, tariff_sensors[2]),
        (4, tariff_sensors[3]), (5, tariff_sensors[4]),
        (1, consumption_sensors[0]), (2, consumption_sensors[1]), (3, consumption_sensors[2]),
        (4, consumption_sensors[3]), (5, consumption_sensors[4]),
    ]

    total_sensor = TotalCostSensor(
        hass, entry, "total_cost", device_identifiers, always_sensors, block_sensors
    )

    async_add_entities(
        [vt_sensor, mt_sensor, total_sensor] + tariff_sensors + consumption_sensors
        + [additional_cost_sensor, contributions_sensor],
        True
    )
    _LOGGER.info("Added all cost sensors to Home Assistant")


class BaseCostSensor(SensorEntity):
    """Base class with shared helpers for all cost sensors."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        device_identifiers: List[str]
    ):
        super().__init__()
        self._hass = hass
        self._entry = entry
        self._entity_name = name  # e.g. "blok_1_tariff_cost"
        self.entity_id = f"sensor.{INITIALS}_{name}"  # e.g. "sensor.etc_blok_1_tariff_cost"
        self._attr_name = friendly_name_from_id(name)
        self._attr_unique_id = f"{entry.entry_id}_etc_{name}"
        self._device_identifiers = device_identifiers
        self._state: Optional[float] = None
        self._attr_unit_of_measurement = "€"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:currency-eur"

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def object_id(self) -> str:
        return self._entity_name.lower()

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {tuple(self._device_identifiers)},
            "name": "Energy & Tariff Costs",
            "manufacturer": "Energy & Tariff Costs",
            "model": "Beta",
        }

    @property
    def state(self) -> Optional[float]:
        return self._state

    def _valid_state(self, state) -> bool:
        return state is not None and state.state not in (None, "unknown", "unavailable")

    def _get_number_value(self, name: str) -> Optional[float]:
        """Retrieve a numeric value from one of this integration's number entities."""
        entity_id = self._find_entity_id(name)
        if not entity_id:
            _LOGGER.warning("Entity ID not found for name: %s", name)
            return None
        s = self._hass.states.get(entity_id)
        if s is None or s.state in (None, "unknown", "unavailable"):
            return None
        try:
            return float(s.state)
        except ValueError:
            _LOGGER.error("Invalid state value for %s: %s", name, s.state)
            return None

    def _find_entity_id(self, name: str) -> Optional[str]:
        """Find the entity ID of a number entity by its unique ID."""
        registry = er.async_get(self._hass)
        return registry.async_get_entity_id("number", DOMAIN, f"{self._entry.entry_id}_{name}")

    def _get_sensor_float(self, entity_id: str) -> Optional[float]:
        state = self._hass.states.get(entity_id)
        if not self._valid_state(state):
            return None
        try:
            return float(state.state)
        except ValueError:
            _LOGGER.error("Invalid state value for %s: %s", entity_id, state.state)
            return None

    async def _get_monthly_sum_if_daily_sensor(self, sensor_id: str) -> Optional[float]:
        """Monthly kWh of a daily Moj Elektro sensor, read from long-term statistics.

        Returns None if sensor_id is not a daily sensor (caller then uses its
        state directly). Statistics are used instead of state history because
        they survive recorder purging and already handle the midnight resets
        of total_increasing sensors.
        """
        if not sensor_id.startswith(DAILY_SENSOR_PREFIX):
            return None

        _, start, end = billing_window()
        if end <= start:
            return 0.0

        try:
            stats = await get_instance(self._hass).async_add_executor_job(
                statistic_during_period,
                self._hass, start, end, sensor_id, {"change"}, None,
            )
        except Exception as e:
            _LOGGER.error("Statistics query failed for %s: %s", sensor_id, e)
            return None

        change = stats.get("change") if stats else None
        _LOGGER.debug(
            "Monthly change for %s (%s - %s): %s kWh", sensor_id, start, end, change
        )
        return float(change) if change is not None else 0.0


class SimpleCostSensor(BaseCostSensor):
    """Cost = consumption x price x (1 + tax)."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        device_identifiers,
        consumption_sensor: str,
        price_name: str,
        tax_name: str,
        cost_formula: Callable
    ):
        super().__init__(hass, entry, name, device_identifiers)
        self._consumption_sensor = consumption_sensor
        self._price_name = price_name
        self._tax_name = tax_name
        self._cost_formula = cost_formula

    async def async_update(self):
        monthly_sum = await self._get_monthly_sum_if_daily_sensor(self._consumption_sensor)
        if monthly_sum is not None:
            consumption = monthly_sum
        elif self._consumption_sensor.startswith(DAILY_SENSOR_PREFIX):
            # Daily sensor whose statistics query failed
            self._state = None
            return
        else:
            consumption = self._get_sensor_float(self._consumption_sensor)
            if consumption is None:
                _LOGGER.warning("Invalid consumption state for sensor %s", self._consumption_sensor)
                self._state = None
                return

        price = self._get_number_value(self._price_name)
        tax = self._get_number_value(self._tax_name)
        if price is None or tax is None:
            # Normal right after startup, before number entities restored their value
            self._state = None
            return

        try:
            self._state = round(self._cost_formula(consumption, price, tax), 4)
        except Exception as e:
            _LOGGER.error("Error calculating cost for sensor %s: %s", self._attr_unique_id, e)
            self._state = None


class AdditionalCostSensor(BaseCostSensor):
    """Fixed monthly price with tax."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        device_identifiers,
        price_name: str,
        tax_name: str
    ):
        super().__init__(hass, entry, name, device_identifiers)
        self._price_name = price_name
        self._tax_name = tax_name

    async def async_update(self):
        price = self._get_number_value(self._price_name)
        tax = self._get_number_value(self._tax_name)
        if price is None or tax is None:
            self._state = None
            return
        self._state = round(price * (1 + tax / 100), 4)


class ContributionsCostSensor(BaseCostSensor):
    """Per-kWh contributions on total monthly consumption (sum of several sensors)."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        device_identifiers,
        consumption_sensors: List[str],
        price_name: str,
        tax_name: str
    ):
        super().__init__(hass, entry, name, device_identifiers)
        self._consumption_sensors = consumption_sensors
        self._price_name = price_name
        self._tax_name = tax_name

    async def async_update(self):
        total_kwh = 0.0
        for sensor_id in self._consumption_sensors:
            value = self._get_sensor_float(sensor_id)
            if value is None:
                _LOGGER.warning("Invalid consumption state for sensor %s", sensor_id)
                self._state = None
                return
            total_kwh += value

        price = self._get_number_value(self._price_name)
        tax = self._get_number_value(self._tax_name)
        if price is None or tax is None:
            self._state = None
            return
        self._state = round(total_kwh * price * (1 + tax / 100), 4)


class TotalCostSensor(SensorEntity):
    """Sum of all cost sensors, billing only the blocks active for the billing month
    (winter: blocks 1-4, summer: blocks 2-5)."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        name: str,
        device_identifiers,
        always_sensors,
        block_sensors,
    ):
        self._hass = hass
        self._entry = entry
        self._entity_name = name
        self.entity_id = f"sensor.{INITIALS}_{name}"
        self._attr_name = friendly_name_from_id(name)
        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._device_identifiers = device_identifiers
        self._always_sensors = always_sensors
        self._block_sensors = block_sensors  # list of (block_number, sensor)
        self._attr_unit_of_measurement = "€"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self._attr_icon = "mdi:currency-eur"
        self._active = set()

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        ref, start, end = billing_window()
        return {
            "billing_month": ref.strftime("%Y-%m"),
            "active_blocks": sorted(self._active),
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {self._device_identifiers},
            "name": "Energy & Tariff Costs",
            "manufacturer": "Energy & Tariff Costs",
            "model": "Beta",
        }

    async def async_update(self):
        # Refresh everything so all sensors (also inactive blocks) stay current
        for sensor in self._always_sensors:
            await sensor.async_update()
        for _, sensor in self._block_sensors:
            await sensor.async_update()

        self._active = active_blocks()

        costs = [sensor.state for sensor in self._always_sensors]
        costs += [
            sensor.state
            for block_num, sensor in self._block_sensors
            if block_num in self._active
        ]

        if any(c is None for c in costs):
            _LOGGER.warning("One or more cost sensors have no value; total not calculated")
            self._state = None
        else:
            self._state = round(sum(costs), 4)