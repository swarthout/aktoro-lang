type Message interface {
	message()
}

type Push struct {
	A interface{}
}
  
 func (Push) message() {}

 type Pop struct {}

 func (Pop) message() {}

 type GetTop struct {}

 func (GetTop) message() {}

 type State struct {
	 data []interface{}
 }

 func Reducer(m Message) State {
	switch m := m.(type) {
	case Push:
	  return State{data: []interface{}{m.A}}
	case Pop:
	  return State{}
	case GetTop:
		return State{}
	}
  }