type car = {name string, miles int}

type user = {user_id string, age int, car car}

let u = {
        user_id = "Scott",
        age = 21,
        car = {
            name = "Mustang",
            miles = 12345
         }
    }

print(u.car.miles)