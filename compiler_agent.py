import tempfile
import os
import subprocess

from state import AgentState, Language
from util import get_code_by_task

def compile_code(state : AgentState) -> bool:
    code = None
    code = get_code_by_task(state)
    
    if not code:
        raise ValueError("No code available for compilation.")

    # Determine the language and check compilation accordingly
    if state.router.target_language == Language.JAVA:
        compilation_success = check_java_compilation(code)
    elif state.router.target_language == Language.PYTHON:
        compilation_success = check_python_compilation(code)
    else:
        raise ValueError(f"Unsupported language: {state.router.target_language}")
    
    return compilation_success

def check_java_compilation(java_code):
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the Java code to a .java file
        file_path = os.path.join(tmpdir, "Solution.java")
        with open(file_path, "w") as f:
            f.write(java_code)

        # Try to compile the Java file
        try:
            # Use subprocess to run javac
            compile_process = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True,
                check=False # Do not raise an exception for non-zero exit codes
            )
            # If javac returns 0, compilation was successful
            if compile_process.returncode == 0:
                return True
            else:
                # print(f"Compilation error: {compile_process.stderr}")
                return False
        except FileNotFoundError:
            print("Error: javac command not found. Make sure Java Development Kit (JDK) is installed and in your PATH.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during compilation check: {e}")
            return False
        
def check_python_compilation(python_code):
    try:
        # Try to compile the Python code
        compile(python_code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        # print(f"Compilation error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during compilation check: {e}")
        return False