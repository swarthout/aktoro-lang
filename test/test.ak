type HashMap k v = { keys [k], val v }

numbers = %{
    2 => "two",
    3 => "three",
    4 => "four"
}

more_numbers = %{ numbers | 5 => "five"}
print(more_numbers)

h = {keys: ["Hello", "Everyone"], val: 4}

first :: [a] -> a
first (xs) -> {
    xs[0]
}

first_hashmap :: HashMap a b -> a
first_hashmap (h) -> {
    first (h.keys)
}

print(first_hashmap(h))

filter :: ([a], (a -> Bool)) -> [a]
filter (xs, f) -> {
    if list.empty(xs) {
        return xs
    }
    [x | rest] = xs
    res = match {
        f(x) => [x | filter(rest, f)],
        _    => filter(rest, f)
    }
    res
}
xs = [1, 2, 3, 4]
x = first(xs)
print(x)

is_even :: Int -> Bool
is_even (x) -> (x % 2 == 0)

print(xs |> filter(is_even))