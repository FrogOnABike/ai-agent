import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sys import argv
# from subdirectory.filename import function_name
from functions.get_files_info import get_files_info

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


if len(argv) == 1:
    print ("No prompt input!")
    exit(1)
else:
    user_prompt = argv[1]

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents=messages)

print(response.text)

if "--verbose" in argv:
    print (f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
