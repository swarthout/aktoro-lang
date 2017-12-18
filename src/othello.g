// Grammar for Othello Language

program: _line*

_line: _NEWLINE
     | stmt _NEWLINE?

?stmt: decl
     | expr
     | type_def

decl: "let" NAME "=" expr

?expr: NUMBER -> number
     | BOOL   -> bool
     | NAME   -> var
     | STRING -> string
     | list
     | func_def
     | arith_expr
     | func_call

arith_expr: expr "+" expr  -> addition
          | expr "-" expr  -> subtraction
          | expr "/" expr  -> division
          | expr "*" expr  -> multiplication
          | expr "<>" expr -> concatenation

list: "[" _expr_list? "]"
_expr_list: expr ("," expr)*

type_def: "type" type_name "=" (record_def | variant_def)
type_name: NAME

record_def: "{" param_list? "}"
variant_def: variant_constructor ("|" variant_constructor)+
variant_constructor: atom type_name*
atom: ":" NAME

func_def: "fn" "(" param_list? ")" [type_name] "=>" func_body
func_body: stmt | block
param_list: param ("," param)*
param: NAME type_name
block: "{" _line* "}"

func_call: NAME "(" _expr_list? ")"

BOOL.2: "true"
      | "false"

_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+
COMMENT: /#[^\n]*/

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING

%ignore WS_INLINE