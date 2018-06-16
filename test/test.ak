type car = {name string, year int}

let first = fn (cars list car) car => {
    cars[0]
}
let cars = [{name="Mustang", year=2013}, {name="Wrangler", year=1990}, {name="Corvette", year=1990}]
let first_car = first(cars)
print(first_car.year)
print(cars[..2])
let numbers = %{
    2 => "two",
    3 => "three",
    4 => "four"
    }

print(numbers)
print(numbers[4])

let more_cars = [{name="Boxster", year=2017}, {name="Malibu", year=2012} | cars]
print(more_cars)
print(cars)

let more_numbers = %{numbers | 5 => "five", 6 => "six"}
print(more_numbers)
print(numbers)

let spanish_five = %{more_numbers | 5 => "cinco"}
print(spanish_five)
print(more_numbers)

let mustang = {name="Mustang", year=2013}
let new_mustang = {mustang | year=2018}
print(new_mustang)

let age = if new_mustang.year > 2015 {
    "new"
    } else { "old" }

#print(age)