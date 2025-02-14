""" A single instance of a Schluter Thermostat """


class EnergyCalculationDuration(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"


class DayEnergyUsage:
    def __init__(self, json):
        usage_jsons = json["Usage"]
        hour_usages = []
        for index, usage_json in enumerate(usage_jsons):
            hour_usages.append(HourEnergyUsage(usage_json, index))
        self.hour_usages = hour_usages

class HourEnergyUsage:
    def __init__(self, json, time):
        self.energy_in_kwh = json["EnergyKWattHour"]
        self.time = time

class Thermostat:
    """A Schluter Thermostat"""

    def __init__(self, data):
        """Initialize Thermostat."""
        self._serial_number = data["SerialNumber"]
        self._name = data["Room"]
        self._group_name = data["GroupName"]
        self._group_id = data["GroupId"]
        self._temperature = data["Temperature"]
        self._set_point_temp = data["SetPointTemp"]
        self._regulation_mode = data["RegulationMode"]
        self._vacation_enabled = data["VacationEnabled"]
        self._vacation_begin_day = data["VacationBeginDay"]
        self._vacation_end_day = data["VacationEndDay"]
        self._vacation_temperature = data["VacationTemperature"]
        self._comfort_temperature = data["ComfortTemperature"]
        self._comfort_end_time = data["ComfortEndTime"]
        self._manual_temp = data["ManualTemperature"]
        self._is_online = data["Online"]
        self._is_heating = data["Heating"]
        self._is_early_start_of_heating = ["EarlyStartOfHeating"]
        self._max_temp = data["MaxTemp"]
        self._min_temp = data["MinTemp"]
        self._error_code = data["ErrorCode"]
        self._is_confirmed = data["Confirmed"]
        self._email = data["Email"]
        self._tz_offset = data["TZOffset"]
        self._kwh_charge = data["KwhCharge"]
        self._is_load_measuring_active = data["LoadMeasuringActive"]
        self._load_manually_set_watt = data["LoadManuallySetWatt"]
        self._load_measured_watt = data["LoadMeasuredWatt"]
        self._sw_version = data["SWVersion"]
        self._is_assigned = data["HasBeenAssigned"]
        self._distributer_id = data["DistributerId"]
        self._support = data["Support"]
        self.day_energy_usages = DayEnergyUsage(data)

    def __repr__(self):
        """Print Method."""
        return f"Thermostat: {self._serial_number}, {self._name}"
    
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
            if index >= len(self._usage):
                break
            hour_usages = self._usage[index].hour_usages
            for usage in hour_usages:
                energy_usage_total += usage.energy_in_kwh

        return energy_usage_total


    @property
    def serial_number(self):
        """Serial Number."""
        return self._serial_number

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def group_id(self):
        """Group ID."""
        return self._group_id

    @property
    def group_name(self):
        """Group Name."""
        return self._group_name

    @property
    def temperature(self):
        """Temperature."""
        return round((self._temperature / 100) * 2) / 2

    @property
    def set_point_temp(self):
        """Set Point Temperature."""
        return round((self._set_point_temp / 100) * 2) / 2

    @property
    def regulation_mode(self):
        """Regulation Mode."""
        return self._regulation_mode

    @property
    def manual_temp(self):
        """Manual Temperature."""
        return round((self._manual_temp / 100) * 2) / 2

    @property
    def is_online(self):
        """Is Thermostat Online."""
        return self._is_online

    @property
    def is_heating(self):
        """Is Thermostat Heating."""
        return self._is_heating

    @property
    def max_temp(self):
        """Maximum Temperature."""
        return round((self._max_temp / 100) * 2) / 2

    @property
    def min_temp(self):
        """Minimum Temperature."""
        return round((self._min_temp / 100) * 2) / 2

    @property
    def kwh_charge(self):
        """KwH Charge."""
        return self._kwh_charge

    @property
    def load_measured_watt(self):
        """Measured Load in Watt."""
        return self._load_measured_watt

    @property
    def sw_version(self):
        """Software Version of the Thermostat."""
        return self._sw_version
