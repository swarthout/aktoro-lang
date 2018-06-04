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
    def go_code(self):
        pass


class ListType(AkType):
    def __init__(self, elem_type):
        super().__init__("list")
        self.elem_type = elem_type

    def __str__(self):
        return "ListType({})".format(self.elem_type)

    __repr__ = __str__

    def go_code(self):
        return "[]{}".format(self.elem_type.go_code())


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

    def go_code(self):
        if self.name in self.primitive_types:
            return self.primitive_types[self.name]


class DictType(AkType):
    def __init__(self, key_type, val_type):
        super().__init__("dict")
        self.key_type = key_type
        self.val_type = val_type

    def go_code(self):
        return "map[{}]{}".format(self.key_type, self.val_type)


class RecordType(AkType):
    def __init__(self, name, type_params, fields):
        super().__init__(name)
        self.type_params = type_params
        self.fields = fields

    def go_code(self):
        return snake_to_camel(self.name)


class FuncType(AkType):
    def __init__(self, params, return_type):
        super().__init__("fn")
        self.params = params
        self.return_type = return_type

    def go_code(self):
        param_type_usage = ", ".join([p.ak_type.go_code() for p in self.params.values()])
        return "func({}) {}".format(param_type_usage, self.return_type.go_code())


class VariantType(AkType):
    pass


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name
