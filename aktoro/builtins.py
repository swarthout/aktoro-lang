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
        "reverse": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                      types.ListType(types.TypeParameter("a")))),
        "at": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                  types.PrimitiveType("Int")],
                                                 types.TypeParameter("a"))),
        "length": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                     types.PrimitiveType("Int"))),
        "sort": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                   types.ListType(types.TypeParameter("a")))),
        "sort_by": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                       types.FuncType(
                                                           [types.TypeParameter("a"), types.TypeParameter("a")],
                                                           types.PrimitiveType("Bool"))
                                                       ],
                                                      types.ListType(types.TypeParameter("a")))),
        "take": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                    types.PrimitiveType("Int")],
                                                   types.ListType(types.TypeParameter("a")))),
        "take_while": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                          types.FuncType(
                                                              [types.TypeParameter("a")],
                                                              types.PrimitiveType("Bool"))
                                                          ],
                                                         types.ListType(types.TypeParameter("a")))),
        "drop": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                    types.PrimitiveType("Int")],
                                                   types.ListType(types.TypeParameter("a")))),
        "drop_while": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                          types.FuncType(
                                                              [types.TypeParameter("a")],
                                                              types.PrimitiveType("Bool"))
                                                          ],
                                                         types.ListType(types.TypeParameter("a")))),
        "all": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                   types.FuncType(
                                                       [types.TypeParameter("a")],
                                                       types.PrimitiveType("Bool"))
                                                   ],
                                                  types.PrimitiveType("Bool"))),
        "any": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                   types.FuncType(
                                                       [types.TypeParameter("a")],
                                                       types.PrimitiveType("Bool"))
                                                   ],
                                                  types.PrimitiveType("Bool"))),

        "find": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                    types.FuncType(
                                                        [types.TypeParameter("a")],
                                                        types.PrimitiveType("Bool"))
                                                    ],
                                                   types.TypeParameter("a"))),
        "find_index": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a")),
                                                          types.FuncType(
                                                              [types.TypeParameter("a")],
                                                              types.PrimitiveType("Bool"))
                                                          ],
                                                         types.PrimitiveType("Int"))),
        "first": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                    types.TypeParameter("a"))),
        "rest": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                   types.ListType(types.TypeParameter("a")))),
        "empty": BuiltInFunc(ak_type=types.FuncType([types.ListType(types.TypeParameter("a"))],
                                                    types.PrimitiveType("Bool")))

    }
}
OptionType = types.VariantType("types.AkOption", [types.TypeParameter("t")], [])
OptionType.constructors.extend([
    types.VariantConstructor("types.Some", [types.TypeParameter("t")], OptionType),
    types.VariantConstructor("types.None", [], OptionType)
])

ResultType = types.VariantType("types.AkResult", [types.TypeParameter("t")], [])
ResultType.constructors.extend([
    types.VariantConstructor("types.Ok", [types.TypeParameter("t")], ResultType),
    types.VariantConstructor("types.Err", [types.PrimitiveType("String")], ResultType)
])


