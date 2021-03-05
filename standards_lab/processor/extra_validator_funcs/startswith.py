from jsonschema.exceptions import ValidationError


def startswith(validator, schema_value, instance, schema_parent_value):
    if not isinstance(instance, str):
        return
    if not instance.startswith(schema_value):
        yield ValidationError("Should start with '{}'".format(schema_value))


validator_funcs = {"startswith": startswith}
