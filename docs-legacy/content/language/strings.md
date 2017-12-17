---
menu:
  docs:
    parent: "language"
    weight: 20
title: Strings
weight: 40
---
Othello strings are delimited with double quotes.
```
let street_address = "42 Wallaby Way, Sydney"
```

Special characters need to be delimited. Escape characters include:
`\n`, `\t`, `\\`, and `\"`

String concatenation uses the `<>` operator.
```
let first_name = "Johnny"
let last_name = "Appleseed"
let full_name = first_name <> " " <> last_name
```