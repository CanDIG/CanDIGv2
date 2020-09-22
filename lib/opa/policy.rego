package permissions

import input

default allowed = false

allowed = true {
    input.name = "bob"
}