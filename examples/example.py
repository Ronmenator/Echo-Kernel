from tools.code_interpreter import CodeInterpreter

def main():
    # Create an instance of the code interpreter
    interpreter = CodeInterpreter()

    # Example 1: Simple Python code
    code1 = """
print("Hello, World!")
x = 5 + 3
print(f"The sum is: {x}")
"""
    stdout, stderr = interpreter.execute_code(code1)
    print("Example 1 Output:")
    print(stdout)
    if stderr:
        print("Errors:", stderr)
    print("-" * 50)

    # Example 2: Code with an error
    code2 = """
def calculate():
    return 10 / 0

result = calculate()
print(result)
"""
    stdout, stderr = interpreter.execute_code(code2)
    print("Example 2 Output:")
    print(stdout)
    if stderr:
        print("Errors:", stderr)

if __name__ == "__main__":
    main() 