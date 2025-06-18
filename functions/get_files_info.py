import os

def get_files_info(working_directory, directory=None):
    rel_path = os.path.join(working_directory,directory)
    abs_path = os.path.abspath(rel_path)
    
    # print(f"Rel Path: {rel_path}")
    # print(f"Abs Path: {abs_path}")
    
    if not os.path.isdir(abs_path) or directory.startswith(".."):
        return f'Error: "{directory}" is not a directory'
    
    if not os.path.isdir(abs_path) or directory.startswith("/"):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
      
    if os.path.isdir(abs_path):
        items = []
        dir_content = []
        items = os.listdir(abs_path)
        for i in range(0,len(items)):
            dir_content.append(f"- {items[i]}: file_size={os.path.getsize(os.path.join(abs_path,items[i]))} bytes, is_dir={os.path.isdir(os.path.join(abs_path,items[i]))}")
        return "\n".join(dir_content)
    