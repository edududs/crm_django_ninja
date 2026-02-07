import logging
from typing import Any

from django.http import HttpRequest
from ninja import Schema
from ninja_extra import NinjaExtraAPI

logger = logging.getLogger(__name__)


class HelloWorldResponse(Schema):
    message: str
    data: dict[str, Any]


api = NinjaExtraAPI(title="API", description="API for the project")


@api.get("")
def hello_world(request: HttpRequest) -> HelloWorldResponse:
    logger.debug("hello_world called with GET %s", request.GET)
    return HelloWorldResponse(message="Hello, world!", data=dict(request.GET))
