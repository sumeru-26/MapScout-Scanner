import cv2
import os
import numpy as np
from pyzbar.pyzbar import decode
import base64
import json

# Define the image path
image_path = os.path.join(os.path.dirname(__file__), 'image.png')

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

# Check if the image file exists
if not os.path.exists(image_path):
    print(f"Error: Image file not found at {image_path}")
    exit()

# Load the image
image = cv2.imread(image_path)

if image is None:
    print(f"Error: Could not read image from {image_path}")
    exit()

# Decode QR codes
decoded_objects = decode(image)
print(f"Number of codes detected: {len(decoded_objects)}")

# Process results
if len(decoded_objects) > 0:
    for i, obj in enumerate(decoded_objects):
        # Print data
        data = obj.data.decode('utf-8')
        type_name = obj.type
        print(f"Code {i+1} ({type_name}): {data}")
        
        # Try to process as JSON if it's a QR code
        try:
            # Decode base64 data
            decoded = base64.b64decode(data)
            
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
                
                print(f"Appended JSON data from code {i+1} to top of data.json")
            else:
                print(f"Duplicate JSON data detected in code {i+1} - not appending")
                
        except Exception as e:
            print(f"Error processing JSON data from code {i+1}: {e}")
        
        # Draw rectangle
        points = obj.polygon
        if len(points) > 0:
            # Convert points to a format suitable for cv2.polylines
            pts = [(p.x, p.y) for p in points]
            pts = np.array(pts, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 3)
            
        # Add text label
        x, y, w, h = obj.rect
        cv2.putText(image, f"{type_name}: {data[:20]}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Show the image with codes highlighted
    cv2.imshow('Code Scanner - Results', image)
    cv2.waitKey(0)  # Wait until a key is pressed
    
    # Save the annotated image
    output_path = os.path.join(os.path.dirname(__file__), 'result.png')
    cv2.imwrite(output_path, image)
    print(f"Annotated image saved as {output_path}")
else:
    print("No codes detected in the image.")
    cv2.imshow('Code Scanner - No Codes Detected', image)
    cv2.waitKey(0)

cv2.destroyAllWindows()