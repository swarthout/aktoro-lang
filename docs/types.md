---
id: types
title: Types
---
Othello is a statically typed language, but heavily uses type inference to decrease the amount of typing required to write programs.

## Creating new types
New types can be created with the `type` keyword.
```
type user = {name string, age int, user_id string}

let john = {
  name = "John", 
  age = 17,
  user_id = "johnnyrocket123"
}

john.name   # "John"
john.age    # 17
```

Note `john` does not need to be annotated with the user type. Since the user type is in the same module as john, the type is inferred.