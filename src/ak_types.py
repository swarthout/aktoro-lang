from enum import Enum
from abc import ABC, abstractmethod

PRIMITIVE_TYPES = ["int", "float", "string", "bool"]


class TypeKind(Enum):
    RECORD = 1
    VARIANT = 2
    TYPE_ALIAS = 3


class AkType(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_go_type_usage(self):
        pass


class ListType(AkType):
    def __init__(self, elem_type):
        super().__init__("list")
        self.elem_type = elem_type

    def __str__(self):
        return "ListType({})".format(self.elem_type)

    __repr__ = __str__

    def get_go_type_usage(self):
        return "[]{}".format(self.elem_type.get_go_type_usage())


class PrimitiveType(AkType):
    # map primitive aktoro types to their golang equivalents
    primitive_types = {
        "int": "int",
        "float": "float64",
        "string": "string",
        "bool": "bool"
    }

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return "PrimitiveType({})".format(self.name)

    __repr__ = __str__

    def get_go_type_usage(self):
        if self.name in self.primitive_types:
            return self.primitive_types[self.name]


class DictType(AkType):
    def __init__(self, key_type, val_type):
        super().__init__("dict")
        self.key_type = key_type
        self.val_type = val_type

    def get_go_type_usage(self):
        return "map[{}]{}".format(self.key_type, self.val_type)


class RecordType(AkType):
    def __init__(self, name, type_params, fields):
        super().__init__(name)
        self.type_params = type_params
        self.fields = fields

    def get_go_type_usage(self):
        return snake_to_camel(self.name)


class FuncType(AkType):
    def __init__(self, params, return_type):
        super().__init__("fn")
        self.params = params
        self.return_type = return_type

    def get_go_type_usage(self):
        param_type_usage = ", ".join([p.ak_type.get_go_type_usage() for p in self.params.values()])
        return "func({}) {}".format(param_type_usage, self.return_type.get_go_type_usage())


class VariantType(AkType):
    pass


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name
