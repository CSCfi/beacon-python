import json
from aiohttp import web
from functools import wraps
import jsonschema
from ..api.exceptions import BeaconBadRequest
# from jsonschema import Draft7Validator, validators
# from jsonschema.exceptions import ValidationError


# TO DO if required do not set default
# def extend_with_default(validator_class):
#     validate_properties = validator_class.VALIDATORS["properties"]
#
#     def set_defaults(validator, properties, instance, schema):
#         for property, subschema in properties.items():
#             if "default" in subschema:
#                 instance.setdefault(property, subschema["default"])
#
#         for error in validate_properties(
#             validator, properties, instance, schema,
#         ):
#             yield error
#
#     return validators.extend(
#         validator_class, {"properties": set_defaults},
#     )
#
#
# DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


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
                    # TO DO verify match response as in OpenAPI
                    raise BeaconBadRequest(obj, request.host, "Could not properly parse the provided data as JSON.")
                try:
                    jsonschema.validate(obj, schema)
                    # DefaultValidatingDraft7Validator(schema).validate(obj)
                except jsonschema.ValidationError as e:
                    # TO DO verify match response as in OpenAPI
                    raise BeaconBadRequest(obj, request.host, e.message)
            else:
                # response = await handler(request)
                pass
            return await func(*args)
        return wrapped
    return wrapper
