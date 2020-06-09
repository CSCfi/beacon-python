"""JSON Request/Response Validation."""

from functools import wraps
from aiohttp import web
from .logging import LOG
from ..api.exceptions import BeaconBadRequest, BeaconServerError

from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError

from typing import Dict, Tuple


async def parse_request_object(request: web.Request) -> Tuple[str, Dict]:
    """Parse as JSON Object depending on the request method.

    For POST request parse the body, while for the GET request parse the query parameters.
    """
    items = dict()

    if request.method == 'POST':
        LOG.info('Parsed POST request body.')
        items = await request.json()  # we are always expecting JSON

    if request.method == 'GET':
        # GET parameters are returned as strings
        int_params = ['start', 'end', 'endMax', 'endMin', 'startMax', 'startMin']
        items = {k: (int(v) if k in int_params else v) for k, v in request.rel_url.query.items()}
        if 'datasetIds' in items:
            items['datasetIds'] = request.rel_url.query.get('datasetIds').split(',')
        LOG.info('Parsed GET request parameters.')

    return request.method, items


def extend_with_default(validator_class):
    """Include default values present in JSON Schema.

    Source: https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            # Difficult to unit test
            yield error  # pragma: no cover

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)


def validate(schema):
    """
    Validate against JSON schema and return errors, if any.

    Return a parsed object if there is a POST.
    If there is a get do not return anything just validate.
    """
    def wrapper(func):

        @wraps(func)
        async def wrapped(*args):
            request = args[-1]
            try:
                _, obj = await parse_request_object(request)
            except Exception:
                raise BeaconServerError("Could not properly parse the provided Request Body as JSON.")
            try:
                # jsonschema.validate(obj, schema)
                LOG.info('Validate against JSON schema.')
                DefaultValidatingDraft7Validator(schema).validate(obj)
            except ValidationError as e:
                if len(e.path) > 0:
                    LOG.error(f'Bad Request: {e.message} caused by input: {e.instance} in {e.path[0]}')
                    raise BeaconBadRequest(obj, request.host, f"Provided input: '{e.instance}' does not seem correct for field: '{e.path[0]}'")
                else:
                    LOG.error(f'Bad Request: {e.message} caused by input: {e.instance}')
                    raise BeaconBadRequest(obj, request.host, f"Provided input: '{e.instance}' does not seem correct because: '{e.message}'")

            return await func(*args)
        return wrapped
    return wrapper
