# Computer Control Interface Documentation

This interface provides a streamlined way for Claude to control a computer through API endpoints while viewing a live desktop stream.

## Core Components

1. Desktop Stream
- Automatically starts when connecting to http://localhost:5000
- Provides a 900x600 viewport of the desktop
- Streams at 30 FPS

2. API Endpoints

### Computer Control (`/api/computer`)

#### Mouse Movement
```json
POST /api/computer
{
    "action": "mouse_move",
    "coordinate": [x, y]  // x,y coordinates within 900x600 viewport
}
```

#### Keyboard Input
```json
POST /api/computer
{
    "action": "type",
    "text": "Text to type"
}
```

#### Special Keys
```json
POST /api/computer
{
    "action": "key",
    "text": "key_name"  // e.g., "Windows+r", "Enter", etc.
}
```

#### Get Cursor Position
```json
POST /api/computer
{
    "action": "cursor_position"
}
```

### Command Execution

#### PowerShell Commands
```json
POST /api/powershell
{
    "command": "command_to_execute"
}
```

#### Bash Commands
```json
POST /api/bash
{
    "command": "command_to_execute"
}
```

## Example Usage

1. Opening Notepad and Typing:
```powershell
# Open Run dialog
$body = @{action='key';text='Windows+r'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:5000/api/computer' -Method Post -Body $body -ContentType 'application/json'

# Type 'notepad' and press Enter
$body = @{action='type';text='notepad'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:5000/api/computer' -Method Post -Body $body -ContentType 'application/json'

$body = @{action='key';text='Enter'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:5000/api/computer' -Method Post -Body $body -ContentType 'application/json'

# Type text in Notepad
$body = @{action='type';text='Hello from the computer control interface!'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:5000/api/computer' -Method Post -Body $body -ContentType 'application/json'
```

2. Moving Mouse to Coordinates:
```powershell
$body = @{action='mouse_move';coordinate=@(450,300)} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:5000/api/computer' -Method Post -Body $body -ContentType 'application/json'
```

## Best Practices

1. Coordinate System
   - The viewport is fixed at 900x600 pixels
   - Coordinates should be within these bounds
   - (0,0) is the top-left corner

2. Keyboard Input
   - Use the 'type' action for regular text input
   - Use the 'key' action for special keys and combinations
   - Common special keys: 'Enter', 'Tab', 'Windows+r', 'Ctrl+c', etc.

3. Timing
   - Add delays between actions when needed (e.g., Start-Sleep -Milliseconds 500)
   - Allow time for applications to open or respond
   - Consider system responsiveness when chaining multiple actions

4. Error Handling
   - All endpoints return JSON responses
   - Check 'success' field in responses
   - Handle potential errors gracefully

## Implementation Notes

- The interface automatically starts streaming when a client connects
- No UI elements are present to maximize viewport space
- All interactions are handled through API endpoints
- The server runs on localhost:5000 by default
