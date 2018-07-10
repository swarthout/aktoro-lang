type HashMap k v = {keys: [k], val: v}

type Car = {
    name: String,
    year: Int
}

numbers = %{
    2 => "two",
    3 => "three",
    4 => "four"
}

more_numbers = %{ numbers | 5 => "five"}
print(more_numbers)

h = {keys: ["Hello", "Everyone"], val: 4}

first : [a] -> a
first (xs) -> {
    xs[0]
}

first_hashmap : HashMap a Int -> a
first_hashmap (h) -> first(h.keys)

print(first_hashmap(h))

print({keys: ["Hello", "Everyone"], val: 4}.val)