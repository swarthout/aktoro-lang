type car = {name string, year int}

#let first = fn (b list car) car => {
#   {name="Mustang", year=2013}
#}

#let add = fn (a int, b int) int => { a + b }

#let a = 4


let c = {name="Mustang", year=2013}
#print(first([c]))
#print(a, c.name)
#print(add(4, 5))