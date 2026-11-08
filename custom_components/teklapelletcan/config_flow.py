"""Konfiguracja: wykrycie przez mDNS albo ręczny adres IP; parowanie hasłem urządzenia."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import instance_id
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import TeklaAuthError, TeklaClient, TeklaError
from .const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_TOKEN, DEFAULT_NAME, DEFAULT_PORT, DOMAIN


class TeklaPelletCanConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._host = ""
        self._port = DEFAULT_PORT
        self._info: dict = {}

    async def _probe(self) -> str | None:
        """Sprawdza urządzenie; zwraca kod błędu albo None."""
        client = TeklaClient(async_get_clientsession(self.hass), self._host, self._port)
        try:
            self._info = await client.info()
        except TeklaError:
            return "cannot_connect"
        if not self._info.get("id"):
            return "cannot_connect"
        await self.async_set_unique_id(self._info["id"])
        self._abort_if_unique_id_configured(updates={CONF_HOST: self._host, CONF_PORT: self._port})
        return None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._host = user_input[CONF_HOST].strip()
            self._port = user_input.get(CONF_PORT, DEFAULT_PORT)
            err = await self._probe()
            if err:
                errors["base"] = err
            else:
                return await self.async_step_auth()
        schema = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_PORT, default=DEFAULT_PORT): int})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        self._host = discovery_info.host
        self._port = discovery_info.port or DEFAULT_PORT
        err = await self._probe()
        if err:
            return self.async_abort(reason=err)
        self.context["title_placeholders"] = {"name": self._info.get("name", "TeklaPelletCAN")}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return await self.async_step_auth()
        return self.async_show_form(
            step_id="confirm", description_placeholders={"host": self._host, "id": self._info.get("id", "")}
        )

    async def async_step_auth(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        first_setup = not self._info.get("password_set")
        if user_input is not None:
            client = TeklaClient(async_get_clientsession(self.hass), self._host, self._port)
            password = user_input["password"]
            try:
                if first_setup:
                    await client.set_password(password)
                res = await client.pair(password, await instance_id.async_get(self.hass), self.hass.config.location_name or "HA")
            except TeklaAuthError:
                errors["base"] = "invalid_auth"
            except TeklaError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or DEFAULT_NAME,
                    data={
                        CONF_HOST: self._host,
                        CONF_PORT: self._port,
                        CONF_TOKEN: res["token"],
                        CONF_NAME: user_input.get(CONF_NAME) or DEFAULT_NAME,
                    },
                )
        schema = vol.Schema(
            {vol.Required("password"): str, vol.Optional(CONF_NAME, default=DEFAULT_NAME): str}
        )
        return self.async_show_form(
            step_id="auth", data_schema=schema, errors=errors, description_placeholders={"first_setup": str(first_setup)}
        )
