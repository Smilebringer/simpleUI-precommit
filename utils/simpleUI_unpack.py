import json
import base64
import os
import logging
import shutil

# Set up the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the modules folder as a variable
modules_folder = "modules"

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.debug(f"Failed to delete {file_path}. Reason: {e}")

def extract_and_save_py_files(ui_files):
    """Extracts PyFileData from a list of JSON files, decodes it, saves it as .py files,
    replaces PyFileData with the file path, and saves a new JSON file."""
    
    for json_file in ui_files:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if isinstance(data, dict) and "ClientConfiguration" in data and "PyFiles" in data["ClientConfiguration"]:
            py_files = data["ClientConfiguration"]["PyFiles"]
        else:
            continue
        
        # Extract the directory of the original .ui file to match the subfolder structure
        ui_file_directory = os.path.dirname(json_file)
        output_folder = os.path.join(os.getcwd(), ui_file_directory, modules_folder)

        # Ensure the subfolder in modules exists
        os.makedirs(output_folder, exist_ok=True)  
        clear_folder(output_folder)
        
        for entry in py_files:
            if "PyFileKey" in entry and "PyFileData" in entry:
                file_name = f"{entry['PyFileKey']}.py"
                file_path = os.path.join(output_folder, file_name)
                
                with open(file_path, "wb") as py_file:
                    py_file.write(base64.b64decode(entry["PyFileData"]))
                
                entry["PyFileData"] = os.path.join(output_folder, entry['PyFileKey'])
                logger.debug(f"Saved: {file_path}")
        
        unpacked_file = json_file.replace(".ui", "_unpacked.ui")
        with open(unpacked_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)  # Use utf-8 and ensure non-ASCII characters are preserved
        logger.debug(f"Updated JSON saved: {unpacked_file}")

def find_ui_files(directory):
    """Finds all .ui files in a given directory and its subdirectories, 
    excluding those with the _unpacked postfix."""
    ui_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ui") and "_unpacked" not in file:
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                ui_files.append(relative_path)
    
    return ui_files

# Example usage
if __name__ == "__main__":
    directory_to_search = "."  # Use current directory
    ui_files = find_ui_files(directory_to_search)
    logger.debug(f"Found .ui files: {ui_files}")
    
    extract_and_save_py_files(ui_files)