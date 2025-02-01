import json
import base64
import os
import logging

# Set up the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the modules folder as a variable
modules_folder = "modules"

def encode_modules_in_base64(ui_files):
    """Encodes Python files in the 'modules' folder into base64 and updates the .ui files with the encoded data."""
    for json_file in ui_files:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if isinstance(data, dict) and "ClientConfiguration" in data and "PyFiles" in data["ClientConfiguration"]:
            py_files = data["ClientConfiguration"]["PyFiles"]
        else:
            continue
        
        ui_file_directory = os.path.dirname(json_file)
        for entry in py_files:
            if "PyFileKey" in entry and "PyFileData" in entry:
                file_name = f"{entry['PyFileKey']}.py"
                file_path = os.path.join(ui_file_directory, modules_folder, file_name)

                # Check if the file exists in the modules folder
                if os.path.exists(file_path):
                    with open(file_path, "rb") as py_file:
                        # Encode the Python file to base64
                        encoded_data = base64.b64encode(py_file.read()).decode("utf-8")
                    
                    # Update the entry with the encoded base64 data
                    entry["PyFileData"] = encoded_data
                    logger.debug(f"Encoded {file_name} and updated PyFileData")
                else:
                    logger.warning(f"File not found: {file_path}")
        
        repacked_file = json_file.replace("_unpacked.ui", "_repacked.ui")
        with open(repacked_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)  # Use utf-8 and ensure non-ASCII characters are preserved
        logger.debug(f"Repacked JSON saved: {repacked_file}")

def find_unpacked_ui_files(directory):
    """Finds all *_unpacked.ui files in a given directory and its subdirectories."""
    ui_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("_unpacked.ui"):
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                ui_files.append(relative_path)
    
    return ui_files

# Example usage
if __name__ == "__main__":
    directory_to_search = "."  # Use current directory
    ui_files = find_unpacked_ui_files(directory_to_search)
    logger.debug(f"Found *_unpacked.ui files: {ui_files}")
    
    encode_modules_in_base64(ui_files)
