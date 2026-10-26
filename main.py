import ast
import os
import sys
import itertools
import threading


from dotenv import load_dotenv
from pathlib import Path


from google import genai
from gemPrompt import gemPrompt

folder_path = Path(__file__).parent

load_dotenv()  # Load environment variables from .env file


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = "gemini-3.8-flash"


def spinning_cursor(stop_event: threading.Event):
    spinner = itertools.cycle(["/", "-", "\\", "|"])
    while not stop_event.wait(0.1):
        sys.stdout.write(f"\rWaiting for Gemini... {next(spinner)}")
        sys.stdout.flush()

    sys.stdout.write("\r" + " " * 32 + "\r")
    sys.stdout.flush()



class VulnerabilityDetector(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def visit_Call(self, node: ast.Call):
        # Pass code to the Gemini API for analysis
        code_snippet = ast.unparse(node)
        response = client.interactions.create(
            model=model_name,
            input=(
                f"{gemPrompt}\n{code_snippet}\n"
                "----- END UNTRUSTED SOURCE CODE -----"
            ),
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 1024,
            },
        )
        if not response.output_text:
            raise RuntimeError(
                f"Gemini returned no analysis for the call at line {node.lineno}."
            )

        self.findings.append(
            (node.lineno, code_snippet, response.output_text)
        )
        self.generic_visit(node)


def read_code():
    findings = []

    for file_path in folder_path.glob("*.py"):
        if file_path.name != "main.py":
            with open(file_path, "r") as file:
                code = file.read()
                tree = ast.parse(code)
                detector = VulnerabilityDetector()
                detector.visit(tree)
                findings.extend(
                    (file_path.name, lineno, code_snippet, analysis)
                    for lineno, code_snippet, analysis in detector.findings
                )

    return findings


if __name__ == "__main__":
    print("=================================================================")
    print()
    print(" ██████╗███████╗██████╗ ██████╗ ███████╗██████╗ ██╗   ██╗███████╗") 
    print("██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝")
    print("██║     █████╗  ██████╔╝██████╔╝█████╗  ██████╔╝██║   ██║███████╗")
    print("██║     ██╔══╝  ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║   ██║╚════██║")
    print("╚██████╗███████╗██║  ██║███████║███████╗██║  ██║╚██████╔╝███████║")
    print(" ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝")
    print("=================================================================")
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=spinning_cursor,
        args=(stop_spinner,),
    )
    spinner_thread.start()
    try:
        findings = read_code()
    finally:
        stop_spinner.set()
        spinner_thread.join()

    for file_name, lineno, code_snippet, analysis in findings:
        print(f"\nGemini analysis for {file_name}, line {lineno}:")
        print(f"Code: {code_snippet}")
        print(analysis)