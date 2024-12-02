import base64
import json

# Read the base64 data from file
with open('screenshot_response.txt', 'r') as f:
    json_data = json.loads(f.read())
    base64_data = json_data["screenshot"]

# Decode the base64 data
image_data = base64.b64decode(base64_data)

# Save as JPG
with open('decoded_image.jpg', 'wb') as f:
    f.write(image_data)
