import os
import json
import base64

def process_base64_input(base64_input):
    """Process a base64 input string and append the JSON data to data.json"""
    
    # Path to the data.json file
    json_file_path = os.path.join(os.path.dirname(__file__), "data.json")
    
    # Load existing JSON data or create empty list
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []
    
    # Keep track of already processed JSON strings to prevent duplicates
    processed_json_strings = set()
    
    # Add existing items to processed set to prevent duplicating previous entries
    for item in existing_data:
        # Convert each item to a consistent string representation for comparison
        json_str = json.dumps(item, sort_keys=True)
        processed_json_strings.add(json_str)
    
    try:
        # Decode base64 data
        decoded = base64.b64decode(base64_input)
        
        # Parse the decoded data as JSON string
        json_data = decoded.decode('utf-8')
        
        # Parse JSON string to object
        json_obj = json.loads(json_data)
        
        # Convert to standardized string for duplicate comparison
        json_str = json.dumps(json_obj, sort_keys=True)
        
        # Check if we've seen this JSON content before
        if json_str not in processed_json_strings:
            # Add to the beginning of existing data
            existing_data.insert(0, json_obj)
            
            # Mark as processed
            processed_json_strings.add(json_str)
            
            # Write back to file
            with open(json_file_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print("Appended new JSON data to top of data.json")
            return True, "Success: Data was added to data.json"
        else:
            print("Duplicate JSON data - not appending")
            return False, "Warning: Duplicate JSON data - not appended"
            
    except base64.binascii.Error:
        error_msg = "Error: Invalid base64 encoding"
        print(error_msg)
        return False, error_msg
    except UnicodeDecodeError:
        error_msg = "Error: Could not decode data as UTF-8"
        print(error_msg)
        return False, error_msg
    except json.JSONDecodeError:
        error_msg = "Error: Decoded data is not valid JSON"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error processing data: {str(e)}"
        print(error_msg)
        return False, error_msg

def main():
    print("MapScout Text Input Processor")
    print("Enter or paste a base64 encoded string (press Ctrl+D or Ctrl+Z to submit):")
    
    # Collect multiline input from user
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    # Join all lines and remove any whitespace
    base64_input = ''.join(lines).strip()
    
    if not base64_input:
        print("Error: No input provided")
        return
    
    print("\nProcessing input...")
    success, message = process_base64_input(base64_input)
    
    if success:
        print(message)
    else:
        print(f"Failed: {message}")

if __name__ == "__main__":
    main()