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
        "reduce": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                      types.TypeParameter("b"),
                                                      types.FuncType(
                                                          [types.TypeParameter("b"),
                                                           types.TypeParameter("a")],
                                                          types.TypeParameter("b"))
                                                      ],
                                                     types.TypeParameter("b"))),
        "each": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                    types.FuncType(
                                                        [types.TypeParameter("a")],
                                                        types.EmptyTuple())],
                                                   types.EmptyTuple())),
        # "reverse": BuiltInFunc(ak_type=None)
    }
}
