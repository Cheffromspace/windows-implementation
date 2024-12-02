# Computer Control API Usage

Start the API server:
```bash
uvicorn api_endpoints:app --reload
```

## Endpoints

### Get Screenshot
Returns base64 encoded JPEG of current desktop
```bash
curl http://127.0.0.1:8000/screenshot
```

### Get Screen Size
Returns screen dimensions
```bash
curl http://127.0.0.1:8000/screen/size
```

### Mouse Control

Move mouse to coordinates:
```bash
curl -X POST http://127.0.0.1:8000/mouse/move \
  -H "Content-Type: application/json" \
  -d '{"x": 500, "y": 300}'
```

Click mouse:
```bash
curl -X POST http://127.0.0.1:8000/mouse/click \
  -H "Content-Type: application/json" \
  -d '"left"'  # or "right" for right click
```

Double click:
```bash
# At current position
curl -X POST http://127.0.0.1:8000/mouse/double-click

# At specific coordinates
curl -X POST http://127.0.0.1:8000/mouse/double-click \
  -H "Content-Type: application/json" \
  -d '{"x": 500, "y": 300}'
```

Get cursor position:
```bash
curl http://127.0.0.1:8000/mouse/position
```

### Keyboard Control

Press a key:
```bash
# Simple key press
curl -X POST http://127.0.0.1:8000/keyboard/press \
  -H "Content-Type: application/json" \
  -d '{"key": "a"}'

# Key combination (Ctrl+C)
curl -X POST http://127.0.0.1:8000/keyboard/press \
  -H "Content-Type: application/json" \
  -d '{"key": "c", "ctrl": true}'
```

Type text:
```bash
curl -X POST http://127.0.0.1:8000/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!"}'
```

## Example Response Formats

Screenshot response:
```json
{
    "screenshot": "base64_encoded_jpeg_data..."
}
```

Screen size response:
```json
{
    "width": 1920,
    "height": 1080
}
```

Mouse position response:
```json
{
    "x": 500,
    "y": 300
}
```

Action responses:
```json
{
    "success": true
}
```

Error response:
```json
{
    "detail": "Error message here"
}
