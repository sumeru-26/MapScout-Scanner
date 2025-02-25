import cv2
import os
import numpy as np
from pyzbar.pyzbar import decode

# Define the image path
image_path = os.path.join(os.path.dirname(__file__), 'image.png')

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