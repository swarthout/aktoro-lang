// Grammar for Aktoro Language

program: _line*

_line: _NEWLINE
     | stmt _NEWLINE?

?stmt: var_decl
     | expr
     | type_decl
     | func_def
     | print_stmt
     | return_stmt

var_decl: VAR_NAME "=" expr                          -> var_decl
        | "{" VAR_NAME ("," VAR_NAME)* "}" "=" expr  -> record_destruct_decl
        | "[" VAR_NAME ("," VAR_NAME)* (SINGLE_PIPE VAR_NAME )? "]" "=" expr  -> list_destruct_decl

SINGLE_PIPE: "|"
var_name: VAR_NAME
var_usage: VAR_NAME

?non_record_expr: pipe_expr
?record_expr: pipe_record_expr
?expr: record_expr | non_record_expr
?pipe_expr: logical_expr ( _PIPE_FORWARD caller _NEWLINE?)*

?logical_expr: equality_expr ( ( AND | OR ) equality_expr)*

?equality_expr: add_expr ( ( COMP_EQU
                           | COMP_NEQU
                           | COMP_GTR
                           | COMP_GTE
                           | COMP_LESS
                           | COMP_LTE ) add_expr )*

?add_expr: mult_expr ( ( PLUS | MINUS ) mult_expr )*
?mult_expr: primary ( ( MULTIPLY | DIVIDE | REMAINDER) primary )*

?primary: "(" expr ")" -> paren_expr
        | INT          -> int_literal
        | FLOAT        -> float_literal
        | BOOL         -> bool_literal
        | PRINT        -> print_func
        | var_usage
        | string_literal
        | list_literal
        | dict_literal
        | variant_literal
        | func_call
        | list_cons
        | dict_update
        | index_expr
        | if_expr
        | field_access
        | string_concat
        | builtin_func_call
        | NOT expr     -> not_expr
        | match_expr

?pipe_record_expr: equality_record_expr ( _PIPE_FORWARD caller _NEWLINE?)*
?equality_record_expr: record_literal_expr ( ( COMP_EQU | COMP_NEQU )  record_literal_expr )*

?record_literal_expr: record_literal
                    | record_update
                    | literal_field_access

string_literal: STRING

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
REMAINDER: "%"
NOT.2: "not"
AND.2: "and"
OR.2: "or"

?caller: func_call
       | print_stmt
       | builtin_func_call

list_literal: "[" _NEWLINE? list_elems _NEWLINE? "]" (":" type_usage)?
list_elems: (expr ("," _NEWLINE? expr)*)?

list_cons: "[" _NEWLINE? cons_args "|" expr _NEWLINE? "]"
cons_args: expr ("," _NEWLINE? expr)*

dict_literal: "%{" _NEWLINE? kv_pair_list _NEWLINE? "}" (":" type_usage)?
kv_pair_list:  (kv_pair ("," _NEWLINE? kv_pair)*)?
kv_pair: expr "=>" expr

dict_update: "%{" expr "|" kv_pair ("," _NEWLINE? kv_pair)* "}"

index_expr: ( var_usage
            | list_literal
            | dict_literal
            | string_literal
            | func_call
            | field_access ) "[" ( expr | range_index ) "]"

range_index: low ".." high
low: expr?
high: expr?

type_decl: "type" type_name type_params "=" (record_def | variant_def)
type_name: TYPE_NAME
type_params: _name*
_name: VAR_NAME | TYPE_NAME

type_usage: _t
_t: _name
  | _t _t
  | paren_type
  | func_type
  | list_type
  | dict_type

paren_type: "(" _t ")" -> type_usage

func_type: "(" "(" type_list? ")" "->" return_type ")"
         | "(" type_usage "->" return_type ")"

type_list: type_usage ("," type_usage)*

list_type: "[" type_usage "]"
dict_type: "%{" type_usage "=>" type_usage "}"

record_def: "{" _NEWLINE? field_list _NEWLINE? "}"
field_list: field_decl ("," _NEWLINE? field_decl)*
field_decl: VAR_NAME ":" type_usage

variant_def: variant_constructor ("|" variant_constructor)+
variant_constructor: TYPE_NAME type_usage*

variant_literal: TYPE_NAME ( expr | "_")*

record_literal: "{" _NEWLINE? field_assignment ("," _NEWLINE? field_assignment)* _NEWLINE? "}"
field_assignment: field_name ":" expr
field_name: VAR_NAME

record_update: "{" expr "|" field_assignment ("," _NEWLINE? field_assignment)* "}"

func_def: func_header "->" func_body
func_header: func_signature _NEWLINE VAR_NAME "(" params ")"

func_signature: VAR_NAME ":" param_types "->" return_type

param_types: "(" (param_type ("," param_type )*)? ")"
           | param_type

?return_type: param_type
            | empty_tuple

?param_type: type_usage

?func_body: block
           | non_record_expr     -> simple_return
           | "(" record_expr ")" -> simple_return


block: open_block _NEWLINE? _line* close_block
open_block: "{"
close_block: "}"

params: (param ("," param)*)?
?param: var_name
open_params: "("
close_params: ")"
empty_tuple: "(" ")"

func_call: var_usage "(" _expr_list? ")"

LIST.2: "list"
DICT.2: "dict"
?builtin_module_name: LIST | DICT
builtin_func_call: builtin_module_name "." VAR_NAME "(" _expr_list? ")"

PRINT.2: "print"
print_stmt: PRINT "(" _NEWLINE? _expr_list? ")"
_expr_list: expr ("," _NEWLINE? expr)*

return_stmt: "return" expr

if_expr: "if" expr "{" if_body "}" else_expr
if_body: _line*
else_expr: ("else" "{" _else_body "}")?
_else_body: _line*

match_expr: "match" test_expr? "{" _NEWLINE? match_patterns _NEWLINE? "}"
test_expr: expr
match_patterns:  (pattern ("," _NEWLINE? pattern)*)
pattern: expr "=>" pattern_body
       | UNDERSCORE "=>" pattern_body -> pattern_default

UNDERSCORE: "_"
pattern_body: non_record_expr
            | "(" record_expr ")"
            | print_stmt
            | return_stmt
            | "{" _line* "}"


field_access: ( var_usage
              | func_call
              | field_access ) "." VAR_NAME

literal_field_access: ( record_literal | record_update ) "." VAR_NAME -> field_access

string_concat: primary "<>" primary

BOOL.2: "true"
      | "false"

_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+
COMMENT: /#[^\n]*/

DECIMAL: UINT "." UINT
_EXP: ("e"|"E") ["+" | "-"] INT
UFLOAT: INT _EXP | DECIMAL _EXP?
FLOAT: ["+" | "-"] UFLOAT

LCASE_LETTER: "a".."z"
UCASE_LETTER: "A".."Z"
DIGIT: "0".."9"

LETTER: UCASE_LETTER | LCASE_LETTER

TYPE_NAME: UCASE_LETTER (LETTER|DIGIT)*

VAR_NAME: LCASE_LETTER ("_"|LCASE_LETTER|DIGIT)*

%import common.INT -> UINT
%import common.SIGNED_INT -> INT
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING

%ignore WS_INLINE