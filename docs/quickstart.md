---
id: quickstart
title: Quick Start
sidebar_label: Quick Start
---

## Install Othello

1. Prepare Golang environment
    - Install Golang >= 1.9
    - Make sure $GOPATH in your shell's config file( like .bashrc) is correct
    - Add you $GOPATH/bin to $PATH
2. Run `go get github.com/othello-lang/othello`

3. Set the Othello project's exact root path $OTHELLO_ROOT manually, which should be:
```sh
$GOPATH/src/github.com/othello-lang/othello
```

Let's make sure Othello is set up as expected. You should see a similar version number in your terminal:

```sh
$ othello version
othello version 0.1 linux/amd64
```

## Writing your first Othello program

Create a new file named `favorite-number.ol` and copy and paste the following:
```
import rand from "std/math/rand"

let get_random_number = fn () => {
     "My favorite number is \(rand.int(10))"
}

get_random_number()
```

## Compile and run

```sh
$ othello run favorite-number.ol
My favorite number is 10

$ othello build favorite-number.ol
$ ls
favorite-number.ol  favorite-number

$ ./favorite-number
My favorite number is 10
```
