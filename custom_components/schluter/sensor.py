"""Break out the temperature of the thermostat into a separate sensor entity."""
from enum import Enum
from aioschluter import Thermostat

from custom_components.schluter.aioschluter.thermostat import EnergyCalculationDuration
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfEnergy, UnitOfPower
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity import EntityCategory

from . import SchluterData
from .const import DOMAIN, ZERO_WATTS

from datetime import datetime, date

def get_todays_midnight():
    today = date.today()
    return datetime.combine(today, datetime.min.time())

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    data: SchluterData = hass.data[DOMAIN][config_entry.entry_id]

    # Add the Temperature Sensor
    async_add_entities(
        SchluterTemperatureSensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )

    # Add the Target Temperature Sensor
    async_add_entities(
        SchluterTargetTemperatureSensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )

    # Add the Power Sensor
    async_add_entities(
        SchluterPowerSensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )

    # Add the price per kwh Sensor
    async_add_entities(
        SchluterEnergyPriceSensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )

    # Add the virtual/calculated KwH Sensor
    async_add_entities(
        SchluterEnergySensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )

    async_add_entities(
        ThermostatSensor(data.coordinator, thermostat_id)
        for thermostat_id in data.coordinator.data
    )


class SchluterTargetTemperatureSensor(
    CoordinatorEntity[DataUpdateCoordinator], SensorEntity
):
    """Representation of a Sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Thermostat]]],
        thermostat_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data[thermostat_id].name + " Target Temperature"
        self._thermostat_id = thermostat_id
        self._attr_unique_id = (
            f"{coordinator.data[thermostat_id].name}-target-{self._attr_device_class}"
        )

    @property
    def available(self) -> bool:
        """Return True if Schluter thermostat is available."""
        return self.coordinator.data[self._thermostat_id].is_online

    @property
    def device_info(self):
        """Return information to link this entity."""
        return {
            "identifiers": {(DOMAIN, self._thermostat_id)},
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data[self._thermostat_id].set_point_temp


class SchluterTemperatureSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Thermostat]]],
        thermostat_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data[thermostat_id].name + " Current Temperature"
        self._thermostat_id = thermostat_id
        self._attr_unique_id = (
            f"{coordinator.data[thermostat_id].name}-{self._attr_device_class}"
        )

    @property
    def available(self) -> bool:
        """Return True if Schluter thermostat is available."""
        return self.coordinator.data[self._thermostat_id].is_online

    @property
    def device_info(self):
        """Return information to link this entity."""
        return {
            "identifiers": {(DOMAIN, self._thermostat_id)},
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data[self._thermostat_id].temperature


class SchluterPowerSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Thermostat]]],
        thermostat_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data[thermostat_id].name + " Power"
        self._thermostat_id = thermostat_id
        self._attr_unique_id = (
            f"{coordinator.data[thermostat_id].name}-{self._attr_device_class}"
        )

    @property
    def available(self) -> bool:
        """Return True if Schluter thermostat is available."""
        return self.coordinator.data[self._thermostat_id].is_online

    @property
    def device_info(self):
        """Return information to link this entity."""
        return {
            "identifiers": {(DOMAIN, self._thermostat_id)},
        }

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if self.coordinator.data[self._thermostat_id].is_heating:
            return self.coordinator.data[self._thermostat_id].load_measured_watt
        return ZERO_WATTS


class SchluterEnergySensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of a PowerSensor."""

    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Thermostat]]],
        thermostat_id: str,
        values=60,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data[thermostat_id].name + " Energy"
        self._thermostat_id = thermostat_id
        self._attr_unique_id = (
            f"{coordinator.data[thermostat_id].name}-{self._attr_device_class}"
        )
        self._wattage_list = []
        self._values = values

    def add(self, watt):
        """Queue a number wattage for kwh calculation."""
        self._wattage_list.insert(0, watt)
        if len(self._wattage_list) == self._values:
            self._wattage_list.pop()

    @property
    def available(self) -> bool:
        """Return True if Schluter thermostat is available."""
        return self.coordinator.data[self._thermostat_id].is_online

    @property
    def device_info(self):
        """Return information to link this entity."""
        return {
            "identifiers": {(DOMAIN, self._thermostat_id)},
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        if self.coordinator.data[self._thermostat_id].is_heating:
            self.add(self.coordinator.data[self._thermostat_id].load_measured_watt)
        return round((sum(self._wattage_list) / self._values) / 1000, 2)


class SchluterEnergyPriceSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_native_unit_of_measurement = "$/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Thermostat]]],
        thermostat_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data[thermostat_id].name + " Price"
        self._thermostat_id = thermostat_id
        self._attr_unique_id = (
            f"{coordinator.data[thermostat_id].name}-{self._attr_device_class}"
        )

    @property
    def available(self) -> bool:
        """Return True if Schluter thermostat is available."""
        return self.coordinator.data[self._thermostat_id].is_online

    @property
    def device_info(self):
        """Return information to link this entity."""
        return {
            "identifiers": {(DOMAIN, self._thermostat_id)},
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data[self._thermostat_id].kwh_charge

class ThermostatSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensors"""
    def __init__(
        self,
        coordinator,
        thermostat_id,
        energy_type
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.thermostat = coordinator.data[thermostat_id]
        self.energy_type = energy_type
        self._attr_unique_id = f"{self.thermostat.serial_number}-{self.energy_type.value}"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_suggested_display_precision = 2
        self._attr_available = True
        self._attr_name = self._get_name(energy_type)
        self._attr_state = self._calculate_energy_usage(energy_type)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.thermostat.serial_number)},
            "manufacturer": "Schluter",
            "name": f"{self.thermostat.room} Thermostat",
        }
    @property
    def last_reset(self):
        return get_todays_midnight()

    @property
    def state(self) -> Optional[str]:
        return self._calculate_energy_usage(self.energy_type)

    def _calculate_energy_usage(self, energy_type):
        number_of_days = 1
        match energy_type:
            case EnergyCalculationDuration.DAY:
                number_of_days = 1
            case EnergyCalculationDuration.WEEK:
                number_of_days = 7
            case EnergyCalculationDuration.MONTH:
                number_of_days = 30

        energy_usage_total = 0
        for index in range(0, number_of_days):
            if index >= len(self.thermostat.day_energy_usages):
                break
            hour_usages = self.thermostat.day_energy_usages[index].hour_usages
            for usage in hour_usages:
                energy_usage_total += usage.energy_in_kwh

        return energy_usage_total

    def _get_name(self, energy_type):
        name = self.thermostat.room
        match energy_type:
            case EnergyCalculationDuration.DAY:
                name += " Energy Used Today"
            case EnergyCalculationDuration.WEEK:
                name += " Energy Used Last 7 Days"
            case EnergyCalculationDuration.MONTH:
                name += " Energy Used Last 30 Days"
        return name