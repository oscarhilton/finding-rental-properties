import os
import json

def compile_folder_to_json(folder_path, output_file):
    compiled_data = []

    if not os.path.isdir(folder_path):
        print("Error: Folder not found.")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        try:
            # Read the file with UTF-8 encoding
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read().replace('\n', '')  # Strip newlines

                # Attempt to load as JSON, if it is valid JSON
                try:
                    json_data = json.loads(file_content)
                    compiled_data.append(json_data)
                except json.JSONDecodeError:
                    print(f"Skipping {filename} (invalid JSON format)")

        except Exception as e:
            print(f"Skipping {filename}: {e}")

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(compiled_data, json_file, indent=4, ensure_ascii=False)

    print(f"JSON file saved as {output_file}")

# Example usage
folder_path = "./maps"  # Change this to your folder path
output_file = "compiled.json"  # Change this to your desired output file
compile_folder_to_json(folder_path, output_file)
