---
id: quickstart
title: Quick Start
sidebar_label: Quick Start
---

## Install Aktoro

1. Prepare Golang environment
    - Install Golang >= 1.9
    - Make sure $GOPATH in your shell's config file( like .bashrc) is correct
    - Add you $GOPATH/bin to $PATH
2. Run `go get github.com/aktoro-lang/aktoro`

3. Set the Othello project's exact root path $OTHELLO_ROOT manually, which should be:
```sh
$GOPATH/src/github.com/aktoro-lang/aktoro`
```

Let's make sure Aktoro is set up as expected. You should see a similar version number in your terminal:

```sh
$ aktoro version
aktoro version 0.1 linux/amd64
```

## Writing your first Aktoro program

Create a new file named `favorite-number.ak` and copy and paste the following:
```
import rand from "std/math/rand"

let get_random_number = fn () => {
     "My favorite number is \(rand.int(10))"
}

get_random_number()
```

## Compile and run

```sh
$ aktoro run favorite-number.ak
My favorite number is 10

$ aktoro build favorite-number.ak
$ ls
favorite-number.ak  favorite-number

$ ./favorite-number
My favorite number is 10
```
