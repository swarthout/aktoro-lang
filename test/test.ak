let add = fn (a int, b int) int => {
    a + b
}

let get_add_fn = fn () fn (int, int) int => {
    add
}

let also_add = get_add_fn()

print(also_add(3,4))


type car = {name string, year int, owners list string}

type person = {first_name string, last_name string, car car}

let me = {first_name="Scott",
          last_name="Swarthout",
          car={name="Mustang",
               year=2013,
               owners=["Scott"]
               }
          }
print(me.car.year)

let first = fn (cars list car) car => {
    cars[0]
}
let cars = [{name="Mustang", year=2013, owners=["Scott"]},
            {name="Wrangler", year=1990, owners=["Zach", "Tim"]},
            {name="Corvette", year=1990, owners=["Jack"]}]
print(first(cars).year)
print(cars[..2])
let numbers = %{
    2 => "two",
    3 => "three",
    4 => "four"
    }

print(numbers)
print(numbers[4])

let more_cars = [{name="Boxster", year=2017, owners=["Jake"]}, {name="Malibu", year=2012, owners=["Ken"]} | cars]
print(more_cars)
print(cars)

let more_numbers = %{numbers | 5 => "five", 6 => "six"}
print(more_numbers)
print(numbers)

let spanish_five = %{more_numbers | 5 => "cinco"}
print(spanish_five)
print(more_numbers)

let mustang = {name="Mustang", year=2013, owners=["Jake", "Amir"]}
let new_mustang = {mustang | year=2018}
print(new_mustang)
print(new_mustang.owners)

if new_mustang.year > 2015 {
   print("hello from new mustang")
}

let month = 3

let season = if month >= 6 { "spring" } else { "fall" }
print(season)

print("Hello" <> "World")

let double = fn (x int) int => {
    x * 2
}

print(3 * (4 + 5 * 2))

print(double(add(3, 2)))

let ten = 3
          |> add(2)
          |> double()

print(ten)

3 |> add(2) |> double() |> print()

