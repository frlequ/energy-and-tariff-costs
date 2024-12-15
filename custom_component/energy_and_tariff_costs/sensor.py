import logging
from collections import defaultdict
from typing import Optional, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er
from homeassistant.components.recorder.history import get_significant_states
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, VT_PRICE, MT_PRICE, TAX,
    BLOK_1_CONS_PRICE, BLOK_2_CONS_PRICE, BLOK_3_CONS_PRICE, BLOK_4_CONS_PRICE, BLOK_5_CONS_PRICE,
    BLOK_1_TAR_PRICE, BLOK_2_TAR_PRICE, BLOK_3_TAR_PRICE, BLOK_4_TAR_PRICE, BLOK_5_TAR_PRICE,
    MOJELEKTRO_PEAK, MOJELEKTRO_OFFPEAK,
    MOJELEKTRO_BLOK_1, MOJELEKTRO_BLOK_2, MOJELEKTRO_BLOK_3, MOJELEKTRO_BLOK_4, MOJELEKTRO_BLOK_5,
    MOJELEKTRO_DAILY_BLOK_1, MOJELEKTRO_DAILY_BLOK_2, MOJELEKTRO_DAILY_BLOK_3, MOJELEKTRO_DAILY_BLOK_4, MOJELEKTRO_DAILY_BLOK_5
)

# Initialize logger
_LOGGER = logging.getLogger(__name__)

def friendly_name_from_id(name: str) -> str:
    """Convert an entity ID to a friendly name."""
    return name.replace("_", " ").title()

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
):
    """Set up sensors from a config entry."""
    _LOGGER.debug("Setting up entry for domain %s with entry ID %s", DOMAIN, entry.entry_id)
    data = hass.data[DOMAIN][entry.entry_id]
    device_identifiers = data["device_identifiers"]

    # Initialize VT and MT cost sensors
    vt_sensor = SimpleCostSensor(
        hass, entry, "vt_cost", device_identifiers,
        consumption_sensor=MOJELEKTRO_PEAK, price_name=VT_PRICE, tax_name=TAX,
        cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
    )
    mt_sensor = SimpleCostSensor(
        hass, entry, "mt_cost", device_identifiers,
        consumption_sensor=MOJELEKTRO_OFFPEAK, price_name=MT_PRICE, tax_name=TAX,
        cost_formula=lambda cons, price, tax: cons * price * (1 + tax / 100)
    )
    _LOGGER.debug("Initialized VT and MT cost sensors")

    # Initialize tariff cost sensors
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
    _LOGGER.debug("Initialized tariff cost sensors: %s", [sensor.name for sensor in tariff_sensors])

    # Initialize consumption cost sensors
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
    _LOGGER.debug("Initialized consumption cost sensors: %s", [sensor.name for sensor in consumption_sensors])

    # Initialize Total Cost Sensor
    all_cost_sensors = [vt_sensor, mt_sensor] + tariff_sensors + consumption_sensors
    total_sensor = TotalCostSensor(
        hass, entry, "total_cost", device_identifiers, all_cost_sensors
    )
    _LOGGER.debug("Initialized Total Cost Sensor")

    # Add all entities to Home Assistant
    async_add_entities(
        [vt_sensor, mt_sensor, total_sensor] + tariff_sensors + consumption_sensors, 
        True
    )
    _LOGGER.info("Added all cost sensors to Home Assistant")

