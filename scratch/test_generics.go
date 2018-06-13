package main
import (
"fmt"
)

func main() {
        
	isEven := func (params ...interface{}) interface{} {
		a := params[0]
		return a.(int) % 2 == 0
	}
	
	filter := func(p ...interface{}) interface{} {
		l := p[0].([]interface{})
		f := p[1].(func (...interface{}) interface{})
		output := []interface{}{}
		
		for el := range l {
			if f(el).(bool) {
				output = append(output, el)
			}
		}
		return output
	}
	
	fmt.Println(filter([]interface{}{1,2,3}, isEven))
}