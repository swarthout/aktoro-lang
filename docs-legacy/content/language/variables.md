---
menu:
  docs:
    parent: "language"
    weight: 10
title: Variables
weight: 30
---
#### Let Binding

Variables are declared with `let`. Let bindings give names to values.

```
let greeting = "hello!"
let score = 10

let new_score = 10 + score
```

#### Mutability
By default, all variables are immutable. To create a mutable variable, the `mut` keyword  can be added to the declaration.

```
let a = 10
a = 40 # ERROR
let mut b = 3
b = 4
```
