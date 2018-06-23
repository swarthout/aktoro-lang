
import "fmt"

type myInt int

func (y *myInt) String() string {
	return "hello"
}

type thing struct {
	name  string
	other *myInt
}

func main() {
	x := myInt(42)
	myThing := thing{"scott", &x}
	fmt.Printf("{name=%v, other=%v}", myThing.name, myThing.other)
}
