type car = {name string, year int}

let first = fn (a list (list car)) int => {
   print("I'm in the first function!")
   0
}



let a = 4


let c = {name="Mustang", year=2013}
print(first([[c]]))
print(a, c.name)