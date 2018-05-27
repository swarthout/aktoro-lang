class AST(object):
    '''
    Base class for all of the AST nodes.  Each node is expected to
    define the _fields attribute which lists the names of stored
    attributes.   The __init__() method below takes positional
    arguments and assigns them to the appropriate fields.  Any
    additional arguments specified as keywords are also assigned.
    '''
    _fields = []

    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __repr__(self):
        attrs = [(a, str(getattr(self, a))) for a in self.__dir__()
                 if not a.startswith('_') and a != 'lineno' and not isinstance(getattr(self, a), AST)
                 and not isinstance(getattr(self, a), list) and getattr(self, a) is not None]
        return "<{}: {}>".format(self.__class__.__name__, ", ".join(["{}: {}".format(a[0], a[1]) for a in attrs]))


class Program(AST):
    _fields = ["statements"]


class VarDecl(AST):
    _fields = ["var", "expr", "ak_type"]


class VarUsage(AST):
    _fields = ["name", "ak_type"]


class PrimitiveLiteral(AST):
    _fields = ["value", "ak_type"]


class ListLiteral(AST):
    _fields = ["values", "ak_type"]


class DictLiteral(AST):
    _fields = ["dict", "ak_type"]


class RecordLiteral(AST):
    _fields = ["field_dict", "ak_type"]


class BinaryOpExpr(AST):
    _fields = ["left", "op", "right", "ak_type"]


class FieldDecl(AST):
    _fields = ["name", "ak_type"]


class FieldAssignment(AST):
    _fields = ["name", "expr"]


class FuncDef(AST):
    _fields = ["params", "return_type", "body"]


class FuncCall(AST):
    _fields = ["func_name", "args"]


class ReturnExpr(AST):
    _fields = ["expr", "ak_type"]


class PrintStmt(AST):
    _fields = ["exprs"]


class IndexExpr(AST):
    _fields = ["var", "index_expr", "ak_type"]


class NodeVisitor(object):
    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None

    def generic_visit(self, node):
        '''
        Method executed if no applicable visit_ method can be found.
        This examines the node to see if it has _fields, is a list,
        or can be further traversed.
        '''
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)


class NodeTransformer(NodeVisitor):
    '''
    Class that allows nodes of the parse tree to be replaced/rewritten.
    This is determined by the return value of the various visit_() functions.
    If the return value is None, a node is deleted. If any other value is returned,
    it replaces the original node.

    The main use of this class is in code that wants to apply transformations
    to the parse tree.  For example, certain compiler optimizations or
    rewriting steps prior to code generation.
    '''

    def generic_visit(self, node):
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                newvalues = []
                for item in value:
                    if isinstance(item, AST):
                        newnode = self.visit(item)
                        if newnode is not None:
                            newvalues.append(newnode)
                    else:
                        newvalues.append(n)
                value[:] = newvalues
            elif isinstance(value, AST):
                newnode = self.visit(value)
                if newnode is None:
                    delattr(node, field)
                else:
                    setattr(node, field, newnode)
        return node


# DO NOT MODIFY
def flatten(top):
    '''
    Flatten the entire parse tree into a list for the purposes of
    debugging and testing.  This returns a list of tuples of the
    form (depth, node) where depth is an integer representing the
    parse tree depth and node is the associated AST node.
    '''

    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []

        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
