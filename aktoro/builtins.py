import aktoro.types as types
from collections import namedtuple

BuiltInFunc = namedtuple("BuiltInFunc", ["ak_type"])

BUILTIN_PACKAGES = {
    "list": {
        "map": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                   types.FuncType(
                                                       [types.TypeParameter("a")],
                                                       types.TypeParameter("b"))],
                                                  types.ListType(types.TypeParameter("b")))),
        "filter": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                      types.FuncType(
                                                          [types.TypeParameter("a")],
                                                          types.PrimitiveType("Bool"))
                                                      ],
                                                     types.ListType(types.TypeParameter("a")))),
        # "reduce": BuiltInFunc(ak_type=None),
        # "each": BuiltInFunc(ak_type=None),
        # "reverse": BuiltInFunc(ak_type=None)
    }
}
