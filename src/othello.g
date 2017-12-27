// Grammar for Othello Language

program: _line*

_line: _NEWLINE
     | stmt _NEWLINE?

?stmt: decl
     | expr
     | type_def
     | print_stmt

decl: "let" var_decl "=" expr
var_decl: NAME
var_usage: NAME ("." NAME)*

?expr: INT    -> int_literal
     | FLOAT  -> float_literal
     | BOOL   -> bool_literal
     | var_usage
     | STRING -> string_literal
     | list_literal
     | func_def
     | arith_expr
     | logical_expr
     | func_call
     | record_literal
     | record_update

arith_expr: expr "+" expr  -> add_expr
          | expr "-" expr  -> subtract_expr
          | expr "/" expr  -> divide_expr
          | expr "*" expr  -> mult_expr
          | expr "<>" expr -> concat_expr

logical_expr: expr "and" expr -> and_expr
            | expr "or" expr  -> or_expr
            | "not" expr      -> not_expr

list_literal: "[" _expr_list? "]"
_expr_list: expr ("," expr)*

type_def: "type" type_decl "=" (record_def | variant_def)
type_decl: NAME
type_usage: _t

_t: NAME
  | _t _t
  | paren_type
  | func_type

paren_type: "(" _t ")" -> type_usage

func_type: "fn" "(" type_list? ")" type_usage

type_list: type_usage ("," type_usage)*

record_def: "{" field_list "}"
field_list: field_decl ("," field_decl)*
field_decl: NAME type_usage

variant_def: variant_constructor ("|" variant_constructor)+
variant_constructor: atom_literal type_usage*
atom_literal: ":" NAME

record_literal: "{" _NEWLINE? field_assignment ("," _NEWLINE? field_assignment)* _NEWLINE? "}"
field_assignment: field_name "=" expr
field_name: NAME

record_update: "{" var_usage "|" field_assignment ("," _NEWLINE? field_assignment)* "}"

func_def: "fn" open_params param_list? close_params [type_usage] "=>" func_body
func_body: open_block _line* close_block
param_list: param ("," param)*
param: var_decl type_usage
open_params: "("
close_params: ")"
open_block: "{"
close_block: "}"

func_call: var_usage "(" _expr_list? ")"
print_stmt: "print" "(" _expr_list? ")"

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