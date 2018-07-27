type BinaryTree a = Node (BinaryTree a) (BinaryTree a) | Leaf a

type Car = {
    name: String,
    my_year: Option Int,
    owners: [String]
}

d = %{
    2 => "two"
}
e = %{d | 3 => "three"}
print(e, 2)

c = {name: "Mustang", my_year: Some 2013, owners: ["Scott", "Jake"]}

print(c)
print([1, 2, 3])
get_name: Car -> String
get_name c -> c.name

get_name_destruct: Car -> String
get_name_destruct {name} -> name

print(get_name(c))
print(get_name_destruct(c))

a = Node (Leaf "Hi") (Leaf "Bye")

print_tree : BinaryTree a -> ()
print_tree t -> {
    match t {
        Node left right => {
            print_tree(left)
            print_tree(right)
        },
        Leaf val => print(val)
    }
}

print_tree(a)

print(a)