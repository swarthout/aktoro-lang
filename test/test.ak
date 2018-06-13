type car = {name string, year int}

let first = fn (cars list (list car)) car => {
    print(cars)
    {name="Mustang", year=2013}
}
let cars = [[{name="Mustang", year=2013}, {name="Wrangler", year=1990}]]
first(cars)