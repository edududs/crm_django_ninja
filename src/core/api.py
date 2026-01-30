from typing import Any

from django.http import HttpRequest
from ninja import Schema
from ninja_extra import NinjaExtraAPI


class HelloWorldResponse(Schema):
    message: str
    data: dict[str, Any]


api = NinjaExtraAPI()


@api.get("/")
def hello_world(request: HttpRequest) -> HelloWorldResponse:
    return HelloWorldResponse(message="Hello, world!", data=dict(request.GET))
