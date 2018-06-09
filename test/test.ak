type car = {name string, year int}

let first = fn (b list (list car)) car => {
   {name="Mustang", year=2013}
}

let add = fn (a int, b int) int => { a + b }

let a = [2, 3, 4] :: list int

let d = %{
    "one" => 1,
    "two" => 2,
    "three" => 3
}
print(d["two"])

print(a[1])
let f = -0.5
print(a[..1])

let e = %{} :: dict int string

let my_car = {name="Mustang", year=2013}
print(first([[my_car]]))
print(a, my_car.name)
print(add(4, 5))
print(d, e)
print(f)