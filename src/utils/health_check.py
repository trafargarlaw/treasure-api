from math import ceil

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from src.common.exception import errors


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    Check if route names are unique

    :param app:
    :return:
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f"Non-unique route name: {route.name}")
            temp_routes.add(route.name)


async def http_limit_callback(request: Request, response: Response, expire: int):
    """
    Default callback function for request rate limiting

    :param request:
    :param response:
    :param expire: remaining milliseconds
    :return:
    """
    expires = ceil(expire / 1000)
    raise errors.HTTPError(
        code=429,
        msg="Too many requests, please try again later",
        headers={"Retry-After": str(expires)},
    )
