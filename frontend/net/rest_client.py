from __future__ import annotations

__all__ = ("RestClient",)

import typing

from frontend.internal.rest_client import RestClientBase
from frontend.net import routes
from shared.models import requests
from shared.models import responses


class RestClient(RestClientBase):
    @typing.override
    def login(self, username: str, password: str) -> responses.LoginResponse:
        body = requests.LoginRequest(username=username, password=password)
        route = routes.POST_LOGIN.compile()
        return self._perform_request(expected_response=responses.LoginResponse, endpoint=route, data=body)

    def register(self, username: str, password: str) -> None:
        body = requests.LoginRequest(username=username, password=password)
        route = routes.POST_REGISTER.compile()
        return self._perform_request(expected_response=type(None), endpoint=route, data=body)

    def get_lobbys(self, game: str) -> list[responses.PublicGameLobby]:
        route = routes.GET_LOBBYS.compile(game=game)
        return self._perform_request(expected_response=list[responses.PublicGameLobby], endpoint=route)

    def create_lobby(self, game: str) -> responses.PublicGameLobby:
        route = routes.POST_LOBBYS.compile(game=game)
        return self._perform_request(expected_response=responses.PublicGameLobby, endpoint=route)
