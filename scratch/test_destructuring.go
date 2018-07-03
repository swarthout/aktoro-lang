package main

import (
	"fmt"
)

type Vertex struct {
	x, y int
}

func main() {
	var x, y int
	{
		v := Vertex{2, 3}
		x = v.x
		y = v.y

	}
	v := Vertex{0, 0} // Name does not collide
	fmt.Println(v)
	fmt.Println(x, y)
}

/*
type Vertex = { x int, y int }
v = { x: 2, y: 3 }
{ x, y } = v
print(x, y)
*/