import importlib
import pkgutil
import inspect


def load_concrete_classes_from_pkg[T](package: str, cls: type[T]) -> list[type[T]]:
    classes: list[type[T]] = []
    module = importlib.import_module(package)
    if module.__spec__ is None:
        return []

    submodule_search_locations = module.__spec__.submodule_search_locations

    if submodule_search_locations is None or len(submodule_search_locations) == 0:
        return []

    for moduleinfo in pkgutil.iter_modules(submodule_search_locations):
        full_module_name = f'{package}.{moduleinfo.name}'
        module = importlib.import_module(full_module_name)

        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, cls) and obj is not cls:
                classes.append(obj)

    return classes
