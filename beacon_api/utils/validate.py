import json
from aiohttp import web
from functools import wraps
import jsonschema
from ..api.exceptions import BeaconBadRequest


def validate(schema):
    """
    Validate against JSON schema an return something.

    Return a parsed object if there is a POST.
    If there is a get do not return anything just validate.
    """
    def wrapper(func):

        @wraps(func)
        async def wrapped(*args):
            request = args[-1]
            assert isinstance(request, web.Request)
            if request.method == 'POST' and request.path == '/query':
                try:
                    raw_json = await request.read()
                    obj = json.loads(raw_json.decode('utf-8'))
                except Exception:
                    # TO DO match response as in OpenAPI
                    raise BeaconBadRequest(obj, "Could not properly parse the provided data as JSON.")
                try:
                    jsonschema.validate(obj, schema)
                except jsonschema.ValidationError as e:
                    # TO DO match response as in OpenAPI
                    raise BeaconBadRequest(obj, e.message)
            else:
                # response = await handler(request)
                pass
            return await func(*args)
        return wrapped
    return wrapper
