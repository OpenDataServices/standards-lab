from jsonschema.exceptions import ValidationError


def endswith(validator, schema_value, instance, schema_parent_value):
    if not isinstance(instance, str):
        return
    if not instance.endswith(schema_value):
        yield ValidationError("Should end with '{}'".format(schema_value))


validator_funcs = {"endswith": endswith}
