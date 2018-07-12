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

get_hashmap : () -> HashMap String Int
get_hashmap () -> ({keys: ["Hello", "Everyone"], val: 4})

first_hashmap : HashMap a Int -> a
first_hashmap (h) -> first(h.keys)

print(first_hashmap(h))

print({keys: ["Hello", "Everyone"], val: 4}.val)
print(get_hashmap().val)

type BinaryTree = Node BinaryTree BinaryTree | Leaf Int

t = Node (Leaf 3) (Leaf 4)

print(t)

print_tree : BinaryTree -> ()
print_tree (t) -> {
    match t {
        Node left right => {
            print_tree(left)
            print_tree(right)
        },
        Leaf val => print(val)
    }
}

print_tree(t)

filter : ([a], (a -> Bool)) -> [a]
filter (xs, f) -> {
    if list.empty(xs) {
        return [] : [a]
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

is_even : Int -> Bool
is_even (x) -> (x % 2 == 0)

print(xs |> filter(is_even))