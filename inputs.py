def get_input(prompt= "", type_func=float, allow_back=False):
    while True:
        value = input(prompt).strip().lower()
        if allow_back and value == "back":
            return "BACK"
        try:
            value = type_func(value)
            if value <= 0:
                raise ValueError
            return value
        except:
            print("Please enter a valid positive number." if type_func == float else "Please enter a valid positive integer.")
