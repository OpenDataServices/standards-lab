import importlib
import os


def patch_validator(validator):
    for module_filename in os.listdir(os.path.dirname(__file__)):
        if module_filename.endswith(".py") and module_filename != "__init__.py":
            module = importlib.import_module(
                "processor.extra_validator_funcs.{}".format(module_filename[:-3])
            )
            validator.VALIDATORS.update(module.validator_funcs)
