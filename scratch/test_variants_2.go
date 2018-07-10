package main

import "fmt"

type BinaryTree interface {
	BinaryTree()
}

type Node struct {
	p0 BinaryTree
	p1 BinaryTree
}

func (Node) BinaryTree() {}

type Leaf struct {
	p0 int
}

func (Leaf) BinaryTree() {}

func Print(t BinaryTree) {
	switch t := t.(type) {
	case Node:
		left := t.p0
		right := t.p1
		Print(left)
		Print(right)
	case Leaf:
		val := t.p0
		fmt.Println(val)
	}
}
func main() {
	tree := Node{Leaf{1}, Leaf{2}}
	Print(tree)
}
