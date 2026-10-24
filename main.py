with open("example.py", "r") as file:
    code = file.read()


if __name__ == "__main__":
    exec(code)