import os
import subprocess

def run_python_file(working_directory, file_path):
    output = []
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    file_dir = os.path.dirname(target_file)
    
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File "{file_path}" not found.'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        result = subprocess.run(["python3",target_file],timeout = 30,capture_output = True,cwd = file_dir, text = True)
        if result.stdout != "":
            output.append(f"STDOUT: {result.stdout}")
        if result.stderr != "":
            output.append(f"STDERR: {result.stderr}")
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")
        if len(output) == 0:
            return "No output produced"
        return "\n".join(output)
    except Exception as e:
        return f"Error: executing Python file: {e}"
    