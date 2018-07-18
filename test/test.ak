type BinaryTree a = Node (BinaryTree a) (BinaryTree a) | Leaf a

type Car = {
    name: String,
    year: Option Int
}

c = {name: "Mustang", year: Some 2013}
print(c)

a = Node (Leaf "Hi") (Leaf "Bye")

print_tree : BinaryTree a -> ()
print_tree (t) -> {
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