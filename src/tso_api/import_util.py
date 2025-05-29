import importlib
import inspect
import pkgutil


def load_concrete_classes_from_pkg[T](package: str, cls: type[T]) -> list[type[T]]:
    """
    Return all classes which inherit from `cls` in the given package.
    Does not recurse into sub-packages.
    This function guarantees that the base class will not be returned even if defined in the given package.

    Example: `classes = load_concrete_classes_from_pkg('tso_api.service.scraper.html', HTMLScraper)`

    :param package: A string representing a python package that should be searched for matching sub-classes
    :param cls: The type of the class for which sub-classes should be searched. This is **not** an instance of the class but rather the type
    :return: A list of subclasses, not initialized. Does not include the class given by `cls`.
    """
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
