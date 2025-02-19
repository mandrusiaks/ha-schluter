"""Async Python wrapper to get data from schluter ditra heat thermostats."""

import logging
from datetime import date, datetime, timezone
from typing import Any, Optional

from aiohttp import ClientSession

from .const import (
    API_APPLICATION_ID,
    API_AUTH_URL,
    API_GET_THERMOSTATS_URL,
    API_SET_THERMOSTAT_URL,
    API_GET_ENERGY_USAGE_URL,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
)
from .thermostat import DayEnergyUsage, Thermostat

_LOGGER = logging.getLogger(__name__)
DAYS_OF_HISTORY = 29 # 29 + today, so 30 days total including today


class SchluterApi:
    """Main class to perform Schluter API requests."""

    # Disable the Alternative Union Syntax, in 3.10
    # pylint: disable=consider-alternative-union-syntax

    def __init__(
        self,
        session: ClientSession,
    ):
        """Initialize."""
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._session = session
        self._sessionid: Optional[str] = None
        self._sessionid_timestamp: Optional[datetime] = None

    @property
    def username(self):
        """Username."""
        return self._username

    @property
    def password(self):
        """Password."""
        return self._password

    @property
    def sessionid(self):
        """SessionId."""
        return self._sessionid

    @property
    def sessionid_timestamp(self):
        """Timestamp the session was created on."""
        return self._sessionid_timestamp

    async def _extract_thermostats_from_data(self, data: dict[str, Any]) -> dict[str, Any]:
        thermostats = {}
        for group in data["Groups"]:
            for tdata in group["Thermostats"]:
                tstat = Thermostat(tdata)
                updated_tstat = await self.async_get_energy_usage(tstat)
                thermostats[tdata["SerialNumber"]] = updated_tstat
        return thermostats

    async def async_get_sessionid(self, username, password) -> Optional[str]:
        """Validate the username and password for the Schluter API."""

        self._username = username
        self._password = password

        async with self._session.post(
            API_AUTH_URL,
            json={
                "Email": username,
                "Password": password,
                "Application": API_APPLICATION_ID,
            },
        ) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                raise InvalidUserPasswordError("Invalid username or password")
            if resp.status != HTTP_OK:
                raise ApiError(f"Invalid Response from Schluter API: {resp.status}")

            _LOGGER.debug(
                "Data retrieved from %s, status: %s", API_AUTH_URL, resp.status
            )
            self._sessionid_timestamp = datetime.now()
            data = await resp.json()

        if data["SessionId"] == "":
            if data["ErrorCode"] == 1 or data["ErrorCode"] == 2:
                raise InvalidUserPasswordError("Invalid username or password")
            _LOGGER.error(
                "Unkonwn ErrorCode was returned by Schluter API: %i",
                data["ErrorCode"],
            )
            raise ApiError("Unknown ErrorCode was returned by Schluter Api")

        self._sessionid = data["SessionId"]
        return self._sessionid

    async def async_get_current_thermostats(self, sessionid) -> dict[str, Any]:
        """Get the current settings for all thermostats."""
        if len(sessionid) == 0:
            raise InvalidSessionIdError("Invalid Session Id")

        self._sessionid = sessionid
        params = {"sessionId": sessionid}
        async with self._session.get(API_GET_THERMOSTATS_URL, params=params) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                raise InvalidSessionIdError(
                    "An invalid or expired sessionid was supplied"
                )
            if resp.status != HTTP_OK:
                raise ApiError(f"Invalid Response: {resp.status}")

            _LOGGER.debug(
                "Data retrieved from %s, status: %s",
                API_GET_THERMOSTATS_URL,
                resp.status,
            )
            data = await resp.json()
            return await self._extract_thermostats_from_data(data)

            # for group in data["Groups"]:
            #     for tdata in group["Thermostats"]:
            #         tstat = thermostats[tdata["SerialNumber"]]
            #         await self.async_get_energy_usage([tstat])


            # return await self.async_get_energy_usage(thermostats)


    async def async_set_temperature(self, sessionid, serialnumber, temperature) -> bool:
        """Set the temperature for a thermostat."""
        if len(sessionid) == 0:
            raise InvalidSessionIdError("Invalid Session Id")

        self._sessionid = sessionid
        adjusted_temp = int(temperature * 100)
        params = {"sessionId": sessionid, "serialnumber": serialnumber}

        async with self._session.post(
            API_SET_THERMOSTAT_URL,
            params=params,
            json={
                "ManualTemperature": adjusted_temp,
                "RegulationMode": 3,
                "VacationEnabled": False,
            },
        ) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                raise InvalidSessionIdError(
                    "An invalid or expired sessionid was supplied"
                )
            if resp.status != HTTP_OK:
                raise ApiError(f"Invalid Response from Schluter API: {resp.status}")

            _LOGGER.debug(
                "Temperature set via %s, status: %s",
                API_SET_THERMOSTAT_URL,
                resp.status,
            )
            data = await resp.json()
        return data["Success"]

    async def async_set_regulation_mode(self, sessionid, serialnumber, mode) -> bool:
        """set the regulation mode to SCHEDULE, MANUAL or AWAY"""
        self._sessionid = sessionid
        params = {"sessionId": sessionid, "serialnumber": serialnumber}

        async with self._session.post(
            API_SET_THERMOSTAT_URL,
            params=params,
            json={"SerialNumber": serialnumber, "RegulationMode": mode},
        ) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                raise InvalidSessionIdError(
                    "An invalid or expired sessionid was supplied"
                )
            if resp.status != HTTP_OK:
                raise ApiError(f"Invalid Response from Schluter API: {resp.status}")

            _LOGGER.debug(
                "HVAC mode set via %s, status: %s",
                API_SET_THERMOSTAT_URL,
                resp.status,
            )
            data = await resp.json()
        return data["Success"]
    
    async def async_get_energy_usage(self, thermostat):
        """test"""
        today = date.today()
        today_param = today.strftime("%d/%m/%Y")
        params = {"sessionId": self._sessionid, "serialnumber": thermostat.serial_number, "view": "day", "date": today_param, "history": str(DAYS_OF_HISTORY), "calc": "false", "weekstart": "monday"}
        async with self._session.get(API_GET_ENERGY_USAGE_URL, params=params) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                raise InvalidSessionIdError(
                    "An invalid or expired sessionid was supplied"
                )
            if resp.status != HTTP_OK:
                raise ApiError(f"Invalid Response from Schluter API: {resp.status}")

            data = await resp.json()
            energy_usage_jsons = data["EnergyUsage"]
            day_energy_usages = []
            for json in energy_usage_jsons:
                day_energy_usages.append(DayEnergyUsage(json))
                thermostat.update_energy_usage(day_energy_usages)
        return thermostat


class ApiError(Exception):
    """Raised when Schluter API request ended in error."""

    def __init__(self, status) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class InvalidUserPasswordError(Exception):
    """Raise when Username is incorrect."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class InvalidSessionIdError(Exception):
    """Raise when the Schluter Session Id is missing."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
