class TypeMapperVisitor():

    def __init__(self):
        self.param_map = {}

    def visit(self, node, arg_type):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method)
            return visitor(node, arg_type)
        else:
            return None

    def get_param_map(self):
        return self.param_map

    def visit_ListType(self, node, arg_type):
        self.visit(node.elem_type, arg_type.elem_type)

    def visit_PrimitiveType(self, node, arg_type):
        pass

    def visit_DictType(self, node, arg_type):
        self.visit(node.key_type, arg_type.key_type)
        self.visit(node.val_type, arg_type.val_type)

    def visit_RecordType(self, node, arg_type):
        for n_field, a_field in zip(node.fields.values(), arg_type.fields.values()):
            self.visit(n_field, a_field)

    def visit_FuncType(self, node, arg_type):
        for n_param, a_param in zip(node.param_types, arg_type.param_types):
            self.visit(n_param, a_param)
        self.visit(node.return_type, arg_type.return_type)

    def visit_TypeParameter(self, node, arg_type):
        self.param_map[node.param] = arg_type

    def visit_EmptyTuple(self, node, arg_type):
        pass

    def visit_VariantType(self, node, arg_type):
        for n_param, a_param in zip(node.type_params, arg_type.type_params):
            self.visit(n_param, a_param)

    def visit_VariantConstructor(self, node, arg_type):
        for n_param, a_param in zip(node.params, arg_type.params):
            self.visit(n_param, a_param)


class TypeResolverVisitor():

    def __init__(self, param_map):
        self.param_map = param_map

    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method)
            return visitor(node)
        else:
            return None

    def visit_ListType(self, node):
        node.elem_type = self.visit(node.elem_type)
        return node

    def visit_PrimitiveType(self, node):
        return node

    def visit_DictType(self, node):
        node.key_type = self.visit(node.key_type)
        node.val_type = self.visit(node.val_type)
        return node

    def visit_RecordType(self, node):
        for field_name, ak_type in node.fields.items():
            node.fields[field_name] = self.visit(ak_type)
        return node

    def visit_FuncType(self, node):
        for i, param in enumerate(node.param_types):
            node.param_types[i] = self.visit(param)
        node.return_type = self.visit(node.return_type)
        return node

    def visit_TypeParameter(self, node):
        type_param = self.param_map[node.param]
        return type_param

    def visit_EmptyTuple(self, node):
        return node

    def visit_VariantType(self, node):

        for i, constructor in enumerate(node.constructors):
            node.constructors[i] = self.visit(constructor)
        return node

    def visit_VariantConstructor(self, node):
        for i, param in enumerate(node.params):
            node.params[i] = self.visit(param)
        return node
