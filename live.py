import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import base64
import json

# Try with DirectShow backend for better compatibility on Windows
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open camera. Trying default backend...")
    cap = cv2.VideoCapture(0)  # Try with default backend
    
    if not cap.isOpened():
        print("Error: Failed to access camera with both backends.")
        exit()

# Set resolution to something common that most cameras support
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# To save detected QR codes (avoid duplicates)
last_codes = set()
save_results = True
result_folder = os.path.join(os.path.dirname(__file__), "results")

# Create results folder if it doesn't exist
if save_results and not os.path.exists(result_folder):
    os.makedirs(result_folder)

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
# We'll store them as string representations for comparison
processed_json_strings = set()

# Add existing items to processed set to prevent duplicating previous entries
for item in existing_data:
    # Convert each item to a consistent string representation for comparison
    json_str = json.dumps(item, sort_keys=True)
    processed_json_strings.add(json_str)

print("QR Code Scanner Started")
print("Press 'ESC' to exit, 's' to save current frame")

while True:
    # Read the current frame
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame from camera")
        break
    
    # Create a clean copy of the frame for display with annotations
    display_frame = frame.copy()
    
    # Decode QR codes in the current frame
    decoded_objects = decode(frame)
    
    # Current set of codes in this frame
    current_codes = set()
    
    for obj in decoded_objects:
        # Get data
        data = obj.data.decode('utf-8')
        type_name = obj.type
        current_codes.add(data)
        
        # Check if this is a new code
        if data not in last_codes:
            print(f"New {type_name} detected: {data}")
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
                    # Add to existing data
                    existing_data.append(json_obj)
                    
                    # Mark as processed
                    processed_json_strings.add(json_str)
                    
                    # Write back to file
                    with open(json_file_path, 'w') as f:
                        json.dump(existing_data, f, indent=2)
                    
                    print("Appended new JSON data to data.json")
                else:
                    print("Duplicate JSON data - not appending")
                    
            except Exception as e:
                print(f"Error processing JSON data: {e}")
        
        # Draw rectangle around the code
        points = obj.polygon
        if len(points) > 0:
            pts = [(p.x, p.y) for p in points]
            pts = np.array(pts, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(display_frame, [pts], True, (0, 255, 0), 3)
            
        # Add text label
        x, y, w, h = obj.rect
        cv2.putText(display_frame, f"{type_name}: {data[:20]}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Update the set of previously seen codes
    last_codes = current_codes
    
    # Display the frame with annotations
    cv2.imshow('Live QR Code Scanner', display_frame)
    
    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key
        break
    elif key == ord('s'):  # 's' key to save current frame
        if len(decoded_objects) > 0:
            timestamp = cv2.getTickCount()
            save_path = os.path.join(result_folder, f"scan_{timestamp}.png")
            cv2.imwrite(save_path, display_frame)
            print(f"Saved frame with QR codes to {save_path}")
        else:
            print("No QR codes detected in current frame - not saving")

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
print("Scanner stopped")