class BaseCostSensor(SensorEntity):
    """Base class with logic to handle daily vs monthly sensors by summing daily sensor values for the month."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        entry: ConfigEntry, 
        name: str, 
        device_identifiers
    ):
        """Initialize the BaseCostSensor."""
        self._hass = hass
        self._entry = entry
        self._entity_name = name
        self._attr_name = friendly_name_from_id(name)
        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._device_identifiers = device_identifiers
        self._state = None
        self._attr_unit_of_measurement = "€"
        _LOGGER.debug("Initialized BaseCostSensor: %s", self._attr_unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {self._device_identifiers},
            "name": "Energy Costs Device",
            "manufacturer": "Test Manufacturer",
            "model": "Test Model",
        }

    def _valid_state(self, state) -> bool:
        """Check if the state is valid."""
        valid = state is not None and state.state not in (None, "unknown", "unavailable")
        _LOGGER.debug("Validating state for entity %s: %s", self._attr_unique_id, valid)
        return valid

    def _get_number_value(self, name):
        """Retrieve a numerical value from a sensor by name."""
        entity_id = self._find_entity_id(name)
        if not entity_id:
            _LOGGER.warning("Entity ID not found for name: %s", name)
            return None
        s = self._hass.states.get(entity_id)
        if s is None or s.state in (None, "unknown", "unavailable"):
            _LOGGER.warning("State unavailable for entity: %s", entity_id)
            return None
        try:
            value = float(s.state)
            _LOGGER.debug("Retrieved value for %s: %f", name, value)
            return value
        except ValueError:
            _LOGGER.error("Invalid state value for %s: %s", name, s.state)
            return None

    def _find_entity_id(self, name):
        """Find the entity ID based on a unique name."""
        entity_registry = er.async_get(self._hass)
        unique_id = f"{self._entry.entry_id}_{name}"
        for entity_id, ent in entity_registry.entities.items():
            if ent.unique_id == unique_id:
                _LOGGER.debug("Found entity ID %s for unique ID %s", entity_id, unique_id)
                return entity_id
        _LOGGER.warning("Entity ID not found for unique ID: %s", unique_id)
        return None

    async def _get_monthly_sum_if_daily_sensor(self, sensor_id: str) -> Optional[float]:
        """
        Sum the monthly consumption from a daily sensor, ignoring the first value of each day 
        if a second value exists.
        """
        if not sensor_id.startswith("sensor.moj_elektro_daily_input_"):
            _LOGGER.debug("Sensor %s is not a daily sensor", sensor_id)
            return None  # Not a daily sensor

        now = dt_util.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = now

        _LOGGER.debug(
            "Fetching significant states for sensor %s from %s to %s", 
            sensor_id, start_of_month, end_time
        )

        try:
            states = await self._hass.async_add_executor_job(
                get_significant_states,
                self._hass,
                start_of_month,
                end_time,
                [sensor_id],
                None,
                True
            )
            _LOGGER.debug("Retrieved states for sensor %s", sensor_id)
        except Exception as e:
            _LOGGER.error("Error fetching states for sensor %s: %s", sensor_id, e)
            return None

        if not states or sensor_id not in states:
            _LOGGER.info("No states found for sensor %s", sensor_id)
            return 0.0

        # Group states by day
        states_by_day = defaultdict(list)
        for state in states[sensor_id]:
            day = state.last_changed.date()
            states_by_day[day].append(state)

        total = 0.0
        for day, day_states in states_by_day.items():
            _LOGGER.debug("Processing day: %s with %d states", day, len(day_states))
            if len(day_states) > 1:
                _LOGGER.debug(
                    "Multiple states found for %s on %s. Ignoring the first state.", 
                    sensor_id, day
                )
                # Ignore the first state
                states_to_sum = day_states[1:]
            else:
                _LOGGER.debug(
                    "Single state found for %s on %s. Including it in the sum.", 
                    sensor_id, day
                )
                states_to_sum = day_states

            for s in states_to_sum:
                if s.state not in (None, "unknown", "unavailable"):
                    try:
                        val = float(s.state)
                        total += val
                        _LOGGER.debug(
                            "Added value %f from sensor %s on %s", 
                            val, sensor_id, day
                        )
                    except ValueError:
                        _LOGGER.error(
                            "Invalid state value '%s' in sensor %s on %s", 
                            s.state, sensor_id, day
                        )

        _LOGGER.debug("Monthly sum for sensor %s: %f", sensor_id, total)
        return total

class SimpleCostSensor(BaseCostSensor):
    """Cost sensor that computes cost from a consumption sensor, price, and tax."""

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
        """Initialize the SimpleCostSensor."""
        super().__init__(hass, entry, name, device_identifiers)
        self._consumption_sensor = consumption_sensor
        self._price_name = price_name
        self._tax_name = tax_name
        self._cost_formula = cost_formula
        _LOGGER.debug(
            "Initialized SimpleCostSensor: %s with consumption_sensor: %s, price_name: %s, tax_name: %s",
            self._attr_unique_id, self._consumption_sensor, self._price_name, self._tax_name
        )

    async def async_update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.debug("Updating sensor: %s", self._attr_unique_id)
        monthly_sum = await self._get_monthly_sum_if_daily_sensor(self._consumption_sensor)
        if monthly_sum is not None:
            # Use monthly_sum for consumption
            consumption = monthly_sum
            _LOGGER.debug("Using monthly sum for consumption: %f", consumption)
        else:
            # Not a daily sensor, use current state directly
            consumption_state = self._hass.states.get(self._consumption_sensor)
            if not self._valid_state(consumption_state):
                _LOGGER.warning(
                    "Invalid consumption state for sensor %s", 
                    self._consumption_sensor
                )
                self._state = None
                return
            try:
                consumption = float(consumption_state.state)
                _LOGGER.debug("Using direct consumption value: %f", consumption)
            except ValueError:
                _LOGGER.error(
                    "Invalid consumption state value for sensor %s: %s", 
                    self._consumption_sensor, 
                    consumption_state.state
                )
                self._state = None
                return

        price = self._get_number_value(self._price_name)
        tax = self._get_number_value(self._tax_name)
        if price is None or tax is None:
            _LOGGER.error(
                "Price or tax value missing for sensor %s", 
                self._attr_unique_id
            )
            self._state = None
            return

        try:
            cost = self._cost_formula(consumption, price, tax)
            self._state = round(cost, 4)
            _LOGGER.info(
                "Updated cost for sensor %s: %f", 
                self._attr_unique_id, 
                self._state
            )
        except Exception as e:
            _LOGGER.error(
                "Error calculating cost for sensor %s: %s", 
                self._attr_unique_id, 
                e
            )
            self._state = None

class TotalCostSensor(SensorEntity):
    """Sensor that sums all individual cost sensors."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        entry: ConfigEntry, 
        name: str, 
        device_identifiers, 
        sensors
    ):
        """Initialize the TotalCostSensor."""
        self._hass = hass
        self._entry = entry
        self._entity_name = name
        self._attr_name = friendly_name_from_id(name)
        self._attr_unique_id = f"{entry.entry_id}_{name}"
        self._device_identifiers = device_identifiers
        self._sensors = sensors
        self._attr_unit_of_measurement = "€"
        self._state = None
        _LOGGER.debug("Initialized TotalCostSensor: %s", self._attr_unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {self._device_identifiers},
            "name": "Energy & Tariff Costs",
            "manufacturer": "Energy & Tariff Costs",
            "model": "Beta",
        }

    async def async_update(self):
        """Fetch new state data for the total cost sensor."""
        _LOGGER.debug("Updating TotalCostSensor: %s", self._attr_unique_id)
        # Update all individual sensors first
        for sensor in self._sensors:
            await sensor.async_update()

        costs = [sensor.state for sensor in self._sensors]
        if any(c is None for c in costs):
            _LOGGER.warning(
                "One or more sensor states are None. Total cost cannot be calculated."
            )
            self._state = None
        else:
            self._state = round(sum(costs), 4)
            _LOGGER.info("Updated total cost: %f", self._state)
