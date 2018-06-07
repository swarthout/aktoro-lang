type car = {name string, year int}

let first = fn (b list (list car)) car => {
   {name="Mustang", year=2013}
}

let add = fn (a int, b int) int => { a + b }

let a = [] :: list int

let d = %{
    1 => "one",
    2 => "two",
    3 => "three"
}

let e = %{} :: dict int string

let my_car = {name="Mustang", year=2013}
print(first([[my_car]]))
print(a, my_car.name)
print(add(4, 5))
print(d, e)