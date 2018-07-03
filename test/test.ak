add :: (Int, Int) -> Int
add (a, b) -> (a + b)

type Car = {
    name String,
    year Int
}

type Person = {
    first_name String,
    last_name String,
    car Car
}

first :: [Car] -> Car
first (c) -> {
    print("Hello from the first function!")
    c[0]
}

look_up :: (%{Int => String}, Int) -> String
look_up (d, i) -> {
    d[i]
}

append_string :: (String, String) -> String
append_string(s, t) -> (s <> t)

apply_first :: ([String], ((String, String) -> String)) -> String
apply_first (l, f) -> {
    f(l[0], "world")
}

me = {
  first_name: "Scott",
  last_name: "Swarthout",
  car: {
    name: "Mustang",
    year: 2013
  }
}

numbers = %{
    2 => "two",
    3 => "three",
    4 => "four"
}

cars = [
  { name: "Mustang", year: 2013 },
  { name: "Wrangler", year: 1990 },
  { name: "Corvette", year: 1991 }
]

print(apply_first(["Hello", "Waynes"], append_string))
print(look_up(numbers, 3))
print(me.car.year)
print(first(cars).year)
print(add(3, 4))

mustang = { name: "Mustang", year: 2013 }

new_mustang = { mustang | year: 2018 }
print(new_mustang)

if new_mustang.year > 2015 {
   print("hello from new mustang")
}

month = 3

season = if month >= 6 { "spring" } else { "fall" }
print(season)

print("Hello" <> "World")

double :: Int -> Int
double (x) -> (x * 2)

print(3 * (4 + 5 * 2))

print(double(add(3, 2)))

ten = 3
      |> add(2)
      |> double()


print(ten)

3 |> add(2) |> double() |> print()

type Thing = {a Int, b String}

get_thing :: () -> Thing
get_thing () -> ({ a: 4, b: "hey" })
print(get_thing())

is_even :: Int -> Bool
is_even (x) -> (x % 2 == 0)


new_car :: Car -> Bool
new_car (c) -> (c.year >= 2000)
xs = [0, 1, 2, 3, 4, 5, 6]
evens = xs |> list.filter(is_even)
print(evens)

empty_list = [] :: [Int]
empty_list |> list.filter(is_even) |> print()

empty_list |> list.map(double) |> print()

twice = list.map(xs, double)
print("twice: ", twice)

list.each([1, 2, 3], print)

print(xs[2..])
print(xs[1..4])
print(xs[..3])

cars |> list.filter(new_car) |> print()


cars |> list.drop_while(new_car) |> print()
print(not new_car({ name: "Mustang", year: 2013 }) and true)

print("hello"[0])
print("hello"[1..])
n = "Mustang"
match {
    n == "Corvette" => print("n is Corvette"),
    20 > 18 => {
        print("20 > 18")
    }
}

number = "five"
value = match number {
    "three" => 3,
    "four"  => 4,
    "five"  => 5,
    _       => 0
}
print(value)

{name, year} = mustang
print(name, year)
[x, y | rest] = xs
print(x, y, rest)

[a | b] = [1]
print(a, b)