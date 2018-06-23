package main

import (
	"container/list"
	"fmt"
)

func main() {

	isEven := func(p0 interface{}) interface{} {
		a := p0.(int)
		return a%2 == 0
	}

	filter := func(p0 interface{}, p1 interface{}) interface{} {
		l := p0.(*list.List)
		f := p1.(func(interface{}) interface{})
		output := []interface{}{}

		for e := l.Front(); e != nil; e = e.Next() {
			if f(e.Value).(bool) {
				output = append(output, e.Value)
			}
		}
		return output
	}

	l := list.New()
	l.PushBack(4)
	l.PushFront(1)

	fmt.Println(filter(l, isEven))
}
