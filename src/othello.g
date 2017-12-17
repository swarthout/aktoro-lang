// Grammar for Othello Language

program: _line*

_line: _NEWLINE
     | stmt

?stmt: decl _NEWLINE?

decl: "let" NAME "=" expr

expr: NUMBER -> number
    | NAME   -> var
    | STRING -> string


_NEWLINE: ( /\r?\n[\t ]*/ | COMMENT )+

COMMENT: /#[^\n]*/

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE
%import common.ESCAPED_STRING -> STRING

%ignore WS_INLINE