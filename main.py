import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sys import argv
# from subdirectory.filename import function_name
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

work_dir = "./calculator"

model_name = "gemini-2.0-flash-001"
system_prompt = system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
#  Function declaraions: 

# Get File Info
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

# Get File Content

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get the file contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The full path to file you need to get contents of, relative to the working directory. Must be supplied!",
            ),
        },
    ),
)

# Run Python file

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file and return results.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The full path to file you want to run, relative to the working directory. Must be supplied!",
            ),
        },
    ),
)

# Write file

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write to a file to update content.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The full path to file you want to write to (either existing or new), relative to the working directory. Must be supplied!",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content that will be written/overwritten to specified file. Must be supplied!",
            ),
        },
    ),
)
# List of functions available to LLM - List functions above!

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# Helper function to handle running the actual functions suggested by model

def call_function(function_call_part, verbose=False):
    func_name = function_call_part.name
    func_kw = function_call_part.args
    # print(f"KW Args: {func_kw}")
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
        
    match function_call_part.name:
        case "get_files_info":
            function_result = get_files_info(working_directory=work_dir,**func_kw)
            # print(f"Func Result: {function_result}")
        case "get_file_content":
            function_result = get_file_content(working_directory=work_dir,**func_kw)
        case "write_file":
            function_result = write_file(working_directory=work_dir,**func_kw)
        case "run_python_file":
            function_result = run_python_file(working_directory=work_dir,**func_kw)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=func_name,
                        response={"error": f"Unknown function: {func_name}"},
                    )
                ],
            )
        
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=func_name,
                response={"result": function_result},
            )
        ],
    )
    
# Logic for prompt below

# Check if any prompt actually input, if not exit gracefull

if len(argv) == 1:
    print ("No prompt input!")
    exit(1)
else:
    user_prompt = argv[1]

# Submit prompt to the model and get response

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

for i in range(1,20):    
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt),
    )
    
    if response.candidates is not None:
        for c in response.candidates:
            # print(f"Response: {c}")
            messages.append(c.content)
    
    # Process response - Need to check if agent asking to run a function and get those results
    if response.function_calls is not None:
        function_call_part = response.function_calls[0]
        function_call_content = response.candidates[0].content
        if "--verbose" in argv:
            function_call_result = call_function(function_call_part,True)
        else:
            function_call_result = call_function(function_call_part)
        
        # Add function call results to the messages list to return to model
        messages.append(function_call_result)
        
        if function_call_result.parts[0].function_response.response:
            if "--verbose" in argv:
                print(f"-> {function_call_result.parts[0].function_response.response}")
        else:
            raise Exception("Fatal Error! No valid response")
    else:
        print(response.text)
        break

# Check if asked for verbose output, will print the prompt and API token use stats

if "--verbose" in argv:
    print (f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")



