---
menu:
  docs:
    parent: "language"
    weight: 30
title: Functions
weight: 40
---
Functions are declared with the `fn` keyword.
```
let greet = fn (name string) => "Hello " <> name
```

This declares a function and assigns it to the name `greet`, which can be called like so:
```
greet ("world!") # "Hello world!
```

If a function does not fit on a single line, a block can be used for the body.
```
let translate_left = fn (x int, y int, delta int) tuple int int => {
  let x_prime = x + delta
  let y_prime = y + delta
  (x, y)
}

(x, y) = translate_left(3, 4, 1) # x = 2, y = 4

pair = translate_left(5, 6, 2)
a = pair[0]
b = pair[1]
```