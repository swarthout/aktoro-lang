type Option t = Some t | None

type BinaryTree a = Node (BinaryTree a) (BinaryTree a) | Leaf a

type Car = {
    name: String,
    year: Option Int
}

c = {name: "Mustang", year: Some 2013}
print(c)

a = Node (Leaf "Hi") (Leaf "Bye")

print(a)