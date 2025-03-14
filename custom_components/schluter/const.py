"""Constants for the schluter integration."""

DOMAIN = "schluter"
ZERO_WATTS = 0
PRESET_MANUAL = "On Manual"
PRESET_SCHEDULE = "On Schedule"

""" constants for aioschluter """

# API_BASE_URL = "https://ditra-heat-e-wifi.schluter.com" - original code base url
API_BASE_URL = "https://mythermostat.info" # my apps api (either worked)
API_AUTH_URL = API_BASE_URL + "/api/authenticate/user"
API_GET_THERMOSTATS_URL = API_BASE_URL + "/api/thermostats"
API_SET_THERMOSTAT_URL = API_BASE_URL + "/api/thermostat"
API_GET_ENERGY_USAGE_URL = API_BASE_URL + "/api/energyusage"
API_APPLICATION_ID = 7
HTTP_UNAUTHORIZED: int = 401
HTTP_OK: int = 200
REGULATION_MODE_SCHEDULE = 1
REGULATION_MODE_MANUAL = 2
REGULATION_MODE_AWAY = 3
