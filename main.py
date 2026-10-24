from pathlib import Path

## This will probably have to change to be dynamic, but for now it will just check the current directory for any .py files and read them in. If any of them contain 'eval', it will raise an exception.
folder_path = Path(__file__).parent

def read_code():
    findings = []

    for file_path in folder_path.glob("*.py"):
        if file_path.name != "main.py":
            with open(file_path, "r") as file:
                code = file.read()
                code = code.splitlines()
                for line_number, line in enumerate(code, start=1):
                    if "eval" in line:
                        vulnerability_type = "Use of 'eval' function"
                        findings.append((file_path.name, line_number, vulnerability_type))

    return findings


if __name__ == "__main__":
    read_code()
    print(read_code())
    