import importlib

from functools import lru_cache
from typing import Any

from src.common.exception import errors


def parse_module_str(module_path: str) -> tuple:
    """
    Parse a module string into a Python module and class/function.

    :param module_path:
    :return:
    """
    module_name, class_or_func = module_path.rsplit(".", 1)
    return module_name, class_or_func


@lru_cache(maxsize=512)
def import_module_cached(module_name: str) -> Any:
    """
    Cache imported modules

    :param module_name:
    :return:
    """
    return importlib.import_module(module_name)


def dynamic_import(module_path: str) -> Any:
    """
    Dynamic import

    :param module_path:
    :return:
    """
    module_name, obj_name = parse_module_str(module_path)

    try:
        module = import_module_cached(module_name)
        class_or_func = getattr(module, obj_name)
        return class_or_func
    except (ImportError, AttributeError):
        raise errors.ServerError(
            msg=f"Failed to dynamically import data model {module_name}, please contact system administrator"
        )
