import importlib
from os import path, listdir
from os.path import isfile, join
from re import sub
from typing import Union


class Importer:
    __restrictions = ["__init__.py"]
    __config = None

    def __init__(self, config) -> None:
        self.__config = config

    def importFromPath(self, file_path: str, restrictions: list = None, interface=None) -> Union:
        if file_path is None:
            return []
        elif file_path.strip() == "" or not path.isdir(file_path):
            return []

        restrictions = [restriction.lower() for restriction in (restrictions if restrictions is not None else [])] \
                       + self.__restrictions

        target_package = sub(r"[/\\]", ".", file_path.replace(self.__config.projectRoot, ""))
        modules = []
        for module_name in [f"{target_package}.{f}"[1:-3] for f in listdir(file_path)
                            if (isfile(join(file_path, f)) and f.lower().endswith(".py"))
                               and f.lower() not in restrictions and f[:-3].lower() not in restrictions]:

            class_type = getattr(importlib.import_module(module_name), module_name.split(".")[-1])
            if interface is not None:
                print(isinstance(interface, class_type))
                print(isinstance(class_type, interface))
                print(issubclass(class_type, interface))
                print(issubclass(interface, class_type))
            modules.append(class_type)

        return modules
