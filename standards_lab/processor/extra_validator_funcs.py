from jsonschema.exceptions import ValidationError


def startswith(validator, schema_value, instance, schema_parent_value):
    if not isinstance(instance, str):
        return
    if not instance.startswith(schema_value):
        yield ValidationError("Should start with '{}'".format(schema_value))


def patch_validator(validator):
    validator.VALIDATORS.update(
        {
            # Add validator functions above, and to this dict here
            "startswith": startswith
        }
    )
