type user = {user_id string, age int}

type account = {id int, person user}

let u = {user_id = "Scott", age = 21}

let a = 4

let x = [u, u]

print(a, x)