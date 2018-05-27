from collections import namedtuple
from enum import Enum
from abc import ABC, abstractmethod

Expression = namedtuple('Expression', ['type_name', 'go_code'])
Statement = namedtuple('Statement', ['go_code'])
Variable = namedtuple('Variable', ['name', 'type_name'])
Record = namedtuple('Record', ['name', 'fields'])

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

    def get_go_type_def(self, type_args):
        """
        Gets a go struct definition for a given record
        :param type_args: dict of type_param to specialized type
        :return: specialized go struct
        """
        pass


class UnknownRecordType(AkType):
    def __init__(self, fields):
        super().__init__("UNKNOWN")
        self.fields = fields


class VariantType(AkType):
    pass


def snake_to_camel(name):
    words = name.split("_")
    if len(words) > 1:
        camel_name = words[0] + "".join(map(str.capitalize, words[1:]))
    else:
        camel_name = words[0]
    return camel_name
