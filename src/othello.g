// Grammar for Othello Language

program: _line*

_line: _NEWLINE
     | stmt _NEWLINE?

?stmt: decl
     | expr
     | type_def

decl: "let" var_decl "=" expr
var_decl: NAME
var_usage: NAME

?expr: INT    -> int
     | FLOAT  -> float
     | BOOL   -> bool
     | NAME   -> var_usage
     | STRING -> string
     | list
     | func_def
     | arith_expr
     | logical_expr
     | func_call
     | record_usage

arith_expr: expr "+" expr  -> add
          | expr "-" expr  -> subtract
          | expr "/" expr  -> divide
          | expr "*" expr  -> mult
          | expr "<>" expr -> concat

logical_expr: expr "and" expr -> and
            | expr "or" expr  -> or
            | "not" expr      -> not

list: "[" _expr_list? "]"
_expr_list: expr ("," expr)*

type_def: "type" type_decl "=" (record_def | variant_def)
type_decl: NAME
type_usage: NAME

record_def: "{" param_list? "}"
variant_def: variant_constructor ("|" variant_constructor)+
variant_constructor: atom type_usage*
atom: ":" NAME

record_usage: "{" _NEWLINE? field_assignment ("," _NEWLINE? field_assignment)* _NEWLINE? "}"
field_assignment: var_usage "=" expr

func_def: "fn" "(" param_list? ")" [type_usage] "=>" func_body
func_body: stmt | block
param_list: param ("," param)*
param: var_decl type_usage
block: "{" _line* "}"

func_call: var_usage "(" _expr_list? ")"

BOOL.2: "true"
      | "false"

_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+
COMMENT: /#[^\n]*/

%import common.CNAME -> NAME
%import common.SIGNED_INT -> INT
%import common.FLOAT
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING

%ignore WS_INLINE