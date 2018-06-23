// Grammar for Aktoro Language

program: _line*

_line: _NEWLINE
     | stmt _NEWLINE?

?stmt: var_decl
     | expr
     | type_decl
     | print_stmt

var_decl: "let" var_name "=" expr
var_name: NAME
var_usage: NAME


?expr: pipe_expr
?pipe_expr: equality_expr _NEWLINE? ( _PIPE_FORWARD (func_call | print_stmt) _NEWLINE?)*
?equality_expr: add_expr ( ( COMP_EQU
                           | COMP_NEQU
                           | COMP_GTR
                           | COMP_GTE
                           | COMP_LESS
                           | COMP_LTE ) add_expr )*

?add_expr: mult_expr ( ( PLUS | MINUS ) mult_expr )*
?mult_expr: primary ( ( MULTIPLY | DIVIDE ) primary )*
?primary: "(" expr ")" -> paren_expr
        | INT          -> int_literal
        | FLOAT        -> float_literal
        | BOOL         -> bool_literal
        | var_usage
        | STRING       -> string_literal
        | list_literal
        | dict_literal
        | func_def
        | func_call
        | record_literal
        | record_update
        | list_cons
        | dict_update
        | index_expr
        | if_expr
        | field_access
        | string_concat

_PIPE_FORWARD: "|>"
COMP_EQU: "=="
COMP_NEQU: "!="
COMP_GTR: ">"
COMP_GTE: ">="
COMP_LESS: "<"
COMP_LTE: "<="
PLUS: "+"
MINUS: "-"
MULTIPLY: "*"
DIVIDE: "/"

list_literal: "[" _NEWLINE? list_elems _NEWLINE? "]" ("::" type_usage)?
list_elems: (expr ("," _NEWLINE? expr)*)?

list_cons: "[" _NEWLINE? cons_args "|" expr _NEWLINE? "]"
cons_args: expr ("," _NEWLINE? expr)*

dict_literal: "%{" _NEWLINE? kv_pair_list _NEWLINE? "}" ("::" type_usage)?
kv_pair_list:  (kv_pair ("," _NEWLINE? kv_pair)*)?
kv_pair: expr "=>" expr

dict_update: "%{" expr "|" kv_pair ("," _NEWLINE? kv_pair)* "}"

index_expr: var_usage "[" ( expr | range_index ) "]"
range_index: low ".." high
low: expr?
high: expr?

type_decl: "type" type_name "=" (record_def | variant_def)
type_name: NAME
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

record_update: "{" expr "|" field_assignment ("," _NEWLINE? field_assignment)* "}"

func_def: "fn" open_params param_list close_params [type_usage] "=>" func_body
func_body: open_block _line* close_block
param_list: (param ("," param)*)?
param: var_name type_usage
open_params: "("
close_params: ")"
open_block: "{"
close_block: "}"

func_call: var_usage "(" _expr_list? ")"
_PRINT.2: "print"
print_stmt: _PRINT "(" _NEWLINE? _expr_list? ")"
_expr_list: expr ("," _NEWLINE? expr)*

if_expr: "if" expr "{" if_body "}" else_expr
if_body: _line*
else_expr: ("else" "{" _else_body "}")?
_else_body: _line*

field_access: ( var_usage
              | func_call
              | record_literal
              | record_update
              | field_access ) ("." NAME)

string_concat: primary "<>" primary

BOOL.2: "true"
      | "false"

_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+
COMMENT: /#[^\n]*/

DECIMAL: UINT "." UINT
_EXP: ("e"|"E") ["+" | "-"] INT
UFLOAT: INT _EXP | DECIMAL _EXP?
FLOAT: ["+" | "-"] UFLOAT

%import common.CNAME -> NAME
%import common.INT -> UINT
%import common.SIGNED_INT -> INT
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING

%ignore WS_INLINE