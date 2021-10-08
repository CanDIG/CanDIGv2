AGE = {
    "description": "An ISO8601 duration string (e.g. P40Y10M05D for 40 years, 10 months, 5 days) representing an age "
                   "of a subject.",
    "help": "Age of a subject."
}

AGE_RANGE = {
    "description": "Age range of a subject (e.g. when a subject's age falls into a bin.)",
    "properties": {
        "start": "An ISO8601 duration string representing the start of the age range bin.",
        "end": "An ISO8601 duration string representing the end of the age range bin."
    }
}

AGE_NESTED = {
    "description": AGE["description"],
    "properties": {
        "age": AGE
    }
}
