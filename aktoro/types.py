from enum import Enum
from abc import ABC, abstractmethod


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
        return "*list.List"


class PrimitiveType(AkType):
    # map primitive aktoro types to their golang equivalents
    primitive_types = {
        "Int": "types.AkInt",
        "Float": "types.AkFloat",
        "String": "types.AkString",
        "Bool": "types.AkBool"
    }

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return "PrimitiveType({})".format(self.name)

    __repr__ = __str__

    def go_code(self):
        if self.name in self.primitive_types.keys():
            return self.primitive_types[self.name]


class DictType(AkType):
    def __init__(self, key_type, val_type):
        super().__init__("Dict")
        self.key_type = key_type
        self.val_type = val_type

    def __str__(self):
        return "DictType({} => {})".format(self.key_type, self.val_type)

    __repr__ = __str__

    def go_code(self):
        return "dict.Dict"


class RecordType(AkType):
    def __init__(self, name, type_params, fields):
        super().__init__(name)
        self.type_params = type_params
        self.fields = fields

    def __str__(self):
        return "RecordType({})".format(self.name)

    __repr__ = __str__

    def go_code(self):
        return self.name


class FuncType(AkType):
    def __init__(self, param_types, return_type):
        super().__init__("fn")
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self):
        return "FuncType({} -> {})".format(self.param_types, self.return_type)

    __repr__ = __str__

    def go_code(self):
        params = ", ".join(["interface{}"] * len(self.param_types))
        return "func({}) interface{{}}".format(params)


class VariantType(AkType):
    pass


class TypeParameter(AkType):
    def __init__(self, param):
        super().__init__("TypeParameter")
        self.param = param

    def __str__(self):
        return "TypeParameter({})".format(self.param)

    __repr__ = __str__

    def go_code(self):
        return "interface{}"


class EmptyTuple(AkType):
    def __init__(self):
        super().__init__("empty")

    def __str__(self):
        return "EmptyTuple"

    __repr__ = __str__

    def go_code(self):
        return "interface{}"
